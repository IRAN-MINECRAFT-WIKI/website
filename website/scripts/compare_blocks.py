#!/usr/bin/env python3
"""Compare our repo's blocks against minecraft.wiki's canonical Block list.

Steps:
1. Fetch Category:Blocks members from minecraft.wiki api.php (paginated).
2. Filter out April Fools / Education / removed-legacy / disambiguation / template pages.
3. Convert titles to kebab-case ids; apply manual mapping for known mismatches.
4. Diff against src/data/blocks/*.json (excluding index.json).
5. Write /tmp/wiki_blocks.txt (canonical) and /tmp/missing_blocks.txt (diff).
6. Print a human-readable summary.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

UA = "iran-minecraft-wiki/1.0 (github.com/IRAN-MINECRAFT-WIKI/website)"
API = "https://minecraft.wiki/api.php"
ROOT = Path(__file__).resolve().parents[1]
BLOCKS_DIR = ROOT / "src" / "data" / "blocks"

# ---------------------------------------------------------------------------
# 1. Filters
# ---------------------------------------------------------------------------

# April Fools (24w14potato snapshot) — block ids / titles we must drop.
# Matched against the kebab id, as substring (case-insensitive).
APRIL_FOOLS_SUBSTRINGS = (
    "potato", "poisonous", "taterstone", "potone", "sulfur", "cinnabar",
    "peelgrass", "terre-de-pomme", "funky-portal", "how-did-we-get-here",
    "swaggiest", "big-brain", "brittle-ice", "cheese", "floatater",
    "floatato", "gravtater", "powerful-potato", "vicious-potato",
    "potent-sulfur", "baked-potato-brick", "charred-baked", "expired-baked",
    "compressed-poisonous",
)

# Education Edition — drop by id substring.
EDUCATION_SUBSTRINGS = (
    "camera", "balloon", "chalkboard", "poster", "board", "slate",
    "compound", "element", "bleach", "ice-bomb", "sparkler", "medicine",
    "heat-block", "underwater-tnt", "underwater-torch", "glow-stick",
    "hardened-glass", "npc", "agent",
)

# Removed / legacy / "carried" data-version blocks — drop by id substring.
REMOVED_LEGACY_SUBSTRINGS = (
    "locked-chest", "deprecated", "six-sided-piston", "seamless-stone-slab",
    "grass-carried", "leaves-carried", "infinite-lava", "infinite-water",
    "attached-melon", "attached-pumpkin", "melon-stem", "pumpkin-stem",
    "frosted-ice", "cave-air", "void-air",
    "wool-slab", "wool-stairs", "wooden-slab", "wooden-stairs",
    "wooden-fence", "wooden-pressure-plate", "wooden-trapdoor",
    "wooden-door", "wooden-button",  # these are not real block ids
    "old-log", "old-wood", "old-stone", "paeonia", "etho-slab",
)

# Disambiguation / meta category pages — exact title match (after kebab).
DISAMBIG_EXACT = {
    "block", "blocks", "block-of", "block-sprite", "block-tag",
    "removed-blocks", "technical-blocks", "invisible-blocks",
    "interactable-blocks", "air", "structure-void", "light-block",
    "jigsaw-block",
    # These are real technical blocks that we keep — they're NOT in this set.
    # "allow", "deny", "border", "border-block", "structure-void",
}

# Pages with prefixes that are clearly not block pages.
PREFIX_BLOCKLIST = (
    "Category:", "Template:", "File:", "User:", "User talk:",
    "Minecraft Wiki:", "Help:", "Module:", "Talk:",
    "Block of the Month:", "Block sprite/", "Opacity/",
)

# Manual title → id mapping for known wiki/kebab mismatches.
# (Mostly obsolete "Wooden X" titles that should resolve to the Oak variant.)
MANUAL_MAP = {
    # The wiki sometimes lists "Wooden X" as a redirect-era title;
    # canonical block id is the oak variant.
    "wooden-door": "oak-door",
    "wooden-button": "oak-button",
    "wooden-pressure-plate": "oak-pressure-plate",
    "wooden-trapdoor": "oak-trapdoor",
    "wooden-fence": "oak-fence",
    "wooden-slab": "oak-slab",
    "wooden-stairs": "oak-stairs",
    "wood": "oak-wood",  # ambiguous on wiki — we use oak-wood
    "log": "oak-log",
    "planks": "oak-planks",
    "leaves": "oak-leaves",
    "sapling": "oak-sapling",
    "boat": "oak-boat",  # not a block anyway, will be filtered by category
    "fence": "oak-fence",
    "fence-gate": "oak-fence-gate",
    "sign": "oak-sign",
    "wall-sign": "oak-wall-sign",
    "hanging-sign": "oak-hanging-sign",
    "wall-hanging-sign": "oak-wall-hanging-sign",
    "banner-pattern": "banner-pattern",  # item, not block; safe to ignore
    # "An Ant" — April-fools joke page on wiki
    "an-ant": "",
}


# ---------------------------------------------------------------------------
# 2. Helpers
# ---------------------------------------------------------------------------

def kebab(title: str) -> str:
    """Convert a wiki title to a kebab-case id."""
    # Strip disambiguation parentheses, e.g. "Button (block)" -> "Button"
    title = re.sub(r"\s*\([^)]*\)\s*$", "", title)
    # Replace punctuation with spaces.
    s = re.sub(r"[''`]", "", title)
    s = s.replace("&", "and")
    s = re.sub(r"[^A-Za-z0-9]+", " ", s).strip().lower()
    s = re.sub(r"\s+", "-", s)
    return s


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_all_category_members(category: str = "Blocks") -> list[str]:
    titles: list[str] = []
    cmcontinue = None
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "cmlimit": "500",
            "cmtype": "page",
            "format": "json",
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue
        url = API + "?" + urllib.parse.urlencode(params)
        data = fetch_json(url)
        members = data.get("query", {}).get("categorymembers", [])
        titles.extend(m["title"] for m in members if m.get("ns", 0) == 0)
        cont = data.get("continue", {})
        cmcontinue = cont.get("cmcontinue")
        if not cmcontinue:
            break
        time.sleep(0.5)  # polite
    return titles


def should_drop_by_id(kid: str) -> tuple[bool, str]:
    """Return (drop, reason) based on substring / exact filters."""
    if kid in DISAMBIG_EXACT:
        return True, "disambiguation"
    for s in APRIL_FOOLS_SUBSTRINGS:
        if s in kid:
            return True, "april-fools"
    for s in EDUCATION_SUBSTRINGS:
        # use word-boundary-ish check so we don't accidentally drop, e.g.,
        # "chalkboard" but also drop "board" exact... keep substring but
        # require that the substring is the whole id or joined by '-'.
        parts = kid.split("-")
        if s in parts or kid == s or kid.startswith(s + "-") or kid.endswith("-" + s):
            return True, "education"
    for s in REMOVED_LEGACY_SUBSTRINGS:
        if s in kid:
            return True, "removed/legacy"
    return False, ""


# ---------------------------------------------------------------------------
# 3. Main
# ---------------------------------------------------------------------------

def main() -> int:
    print(">> Fetching canonical block titles from minecraft.wiki ...", flush=True)
    titles = fetch_all_category_members("Blocks")
    print(f"   fetched {len(titles)} page titles", flush=True)

    # Sort + dedupe.
    titles = sorted(set(titles))

    canonical: dict[str, str] = {}  # kid -> wiki title
    dropped: list[tuple[str, str, str]] = []  # (kid, title, reason)

    for t in titles:
        # Skip pages from non-main namespaces.
        if any(t.startswith(p) for p in PREFIX_BLOCKLIST):
            dropped.append(("", t, "namespace"))
            continue
        kid = kebab(t)
        if not kid:
            dropped.append(("", t, "empty-id"))
            continue
        # Apply manual mapping.
        mapped = MANUAL_MAP.get(kid)
        if mapped is not None:
            if mapped == "":
                dropped.append((kid, t, "manual-skip"))
                continue
            kid = mapped
        drop, reason = should_drop_by_id(kid)
        if drop:
            dropped.append((kid, t, reason))
            continue
        if kid in canonical:
            continue
        canonical[kid] = t

    # Special inclusion: technical blocks that the wiki lists as "Allow",
    # "Deny", "Border", "Structure void", "Light block", "Jigsaw block" —
    # these are real technical blocks. Make sure they're in canonical
    # (we filter "block" / "blocks" disambiguation only).
    for t in ("Allow", "Deny", "Border", "Border block",
              "Structure void", "Light block", "Jigsaw block"):
        kid = kebab(t)
        if kid not in canonical:
            canonical[kid] = t

    print(f"   canonical ids after filter: {len(canonical)}", flush=True)
    print(f"   dropped {len(dropped)} non-canonical entries", flush=True)

    # Write canonical list.
    with open("/tmp/wiki_blocks.txt", "w") as f:
        for kid in sorted(canonical):
            f.write(kid + "\t" + canonical[kid] + "\n")

    # Compare with our repo.
    our_ids = {
        p.stem for p in BLOCKS_DIR.glob("*.json") if p.stem != "index"
    }
    print(f">> our repo has {len(our_ids)} block ids", flush=True)

    canonical_ids = set(canonical.keys())
    missing = sorted(canonical_ids - our_ids)
    extra = sorted(our_ids - canonical_ids)

    with open("/tmp/missing_blocks.txt", "w") as f:
        for kid in missing:
            f.write(kid + "\t" + canonical[kid] + "\n")

    with open("/tmp/extra_blocks.txt", "w") as f:
        for kid in extra:
            f.write(kid + "\n")

    print(f">> MISSING (in wiki, not in repo): {len(missing)}", flush=True)
    for kid in missing:
        print(f"   + {kid}\t{canonical[kid]}")
    print(f">> EXTRA (in repo, not in canonical wiki list): {len(extra)}",
          flush=True)
    if len(extra) <= 30:
        for kid in extra:
            print(f"   - {kid}")
    else:
        for kid in extra[:15]:
            print(f"   - {kid}")
        print(f"   ... ({len(extra) - 15} more)")

    # Write a JSON summary for downstream consumers.
    summary = {
        "canonical_count": len(canonical),
        "our_count": len(our_ids),
        "missing": [{"id": k, "title": canonical[k]} for k in missing],
        "extra": list(extra),
        "dropped_samples": [{"id": k, "title": t, "reason": r}
                            for (k, t, r) in dropped[:40]],
    }
    with open("/tmp/compare_blocks_summary.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
