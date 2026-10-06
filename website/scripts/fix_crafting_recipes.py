#!/usr/bin/env python3
"""
fix_crafting_recipes.py

Verifies the 15 must-verify vanilla Minecraft crafting recipes in
src/data/crafting-recipes.json against their canonical patterns and
fixes any wrong grid / output.

Only the recipes explicitly listed in task SA-RECIPES-FIX are checked.
The canonical patterns are taken from the official Minecraft Wiki /
Bedrock Edition crafting recipes.

Run:
    python3 scripts/fix_crafting_recipes.py
"""

import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Canonical patterns for the 15 must-verify recipes
# ---------------------------------------------------------------------------
# Each entry maps recipe_id -> canonical_grid (3x3 list of item IDs or None).
# Patterns are taken from the official Minecraft Wiki / Bedrock Edition.
# ---------------------------------------------------------------------------
CANONICAL = {
    # 1. Bow — 3 sticks (left diagonal) + 3 strings (right column) → 1 bow
    "bow": [
        ["stick",   None,    "string"],
        [None,      "stick", "string"],
        ["stick",   None,    "string"],
    ],

    # 2. Arrow — flint (top) + stick (middle) + feather (bottom) → 4 arrows
    "arrow": [
        [None, "flint",  None],
        [None, "stick",  None],
        [None, "feather", None],
    ],

    # 3. Diamond Sword — 2 diamonds (top + middle center) + 1 stick (bottom center)
    "diamond-sword": [
        [None, "diamond", None],
        [None, "diamond", None],
        [None, "stick",   None],
    ],

    # 4. Diamond Pickaxe — 3 diamonds (top row) + 2 sticks (middle + bottom center)
    "diamond-pickaxe": [
        ["diamond", "diamond", "diamond"],
        [None,      "stick",   None],
        [None,      "stick",   None],
    ],

    # 5. Crafting Table — 4 planks (2x2) → 1 table
    "crafting-table": [
        ["oak-planks", "oak-planks", None],
        ["oak-planks", "oak-planks", None],
        [None,         None,         None],
    ],

    # 6. Furnace — 8 cobblestone (ring) → 1 furnace
    "furnace": [
        ["cobblestone", "cobblestone", "cobblestone"],
        ["cobblestone", None,          "cobblestone"],
        ["cobblestone", "cobblestone", "cobblestone"],
    ],

    # 7. Torch — 1 coal (top) + 1 stick (below) → 4 torches
    "torch": [
        [None, "coal",  None],
        [None, "stick", None],
        [None, None,    None],
    ],

    # 8. Chest — 8 planks (ring) → 1 chest
    "chest": [
        ["oak-planks", "oak-planks", "oak-planks"],
        ["oak-planks", None,         "oak-planks"],
        ["oak-planks", "oak-planks", "oak-planks"],
    ],

    # 9. Bread — 3 wheat (horizontal middle row) → 1 bread
    "bread": [
        [None,   None,   None],
        ["wheat","wheat","wheat"],
        [None,   None,   None],
    ],

    # 10. Stick — 2 planks (vertical) → 4 sticks
    "stick": [
        [None, "oak-planks", None],
        [None, "oak-planks", None],
        [None, None,         None],
    ],

    # 11. Ladder — 7 sticks (H pattern) → 3 ladders
    "ladder": [
        ["stick", None,    "stick"],
        ["stick", "stick", "stick"],
        ["stick", None,    "stick"],
    ],

    # 12. Oak Door (task: "Door") — 6 planks (2 columns) → 3 doors
    "oak-door": [
        ["oak-planks", "oak-planks", None],
        ["oak-planks", "oak-planks", None],
        ["oak-planks", "oak-planks", None],
    ],

    # 13. TNT — 5 gunpowder + 4 sand (X pattern) → 1 TNT
    "tnt": [
        ["gunpowder", "sand", "gunpowder"],
        ["sand",      "gunpowder", "sand"],
        ["gunpowder", "sand", "gunpowder"],
    ],

    # 14. Book — 3 paper (vertical) + 1 leather (below) → 1 book
    "book": [
        [None, "paper",    None],
        [None, "paper",    None],
        [None, "leather",  None],
    ],

    # 15. Empty Map (task: "Map") — 8 paper (ring) + 1 compass (center) → 1 map
    "empty-map": [
        ["paper", "paper",   "paper"],
        ["paper", "compass", "paper"],
        ["paper", "paper",   "paper"],
    ],
}

# Expected output (item + count) for each recipe.
CANONICAL_OUTPUT = {
    "bow":            ("bow",    1),
    "arrow":          ("arrow",  4),
    "diamond-sword":  ("diamond-sword",  1),
    "diamond-pickaxe":("diamond-pickaxe",1),
    "crafting-table": ("crafting-table-top", 1),
    "furnace":        ("furnace-side", 1),
    "torch":          ("torch",  4),
    "chest":          ("chest",  1),
    "bread":          ("bread",  1),
    "stick":          ("stick",  4),
    "ladder":         ("ladder", 3),
    "oak-door":       ("oak-door", 3),
    "tnt":            ("tnt",    1),
    "book":           ("book",   1),
    "empty-map":      ("map",    1),
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
SRC = Path(__file__).resolve().parent.parent / "src" / "data" / "crafting-recipes.json"

def grids_equal(a, b):
    """Compare two 3x3 grids, treating None and missing as None."""
    if a is None or b is None:
        return a is None and b is None
    if len(a) != 3 or len(b) != 3:
        return False
    for ra, rb in zip(a, b):
        if len(ra) != 3 or len(rb) != 3:
            return False
        for ca, cb in zip(ra, rb):
            if (ca or None) != (cb or None):
                return False
    return True

def main():
    with open(SRC, "r", encoding="utf-8") as f:
        data = json.load(f)

    recipes_by_id = {r["id"]: r for r in data["recipes"]}

    print("=" * 72)
    print("SA-RECIPES-FIX  —  verifying 15 must-check recipes")
    print("=" * 72)

    fixed = []  # list of (id, what_changed)
    for rid, canonical_grid in CANONICAL.items():
        if rid not in recipes_by_id:
            print(f"\n[!] MISSING  recipe '{rid}' in JSON — cannot verify")
            continue

        rec = recipes_by_id[rid]
        current_grid = rec.get("grid")
        out = rec.get("output", {})
        out_item = out.get("item")
        out_count = out.get("count")
        canon_item, canon_count = CANONICAL_OUTPUT[rid]

        grid_ok = grids_equal(current_grid, canonical_grid)
        out_item_ok = (out_item == canon_item)
        out_count_ok = (out_count == canon_count)

        status = "OK" if (grid_ok and out_item_ok and out_count_ok) else "WRONG"
        print(f"\n[{status}]  {rid:18s}  ({rec.get('nameEn','')})")

        if not grid_ok:
            print(f"    current  grid: {current_grid}")
            print(f"    canonical grid: {canonical_grid}")

        if not out_item_ok:
            print(f"    current  output.item:   {out_item!r}  (expected {canon_item!r})")
        if not out_count_ok:
            print(f"    current  output.count:  {out_count!r}  (expected {canon_count!r})")

        if not (grid_ok and out_item_ok and out_count_ok):
            # apply fix
            rec["grid"] = [list(row) for row in canonical_grid]
            out["item"] = canon_item
            out["count"] = canon_count
            fixed.append(rid)
            print("    -> FIXED in memory")

    print("\n" + "=" * 72)
    if fixed:
        print(f"Recipes fixed: {len(fixed)}  ->  {', '.join(fixed)}")
    else:
        print("No changes needed; all 15 recipes already correct.")
    print("=" * 72)

    if fixed:
        with open(SRC, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"Saved {len(fixed)} fix(es) to {SRC}")
    else:
        print("File left untouched.")

if __name__ == "__main__":
    main()
