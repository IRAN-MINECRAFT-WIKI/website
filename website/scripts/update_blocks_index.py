#!/usr/bin/env python3
"""Update src/data/blocks/index.json to include newly-added block files.

Reads every src/data/blocks/*.json (except index.json itself) and rebuilds
the "blocks" array with minimal {id, nameEn, nameFa, category, icon} entries.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCKS_DIR = ROOT / "src" / "data" / "blocks"
INDEX = BLOCKS_DIR / "index.json"


def main() -> int:
    # Load existing index to preserve top-level keys (intro, behavior, etc.)
    with open(INDEX, encoding="utf-8") as f:
        data = json.load(f)

    # Collect every block file's minimal entry.
    entries = []
    seen_ids = set()
    for fp in sorted(BLOCKS_DIR.glob("*.json")):
        if fp.name == "index.json":
            continue
        try:
            with open(fp, encoding="utf-8") as f:
                b = json.load(f)
        except json.JSONDecodeError as e:
            print(f"   ! parse error in {fp.name}: {e}")
            continue
        if "id" not in b or "nameEn" not in b or "nameFa" not in b:
            print(f"   ! missing required keys in {fp.name}")
            continue
        if b["id"] in seen_ids:
            # Duplicate id (shouldn't happen) — skip.
            continue
        seen_ids.add(b["id"])
        entries.append({
            "id": b["id"],
            "nameEn": b["nameEn"],
            "nameFa": b["nameFa"],
            "category": b.get("category", "?"),
            "icon": b.get("icon", b["id"]),
        })

    # Preserve original ordering: keep existing index entries first (in their
    # original order), then append new entries that weren't in the original.
    original_ids = [e["id"] for e in data.get("blocks", [])]
    by_id = {e["id"]: e for e in entries}
    ordered = []
    for oid in original_ids:
        if oid in by_id:
            ordered.append(by_id.pop(oid))
    # Then append any new entries (sorted by id for stability).
    for e in sorted(by_id.values(), key=lambda x: x["id"]):
        ordered.append(e)

    data["blocks"] = ordered
    INDEX.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")
    print(f">> index.json now contains {len(ordered)} block entries")
    print(f"   (added {len(ordered) - len(original_ids)} new entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
