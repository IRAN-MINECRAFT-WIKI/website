"""
MineBed Admin — mods.json CRUD.

Reads and writes the local ``mods.json`` file in the Astro website data
directory.  Each mod has a stable ``id`` (slug) so the UI can update /
delete them.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from . import config


def _path() -> Path:
    p = config.MODS_JSON_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load() -> list[dict]:
    p = _path()
    if not p.exists():
        return []
    try:
        raw = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except Exception:
        return []
    # Accept either a bare array or an object with ``mods`` key.
    if isinstance(data, dict):
        mods = data.get("mods") or data.get("data") or []
    else:
        mods = data
    return [m for m in mods if isinstance(m, dict)]


def _save(mods: list[dict]) -> None:
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(mods, ensure_ascii=False, indent=2),
                 encoding="utf-8")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def list_all() -> list[dict]:
    """Return all mods as a list."""
    return _load()


def get(mod_id: str) -> Optional[dict]:
    for m in _load():
        if str(m.get("id") or m.get("slug") or "") == str(mod_id):
            return m
    return None


def exists(slug: str) -> bool:
    return get(slug) is not None


def add(mod: dict) -> dict:
    """Add or replace a mod (by id/slug)."""
    mods = _load()
    mid = str(mod.get("id") or mod.get("slug") or "")
    if not mid:
        mid = mod.get("url", "").rsplit("/", 1)[-1] or f"mod-{int(time.time())}"
        mod["id"] = mid
    else:
        mod.setdefault("id", mid)

    # Replace if exists, else append
    replaced = False
    for i, m in enumerate(mods):
        if str(m.get("id") or m.get("slug") or "") == mid:
            mods[i] = mod
            replaced = True
            break
    if not replaced:
        mods.append(mod)
    _save(mods)
    return mod


def delete(mod_id: str) -> bool:
    mods = _load()
    before = len(mods)
    mods = [m for m in mods
            if str(m.get("id") or m.get("slug") or "") != str(mod_id)]
    _save(mods)
    return len(mods) < before


def count() -> int:
    return len(_load())


def export_json() -> str:
    """Return the current mods.json as a pretty JSON string."""
    return json.dumps(_load(), ensure_ascii=False, indent=2)


def build_mod_record(crawled: dict, ai: dict) -> dict:
    """
    Combine crawled page data + Agnes AI content into a single mod record
    that matches the website's TypeScript ``Mod`` type (see website/src/lib/data.ts).

    Required fields per Mod type:
      id, name, nameFa, category (cat ID like "gameplay"), tagline, desc, downloadUrl
    Optional fields:
      keywords (space-separated string), catName (Persian), icon, version, size,
      downloads, cover, gallery, featured, isNew, author, updated
    """
    slug = crawled.get("slug") or crawled.get("url", "").rsplit("/", 1)[-1]

    # Category — must be a cat ID (gameplay, graphics, maps, ...) not Persian name
    cat_id = ai.get("category") or "gameplay"
    cat_name_map = {
        "gameplay": "گیم\u200cپلی",
        "graphics": "گرافیک",
        "maps": "مپ",
        "mobs": "موجودات",
        "decoration": "دکوراسیون",
        "world": "دنیا",
        "utility": "ابزار",
    }
    cat_name = cat_name_map.get(cat_id, "ماد")

    # Keywords — must be a space-separated string, not a list
    keywords = ai.get("keywords") or ""
    if isinstance(keywords, list):
        keywords = " ".join(str(k) for k in keywords)

    # Pick the best download URL from crawled files (prefer .mcaddon, then .mcpack)
    files = crawled.get("files") or []
    download_url = ai.get("download") or ""
    if not download_url and files:
        # Prefer combined .mcaddon over .mcpack
        for f in files:
            name = (f.get("name") or "").lower()
            if name.endswith(".mcaddon"):
                download_url = f.get("link") or f.get("url") or ""
                break
        if not download_url:
            download_url = files[0].get("link") or files[0].get("url") or ""

    # Compute human-readable size from first file if available
    size = ""
    if files:
        first_size = files[0].get("size")
        if first_size:
            try:
                # If numeric (bytes), format as MB
                if isinstance(first_size, (int, float)) or (
                    isinstance(first_size, str) and first_size.isdigit()
                ):
                    bytes_ = int(first_size)
                    if bytes_ >= 1024 * 1024:
                        size = f"{bytes_ / (1024 * 1024):.1f} MB"
                    else:
                        size = f"{bytes_ / 1024:.1f} KB"
                else:
                    size = str(first_size)
            except Exception:
                size = str(first_size)

    return {
        "id": slug,
        "name": crawled.get("title") or ai.get("nameFa") or slug,
        "nameFa": ai.get("nameFa") or crawled.get("title") or slug,
        "keywords": keywords,
        "category": cat_id,
        "catName": cat_name,
        "tagline": ai.get("tagline") or "",
        "desc": ai.get("desc") or crawled.get("description") or "",
        "icon": "🎮",
        "version": crawled.get("version") or "",
        "size": size,
        "downloads": "0",
        "downloadUrl": download_url,
        "cover": crawled.get("cover"),
        "gallery": crawled.get("gallery") or [],
        "featured": False,
        "isNew": True,
        "author": crawled.get("author") or "",
        "updated": crawled.get("updated") or "",
        "source": crawled.get("url"),
        "aiGenerated": bool(ai.get("_ai_used")),
        "createdAt": int(time.time()),
    }
