#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared helpers for SA-WIKI-200 (200 more block wiki entries).

Contains:
- COLORS dict: 16 Minecraft color keys -> {fa, en, hex}
- BLOCK_CONTENT: dict-of-dicts assembled by importing each part script.
- fill_block_file(): idempotent filler (only writes empty arrays).
"""
import json
from pathlib import Path

PROJECT_ROOT = Path("/home/z/imc-website/website")
BLOCKS_DIR = PROJECT_ROOT / "src" / "data" / "blocks"

WIKI_FIELDS = ("intro", "behavior", "trivia", "differences")
HISTORY_FIELD = "history"

# 16 standard Minecraft colors.  Hex codes are canonical Minecraft map colors.
COLORS = {
    "white":       {"fa": "سفید",        "en": "White",       "hex": "#F9FFFE"},
    "orange":      {"fa": "نارنجی",      "en": "Orange",      "hex": "#F9801B"},
    "magenta":    {"fa": "سرخابی",      "en": "Magenta",     "hex": "#C74EBD"},
    "light-blue": {"fa": "آبی روشن",    "en": "Light Blue",  "hex": "#3AB3DA"},
    "yellow":      {"fa": "زرد",         "en": "Yellow",      "hex": "#FED83D"},
    "lime":        {"fa": "لیمویی",      "en": "Lime",        "hex": "#80C71F"},
    "pink":        {"fa": "صورتی",        "en": "Pink",        "hex": "#F38BAA"},
    "gray":        {"fa": "خاکستری",     "en": "Gray",        "hex": "#5D5D5D"},
    "light-gray":  {"fa": "خاکستری روشن","en": "Light Gray",  "hex": "#9C9C9C"},
    "cyan":        {"fa": "فیروزه‌ای",    "en": "Cyan",        "hex": "#169C9C"},
    "purple":      {"fa": "بنفش",        "en": "Purple",      "hex": "#8932B2"},
    "blue":        {"fa": "آبی",          "en": "Blue",        "hex": "#3C44AA"},
    "brown":       {"fa": "قهوه‌ای",      "en": "Brown",       "hex": "#51302A"},
    "green":       {"fa": "سبز",          "en": "Green",       "hex": "#4A6A3B"},
    "red":         {"fa": "قرمز",         "en": "Red",         "hex": "#B02E26"},
    "black":       {"fa": "مشکی",        "en": "Black",       "hex": "#1D1D21"},
}

# Natural dye source for each color (Minecraft canonical sources).
DYE_SOURCE_FA = {
    "white":       "Bone Meal (استخوان)",
    "orange":      "Orange Tulip (لاله نارنجی)",
    "magenta":     "Lilac یا Allium (پیچ‌کوشه یا آلیوم)",
    "light-blue": "Blue Orchid (ارکیده آبی)",
    "yellow":      "Dandelion (قاصدک)",
    "lime":        "Sea Pickle (خیار دریایی)",
    "pink":        "Peony یا Pink Tulip (پونی یا لاله صورتی)",
    "gray":        "Bone Meal + Ink Sac یا Azure Bluet",
    "light-gray":  "Oxeye Daisy یا White Tulip",
    "cyan":        "Pitcher Plant",
    "purple":      "Allium (آلیوم)",
    "blue":        "Cornflower یا Lapis Lazuli (گل‌ سپید یا لاژورد)",
    "brown":       "Cocoa Beans (دانه کاکائو)",
    "green":       "Cactus (کاکتوس)",
    "red":         "Poppy یا Rose Bush یا Red Tulip (شقایق یا گل سرخ)",
    "black":       "Ink Sac یا Wither Rose (مایع مرکب یا گل ویکسا)",
}

COLOR_ORDER = [
    "white", "orange", "magenta", "light-blue", "yellow", "lime", "pink",
    "gray", "light-gray", "cyan", "purple", "blue", "brown", "green", "red",
    "black",
]


def is_empty_field(value):
    if value is None:
        return True
    if isinstance(value, list) and len(value) == 0:
        return True
    return False


def fill_block_file(block_id, content):
    """Idempotent filler — only writes empty fields.  Returns n fields written."""
    path = BLOCKS_DIR / f"{block_id}.json"
    if not path.exists():
        print(f"  [MISS] {block_id}: file not found")
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  [ERR ] {block_id}: {e}")
        return 0

    written = 0
    for field in WIKI_FIELDS:
        if is_empty_field(data.get(field)):
            data[field] = list(content.get(field, []))
            written += 1
    if is_empty_field(data.get(HISTORY_FIELD)):
        history = content.get(HISTORY_FIELD, [])
        cleaned = []
        for entry in history:
            if isinstance(entry, dict) and "version" in entry and "change" in entry:
                cleaned.append(entry)
        data[HISTORY_FIELD] = cleaned
        written += 1

    if written > 0:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"  [OK ] {block_id}: {written} fields written")
    else:
        print(f"  [SKIP] {block_id}: already has content")
    return written


def run_parts(content_dict):
    total_written = 0
    total_blocks = 0
    for block_id, content in content_dict.items():
        total_blocks += 1
        total_written += fill_block_file(block_id, content)
    print(f"\nBlocks processed: {total_blocks}")
    print(f"Total field writes: {total_written}")
