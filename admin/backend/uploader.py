"""
uploader.py — Mirrors MCPEDL assets (cover, screenshots, mod files) to
HuggingFace Datasets so the website is not dependent on MCPEDL's CDN
(which is often slow or blocked in Iran).

This is now wired into the autofetch worker (see main.py::_autofetch_worker)
so every mod that gets approved has its assets mirrored to HuggingFace
automatically.  If HF credentials are missing or the upload fails, we
gracefully fall back to the original MCPEDL URLs — the mod is still
usable, just slower for Iranian users.

Public API
----------
    process_mod_assets(mod_record: dict, on_progress=None) -> dict
        Returns a copy of mod_record with cover/gallery/downloadUrl
        replaced by HuggingFace URLs where the upload succeeded.
"""
from __future__ import annotations

import re
import urllib.parse
from pathlib import Path
from typing import Callable, Optional

import requests

from . import config

try:
    from huggingface_hub import HfApi
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


ProgressFn = Optional[Callable[[str, str], None]]


# ---------------------------------------------------------------------------
# HTTP downloader
# ---------------------------------------------------------------------------
def download_file(url: str, save_path: Path,
                  referer: str = "https://mcpedl.com/") -> Optional[Path]:
    """Download a file from ``url`` to ``save_path`` (without extension).

    The actual final path includes an extension discovered from
    Content-Type, URL, or magic bytes.  Returns the final Path, or
    None on failure.
    """
    try:
        r = requests.get(
            url,
            headers={
                "User-Agent": config.CRAWLER_USER_AGENT,
                "Referer": referer,
            },
            timeout=60,
            stream=True,
        )
        if r.status_code != 200:
            return None

        content_type = r.headers.get("Content-Type", "").lower()
        ext_map = {
            "image/png": ".png", "image/jpeg": ".jpg", "image/jpg": ".jpg",
            "image/webp": ".webp", "image/gif": ".gif", "image/avif": ".avif",
            "application/zip": ".zip",
            "application/octet-stream": "",
            "application/x-mcpack": ".mcpack",
            "application/x-mcaddon": ".mcaddon",
            "application/x-mcworld": ".mcworld",
        }
        ext = ext_map.get(content_type, "")

        if not ext:
            url_path = url.split("?")[0].lower()
            for e in [".gif", ".png", ".jpg", ".jpeg", ".webp", ".avif",
                      ".mcpack", ".mcaddon", ".mcworld", ".zip"]:
                if url_path.endswith(e):
                    ext = e
                    break

        save_path.parent.mkdir(parents=True, exist_ok=True)

        if not ext:
            # Sniff magic bytes
            first_bytes = next(r.iter_content(1024), b"")
            if first_bytes[:8] == b'\x89PNG\r\n\x1a\n':
                ext = ".png"
            elif first_bytes[:3] == b'\xff\xd8\xff':
                ext = ".jpg"
            elif first_bytes[:6] in (b'GIF87a', b'GIF89a'):
                ext = ".gif"
            elif first_bytes[:4] == b'RIFF' and len(first_bytes) > 12 \
                    and first_bytes[8:12] == b'WEBP':
                ext = ".webp"
            elif first_bytes[:2] == b'PK':
                ext = ".zip"  # .mcpack/.mcaddon are zip files
            else:
                ext = ".bin"

            final_path = Path(str(save_path) + ext)
            with open(final_path, "wb") as f:
                f.write(first_bytes)
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return final_path

        final_path = Path(str(save_path) + ext)
        with open(final_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return final_path

    except Exception as e:
        print(f"  [uploader] Download error: {e}")
        return None


# ---------------------------------------------------------------------------
# HuggingFace uploader
# ---------------------------------------------------------------------------
def upload_to_huggingface(
    slug: str,
    file_path: Path,
    hf_token: Optional[str] = None,
    hf_repo_id: Optional[str] = None,
) -> Optional[str]:
    """Upload a file to the HuggingFace dataset at ``{slug}/{filename}``.

    Returns the public resolve URL on success, or None on failure.
    If HF credentials are missing or the package isn't installed,
    returns None silently (the caller falls back to the original URL).
    """
    if not HF_AVAILABLE:
        return None
    token = hf_token or config.HF_TOKEN
    repo_id = hf_repo_id or config.HF_REPO_ID
    if not token or not repo_id:
        return None

    try:
        api = HfApi()

        # Ensure the dataset repo exists (create if missing)
        try:
            api.repo_info(repo_id=repo_id, repo_type="dataset", token=token)
        except Exception:
            api.create_repo(
                repo_id=repo_id, repo_type="dataset",
                token=token, private=False, exist_ok=True,
            )

        filename = file_path.name
        path_in_repo = f"{slug}/{filename}"

        api.upload_file(
            path_or_fileobj=str(file_path),
            path_in_repo=path_in_repo,
            repo_id=repo_id,
            repo_type="dataset",
            token=token,
        )

        safe_name = urllib.parse.quote(filename)
        return f"https://huggingface.co/datasets/{repo_id}/resolve/main/{slug}/{safe_name}"

    except Exception as e:
        print(f"  [uploader] HF upload error: {e}")
        return None


# ---------------------------------------------------------------------------
# High-level orchestrator
# ---------------------------------------------------------------------------
def process_mod_assets(
    mod_record: dict,
    hf_token: Optional[str] = None,
    hf_repo_id: Optional[str] = None,
    cache_dir: Optional[Path] = None,
    on_progress: ProgressFn = None,
) -> dict:
    """Mirror a mod's assets (cover, gallery, mod file) to HuggingFace.

    Returns a copy of ``mod_record`` with cover / gallery / downloadUrl
    replaced by HuggingFace URLs where the upload succeeded.  Failures
    are non-fatal — we just keep the original MCPEDL URL so the mod
    still works, just slower.

    Args:
        mod_record: a mod record in the website's Mod shape
            (must have at least ``id``/``slug``; ``cover``, ``gallery``,
             ``downloadUrl`` are optional).
        hf_token: HuggingFace token. Defaults to ``config.HF_TOKEN``.
        hf_repo_id: HuggingFace dataset repo. Defaults to ``config.HF_REPO_ID``.
        cache_dir: where to store downloaded files before upload. Defaults
            to a temp dir under ``cache/{slug}``.
        on_progress: callback ``(phase, message)`` for live logging.
    """
    def log(msg: str) -> None:
        if on_progress:
            on_progress("upload", msg)

    token = hf_token or config.HF_TOKEN
    repo_id = hf_repo_id or config.HF_REPO_ID

    slug = str(mod_record.get("id") or mod_record.get("slug") or "unknown")
    cache_base = cache_dir or (Path("cache") / slug)
    cache_base.mkdir(parents=True, exist_ok=True)

    updated = dict(mod_record)  # shallow copy — we don't mutate nested lists

    if not token or not repo_id or not HF_AVAILABLE:
        log("HuggingFace not configured — skipping asset mirroring")
        return updated

    # 1. Cover image
    cover_url = mod_record.get("cover", "") or ""
    if cover_url.startswith("http") and "huggingface.co" not in cover_url:
        log(f"  mirroring cover → {cover_url[:60]}…")
        cover_path = download_file(cover_url, cache_base / "cover")
        if cover_path:
            hf_url = upload_to_huggingface(slug, cover_path, token, repo_id)
            if hf_url:
                updated["cover"] = hf_url
                log(f"  ✓ cover on HF")
                try:
                    cover_path.unlink(missing_ok=True)
                except Exception:
                    pass
            else:
                log("  ! cover upload failed — keeping original URL")
        else:
            log("  ! cover download failed — keeping original URL")

    # 2. Gallery images (mirror up to 8, keep ALL original URLs)
    gallery = list(mod_record.get("gallery") or [])
    new_gallery = []
    # Process the first 8 with HuggingFace mirroring
    for i, img_url in enumerate(gallery[:8]):
        if not img_url or not isinstance(img_url, str) \
                or not img_url.startswith("http") \
                or "huggingface.co" in img_url:
            new_gallery.append(img_url)
            continue
        log(f"  mirroring gallery {i + 1}/{min(8, len(gallery))}…")
        img_path = download_file(img_url, cache_base / f"screenshot_{i + 1}")
        if img_path:
            hf_url = upload_to_huggingface(slug, img_path, token, repo_id)
            new_gallery.append(hf_url if hf_url else img_url)
            if hf_url:
                try:
                    img_path.unlink(missing_ok=True)
                except Exception:
                    pass
        else:
            new_gallery.append(img_url)
    # Preserve any gallery items beyond the first 8 (don't drop them!)
    if len(gallery) > 8:
        new_gallery.extend(gallery[8:])
    updated["gallery"] = new_gallery

    # 3. Mod file (.mcpack / .mcaddon / .mcworld)
    download_url = mod_record.get("downloadUrl", "") or ""
    if download_url.startswith("http") and "huggingface.co" not in download_url:
        log(f"  mirroring mod file → {download_url[:60]}…")
        # Discover a clean filename — many MCPEDL download URLs redirect
        # to a generic name; we use the mod slug + original extension.
        url_path = download_url.split("?")[0]
        ext = ""
        for e in [".mcpack", ".mcaddon", ".mcworld", ".zip"]:
            if url_path.lower().endswith(e):
                ext = e
                break
        if not ext:
            # Default to .mcaddon for Bedrock content
            ext = ".mcaddon"
        mod_path = download_file(download_url, cache_base / f"{slug}{ext}")
        if mod_path:
            hf_url = upload_to_huggingface(slug, mod_path, token, repo_id)
            if hf_url:
                updated["downloadUrl"] = hf_url
                log(f"  ✓ mod file on HF")
                try:
                    mod_path.unlink(missing_ok=True)
                except Exception:
                    pass
            else:
                log("  ! mod file upload failed — keeping original URL")
        else:
            log("  ! mod file download failed — keeping original URL")

    # Cleanup empty cache dir
    try:
        cache_base.rmdir()  # only succeeds if empty
    except Exception:
        pass

    return updated
