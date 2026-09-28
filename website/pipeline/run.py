"""
run.py — Daily auto-run entrypoint for the MineBed pipeline.

This is the CI entrypoint called from ``.github/workflows/pipeline.yml``.
It:

  1. Discovers the top-N newest MCPEDL mod URLs (using the admin
     crawler's ``fetch_top_mods``).
  2. For each URL:
     a. Crawls the mod page (admin crawler's ``crawl_mod``)
     b. Generates Persian content via Agnes AI (admin ``agnes`` module)
     c. Builds a website-shaped Mod record (admin ``mods.build_mod_record``)
     d. Mirrors cover/gallery/mod-file to HuggingFace (admin ``uploader``)
     e. Merges into existing ``mods.json``
  3. Pushes the merged ``mods.json`` back to GitHub.

This makes the daily cron actually do something useful (the previous
version was a no-op stub that only built a record from the URL alone,
without crawling).

Usage (local):
    cd admin
    python -m backend.pipeline_runner --auto 5

Usage (CI):
    PYTHONPATH=admin python -m backend.pipeline_runner --auto 5
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import datetime as _dt
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Optional

# Allow running both as ``python pipeline/run.py`` (legacy path) and
# ``python -m backend.pipeline_runner`` (preferred).
_HERE = Path(__file__).resolve().parent
_ADMIN_DIR = _HERE.parent.parent / "admin"
if _ADMIN_DIR.is_dir():
    sys.path.insert(0, str(_ADMIN_DIR))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import the admin backend modules — these are the canonical impls.
from backend import config, crawler, agnes, github_service, mods, uploader  # noqa: E402


# ---------------------------------------------------------------------------
# Mods.json sync (uses admin's github_service for proper format)
# ---------------------------------------------------------------------------
GITHUB_MODS_FILE = "website/src/data/mods.json"


def fetch_remote_mods() -> tuple[Optional[list], Optional[str]]:
    """Fetch current mods.json from GitHub + the blob SHA.

    Returns (mods_list, sha). Either may be None on failure.
    """
    if not config.GITHUB_TOKEN:
        print("❌  GITHUB_TOKEN not set — cannot fetch remote mods.json")
        return None, None

    import requests

    url = (f"https://api.github.com/repos/{config.GITHUB_USER}/"
           f"{config.GITHUB_REPO}/contents/{GITHUB_MODS_FILE}")
    try:
        r = requests.get(url,
                         headers={
                             "Authorization": f"Bearer {config.GITHUB_TOKEN}",
                             "Accept": "application/vnd.github+json",
                         },
                         params={"ref": config.GITHUB_BRANCH},
                         timeout=20)
        if r.status_code == 404:
            return [], None  # file doesn't exist yet — that's OK
        if r.status_code != 200:
            print(f"❌  GET mods.json → HTTP {r.status_code}: {r.text[:200]}")
            return None, None
        body = r.json()
        sha = body.get("sha")
        content_b64 = body.get("content", "") or ""
        content = base64.b64decode(content_b64).decode("utf-8", errors="replace")
        try:
            data = json.loads(content)
        except Exception:
            data = []
        if isinstance(data, dict):
            mods_list = data.get("mods") or []
        elif isinstance(data, list):
            mods_list = data
        else:
            mods_list = []
        return mods_list, sha
    except Exception as e:
        print(f"❌  Fetch mods.json failed: {e}")
        return None, None


def push_mods_to_github(mods_list: list, sha: Optional[str] = None) -> bool:
    """PUT the merged mods.json (in ``{ "mods": [...] }`` shape) to GitHub."""
    if not config.GITHUB_TOKEN:
        print("❌  GITHUB_TOKEN not set")
        return False

    import requests

    payload = {"mods": mods_list}
    content_b64 = base64.b64encode(
        json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode("ascii")

    body = {
        "message": (f"chore: daily mod sync — "
                    f"{_dt.datetime.now():%Y-%m-%d %H:%M} UTC"),
        "content": content_b64,
        "branch": config.GITHUB_BRANCH,
    }
    if sha:
        body["sha"] = sha

    url = (f"https://api.github.com/repos/{config.GITHUB_USER}/"
           f"{config.GITHUB_REPO}/contents/{GITHUB_MODS_FILE}")
    try:
        r = requests.put(
            url,
            headers={
                "Authorization": f"Bearer {config.GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
            },
            json=body,
            timeout=30,
        )
        if r.status_code in (200, 201):
            commit = r.json().get("commit", {})
            print(f"✅  Pushed mods.json — commit {commit.get('sha', '')[:7]}")
            return True
        print(f"❌  Push failed: HTTP {r.status_code}: {r.text[:300]}")
        return False
    except Exception as e:
        print(f"❌  Push error: {e}")
        return False


# ---------------------------------------------------------------------------
# Per-URL processing (crawl → AI → build → upload)
# ---------------------------------------------------------------------------
def process_one(url: str) -> Optional[dict]:
    """Crawl + AI-generate + mirror assets for a single mod URL.

    Returns the built mod record, or None on failure.
    """
    slug = crawler._slug_from_url(url)
    print(f"\n🎯  Processing: {slug}")
    print(f"    URL: {url}")

    # 1. Crawl
    try:
        page = crawler.crawl_mod(url)
    except Exception as e:
        print(f"    ! crawl error: {e}")
        return None
    if not page:
        print("    ! empty page, skipping")
        return None

    # 2. AI
    try:
        ai = agnes.generate_mod_content(page)
    except Exception as e:
        print(f"    ! AI error: {e}")
        ai = agnes._fallback(page)
        ai["_ai_used"] = False

    # 3. Build record (matches website's Mod type)
    record = mods.build_mod_record(page, ai)

    # 4. Mirror assets to HuggingFace (best-effort, non-fatal)
    if config.HF_TOKEN and uploader.HF_AVAILABLE:
        print("    → mirroring assets to HuggingFace…")
        try:
            record = uploader.process_mod_assets(record)
        except Exception as e:
            print(f"    ! asset mirror failed: {e}")
    else:
        print("    ~ HuggingFace not configured — keeping MCPEDL URLs")

    ai_used = "yes" if ai.get("_ai_used") else "no"
    print(f"    ✓ queued «{record.get('nameFa')}» (AI={ai_used})")
    return record


# ---------------------------------------------------------------------------
# Merge logic (idempotent — existing mods with same id are updated)
# ---------------------------------------------------------------------------
def merge_new_mods(existing: list, new_mods: list) -> tuple[list, int, int]:
    by_id = {str(m.get("id") or m.get("slug") or ""): m for m in existing}
    added = 0
    updated = 0
    for mod in new_mods:
        mid = str(mod.get("id") or mod.get("slug") or "")
        if not mid:
            continue
        if mid in by_id:
            # Update in place — preserve any manual flags (featured/isNew)
            # the admin set, but override content fields.
            old = by_id[mid]
            for k, v in mod.items():
                if k in ("featured", "isNew"):
                    continue  # don't auto-flip manual flags
                old[k] = v
            updated += 1
        else:
            by_id[mid] = mod
            added += 1
    return list(by_id.values()), added, updated


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
async def main(args):
    print("🚀  MineBed pipeline runner")
    print(f"    GITHUB_USER/REPO: {config.GITHUB_USER}/{config.GITHUB_REPO}")
    print(f"    GITHUB_BRANCH: {config.GITHUB_BRANCH}")
    print(f"    AGNES_MODEL: {config.AGNES_MODEL}")
    print(f"    HF_REPO_ID: {config.HF_REPO_ID}")
    print(f"    Auto-limit: {args.auto if args.auto else 'no limit'}")

    # 1. Fetch existing mods.json from GitHub
    print("\n📥  Fetching existing mods.json from GitHub…")
    existing, sha = fetch_remote_mods()
    if existing is None:
        print("❌  Cannot continue without mods.json baseline")
        return 1
    print(f"    Remote mods.json: {len(existing)} mods (sha={sha[:7] if sha else 'new'})")

    # 2. Discover top-N MCPEDL URLs
    print(f"\n🔍  Discovering top {args.auto} MCPEDL mods…")
    try:
        urls = crawler.fetch_top_mods(count=args.auto)
    except Exception as e:
        print(f"❌  Discovery failed: {e}")
        traceback.print_exc()
        return 1
    if not urls:
        print("    ⚠️  No URLs discovered — aborting")
        return 0

    # Dedup
    existing_ids = {str(m.get("id") or m.get("slug") or "") for m in existing}
    new_urls = [u for u in urls if crawler._slug_from_url(u) not in existing_ids]
    skipped = len(urls) - len(new_urls)
    print(f"    Found {len(urls)} URLs, {len(new_urls)} new, {skipped} already saved")

    if not new_urls:
        print("\n✅  Nothing new to add — exiting")
        return 0

    # 3. Process each URL
    new_mods = []
    for i, url in enumerate(new_urls, 1):
        print(f"\n[{i}/{len(new_urls)}]")
        mod = process_one(url)
        if mod:
            new_mods.append(mod)

    if not new_mods:
        print("\n⚠️  No mods were processed successfully.")
        return 0

    # 4. Merge
    print(f"\n📊  Merging {len(new_mods)} new mods into existing {len(existing)}…")
    merged, added, updated = merge_new_mods(existing, new_mods)
    print(f"    +{added} new, ~{updated} updated → {len(merged)} total")

    # 5. Push back to GitHub
    if args.push:
        print("\n📤  Pushing updated mods.json to GitHub…")
        ok = push_mods_to_github(merged, sha=sha)
        if not ok:
            print("❌  Push failed — see above")
            return 1
    else:
        print("\n   --no-push: skipping push (dry run)")

    print("\n✅  Done")
    return 0


def parse_args():
    p = argparse.ArgumentParser(description="MineBed pipeline runner (CI)")
    p.add_argument("--auto", type=int, default=5,
                   help="Limit to N URLs (default 5)")
    p.add_argument("--push", action="store_true", default=True,
                   help="Push updated mods.json to GitHub (default: true)")
    p.add_argument("--no-push", dest="push", action="store_false",
                   help="Don't push — dry run only")
    return p.parse_args()


if __name__ == "__main__":
    sys.exit(asyncio.run(main(parse_args())))
