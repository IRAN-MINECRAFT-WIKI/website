"""
run.py — Daily auto-run entrypoint for the MineBed pipeline.

Designed to be called from GitHub Actions (cron) and reads the list of
mod URLs from `pipeline/urls.txt`. For each URL, the full pipeline
(crawl → AI write → download → upload to HF → update mods.json on GitHub)
is run.

Usage (local):
    cd pipeline
    python run.py

Usage (CI):
    python pipeline/run.py --auto 5 --urls-file pipeline/urls.txt
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Make sibling modules importable when run from CI (cd website/src/data)
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

DEFAULT_URLS_FILE = BASE_DIR / "urls.txt"


def read_urls(path: Path, limit: int = 0) -> list[dict]:
    """Read URLs from file. Optionally limit to first N entries."""
    if not path.exists():
        print(f"\u26a0\ufe0f  URLs file not found: {path}")
        return []
    urls = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        slug = urlparse(line).path.strip("/").split("/")[-1] or "mod"
        urls.append({"slug": slug, "url": line})
        if limit and len(urls) >= limit:
            break
    return urls


def fetch_remote_mods_json():
    """Fetch current mods.json from GitHub via sync_from_github helpers."""
    try:
        from sync_from_github import fetch_file_from_github, MODS_FILE
    except ImportError as e:
        print(f"\u274c  Cannot import sync_from_github: {e}")
        return None, None
    return fetch_file_from_github(MODS_FILE)


def push_mods_json_to_github(mods_data: dict) -> tuple[bool, str]:
    """Push updated mods.json back to GitHub."""
    try:
        from sync_from_github import (
            save_file_to_github,
            MODS_FILE,
            fetch_file_from_github,
        )
    except ImportError as e:
        return False, f"Cannot import sync_from_github: {e}"

    # Get current SHA so we can update (not create)
    existing, sha = fetch_file_from_github(MODS_FILE)
    return save_file_to_github(
        MODS_FILE, mods_data, "chore: daily mod sync", sha=sha
    )


def merge_new_mods(existing: list, new_mods: list) -> tuple[list, int, int]:
    """Merge new mods into existing list, return (merged, added, updated)."""
    by_id = {str(m.get("id") or m.get("slug") or ""): m for m in existing}
    added = 0
    updated = 0
    for mod in new_mods:
        mid = str(mod.get("id") or mod.get("slug") or "")
        if not mid:
            continue
        if mid in by_id:
            by_id[mid].update(mod)
            updated += 1
        else:
            by_id[mid] = mod
            added += 1
    return list(by_id.values()), added, updated


async def process_one(entry: dict) -> dict | None:
    """Process a single URL entry — fetch metadata + AI-generate Persian content.

    NOTE: This is a simplified version. For full pipeline with file crawling,
    use the admin desktop app's crawler module which is more complete.
    """
    try:
        from ai_writer import generate_persian_content
    except ImportError as e:
        print(f"\u274c  Cannot import ai_writer: {e}")
        return None

    slug = entry["slug"]
    url = entry["url"]
    print(f"\n\U0001f3af  Processing: {slug}")

    # Stage 1: build a minimal page_data stub from the URL alone
    # (In production, the admin crawler would have populated real page data;
    #  CI mode is a no-op placeholder for URL discovery — actual crawling
    #  happens through the admin desktop app.)
    page_data = {
        "title": slug.replace("-", " ").title(),
        "tagline": "",
        "author": "",
        "version": "",
        "tags": [],
        "description": "",
        "full_text": "",
        "url": url,
    }

    # Stage 2: generate Persian content via LM Studio
    result = generate_persian_content(page_data)
    if not result:
        print(f"\u26a0\ufe0f  AI generation failed for {slug}, skipping")
        return None

    # Stage 3: build a mod record that matches the website's Mod type
    cat_id = result.get("category", "gameplay") or "gameplay"
    cat_name_map = {
        "gameplay": "\u06af\u06cc\u0645\u200c\u067e\u0644\u06cc",
        "graphics": "\u06af\u0631\u0627\u0641\u06cc\u06a9",
        "maps": "\u0645\u067e",
        "mobs": "\u0645\u0648\u062c\u0648\u062f\u0627\u062a",
        "decoration": "\u062f\u06a9\u0648\u0631\u0627\u0633\u06cc\u0648\u0646",
        "world": "\u062f\u0646\u06cc\u0627",
        "utility": "\u0627\u0628\u0632\u0627\u0631",
    }
    keywords = result.get("keywords", "")
    if isinstance(keywords, list):
        keywords = " ".join(str(k) for k in keywords)

    return {
        "id": slug,
        "name": page_data["title"],
        "nameFa": result.get("nameFa") or page_data["title"],
        "keywords": keywords,
        "category": cat_id,
        "catName": cat_name_map.get(cat_id, "\u0645\u0627\u062f"),
        "tagline": result.get("tagline", ""),
        "desc": result.get("desc", ""),
        "icon": "\U0001f3ae",
        "version": "",
        "size": "",
        "downloads": "0",
        "downloadUrl": "",
        "cover": "",
        "gallery": [],
        "featured": False,
        "isNew": True,
        "author": "",
        "updated": "",
        "source": url,
    }


async def main(args):
    urls = read_urls(args.urls_file, limit=args.auto)
    if not urls:
        print(f"\u274c  No URLs in {args.urls_file}")
        return 1

    print(f"\U0001f3af  Processing {len(urls)} mods from {args.urls_file}")

    # Fetch existing mods.json from GitHub
    remote_data, sha = fetch_remote_mods_json()
    existing_mods = []
    if remote_data and isinstance(remote_data, dict):
        existing_mods = remote_data.get("mods", [])
    elif remote_data and isinstance(remote_data, list):
        existing_mods = remote_data

    print(f"\U0001f4c5  Remote mods.json has {len(existing_mods)} mods")

    # Process each URL
    new_mods = []
    for entry in urls:
        mod = await process_one(entry)
        if mod:
            new_mods.append(mod)

    if not new_mods:
        print("\u26a0\ufe0f  No mods were processed successfully.")
        return 0

    print(f"\n\u2705  {len(new_mods)} mods ready for merge")

    # Merge into existing mods
    merged, added, updated = merge_new_mods(existing_mods, new_mods)
    print(f"\U0001f4ca  +{added} new, ~{updated} updated")

    # Auto-approve in CI mode — push back to GitHub
    if args.auto_approve:
        print("\U0001f916  Auto-approving all mods, pushing to GitHub...")
        mods_payload = {"mods": merged}
        ok, info = push_mods_json_to_github(mods_payload)
        if ok:
            print(f"\u2705  mods.json pushed to GitHub")
        else:
            print(f"\u274c  Push failed: {info}")
            return 1
    else:
        print("\n\U0001f4cb  To review manually, run the admin desktop app.")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MineBed pipeline")
    parser.add_argument(
        "--urls-file",
        type=Path,
        default=DEFAULT_URLS_FILE,
        help="Path to URLs file (one URL per line)",
    )
    parser.add_argument(
        "--auto",
        type=int,
        default=0,
        help="Limit to N URLs (0 = all). CI passes --auto 5",
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        default=True,
        help="Auto-approve all crawled mods (default for CI)",
    )
    args = parser.parse_args()

    sys.exit(asyncio.run(main(args)))
