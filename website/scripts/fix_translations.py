#!/usr/bin/env python3
"""
Fix Persian translations in features/changelog arrays.
The four required mappings:
  Nether    -> ندر
  End       -> اند
  Bedrock   -> بدراک
  Redstone  -> رداستون

Note: Netherite, Enderman, Ender Dragon are kept as-is (proper nouns).
"""
import json
from pathlib import Path

VERSIONS_FILE = Path(__file__).resolve().parent.parent / "src" / "data" / "versions.json"

# Substitutions — order matters: longer / more specific first.
SUBS = [
    # Redstone compounds (keep the rest of the proper noun in English, just translate "Redstone")
    ("Block of Redstone", "بلوک رداستون"),
    ("Redstone Mechanics", "مکانیک رداستون"),
    ("Redstone Comparator", "Comparator رداستون"),
    ("Redstone Lamp", "لامپ رداستون"),
    ("Redstone Dust", "پودر رداستون"),
    ("Redstone Ore", "سنگ معدن رداستون"),
    # Nether compounds
    ("Nether Fortress", "دژ ندر"),
    ("Nether Quartz", "کوارتز ندر"),
    ("Nether Star", "ستاره‌ی ندر"),
    # End compounds
    ("End Portal Frame", "قاب پرتال اند"),
    ("End Portal", "پرتال اند"),
    ("End Cities", "شهرهای اند"),
    ("End City", "شهر اند"),
    ("The End", "اند"),
    # Standalone terms — must come AFTER compound substitutions
    ("Nether —", "ندر —"),  # standalone "Nether —" used in alpha description-like entries
    ("(Nether)", "(ندر)"),
    # Bedrock standalone (don't touch Bedrock Edition / Bedrock Edition-name)
    ("Bedrock Edition", "بدراک Edition"),
]


def apply_subs(text: str) -> str:
    for src, dst in SUBS:
        text = text.replace(src, dst)
    return text


def main():
    data = json.loads(VERSIONS_FILE.read_text(encoding="utf-8"))
    changed = 0

    for platform in ("java", "bedrock"):
        for version in data[platform]:
            for field in ("features", "changelog"):
                if field not in version:
                    continue
                new_list = []
                for item in version[field]:
                    new_item = apply_subs(item)
                    if new_item != item:
                        changed += 1
                    new_list.append(new_item)
                version[field] = new_list

    VERSIONS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print(f"Fixed {changed} items with English terms.")


if __name__ == "__main__":
    main()
