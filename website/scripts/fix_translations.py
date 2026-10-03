#!/usr/bin/env python3
"""
Fix Persian translations in MineBed Astro data JSON files.

Strategy:
  1) Apply a list of ordered string-replacement rules to EVERY string value
     found anywhere in each JSON file (recursively — dicts, lists, strings).
  2) After step 1, override the top-level `nameFa` (and every `nameFa` inside
     any `related` array) using an explicit nameEn -> nameFa mapping table
     derived from the task spec. This guarantees canonical names for
     entities that have a known correct translation, even if the original
     Persian text was structurally different (e.g. missing "معدن" for ores,
     typos like "گلولم" instead of "گولم", wrong first-letter "غاست" vs "گاست",
     or stray kasra diacritics in "اِندرمن").

Only touches files under:
    src/data/blocks/*.json
    src/data/mobs/*.json

JSON is rewritten with indent=2, ensure_ascii=False, and a trailing newline.
"""

import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path("/home/z/work/imc-website/website")
BLOCKS_DIR = PROJECT_ROOT / "src" / "data" / "blocks"
MOBS_DIR = PROJECT_ROOT / "src" / "data" / "mobs"


# ---------------------------------------------------------------------------
# Explicit nameEn -> nameFa overrides (from the task spec)
# ---------------------------------------------------------------------------
NAME_OVERRIDES = {
    # ---------- Mobs (hostile/neutral/passive) ----------
    "Creeper": "کریپر",
    "Enderman": "اندرمن",
    "Blaze": "بلیز",
    "Ghast": "گاست",
    "Witch": "ویچ",
    "Pillager": "پیلجر",
    "Vindicator": "ویندیکیتور",
    "Evoker": "اووکر",
    "Illusioner": "ایلوژنر",
    "Ravager": "ریوگر",
    "Warden": "واردن",
    "Allay": "الای",
    "Axolotl": "اکسولوتل",
    "Ender Dragon": "اژدهای اندر",
    "Wither": "ویدر",
    "Wither Skeleton": "اسکلتون ویدر",
    "Zombified Piglin": "پیگلین زامبی‌شده",
    "Iron Golem": "گولم آهنی",
    "Snow Golem": "گولم برفی",
    "Villager": "روستایی",
    "Wandering Trader": "تاجر ول‌گرد",
    "Skeleton": "اسکلتون",
    "Spider": "اسپایدر",
    "Zombie": "زامبی",
    "Cave Spider": "اسپایدر غار",  # inferred from Spider -> اسپایدر
    # ---------- Blocks ----------
    "Stone": "سنگ",
    "Dirt": "خاک",
    "Grass Block": "بلوک چمن",
    "Cobblestone": "قلوه‌سنگ",
    "Oak Log": "تنه‌ی بلوط",
    "Oak Planks": "تخته‌ی بلوط",
    "Crafting Table": "میز کرافت",
    "Furnace": "کوره",
    "Chest": "صندوق",
    "Torch": "مشعل",
    "Sand": "ماسه",
    "Glass": "شیشه",
    "Lapis Lazuli Ore": "سنگ معدن لاجورد",
    "Diamond Ore": "سنگ معدن دایمند",
    "Iron Ore": "سنگ معدن آهن",
    "Gold Ore": "سنگ معدن طلا",
    "Redstone Ore": "سنگ معدن رداستون",
    "Emerald Ore": "سنگ معدن امرالد",
    "Coal Ore": "سنگ معدن زغال",
    "Netherrack": "ندراک",
    "Obsidian": "اوبسیدین",
    "Bedrock": "بدراک",
    "TNT": "تی‌ان‌تی",
    "Bookshelf": "کتابخانه",
    "End Stone": "سنگ اند",          # End -> اند (per spec)
    "Ender Chest": "صندوق اندر",     # Ender -> اندر (per Enderman -> اندرمن)
    # Deepslate ore variants — keep the ezafe construct-state used in the
    # existing data ("سنگ معدن Xِ عمیق"), just add "معدن" and fix the mineral.
    "Deepslate Diamond Ore": "سنگ معدن دایمندِ عمیق",
    "Deepslate Iron Ore": "سنگ معدن آهنِ عمیق",
    "Deepslate Gold Ore": "سنگ معدن طلا‌ی عمیق",
    "Deepslate Redstone Ore": "سنگ معدن رداستونِ عمیق",
    "Deepslate Emerald Ore": "سنگ معدن امرالدِ عمیق",
    "Deepslate Coal Ore": "سنگ معدن زغالِ عمیق",
    "Deepslate Copper Ore": "سنگ معدن مسِ عمیق",
    "Deepslate Lapis Ore": "سنگ معدن لاجوردِ عمیق",
    "Nether Gold Ore": "سنگ معدن طلا‌ی ندر",
    "Nether Quartz Ore": "سنگ معدن کوارتز ندر",
}


# ---------------------------------------------------------------------------
# Global string replacement rules (applied to every string in every JSON)
#
# Order matters!  More specific / longer patterns must come before shorter
# prefixes that would otherwise swallow them.
# ---------------------------------------------------------------------------
def build_rules():
    """Return an ordered list of (pattern, replacement) tuples."""
    rules = []

    def add(pat, repl):
        rules.append((pat, repl))

    # --- 1. Compound-specific replacements (must run first) ---
    # "اسکلت ویدر" should be "اسکلتون ویدر" — handle BEFORE generic اسکلت
    add("اسکلت ویدر", "اسکلتون ویدر")
    # "مرد اندر" -> "اندرمن" (must come before any "اندر" handling)
    add("مرد اندر", "اندرمن")
    # "احضارکننده" (Evoker) -> "اووکر"
    add("احضارکننده", "اووکر")

    # --- 2. Netherite variants (must come before generic نتر / ندر rules) ---
    # Correct: Netherite -> ندریت
    add("نِدِرایت", "ندریت")   # kasra diacritics
    add("نِدرایت", "ندریت")    # one kasra
    add("نیدِرایت", "ندریت")   # one kasra
    add("نیدرایت", "ندریت")    # bare
    add("نردریت", "ندریت")     # wrong first letters (نر instead of ند)
    add("نِردریت", "ندریت")
    add("نردَریت", "ندریت")
    add("نرد ریت", "ندریت")

    # --- 3. Netherrack variants (correct: ندراک) ---
    add("نثرَک", "ندراک")      # with fatha diacritic
    add("نِدرَک", "ندراک")      # with kasra+fatha
    add("نِدراک", "ندراک")      # with kasra only
    add("نث رک", "ندراک")      # with space
    add("سنگ ندر", "ندراک")    # per spec: Netherrack -> ندراک (NOT سنگ ندر)
    # (Note: "سنگ ندر" should NOT match "سنگ ندراک" because we replaced first
    #  — order ensures "نثرَک" etc. become "ندراک" before this rule fires. But
    #  "سنگ ندر" appearing literally after step 2 still needs fixing.)

    # --- 4. "ندرلند" (Netherlands — wrong) -> "ندر" ---
    add("ندرلند", "ندر")

    # --- 5. End dimension with kasra diacritic (correct: اند) ---
    # "اِندر" (with kasra after alef) -> "اندر"   (Ender prefix)
    add("اِندرمن", "اندرمن")   # Enderman
    add("اِندر", "اندر")       # generic Ender-
    # "اِند" (with kasra after alef) -> "اند"     (End dimension)
    add("اِند", "اند")

    # --- 6. "نتر" -> "ندr" with safety (avoid کنترل / نترد / نترال) ---
    # Pattern: not preceded by "کن" (control), not followed by د/ل/ال
    # The only actual occurrence of "نتر" in the repo is "کنترلش" (control it),
    # which we must not touch.
    rules.append((re.compile(r"(?<!کن)نتر(?!د|ل|ال)"), "ندر"))

    # --- 7. "الماس" -> "دایمند" ---
    add("الماس", "دایمند")

    # --- 8. "پایان" -> "اند"  (only End dimension, not "پایان بازی") ---
    # Replace "پایان" UNLESS followed by optional whitespace then "بازی".
    rules.append((re.compile(r"پایان(?!\s*بازی)"), "اند"))

    # --- 9. "بدرک" -> "بدراک" (NOT if already "بدراک" — naturally safe) ---
    add("بدرک", "بدراک")

    # --- 10. "سنگ قرمز" -> "رداستون" ---
    add("سنگ قرمز", "رداستون")

    # --- 11. "خرابگر" -> "کریپر" ---
    add("خرابگر", "کریپر")

    # --- 12. "زمرد" -> "امرالد" (also fixes "سنگ معدن زمرد" -> "سنگ معدن امرالد") ---
    add("زمرد", "امرالد")

    # --- 13. "ابسیدین" -> "اوبسیدین" ---
    add("ابسیدین", "اوبسیدین")

    # --- 14. "اسکلت" -> "اسکلتون" (only when not already اسکلتون) ---
    # Use regex negative lookahead so we don't double-fix.
    rules.append((re.compile(r"اسکلت(?!ون)"), "اسکلتون"))

    # --- 15. "عنکبوت" -> "اسپایدر" ---
    add("عنکبوت", "اسپایدر")

    # --- 16. "جادوگر" -> "ویچ" ---
    add("جادوگر", "ویچ")

    # --- 17. "غارتگر" -> "پیلجر" ---
    add("غارتگر", "پیلجر")

    # --- 18. "غاست" (wrong first letter غ) -> "گاست" ---
    add("غاست", "گاست")

    # --- 19. "گلولم" (typo) -> "گولم" ---
    # (the proper compound is "گولم آهنی" / "گولم برفی")
    add("گلولم", "گولم")

    # --- 20. Allay (with kasra) -> الای ---
    # "آلِی" -> "الای"  (alef-madda -> alef, remove kasra, insert alef before yeh)
    add("آلِی", "الای")
    # also catch "آلی" (without kasra) — but be careful, this might appear in
    # unrelated Persian words. The only known usage in the repo is the Allay mob.
    add("آلی", "الای")

    # --- 21. Axolotl variants -> اکسولوتل ---
    add("آژولوتل", "اکسولوتل")
    add("آکسولوتل", "اکسولوتل")

    return rules


REPLACEMENT_RULES = build_rules()


def apply_replacements(s: str) -> str:
    """Apply every replacement rule to the given string."""
    for pat, repl in REPLACEMENT_RULES:
        if isinstance(pat, str):
            s = s.replace(pat, repl)
        else:  # compiled regex
            s = pat.sub(repl, s)
    return s


# ---------------------------------------------------------------------------
# Recursive JSON walker
# ---------------------------------------------------------------------------
def transform_strings(obj, path=""):
    """Recursively apply string replacements to every str in obj."""
    if isinstance(obj, str):
        return apply_replacements(obj)
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            new[k] = transform_strings(v, f"{path}/{k}")
        return new
    if isinstance(obj, list):
        return [transform_strings(v, f"{path}[{i}]") for i, v in enumerate(obj)]
    return obj


def override_namefa(obj):
    """
    Walk the (already string-replaced) object and replace `nameFa` values
    wherever the sibling/parent `nameEn` matches NAME_OVERRIDES.

    Handles:
      - top-level { nameEn, nameFa, ... }
      - items in `related` arrays:  { id, nameEn, nameFa, type }
      - items in `blocks` / `mobs` arrays of index.json files
    """
    if isinstance(obj, dict):
        name_en = obj.get("nameEn")
        if (
            isinstance(name_en, str)
            and "nameFa" in obj
            and isinstance(obj["nameFa"], str)
            and name_en in NAME_OVERRIDES
        ):
            obj["nameFa"] = NAME_OVERRIDES[name_en]
        # Recurse into every value
        for k, v in obj.items():
            obj[k] = override_namefa(v)
        return obj
    if isinstance(obj, list):
        return [override_namefa(v) for v in obj]
    return obj


# ---------------------------------------------------------------------------
# Main per-file processor
# ---------------------------------------------------------------------------
def process_file(path: Path):
    """Return (status, before_namefa, after_namefa, error)."""
    try:
        with path.open("r", encoding="utf-8") as f:
            original_raw = f.read()
    except Exception as e:
        return ("READ_ERROR", None, None, f"READ: {e}")

    try:
        data = json.loads(original_raw)
    except json.JSONDecodeError as e:
        return ("PARSE_ERROR", None, None, str(e))

    # Snapshot nameFa BEFORE for reporting
    before_namefa = None
    if isinstance(data, dict) and "nameFa" in data:
        before_namefa = data["nameFa"]

    # 1) Apply global string replacements everywhere
    new_data = transform_strings(data)

    # 2) Override nameFa where nameEn is in NAME_OVERRIDES
    new_data = override_namefa(new_data)

    after_namefa = None
    if isinstance(new_data, dict) and "nameFa" in new_data:
        after_namefa = new_data["nameFa"]

    # Re-serialize and compare to original
    new_raw = json.dumps(new_data, indent=2, ensure_ascii=False) + "\n"

    if new_raw == original_raw:
        return ("UNCHANGED", before_namefa, after_namefa, None)

    # Write back
    with path.open("w", encoding="utf-8") as f:
        f.write(new_raw)
    return ("UPDATED", before_namefa, after_namefa, None)


def main():
    blocks_files = sorted(BLOCKS_DIR.glob("*.json"))
    mobs_files = sorted(MOBS_DIR.glob("*.json"))

    print(f"Found {len(blocks_files)} block JSON files")
    print(f"Found {len(mobs_files)} mob JSON files")

    blocks_updated = 0
    mobs_updated = 0
    parse_errors = []
    unchanged_blocks = 0
    unchanged_mobs = 0
    samples = []  # (path, before, after)

    for p in blocks_files:
        status, before, after, err = process_file(p)
        if status == "PARSE_ERROR":
            parse_errors.append((p, err))
        elif status == "READ_ERROR":
            parse_errors.append((p, err))
        elif status == "UPDATED":
            blocks_updated += 1
            if before != after and len(samples) < 10:
                samples.append((p, before, after))
        else:
            unchanged_blocks += 1

    for p in mobs_files:
        status, before, after, err = process_file(p)
        if status == "PARSE_ERROR":
            parse_errors.append((p, err))
        elif status == "READ_ERROR":
            parse_errors.append((p, err))
        elif status == "UPDATED":
            mobs_updated += 1
            if before != after and len(samples) < 10:
                samples.append((p, before, after))
        else:
            unchanged_mobs += 1

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Block files updated:    {blocks_updated}  (unchanged: {unchanged_blocks})")
    print(f"Mob files updated:      {mobs_updated}    (unchanged: {unchanged_mobs})")
    print(f"Parse errors:           {len(parse_errors)}")
    for p, e in parse_errors:
        print(f"  - {p}: {e}")
    print()
    print("Sample before/after (up to 10 files where nameFa changed):")
    for i, (p, before, after) in enumerate(samples, 1):
        rel = p.relative_to(PROJECT_ROOT)
        print(f"  {i}. {rel}")
        print(f"     BEFORE: {before}")
        print(f"     AFTER:  {after}")


if __name__ == "__main__":
    main()
