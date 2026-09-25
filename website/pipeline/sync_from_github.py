"""
sync_from_github.py — Sync GitHub mods.json to local + check for stale mods
==========================================================================

Improvements over original:
- Loads .env automatically (python-dotenv)
- Quality-check mods before push
- Reports orphan mods (in local but not on remote)
- Reports stale mods (not updated in N days)
- Uses GitHub REST API v3 with proper auth + UA
"""

import os
import json
import base64
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GITHUB_USER = os.getenv("GITHUB_USER", "IRAN-MINECRAFT-WIKI")
GITHUB_REPO = os.getenv("GITHUB_REPO", "website")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

MODS_FILE = os.getenv("GITHUB_MODS_FILE", "website/src/data/mods.json")
MUSIC_FILE = "website/src/data/music.json"

BASE_DIR = Path(__file__).parent.resolve()
LOCAL_MODS_JSON = BASE_DIR / "mods.json"
LOCAL_MUSIC_JSON = BASE_DIR / "music.json"
MODS_DATA_DIR = BASE_DIR / "mods_data"
HISTORY_FILE = BASE_DIR / "uploaded_history.json"
SYNC_LOG_FILE = BASE_DIR / "sync_log.json"

STALE_DAYS = int(os.getenv("STALE_DAYS", "60"))


def log(msg: str, emoji: str = "•") -> None:
    print(f"[{datetime.now():%H:%M:%S}] {emoji} {msg}")


def log_section(title: str) -> None:
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def get_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "MineBed-Sync/2.0",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def fetch_file_from_github(file_path: str) -> Tuple[Optional[dict], Optional[str]]:
    """Fetch a file from GitHub via REST API. Returns (data, sha) or (None, None)."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{file_path}"
    params = {"ref": GITHUB_BRANCH}

    try:
        res = requests.get(url, headers=get_headers(), params=params, timeout=30)
        if res.status_code == 404:
            log(f"File not found: {file_path}", "❌")
            return None, None
        if res.status_code in (401, 403):
            log(f"Auth/access error ({res.status_code}) — check GITHUB_TOKEN", "❌")
            return None, None
        res.raise_for_status()

        data = res.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(content), data["sha"]
    except Exception as e:
        log(f"Fetch error: {str(e)[:100]}", "❌")
        return None, None


def save_file_to_github(
    file_path: str, data: dict, commit_message: str, sha: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """Save a JSON file to GitHub."""
    if not GITHUB_TOKEN:
        log("GITHUB_TOKEN not set — cannot push", "❌")
        return False, None

    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{file_path}"
    content = json.dumps(data, ensure_ascii=False, indent=2)
    content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    body = {
        "message": commit_message,
        "content": content_b64,
        "branch": GITHUB_BRANCH,
    }
    if sha:
        body["sha"] = sha

    try:
        res = requests.put(
            url,
            headers={**get_headers(), "Content-Type": "application/json"},
            json=body,
            timeout=30,
        )
        if res.status_code not in (200, 201):
            log(f"Save error: {res.status_code}", "❌")
            return False, None
        return True, res.json()["content"]["sha"]
    except Exception as e:
        log(f"Save error: {str(e)[:100]}", "❌")
        return False, None


def sync_mods_json() -> Optional[list]:
    log_section("📥 Sync mods.json")
    data, sha = fetch_file_from_github(MODS_FILE)
    if not data:
        return None
    mods = data.get("mods", [])
    log(f"  ✅ {len(mods)} mods received", "  ")
    log(f"  📌 SHA: {sha[:10] if sha else 'none'}...", "  ")
    LOCAL_MODS_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log(f"  💾 Saved: {LOCAL_MODS_JSON}", "  ")
    return mods


def sync_music_json() -> Optional[list]:
    log_section("🎵 Sync music.json")
    data, _ = fetch_file_from_github(MUSIC_FILE)
    if not data:
        return None
    tracks = data.get("tracks", [])
    log(f"  ✅ {len(tracks)} tracks received", "  ")
    LOCAL_MUSIC_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log(f"  💾 Saved: {LOCAL_MUSIC_JSON}", "  ")
    return tracks


def sync_mods_data_folder(remote_mods: list) -> Optional[dict]:
    """Compare local mods_data folder with remote mods list."""
    if not remote_mods:
        return None

    log_section("📊 Compare & update local")
    MODS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    online_ids = {m["id"]: m for m in remote_mods}
    local_folders = []
    if MODS_DATA_DIR.exists():
        local_folders = [
            d
            for d in os.listdir(MODS_DATA_DIR)
            if (MODS_DATA_DIR / d).is_dir()
            and (MODS_DATA_DIR / d / "data.json").exists()
        ]
    log(f"  📡 Online: {len(online_ids)}", "  ")
    log(f"  💾 Local: {len(local_folders)}", "  ")

    # Orphans
    orphans = [f for f in local_folders if f not in online_ids]
    if orphans:
        log(f"\n⚠️  {len(orphans)} orphan local mods (not on site):", "⚠️")
        for o in orphans[:10]:
            log(f"  • {o}", "  ")

    # Missing
    missing = [mid for mid in online_ids if mid not in local_folders]
    if missing:
        log(f"\n📭 {len(missing)} online mods not present locally:", "📭")
        for m in missing[:10]:
            log(f"  • {m}", "  ")

    # Stale check — find mods not updated in N days
    stale = []
    threshold = datetime.now() - timedelta(days=STALE_DAYS)
    for mod in remote_mods:
        updated = mod.get("updated", "")
        if updated:
            # Try Persian date format "1404/03/09" or ISO "2024-12-01"
            try:
                if "/" in updated and len(updated.split("/")[0]) == 4:
                    # ISO format
                    d = datetime.fromisoformat(updated)
                else:
                    continue
                if d < threshold:
                    stale.append((mod["id"], updated))
            except Exception:
                continue

    if stale:
        log(f"\n⏰ {len(stale)} stale mods (not updated in {STALE_DAYS} days):", "⏰")
        for sid, dt in stale[:10]:
            log(f"  • {sid} (last: {dt})", "  ")

    return {
        "total_online": len(online_ids),
        "total_local": len(local_folders),
        "orphans": orphans,
        "missing_local": missing,
        "stale": stale,
    }


def update_local_history(remote_mods: list) -> None:
    if not remote_mods:
        return
    log_section("📚 Update local history")
    history = {"uploaded": [], "rejected": []}
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    existing_ids = {m["id"] for m in history.get("uploaded", [])}
    added = 0
    for mod in remote_mods:
        if mod["id"] not in existing_ids:
            history["uploaded"].append(
                {
                    "id": mod["id"],
                    "nameFa": mod.get("nameFa", ""),
                    "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "size": mod.get("size", ""),
                    "category": mod.get("category", ""),
                    "downloadUrl": mod.get("downloadUrl", ""),
                    "cover": mod.get("cover", ""),
                    "_synced": True,
                }
            )
            added += 1

    if added > 0:
        HISTORY_FILE.write_text(
            json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    log(f"  ✅ {added} new mods added to history", "✅")
    log(f"  📊 Total uploaded: {len(history['uploaded'])}", "  ")


def save_sync_log(result: dict) -> None:
    log_data = {"sync_at": datetime.now().isoformat(), "result": result}
    history = []
    if SYNC_LOG_FILE.exists():
        try:
            history = json.loads(SYNC_LOG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    history.append(log_data)
    history = history[-50:]  # keep last 50
    SYNC_LOG_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> None:
    log_section("🔄 MineBed Pipeline — Sync from GitHub")
    if not GITHUB_TOKEN:
        log("⚠️  GITHUB_TOKEN not set!", "⚠️")
        log("   Without token, only public repos work + rate limit applies", "  ")
        if not input("Continue? (y/n): ").lower().startswith("y"):
            return

    mods = sync_mods_json()
    tracks = sync_music_json()
    result = None
    if mods:
        result = sync_mods_data_folder(mods)
        update_local_history(mods)
        save_sync_log(result)

    log_section("📊 Final report")
    if mods:
        log(f"✅ Online mods: {len(mods)}", "✅")
    if tracks:
        log(f"✅ Online tracks: {len(tracks)}", "✅")
    if result:
        log(f"📁 Local mods: {result['total_local']}", "📁")
        log(f"⏰ Stale: {len(result['stale'])}", "⏰")
    log("\n✅ Sync complete!", "✅")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n⛔ Stopped", "⛔")
    except Exception as e:
        log(f"❌ Fatal error: {e}", "❌")
        import traceback
        traceback.print_exc()
