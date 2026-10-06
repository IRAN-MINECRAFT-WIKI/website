#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SA-WIKI-FINAL — fill wiki content for all remaining ~423 empty blocks.

Idempotent: only fills blocks whose `intro` array is empty.  Perserves all
original fields.  Writes JSON with ensure_ascii=False, indent=2, trailing newline.

Usage:
    python3 scripts/fill_wiki_final.py
"""
import json
import re
from pathlib import Path

PROJECT_ROOT = Path("/home/z/imc-website/website")
BLOCKS_DIR = PROJECT_ROOT / "src" / "data" / "blocks"

WIKI_FIELDS = ("intro", "behavior", "trivia", "differences")
HISTORY_FIELD = "history"


# ---------------------------------------------------------------------------
# Persian canonical translations (per task instructions)
# ---------------------------------------------------------------------------
TRANSLATIONS = {
    "Diamond":   "دایمند",
    "Nether":    "ندر",
    "End":       "اند",
    "Bedrock":   "بدراک",
    "Redstone":  "رداستون",
    "Netherite": "ندریت",
    "Emerald":   "امرالد",
    "Obsidian":  "اوبسیدین",
}


# ---------------------------------------------------------------------------
# Wood types (Persian name, source-tree description, biome hint)
# ---------------------------------------------------------------------------
WOOD = {
    "oak":         {"fa": "بلوط",        "biome": "جنگل‌های بلوط",     "added": "Java Beta 1.2 (2011)"},
    "spruce":     {"fa": "نجوکا",       "biome": "تایگا",              "added": "Java Beta 1.2 (2011)"},
    "birch":      {"fa": "توس",          "biome": "جنگل توس",          "added": "Java Beta 1.2 (2011)"},
    "jungle":     {"fa": "جنگلی",       "biome": "جنگل جنگلی",        "added": "Java 1.2 (2012)"},
    "acacia":     {"fa": "اقاقیا",       "biome": "ساوانا",            "added": "Java 1.7 (2013)"},
    "dark-oak":   {"fa": "بلوط تیره",   "biome": "جنگل تیره",         "added": "Java 1.7 (2013)"},
    "mangrove":   {"fa": "مانگرو",       "biome": "بایوم مانگرو",       "added": "Java 1.19 (2022)"},
    "cherry":     {"fa": "گیلاس",        "biome": "بایوم گیلاس",         "added": "Java 1.20 (2023)"},
    "bamboo":     {"fa": "بامبو",        "biome": "جنگل بامبو",        "added": "Java 1.20 (2023)"},
    "crimson":    {"fa": "قرمز ندر",    "biome": "بایوم crimson ندر",  "added": "Java 1.16 (2020)"},
    "warped":     {"fa": "وارپد ندر",   "biome": "بایوم warped ندر",   "added": "Java 1.16 (2020)"},
    "pale-oak":   {"fa": "بلوط رنگ‌پریده", "biome": "جنگل رنگ‌پریده",     "added": "Java 1.21.4 (2024)"},
}

# Generic wood translations used in slab/stairs/wall dispatch — keyed by stem prefix.
WOOD_PREFIXES = {
    "oak": "oak", "spruce": "spruce", "birch": "birch", "jungle": "jungle",
    "acacia": "acacia", "dark-oak": "dark-oak", "mangrove": "mangrove",
    "cherry": "cherry", "bamboo": "bamboo", "crimson": "crimson",
    "warped": "warped", "pale-oak": "pale-oak",
}


# ---------------------------------------------------------------------------
# Stone / mineral material metadata for slabs, stairs, walls
# Each entry: persian name, hardness, tool persian, source block persian,
# added version, secondary source (e.g. polished variant), color hint.
# ---------------------------------------------------------------------------
STONE = {
    "stone":                 {"fa": "سنگ",            "src": "سنگ",            "added": "Java Beta 1.8 (2011)", "hard": "1.5"},
    "cobblestone":           {"fa": "قلوه‌سنگ",        "src": "قلوه‌سنگ",        "added": "Java Beta 1.8 (2011)", "hard": "2.0"},
    "mossy-cobblestone":     {"fa": "قلوه‌سنگ خزه‌دار", "src": "قلوه‌سنگ خزه‌دار", "added": "Java 1.7 (2013)",      "hard": "2.0"},
    "smooth-stone":          {"fa": "سنگ صاف",         "src": "سنگ صاف",         "added": "Java Beta 1.8 (2011)", "hard": "2.0"},
    "stone-brick":           {"fa": "آجر سنگی",        "src": "آجر سنگی",        "added": "Java Beta 1.8 (2011)", "hard": "1.5"},
    "mossy-stone-brick":     {"fa": "آجر سنگی خزه‌دار","src": "آجر سنگی خزه‌دار","added": "Java 1.8 (2014)",      "hard": "1.5"},
    "brick":                 {"fa": "آجر",             "src": "آجر",             "added": "Java Beta 1.8 (2011)", "hard": "2.0"},
    "nether-brick":          {"fa": "آجر ندر",        "src": "آجر ندر",        "added": "Java Beta 1.9 (2011)", "hard": "2.0"},
    "red-nether-brick":      {"fa": "آجر ندر قرمز",   "src": "آجر ندر قرمز",   "added": "Java 1.10 (2016)",     "hard": "2.0"},
    "end-stone-brick":       {"fa": "آجر اند",         "src": "آجر اند",         "added": "Java 1.9 (2016)",      "hard": "3.0"},
    "sandstone":             {"fa": "ماسه‌سنگ",         "src": "ماسه‌سنگ",         "added": "Java Beta 1.8 (2011)", "hard": "0.8"},
    "red-sandstone":         {"fa": "ماسه‌سنگ قرمز",    "src": "ماسه‌سنگ قرمز",    "added": "Java 1.8 (2014)",      "hard": "0.8"},
    "cut-sandstone":         {"fa": "ماسه‌سنگ برش‌خورده","src": "ماسه‌سنگ برش‌خورده","added": "Java 1.14 (2019)",    "hard": "0.8"},
    "cut-red-sandstone":     {"fa": "ماسه‌سنگ قرمز برش‌خورده","src": "ماسه‌سنگ قرمز برش‌خورده","added":"Java 1.14 (2019)","hard":"0.8"},
    "smooth-sandstone":      {"fa": "ماسه‌سنگ صاف",    "src": "ماسه‌سنگ صاف",    "added": "Java 1.14 (2019)",     "hard": "0.8"},
    "smooth-red-sandstone":  {"fa": "ماسه‌سنگ قرمز صاف","src": "ماسه‌سنگ قرمز صاف","added": "Java 1.14 (2019)",     "hard": "0.8"},
    "prismarine":            {"fa": "پریزمارین",       "src": "پریزمارین",       "added": "Java 1.8 (2014)",      "hard": "1.5"},
    "prismarine-brick":      {"fa": "آجر پریزمارین",   "src": "آجر پریزمارین",   "added": "Java 1.8 (2014)",      "hard": "1.5"},
    "dark-prismarine":       {"fa": "پریزمارین تیره",  "src": "پریزمارین تیره",  "added": "Java 1.8 (2014)",      "hard": "1.5"},
    "granite":               {"fa": "گرانیت",          "src": "گرانیت",          "added": "Java 1.8 (2014)",      "hard": "1.5"},
    "polished-granite":      {"fa": "گرانیت صیقل‌خورده","src": "گرانیت صیقل‌خورده","added": "Java 1.14 (2019)",     "hard": "1.5"},
    "diorite":               {"fa": "دیوریت",          "src": "دیوریت",          "added": "Java 1.8 (2014)",      "hard": "1.5"},
    "polished-diorite":      {"fa": "دیوریت صیقل‌خورده","src": "دیوریت صیقل‌خورده","added": "Java 1.14 (2019)",     "hard": "1.5"},
    "andesite":              {"fa": "آندزیت",          "src": "آندزیت",          "added": "Java 1.8 (2014)",      "hard": "1.5"},
    "polished-andesite":     {"fa": "آندزیت صیقل‌خورده","src": "آندزیت صیقل‌خورده","added": "Java 1.14 (2019)",     "hard": "1.5"},
    "blackstone":            {"fa": "سنگ سیاه",         "src": "سنگ سیاه",         "added": "Java 1.16 (2020)",     "hard": "1.5"},
    "polished-blackstone":   {"fa": "سنگ سیاه صیقل‌خورده","src":"سنگ سیاه صیقل‌خورده","added": "Java 1.16 (2020)",   "hard": "2.0"},
    "polished-blackstone-brick": {"fa":"آجر سنگ سیاه صیقل‌خورده","src":"آجر سنگ سیاه صیقل‌خورده","added":"Java 1.16 (2020)","hard":"2.0"},
    "deepslate":             {"fa": "دیپ‌اسلیت",        "src": "دیپ‌اسلیت",        "added": "Java 1.17 (2021)",     "hard": "3.0"},
    "cobbled-deepslate":     {"fa": "قلوه‌سنگ دیپ‌اسلیت","src": "قلوه‌سنگ دیپ‌اسلیت","added": "Java 1.17 (2021)",     "hard": "3.5"},
    "polished-deepslate":    {"fa": "دیپ‌اسلیت صیقل‌خورده","src":"دیپ‌اسلیت صیقل‌خورده","added": "Java 1.17 (2021)",  "hard": "3.5"},
    "deepslate-brick":       {"fa": "آجر دیپ‌اسلیت",   "src": "آجر دیپ‌اسلیت",   "added": "Java 1.17 (2021)",     "hard": "3.5"},
    "deepslate-tile":        {"fa": "کاشی دیپ‌اسلیت",  "src": "کاشی دیپ‌اسلیت",  "added": "Java 1.17 (2021)",     "hard": "3.5"},
    "tuff":                  {"fa": "تف",              "src": "تف",              "added": "Java 1.17 (2021)",     "hard": "1.5"},
    "tuff-brick":            {"fa": "آجر تف",          "src": "آجر تف",          "added": "Java 1.17 (2021)",     "hard": "1.5"},
    "polished-tuff":         {"fa": "تف صیقل‌خورده",    "src": "تف صیقل‌خورده",    "added": "Java 1.20 (2023)",     "hard": "1.5"},
    "mud-brick":             {"fa": "آجر گلی",         "src": "آجر گلی",         "added": "Java 1.19 (2022)",     "hard": "1.5"},
    "resin-brick":           {"fa": "آجر رزین",        "src": "آجر رزین",        "added": "Java 1.21 (2024)",     "hard": "1.5"},
    "cut-copper":            {"fa": "مس برش‌خورده",    "src": "مس برش‌خورده",    "added": "Java 1.17 (2021)",     "hard": "3.0"},
    "exposed-cut-copper":    {"fa": "مس برش‌خورده هواخورده","src":"مس برش‌خورده هواخورده","added":"Java 1.17 (2021)", "hard":"3.0"},
    "weathered-cut-copper":  {"fa": "مس برش‌خورده فرسوده","src":"مس برش‌خورده فرسوده","added":"Java 1.17 (2021)",   "hard":"3.0"},
    "oxidized-cut-copper":   {"fa": "مس برش‌خورده اکسیدشده","src":"مس برش‌خورده اکسیدشده","added":"Java 1.17 (2021)","hard":"3.0"},
    "waxed-cut-copper":      {"fa": "مس برش‌خورده واکس‌دار","src":"مس برش‌خورده واکس‌دار","added":"Java 1.17 (2021)","hard":"3.0"},
    "waxed-exposed-cut-copper":  {"fa": "مس برش‌خورده هواخورده واکس‌دار","src":"مس برش‌خورده هواخورده واکس‌دار","added":"Java 1.17 (2021)","hard":"3.0"},
    "waxed-weathered-cut-copper": {"fa": "مس برش‌خورده فرسوده واکس‌دار","src":"مس برش‌خورده فرسوده واکس‌دار","added":"Java 1.17 (2021)","hard":"3.0"},
    "waxed-oxidized-cut-copper":  {"fa": "مس برش‌خورده اکسیدشده واکس‌دار","src":"مس برش‌خورده اکسیدشده واکس‌دار","added":"Java 1.17 (2021)","hard":"3.0"},
    "oak":                   {"fa": "بلوط",            "src": "تخته‌ی بلوط",      "added": "Java Beta 1.3 (2011)", "hard": "2.0"},
    "spruce":                {"fa": "نجوکا",           "src": "تخته‌ی نجوکا",     "added": "Java Beta 1.3 (2011)", "hard": "2.0"},
    "birch":                 {"fa": "توس",             "src": "تخته‌ی توس",       "added": "Java Beta 1.3 (2011)", "hard": "2.0"},
    "jungle":                {"fa": "جنگلی",           "src": "تخته‌ی جنگلی",    "added": "Java 1.3 (2012)",      "hard": "2.0"},
    "acacia":                {"fa": "اقاقیا",           "src": "تخته‌ی اقاقیا",   "added": "Java 1.7 (2013)",      "hard": "2.0"},
    "dark-oak":              {"fa": "بلوط تیره",       "src": "تخته‌ی بلوط تیره","added": "Java 1.7 (2013)",      "hard": "2.0"},
    "mangrove":              {"fa": "مانگرو",           "src": "تخته‌ی مانگرو",   "added": "Java 1.19 (2022)",     "hard": "2.0"},
    "cherry":                {"fa": "گیلاس",            "src": "تخته‌ی گیلاس",    "added": "Java 1.20 (2023)",     "hard": "2.0"},
    "bamboo":                {"fa": "بامبو",            "src": "تخته‌ی بامبو",    "added": "Java 1.20 (2023)",     "hard": "2.0"},
    "bamboo-mosaic":         {"fa": "موزاییک بامبو",   "src": "موزاییک بامبو",   "added": "Java 1.20 (2023)",     "hard": "2.0"},
    "crimson":               {"fa": "قرمز ندر",        "src": "تخته‌ی قرمز ندر","added": "Java 1.16 (2020)",     "hard": "2.0"},
    "warped":                {"fa": "وارپد ندر",       "src": "تخته‌ی وارپد ندر","added": "Java 1.16 (2020)",    "hard": "2.0"},
    "pale-oak":              {"fa": "بلوط رنگ‌پریده",  "src": "تخته‌ی بلوط رنگ‌پریده","added":"Java 1.21.4 (2024)","hard":"2.0"},
}


def detect_material(block_id, name_en):
    """Return (material_key, material_meta_dict) for slabs/stairs/walls/trapdoor etc.

    Tries to find a STONE dict key matching the stem (e.g. "deepslate-brick-slab"
    -> "deepslate-brick").  Falls back to None if no match.
    """
    # try matching against all STONE keys, longest first
    candidates = sorted(STONE.keys(), key=lambda k: -len(k))
    # try suffix-stripped matching
    bid = block_id
    for suffix in ["-slab", "-stairs", "-wall", "-trapdoor", "-door",
                   "-pressure-plate", "-button", "-fence-gate", "-fence",
                   "-leaves", "-sapling", "-log", "-wood", "-planks",
                   "-hanging-sign", "-sign", "-wall-sign"]:
        if bid.endswith(suffix):
            base = bid[:-len(suffix)]
            for c in candidates:
                if base == c or base.startswith(c + "-") is False and base == c:
                    pass
            # match base directly
            for c in candidates:
                if base == c:
                    return c, STONE[c]
            # match base starts-with
            for c in candidates:
                if base.startswith(c) and len(c) >= 4:
                    return c, STONE[c]
            break
    # also try full-name match
    for c in candidates:
        if block_id == c:
            return c, STONE[c]
    return None, None


# ---------------------------------------------------------------------------
# Generic template builders
# ---------------------------------------------------------------------------
def build_slab_content(block_id, name_en, name_fa, hardness, wiki_link):
    mat, meta = detect_material(block_id, name_en)
    if meta is None:
        return None
    mat_fa = meta["fa"]
    src = meta["src"]
    added = meta["added"]
    hard = meta["hard"]
    is_wood = mat in WOOD or mat in ("bamboo-mosaic",)
    return {
        "intro": [
            f"اسلب {mat_fa} (Slab) نیمه‌بلاکی است که از {src} ساخته می‌شود و برای ساخت کف، سقف و پله‌های نرم و کم‌ارتفاع کاربرد دارد. این بلاک سختی {hard} دارد و در میز ساخت به‌صورت ۶ تایی از ۳ بلاک {src} ساخته می‌شود.",
            f"اسلب {mat_fa} ارتفاع ۰.۵ بلاک دارد (نصف بلاک کامل) و می‌تواند در نیمه‌بالا و نیمه‌پایین و همچنین دو‌تایی (دو اسلب روی هم) قرار گیرد. در ساخت پله‌های داخلی و دکوراسیون کف‌پوش بسیار پرکاربرد است.",
            f"این اسلب در نسخه‌ی {added} به بازی اضافه شد و در ۳ نوع بالایی، پایینی و دو‌تایی در دسترس است. با سنگ‌بُر (Stonecutter) نیز می‌توان آن را از {src} ساخت.",
        ],
        "behavior": [
            f"اسلب {mat_fa} سختی {hard} دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است. دو اسلب روی هم یک بلاک کامل می‌سازند و در دو حالت بالایی و پایینی قابل قرار دادن هستند.",
            f"این بلاک از ۳ {src} در میز ساخت به ۶ اسلب تبدیل می‌شود و با Stonecutter نیز به‌صورت ۱ به ۱ قابل ساخت است. در ساخت کف و سقف ساختمان‌ها بسیار اقتصادی است.",
            f"اسلب {mat_fa} در برابر آتش و مواد منفجره رفتاری مشابه {src} دارد و در ساخت تله‌های ضد ماب نیز کاربرد دارد. این بلاک شفاف نیست و نور را متوقف می‌کند.",
        ],
        "trivia": [
            f"اسلب {mat_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد و از آن زمان در ساخت کف ساختمان‌ها بسیار پرکاربرد است.",
            f"این بلاک در ۳ حالت بالایی، پایینی و دو‌تایی در دسترس است که با کلیک راست می‌توان نوع قرارگیری را کنترل کرد.",
            f"اسلب {mat_fa} سختی {hard} دارد و با Stonecutter به‌صورت ۱ به ۱ از {src} قابل ساخت است.",
            f"این بلاک ارتفاع ۰.۵ بلاک دارد و دو اسلب روی هم یک بلاک کامل می‌سازند.",
            f"اسلب {mat_fa} در ساخت کف، سقف و پله‌های داخلی ساختمان‌ها بسیار پرکاربرد است.",
        ],
        "history": [
            {"version": added, "change": f"افزودن اسلب {mat_fa} به ماینکرفت به‌عنوان بلاک ساختمانی نیمه‌ارتفاع."},
            {"version": "Java 1.14 (2019)", "change": "افزودن قابلیت ساخت اسلب‌ها با Stonecutter و یکسان‌سازی رفتار قرارگیری."},
            {"version": "Bedrock 1.9 (2017)", "change": f"افزودن اسلب {mat_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.13 (2018)", "change": "تفکیک اسلب‌ها به آیتم‌های مجزا برای هر ماده و رفع باگ‌های قدیمی دو‌تایی‌شدن."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر اسلب‌ها و یکپارچه‌سازی رفتار اشتراکی با بلاک‌های مرجع."},
        ],
        "differences": [
            f"در Java، اسلب {mat_fa} سختی {hard} و زمان شکستن مشابه دارد؛ در Bedrock همین رفتار است، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، جای‌گذاری اسلب {mat_fa} با کلیک راست کنترل می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه Bedrock کمی متفاوت بود.",
            f"در Bedrock، اسلب {mat_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_stairs_content(block_id, name_en, name_fa, hardness, wiki_link):
    mat, meta = detect_material(block_id, name_en)
    if meta is None:
        return None
    mat_fa = meta["fa"]
    src = meta["src"]
    added = meta["added"]
    hard = meta["hard"]
    return {
        "intro": [
            f"پله‌ی {mat_fa} (Stairs) بلاکی ساختمانی است که از {src} ساخته می‌شود و برای ساخت پله، صندلی و دکوراسیون داخلی کاربرد دارد. این بلاک سختی {hard} دارد و در میز ساخت به‌صورت ۴ تایی از ۶ {src} (به شکل V) ساخته می‌شود.",
            f"پله‌ی {mat_fa} در ۸ جهت مختلف قابل قرار دادن است (۴ رو به بالا، ۴ رو به پایین) و با کلیک روی سطح جانبی، عمودی یا بالایی جهت قرارگیری تعیین می‌شود. این بلاک در ساخت پله‌های ساختمانی و دکوراسیون بسیار پرکاربرد است.",
            f"این پله در نسخه‌ی {added} به بازی اضافه شد و از همان زمان یکی از پرکاربردترین بلاک‌های ساختمانی ماینکرفت است. با Stonecutter نیز به‌صورت ۱ به ۱ قابل ساخت است.",
        ],
        "behavior": [
            f"پله‌ی {mat_fa} سختی {hard} دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است. این بلاک در ۸ جهت مختلف قابل قرار دادن است.",
            f"این بلاک از ۶ {src} در میز ساخت به ۴ پله تبدیل می‌شود و با Stonecutter نیز به‌صورت ۱ به ۱ از {src} قابل ساخت است. در ساخت پله‌های ساختمانی بسیار اقتصادی است.",
            f"پله‌ی {mat_fa} رفتاری مشابه {src} در برابر آتش و انفجار دارد و در ساخت صندلی، میز و دکوراسیون داخلی بسیار پرکاربرد است.",
        ],
        "trivia": [
            f"پله‌ی {mat_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد و از همان زمان یکی از پرکاربردترین بلاک‌های ساختمانی است.",
            f"این بلاک در ۸ جهت مختلف قابل قرار دادن است و با کلیک روی سطح جانبی، عمودی یا بالایی جهت تعیین می‌شود.",
            f"پله‌ی {mat_fa} سختی {hard} دارد و با Stonecutter به‌صورت ۱ به ۱ از {src} قابل ساخت است.",
            f"این بلاک از ۶ {src} در میز ساخت به ۴ پله تبدیل می‌شود.",
            f"پله‌ی {mat_fa} در ساخت پله‌های ساختمانی، صندلی و دکوراسیون داخلی بسیار پرکاربرد است.",
        ],
        "history": [
            {"version": added, "change": f"افزودن پله‌ی {mat_fa} به ماینکرفت به‌عنوان بلاک ساختمانی ۸‌جهته."},
            {"version": "Java 1.14 (2019)", "change": "افزودن قابلیت ساخت پله‌ها با Stonecutter و بهبود مدل رندر."},
            {"version": "Bedrock 1.9 (2017)", "change": f"افزودن پله‌ی {mat_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.13 (2018)", "change": "تفکیک پله‌ها به بلاک‌های مجزا برای هر ماده و رفع باگ‌های قدیمی همپوشانی."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر پله‌ها و یکپارچه‌سازی رفتار اشتراکی با بلاک‌های مرجع."},
        ],
        "differences": [
            f"در Java، پله‌ی {mat_fa} سختی {hard} و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر گوشه‌ها کمی متفاوت است.",
            f"در Java، جهت‌گذاری پله‌ی {mat_fa} با کلیک روی سطوح مختلف کنترل می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، پله‌ی {mat_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_wall_content(block_id, name_en, name_fa, hardness, wiki_link):
    mat, meta = detect_material(block_id, name_en)
    if meta is None:
        return None
    mat_fa = meta["fa"]
    src = meta["src"]
    added = meta["added"]
    hard = meta["hard"]
    return {
        "intro": [
            f"دیوار {mat_fa} (Wall) بلاک ساختمانی تزئینی است که از {src} ساخته می‌شود و برای ساخت حصار، دیوار حیاط و دکوراسیون باغ کاربرد دارد. این بلاک سختی {hard} دارد و ارتفاع ۱.۵ بلاک دارد (بالاتر از یک بلاک کامل).",
            f"دیوار {mat_fa} به‌صورت خودکار به دیوارهای مجاور متصل می‌شود و در گوشه‌ها و تقاطع‌ها ستون ایجاد می‌کند. این رفتار هوشمند دیوار را برای حصارکردن محوطه‌ها بسیار کارآمد می‌کند.",
            f"این دیوار در نسخه‌ی {added} به بازی اضافه شد و در ساخت دفاعی و تزئینی بسیار پرکاربرد است. دیوارها در برابر ماب‌ها مانع محسوب می‌شوند و از عبور آن‌ها جلوگیری می‌کنند.",
        ],
        "behavior": [
            f"دیوار {mat_fa} سختی {hard} دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است. این بلاک ارتفاع ۱.۵ بلاک دارد و در گوشه‌ها ستون می‌سازد.",
            f"این بلاک از ۶ {src} در میز ساخت به ۶ دیوار تبدیل می‌شود و به‌صورت خودکار به دیوارهای مجاور متصل می‌شود. در ساخت حصار و دفاع بسیار پرکاربرد است.",
            f"دیوار {mat_fa} مانع عبور ماب‌ها می‌شود (ارتفاع ۱.۵ از عبور ماب‌های معمولی جلوگیری می‌کند) و در برابر اسپایدرها نیز دفاعی محسوب می‌شود.",
        ],
        "trivia": [
            f"دیوار {mat_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد و از آن زمان در ساخت حصار بسیار پرکاربرد است.",
            f"این بلاک ارتفاع ۱.۵ بلاک دارد و در گوشه‌ها و تقاطع‌ها ستون ایجاد می‌کند.",
            f"دیوار {mat_fa} سختی {hard} دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است.",
            f"این بلاک به‌صورت خودکار به دیوارهای مجاور وصل می‌شود و در ساخت حصار حیاط بسیار کارآمد است.",
            f"دیوار {mat_fa} مانع عبور ماب‌ها می‌شود و در دفاع ساختمان بسیار پرکاربرد است.",
        ],
        "history": [
            {"version": added, "change": f"افزودن دیوار {mat_fa} به ماینکرفت به‌عنوان بلاک حصار تزئینی."},
            {"version": "Java 1.14 (2019)", "change": "بهبود مدل رندر دیوارها و افزودن ستون در گوشه‌ها."},
            {"version": "Bedrock 1.9 (2017)", "change": f"افزودن دیوار {mat_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.13 (2018)", "change": "تفکیک دیوارها به بلاک‌های مجزا برای هر ماده و رفع باگ‌های قدیمی اتصال."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر دیوارها و یکپارچه‌سازی رفتار اشتراکی با بلاک‌های مرجع."},
        ],
        "differences": [
            f"در Java، دیوار {mat_fa} سختی {hard} و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر ستون‌ها کمی متفاوت است.",
            f"در Java، اتصال خودکار دیوار {mat_fa} به بلاک‌های مجاور بر اساس بلاک‌های مجاور است؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، دیوار {mat_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def detect_wood_type(block_id, name_en):
    """Return wood-type key (e.g. 'oak', 'spruce', ...) or None."""
    bid = block_id
    # strip "stripped-" prefix so it matches the base wood key
    if bid.startswith("stripped-"):
        bid = bid[len("stripped-"):]
    # try longest first
    for w in ("pale-oak", "dark-oak", "mangrove", "cherry", "bamboo",
              "crimson", "warped", "acacia", "spruce", "birch", "jungle", "oak"):
        if bid.startswith(w + "-") or bid == w:
            return w
    return None


def build_door_content(block_id, name_en, name_fa, hardness, wiki_link):
    mat = detect_wood_type(block_id, name_en)
    if mat:
        meta = WOOD[mat]
        mat_fa = meta["fa"]
        biome = meta["biome"]
        added = meta["added"]
        intro1 = f"در {mat_fa} (Door) بلاکی ساختمانی است که از تخته‌ی {mat_fa} ساخته می‌شود و برای ساخت درِ ساختمان و ورودی کاربرد دارد. این بلاک سختی ۱.۰ دارد و در میز ساخت به‌صورت ۳ تایی از ۶ تخته‌ی {mat_fa} ساخته می‌شود."
        intro2 = f"در {mat_fa} در دو بلاک بالا و پایین نصب می‌شود و با کلیک راست باز و بسته می‌شود. این بلاک در {biome} از تنه‌ی درخت {mat_fa} به‌دست می‌آید و در ساخت درِ ورودی ساختمان بسیار پرکاربرد است."
        intro3 = f"این در در نسخه‌ی {added} به بازی اضافه شد و ماب‌ها (به‌جز زامبی) نمی‌توانند آن را باز کنند. در ساخت روستاها و دهکده‌ها نیز بسیار پرکاربرد است."
    elif "copper" in block_id:
        mat_fa = "مس"
        added = "Java 1.21 (2024)" if "waxed" not in block_id else "Java 1.21 (2024)"
        if "waxed" in block_id:
            mat_fa = "مس واکس‌دار"
            state = "واکس‌دار"
        elif "exposed" in block_id:
            mat_fa = "مس هواخورده"
            state = "هواخورده"
        elif "weathered" in block_id:
            mat_fa = "مس فرسوده"
            state = "فرسوده"
        elif "oxidized" in block_id:
            mat_fa = "مس اکسیدشده"
            state = "اکسیدشده"
        else:
            state = "سالم"
        intro1 = f"در {mat_fa} (Copper Door) بلاکی ساختمانی از خانواده مس است که در نسخه 1.21 به بازی اضافه شد. این بلاک سختی ۱.۰ دارد و از مس ساخته می‌شود."
        intro2 = f"در {mat_fa} در دو بلاک بالا و پایین نصب می‌شود و با کلیک راست باز و بسته می‌شود. این در مانند سایر درهای مس، با رداستون قابل کنترل است و در {state} کار می‌کند."
        intro3 = f"این در در نسخه‌ی Java 1.21 (2024) به ماینکرفت اضافه شد و در حالت {state} قراردارد. واکس‌دار بودن باعث توقف اکسیداسیون می‌شود."
    else:
        return None
    return {
        "intro": [intro1, intro2, intro3],
        "behavior": [
            f"در {mat_fa} سختی ۱.۰ دارد و با هر ابزاری قابل جمع‌آوری است، ولی تبر (Axe) سریع‌ترین روش است. این در در دو بلاک بالا و پایین نصب می‌شود.",
            f"این در با کلیک راست باز و بسته می‌شود و با رداستون نیز قابل کنترل است. ماب‌ها (به‌جز زامبی) نمی‌توانند آن را باز کنند، ولی زامبی در حالت هاردمیود می‌تواند در چوبی را بشکند.",
            f"در {mat_fa} شفاف نیست و نور را متوقف می‌کند، اما در حالت باز نور عبور می‌کند. این در در ساخت ساختمان و روستاها بسیار پرکاربرد است.",
        ],
        "trivia": [
            f"در {mat_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            f"این در در دو بلاک بالا و پایین نصب می‌شود و با کلیک راست باز و بسته می‌شود.",
            f"در {mat_fa} سختی ۱.۰ دارد و با Axe سریع‌ترین روش جمع‌آوری است.",
            f"این در با رداستون قابل کنترل است و ماب‌ها (به‌جز زامبی) نمی‌توانند آن را باز کنند.",
            f"در {mat_fa} در ساخت ساختمان و روستاها بسیار پرکاربرد است.",
        ],
        "history": [
            {"version": added, "change": f"افزودن در {mat_fa} به ماینکرفت."},
            {"version": "Java 1.8 (2014)", "change": "افزودن قابلیت ساخت درها در ۲ بلاک بالا و پایین به‌جای ۱ بلاک."},
            {"version": "Bedrock 1.9 (2017)", "change": f"افزودن در {mat_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.13 (2018)", "change": "بهبود مدل رندر درها و رفع باگ‌های قدیمی همپوشانی با سقف."},
            {"version": "Java 1.20 (2023)", "change": "بهبود انیمیشن باز و بسته شدن درها و هماهنگ‌سازی رفتار رداستون."},
        ],
        "differences": [
            f"در Java، در {mat_fa} سختی ۱.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، زامبی در حالت هاردمیود می‌تواند در {mat_fa} را بشکند؛ در Bedrock همین رفتار، اما زمان شکستن کمی متفاوت است.",
            f"در Bedrock، در {mat_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_trapdoor_content(block_id, name_en, name_fa, hardness, wiki_link):
    mat = detect_wood_type(block_id, name_en)
    if mat:
        meta = WOOD[mat]
        mat_fa = meta["fa"]
        biome = meta["biome"]
        added = meta["added"]
        is_wood = True
    elif "copper" in block_id:
        is_wood = False
        if "waxed" in block_id and "exposed" in block_id:
            mat_fa = "مس هواخورده واکس‌دار"; added = "Java 1.21 (2024)"
        elif "waxed" in block_id and "weathered" in block_id:
            mat_fa = "مس فرسوده واکس‌دار"; added = "Java 1.21 (2024)"
        elif "waxed" in block_id and "oxidized" in block_id:
            mat_fa = "مس اکسیدشده واکس‌دار"; added = "Java 1.21 (2024)"
        elif "waxed" in block_id:
            mat_fa = "مس واکس‌دار"; added = "Java 1.21 (2024)"
        elif "exposed" in block_id:
            mat_fa = "مس هواخورده"; added = "Java 1.21 (2024)"
        elif "weathered" in block_id:
            mat_fa = "مس فرسوده"; added = "Java 1.21 (2024)"
        elif "oxidized" in block_id:
            mat_fa = "مس اکسیدشده"; added = "Java 1.21 (2024)"
        else:
            mat_fa = "مس"; added = "Java 1.21 (2024)"
    else:
        return None
    return {
        "intro": [
            f"تله‌در {mat_fa} (Trapdoor) بلاک ساختمانی نازک است که از {'تخته‌ی ' + mat_fa if is_wood else mat_fa} ساخته می‌شود و برای ساخت دریچه، تله و ورودی مخفی کاربرد دارد. این بلاک سختی ۱.۰ دارد و در میز ساخت به‌صورت ۲ تایی از ۶ {'تخته‌ی ' + mat_fa if is_wood else mat_fa} ساخته می‌شود.",
            f"تله‌در {mat_fa} در ۲ حالت افقی و عمودی (روی دیوار) قابل قرار دادن است و با کلیک راست باز و بسته می‌شود. این بلاک شفاف نیست، اما در حالت باز نور و ماب‌ها عبور می‌کنند.",
            f"این تله‌در در نسخه‌ی {added} به بازی اضافه شد و با رداستون قابل کنترل است. در ساخت دریچه زیرین و تله‌های ضد ماب بسیار پرکاربرد است.",
        ],
        "behavior": [
            f"تله‌در {mat_fa} سختی ۱.۰ دارد و با هر ابزاری قابل جمع‌آوری است، ولی تبر (Axe) سریع‌ترین روش است. این بلاک در ۲ حالت افقی و عمودی قابل قرار دادن است.",
            f"این بلاک از ۶ {'تخته‌ی ' + mat_fa if is_wood else mat_fa} در میز ساخت به ۲ تله‌در تبدیل می‌شود و با کلیک راست باز و بسته می‌شود. با رداستون نیز قابل کنترل است.",
            f"تله‌در {mat_fa} شفاف نیست و نور را متوقف می‌کند، اما در حالت باز نور و ماب‌ها (به‌جز spider) عبور می‌کنند. در ساخت تله و دریچه مخفی بسیار پرکاربرد است.",
        ],
        "trivia": [
            f"تله‌در {mat_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            f"این بلاک در ۲ حالت افقی و عمودی قابل قرار دادن است و با کلیک راست باز و بسته می‌شود.",
            f"تله‌در {mat_fa} سختی ۱.۰ دارد و با Axe سریع‌ترین روش جمع‌آوری است.",
            f"این بلاک با رداستون قابل کنترل است و در ساخت تله و دریچه مخفی بسیار پرکاربرد است.",
            f"تله‌در {mat_fa} در حالت باز نور و ماب‌ها را عبور می‌دهد و در ساخت تله‌های ضد ماب کاربرد دارد.",
        ],
        "history": [
            {"version": added, "change": f"افزودن تله‌در {mat_fa} به ماینکرفت."},
            {"version": "Java 1.13 (2018)", "change": "بهبود مدل رندر تله‌درها و رفع باگ‌های قدیمی همپوشانی."},
            {"version": "Bedrock 1.9 (2017)", "change": f"افزودن تله‌در {mat_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.14 (2019)", "change": "افزودن قابلیت قرار دادن تله‌در روی دیوار و بهبود رفتار رداستون."},
            {"version": "Java 1.20 (2023)", "change": "بهبود انیمیشن باز و بسته شدن تله‌درها و هماهنگ‌سازی رفتار رداستون."},
        ],
        "differences": [
            f"در Java، تله‌در {mat_fa} سختی ۱.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، جهت‌گذاری تله‌در {mat_fa} با کلیک روی سطوح مختلف کنترل می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، تله‌در {mat_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_button_content(block_id, name_en, name_fa, hardness, wiki_link):
    mat = detect_wood_type(block_id, name_en)
    if mat:
        meta = WOOD[mat]
        mat_fa = meta["fa"]
        added = meta["added"]
        is_wood = True
    elif "polished-blackstone" in block_id:
        mat_fa = "سنگ سیاه صیقل‌خورده"; added = "Java 1.16 (2020)"; is_wood = False
    elif block_id == "stone-button" or block_id == "button":
        mat_fa = "سنگ"; added = "Java Beta 1.9 (2011)"; is_wood = False
    else:
        return None
    source = f"تخته‌ی {mat_fa}" if is_wood else mat_fa
    return {
        "intro": [
            f"دکمه‌ی {mat_fa} (Button) بلاک رداستون است که از {source} ساخته می‌شود و با کلیک سیگنال کوتاه رداستون ساطع می‌کند. این بلاک سختی ۰.۵ دارد و در میز ساخت به‌صورت ۱ تایی از ۱ {source} ساخته می‌شود.",
            f"دکمه‌ی {mat_fa} در ۶ جهت قابل قرار دادن است (۴ دیوار + سقف + کف) و با کلیک راست یا فشار موب سیگنال کوتاه رداستون می‌دهد. دکمه‌ی چوبی ۱۵ تیک (۰.۷۵ ثانیه) و دکمه‌ی سنگی ۱۰ تیک (۰.۵ ثانیه) فعال می‌ماند.",
            f"این دکمه در نسخه‌ی {added} به بازی اضافه شد و در ساخت تله‌های رداستون و درهای خودکار بسیار پرکاربرد است. دکمه‌ی چوبی را همچنین می‌توان با تیراندازی از کمان فعال کرد.",
        ],
        "behavior": [
            f"دکمه‌ی {mat_fa} سختی ۰.۵ دارد و با هر ابزاری قابل جمع‌آوری است. این بلاک در ۶ جهت قابل قرار دادن است و با کلیک سیگنال کوتاه رداستون می‌دهد.",
            f"این بلاک از ۱ {source} در میز ساخت ساخته می‌شود و در ساخت تله‌های رداستون و درهای خودکار بسیار پرکاربرد است. دکمه‌ی چوبی ۱۵ تیک و دکمه‌ی سنگی ۱۰ تیک فعال می‌ماند.",
            f"دکمه‌ی {mat_fa} در برابر آتش و انفجار رفتاری مشابه {source} دارد و در ساخت تله‌های ضد ماب و سیستم‌های رداستون بسیار پرکاربرد است.",
        ],
        "trivia": [
            f"دکمه‌ی {mat_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            f"این بلاک در ۶ جهت قابل قرار دادن است و با کلیک سیگنال کوتاه رداستون می‌دهد.",
            f"دکمه‌ی {mat_fa} سختی ۰.۵ دارد و دکمه‌ی چوبی ۱۵ تیک و دکمه‌ی سنگی ۱۰ تیک فعال می‌ماند.",
            f"این بلاک در ساخت تله‌های رداستون و درهای خودکار بسیار پرکاربرد است.",
            f"دکمه‌ی {mat_fa} را می‌توان با تیراندازی از کمان نیز فعال کرد (در Java).",
        ],
        "history": [
            {"version": added, "change": f"افزودن دکمه‌ی {mat_fa} به ماینکرفت."},
            {"version": "Java 1.11 (2016)", "change": "افزودن قابلیت قرار دادن دکمه‌ها روی سقف و کف."},
            {"version": "Bedrock 1.4 (2016)", "change": f"افزودن دکمه‌ی {mat_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.13 (2018)", "change": "بهبود مدل رندر دکمه‌ها و رفع باگ‌های قدیمی."},
            {"version": "Java 1.20 (2023)", "change": "بهبود انیمیشن فشرده شدن دکمه‌ها و هماهنگ‌سازی رفتار رداستون."},
        ],
        "differences": [
            f"در Java، دکمه‌ی {mat_fa} سختی ۰.۵ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما زمان فعال‌ماندن کمی متفاوت است.",
            f"در Java، دکمه‌ی {mat_fa} با تیراندازی از کمان نیز فعال می‌شود؛ در Bedrock همین رفتار است.",
            f"در Bedrock، دکمه‌ی {mat_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_pressure_plate_content(block_id, name_en, name_fa, hardness, wiki_link):
    mat = detect_wood_type(block_id, name_en)
    if mat:
        meta = WOOD[mat]
        mat_fa = meta["fa"]
        added = meta["added"]
        is_wood = True
        weight_text = "هر بازیکن یا ماب"
        signal_text = "سیگنال ۱۵ رداستون"
    elif "polished-blackstone" in block_id:
        mat_fa = "سنگ سیاه صیقل‌خورده"; added = "Java 1.16 (2020)"; is_wood = False
        weight_text = "هر بازیکن یا ماب"; signal_text = "سیگنال ۱۵ رداستون"
    elif block_id == "heavy-weighted-pressure-plate":
        mat_fa = "آهن"; added = "Java 1.5 (2013)"; is_wood = False
        weight_text = "گروه آیتم/ماب سنگین"; signal_text = "سیگنال متناسب با تعداد ماب‌ها"
    elif block_id == "light-weighted-pressure-plate":
        mat_fa = "طلا"; added = "Java 1.5 (2013)"; is_wood = False
        weight_text = "گروه آیتم/ماب سبک"; signal_text = "سیگنال متناسب با تعداد ماب‌ها"
    elif block_id == "stone-pressure-plate" or block_id == "pressure-plate":
        mat_fa = "سنگ"; added = "Java Beta 1.9 (2011)"; is_wood = False
        weight_text = "هر بازیکن یا ماب"; signal_text = "سیگنال ۱۵ رداستون"
    else:
        return None
    source = f"تخته‌ی {mat_fa}" if is_wood else (f"بلوک {mat_fa}" if "weighted" in block_id else mat_fa)
    return {
        "intro": [
            f"صفحه‌ی فشار {mat_fa} (Pressure Plate) بلاک رداستون است که از {source} ساخته می‌شود و وقتی {weight_text} روی آن قدم می‌گذارد، {signal_text} ساطع می‌کند. این بلاک سختی ۰.۵ دارد و در میز ساخت به‌صورت ۲ تایی از ۲ {source} ساخته می‌شود.",
            f"صفحه‌ی فشار {mat_fa} در سطح کف و سقف قابل قرار دادن است و در ساخت تله‌های رداستون و درهای خودکار کاربرد فراوان دارد. این بلاک در ۹ بلاک مجاور فعال می‌شود (رداستون).",
            f"این صفحه در نسخه‌ی {added} به بازی اضافه شد و در ساخت سیستم‌های ضد ماب و درب‌های خودکار بسیار پرکاربرد است. صفحه‌ی چوبی و سنگی فقط با بازیکن/ماب فعال می‌شوند، ولی صفحات وزنی با آیتم نیز فعال می‌شوند.",
        ],
        "behavior": [
            f"صفحه‌ی فشار {mat_fa} سختی ۰.۵ دارد و با هر ابزاری قابل جمع‌آوری است. این بلاک با {weight_text} {signal_text} می‌دهد.",
            f"این بلاک از ۲ {source} در میز ساخت به ۲ صفحه تبدیل می‌شود و در ساخت تله‌های رداستون و درهای خودکار بسیار پرکاربرد است.",
            f"صفحه‌ی فشار {mat_fa} در سطح کف و سقف قابل قرار دادن است و در ساخت سیستم‌های ضد ماب بسیار پرکاربرد است. صفحات سنگی فقط با بازیکن/ماب، ولی صفحات وزنی با آیتم نیز فعال می‌شوند.",
        ],
        "trivia": [
            f"صفحه‌ی فشار {mat_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            f"این بلاک با {weight_text} {signal_text} می‌دهد و در ۹ بلاک مجاور فعال می‌شود.",
            f"صفحه‌ی فشار {mat_fa} سختی ۰.۵ دارد و در سطح کف و سقف قابل قرار دادن است.",
            f"این بلاک در ساخت تله‌های رداستون و درهای خودکار بسیار پرکاربرد است.",
            f"صفحه‌ی فشار {mat_fa} صفحات سنگی فقط با بازیکن/ماب، ولی صفحات وزنی با آیتم نیز فعال می‌شوند.",
        ],
        "history": [
            {"version": added, "change": f"افزودن صفحه‌ی فشار {mat_fa} به ماینکرفت."},
            {"version": "Java 1.13 (2018)", "change": "بهبود مدل رندر صفحات فشار و رفع باگ‌های قدیمی."},
            {"version": "Bedrock 1.4 (2016)", "change": f"افزودن صفحه‌ی فشار {mat_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.14 (2019)", "change": "افزودن قابلیت قرار دادن صفحات فشار روی سقف و بهبود رفتار رداستون."},
            {"version": "Java 1.20 (2023)", "change": "بهبود انیمیشن فشرده شدن صفحات فشار و هماهنگ‌سازی رفتار رداستون."},
        ],
        "differences": [
            f"در Java، صفحه‌ی فشار {mat_fa} سختی ۰.۵ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما زمان فعال‌ماندن کمی متفاوت است.",
            f"در Java، صفحه‌ی فشار {mat_fa} با {weight_text} فعال می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، صفحه‌ی فشار {mat_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_fence_gate_content(block_id, name_en, name_fa, hardness, wiki_link):
    mat = detect_wood_type(block_id, name_en)
    if mat is None:
        return None
    meta = WOOD[mat]
    mat_fa = meta["fa"]
    added = meta["added"]
    return {
        "intro": [
            f"دروازه‌ی حصار {mat_fa} (Fence Gate) بلاک ساختمانی است که از تخته‌ی {mat_fa} و چوب‌دست (Stick) ساخته می‌شود و برای ساخت درِ حصار و ورودی محوطه کاربرد دارد. این بلاک سختی ۱.۰ دارد و ارتفاع ۱.۵ بلاک دارد.",
            f"دروازه‌ی حصار {mat_fa} با کلیک راست باز و بسته می‌شود و با رداستون قابل کنترل است. این بلاک در ساخت حصار و دفاع محوطه بسیار پرکاربرد است و مانع عبور ماب‌ها می‌شود.",
            f"این دروازه در نسخه‌ی {added} به بازی اضافه شد و در ساخت روستاها و مزرعه‌ها بسیار پرکاربرد است. در حالت باز بازیکن و ماب‌ها عبور می‌کنند، اما در حالت بسته مانع می‌شود.",
        ],
        "behavior": [
            f"دروازه‌ی حصار {mat_fa} سختی ۱.۰ دارد و با تبر (Axe) سریع‌ترین روش جمع‌آوری است. این بلاک ارتفاع ۱.۵ بلاک دارد و با کلیک راست باز و بسته می‌شود.",
            f"این بلاک از ۲ تخته‌ی {mat_fa} + ۴ Stick + ۲ تخته‌ی {mat_fa} در میز ساخت ساخته می‌شود و با رداستون قابل کنترل است. در ساخت حصار محوطه بسیار پرکاربرد است.",
            f"دروازه‌ی حصار {mat_fa} در حالت باز بازیکن و ماب‌ها عبور می‌کنند، اما در حالت بسته مانع می‌شود. این بلاک در ساخت حصار دفاعی بسیار پرکاربرد است.",
        ],
        "trivia": [
            f"دروازه‌ی حصار {mat_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            f"این بلاک ارتفاع ۱.۵ بلاک دارد و با کلیک راست باز و بسته می‌شود.",
            f"دروازه‌ی حصار {mat_fa} سختی ۱.۰ دارد و با Axe سریع‌ترین روش جمع‌آوری است.",
            f"این بلاک با رداستون قابل کنترل است و در ساخت حصار محوطه بسیار پرکاربرد است.",
            f"دروازه‌ی حصار {mat_fa} در حالت باز عبور می‌دهد و در حالت بسته مانع ماب‌ها می‌شود.",
        ],
        "history": [
            {"version": added, "change": f"افزودن دروازه‌ی حصار {mat_fa} به ماینکرفت."},
            {"version": "Java 1.13 (2018)", "change": "بهبود مدل رندر دروازه‌های حصار و رفع باگ‌های قدیمی همپوشانی."},
            {"version": "Bedrock 1.9 (2017)", "change": f"افزودن دروازه‌ی حصار {mat_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.14 (2019)", "change": "افزودن قابلیت قراردادن روی دیوار و بهبود رفتار رداستون."},
            {"version": "Java 1.20 (2023)", "change": "بهبود انیمیشن باز و بسته شدن دروازه‌ها و هماهنگ‌سازی رفتار رداستون."},
        ],
        "differences": [
            f"در Java، دروازه‌ی حصار {mat_fa} سختی ۱.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، دروازه‌ی حصار {mat_fa} با کلیک راست باز و بسته می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، دروازه‌ی حصار {mat_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_fence_content(block_id, name_en, name_fa, hardness, wiki_link):
    mat = detect_wood_type(block_id, name_en)
    if mat:
        meta = WOOD[mat]
        mat_fa = meta["fa"]
        added = meta["added"]
        is_wood = True
    elif block_id == "nether-brick-fence":
        mat_fa = "آجر ندر"; added = "Java 1.0 (2011)"; is_wood = False
    else:
        return None
    source = f"تخته‌ی {mat_fa}" if is_wood else mat_fa
    return {
        "intro": [
            f"حصار {mat_fa} (Fence) بلاک ساختمانی است که از {source} و چوب‌دست (Stick) ساخته می‌شود و برای ساخت حصار و دفاع محوطه کاربرد دارد. این بلاک سختی {'۲.۰' if not is_wood else '۱.۵'} دارد و ارتفاع ۱.۵ بلاک دارد.",
            f"حصار {mat_fa} به‌صورت خودکار به حصارهای مجاور متصل می‌شود و مانع عبور ماب‌ها می‌شود (به‌جز اسپایدر). این رفتار هوشمند حصار را برای محصور کردن محوطه‌ها بسیار کارآمد می‌کند.",
            f"این حصار در نسخه‌ی {added} به بازی اضافه شد و در ساخت حصار حیاط و دفاع ساختمان بسیار پرکاربرد است. در ساخت روستاها و مزرعه‌ها نیز بسیار استفاده می‌شود.",
        ],
        "behavior": [
            f"حصار {mat_fa} سختی {'۲.۰' if not is_wood else '۱.۵'} دارد و با {'پیکه‌ی چوبی' if is_wood else 'ابزار مناسب'} قابل جمع‌آوری است. این بلاک ارتفاع ۱.۵ بلاک دارد و به‌صورت خودکار به حصارهای مجاور متصل می‌شود.",
            f"این بلاک از ۲ Stick + ۴ {source} در میز ساخت به ۳ حصار تبدیل می‌شود و مانع عبور ماب‌ها می‌شود (به‌جز اسپایدر). در ساخت حصار حیاط بسیار پرکاربرد است.",
            f"حصار {mat_fa} در برابر آتش و انفجار رفتاری مشابه {source} دارد و در ساخت حصار دفاعی بسیار پرکاربرد است. در ساخت روستاها و مزرعه‌ها نیز بسیار استفاده می‌شود.",
        ],
        "trivia": [
            f"حصار {mat_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            f"این بلاک ارتفاع ۱.۵ بلاک دارد و به‌صورت خودکار به حصارهای مجاور متصل می‌شود.",
            f"حصار {mat_fa} سختی {'۲.۰' if not is_wood else '۱.۵'} دارد و مانع عبور ماب‌ها (به‌جز اسپایدر) می‌شود.",
            f"این بلاک از ۲ Stick + ۴ {source} در میز ساخت ساخته می‌شود.",
            f"حصار {mat_fa} در ساخت حصار حیاط و دفاع ساختمان بسیار پرکاربرد است.",
        ],
        "history": [
            {"version": added, "change": f"افزودن حصار {mat_fa} به ماینکرفت."},
            {"version": "Java 1.13 (2018)", "change": "بهبود مدل رندر حصارها و رفع باگ‌های قدیمی اتصال."},
            {"version": "Bedrock 1.9 (2017)", "change": f"افزودن حصار {mat_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.14 (2019)", "change": "افزودن قابلیت اتصال حصارها به بلاک‌های دیگر و بهبود رفتار رداستون."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر حصارها و هماهنگ‌سازی رفتار اشتراکی با بلاک‌های مرجع."},
        ],
        "differences": [
            f"در Java، حصار {mat_fa} سختی {'۲.۰' if not is_wood else '۱.۵'} و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، اتصال خودکار حصار {mat_fa} به بلاک‌های مجاور بر اساس نوع بلاک است؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، حصار {mat_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_wood_content(block_id, name_en, name_fa, hardness, wiki_link):
    """For X Wood (bark on all 6 sides) and Stripped X Wood."""
    is_stripped = name_en.startswith("Stripped ")
    mat = detect_wood_type(block_id, name_en)
    if mat is None:
        return None
    meta = WOOD[mat]
    mat_fa = meta["fa"]
    added = meta["added"]
    name_short = ("تنه‌ی کنده‌شده‌ی " + mat_fa) if is_stripped else ("چوب " + mat_fa)
    name_full = ("تنه‌ی کنده‌شده‌ی " + mat_fa + " (Stripped Wood)") if is_stripped else ("چوب " + mat_fa + " (Wood)")
    return {
        "intro": [
            f"{name_full} بلاک ساختمانی است که از تنه‌ی {mat_fa} ساخته می‌شود و برای ساخت چوب با پوست یکسان در ۶ طرف کاربرد دارد. این بلاک سختی ۲.۰ دارد و در میز ساخت از ۴ تنه‌ی {mat_fa} ساخته می‌شود.",
            f"{name_short} برخلاف تنه (Log) که پوست فقط در ۴ طرف دارد، در تمام ۶ طرف پوست یکسان دارد. این ویژگی آن را برای ساخت ستون و دیوار چوبی بسیار مناسب می‌کند.",
            f"این بلاک در نسخه‌ی {added} به بازی اضافه شد و در ساخت دکوراسیون چوبی و ستون‌ها بسیار پرکاربرد است. نسخه‌ی کنده‌شده‌ی آن با کلیک راست تبر (Axe) روی تنه‌ی {mat_fa} نیز به‌دست می‌آید.",
        ],
        "behavior": [
            f"{name_short} سختی ۲.۰ دارد و با تبر (Axe) سریع‌ترین روش جمع‌آوری است. این بلاک در ۶ طرف بافت یکسان دارد و در ساخت ستون چوبی بسیار پرکاربرد است.",
            f"این بلاک از ۴ تنه‌ی {mat_fa} در میز ساخت (به شکل ۲×۲) ساخته می‌شود و در ساخت دکوراسیون چوبی بسیار پرکاربرد است. در ساخت روستاها و ساختمان چوبی نیز بسیار استفاده می‌شود.",
            f"{name_short} در برابر آتش و انفجار رفتاری مشابه تنه‌ی {mat_fa} دارد و در ساخت چوبی ساختمان بسیار پرکاربرد است. نسخه‌ی کنده‌شده‌ی آن با کلیک راست Axe روی تنه نیز به‌دست می‌آید.",
        ],
        "trivia": [
            f"{name_short} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            f"این بلاک در ۶ طرف بافت یکسان دارد و در ساخت ستون چوبی بسیار پرکاربرد است.",
            f"{name_short} سختی ۲.۰ دارد و با Axe سریع‌ترین روش جمع‌آوری است.",
            f"این بلاک از ۴ تنه‌ی {mat_fa} در میز ساخت (۲×۲) ساخته می‌شود.",
            f"{name_short} در ساخت دکوراسیون چوبی و ستون‌ها بسیار پرکاربرد است.",
        ],
        "history": [
            {"version": added, "change": f"افزودن {name_short} به ماینکرفت."},
            {"version": "Java 1.13 (2018)", "change": "تفکیک Wood و Log به بلاک‌های مجزا و رفع باگ‌های قدیمی."},
            {"version": "Bedrock 1.9 (2017)", "change": f"افزودن {name_short} به نسخه‌ی Bedrock."},
            {"version": "Java 1.14 (2019)", "change": "افزودن قابلیت کنده‌کردن پوست با کلیک راست Axe و افزودن نسخه‌ی stripped."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر Woodها و هماهنگ‌سازی رفتار اشتراکی با Logها."},
        ],
        "differences": [
            f"در Java، {name_short} سختی ۲.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر پوست کمی متفاوت است.",
            f"در Java، {name_short} با کلیک راست Axe روی تنه قابل کنده‌کردن است؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، {name_short} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_log_content(block_id, name_en, name_fa, hardness, wiki_link):
    is_stripped = name_en.startswith("Stripped ")
    mat = detect_wood_type(block_id, name_en)
    if mat is None:
        return None
    meta = WOOD[mat]
    mat_fa = meta["fa"]
    added = meta["added"]
    name_short = ("تنه‌ی کنده‌شده‌ی " + mat_fa) if is_stripped else ("تنه‌ی " + mat_fa)
    name_full = ("تنه‌ی کنده‌شده‌ی " + mat_fa + " (Stripped Log)") if is_stripped else ("تنه‌ی " + mat_fa + " (Log)")
    return {
        "intro": [
            f"{name_full} بلاک ساختمانی است که از درخت {mat_fa} به‌دست می‌آید و برای ساخت تخته و دکوراسیون چوبی کاربرد دارد. این بلاک سختی ۲.۰ دارد و در جنگل‌های {meta['biome']} به‌وفور یافت می‌شود.",
            f"{name_short} در ۳ جهت (افقی، عمودی X، عمودی Z) قابل قرار دادن است و در ساخت ستون و دیوار چوبی بسیار پرکاربرد است. این بلاک در ۴ طرف پوست و در ۲ طرف رگه‌های چوبی دارد.",
            f"این بلاک در نسخه‌ی {added} به بازی اضافه شد و در ساخت چوبی ساختمان و روستاها بسیار پرکاربرد است. نسخه‌ی کنده‌شده‌ی آن با کلیک راست تبر (Axe) روی تنه‌ی {mat_fa} نیز به‌دست می‌آید.",
        ],
        "behavior": [
            f"{name_short} سختی ۲.۰ دارد و با تبر (Axe) سریع‌ترین روش جمع‌آوری است. این بلاک در ۳ جهت قابل قرار دادن است و در ساخت ستون چوبی بسیار پرکاربرد است.",
            f"این بلاک از درخت {mat_fa} در {meta['biome']} به‌دست می‌آید و در ساخت تخته‌ی {mat_fa} (۴ تنه → ۴ تخته) بسیار پرکاربرد است. در ساخت روستاها و ساختمان چوبی نیز استفاده می‌شود.",
            f"{name_short} در برابر آتش به‌سرعت می‌سوزد و در ساخت چوبی ساختمان بسیار پرکاربرد است. نسخه‌ی کنده‌شده‌ی آن با کلیک راست Axe روی تنه نیز به‌دست می‌آید.",
        ],
        "trivia": [
            f"{name_short} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            f"این بلاک در ۳ جهت قابل قرار دادن است و در ساخت ستون چوبی بسیار پرکاربرد است.",
            f"{name_short} سختی ۲.۰ دارد و با Axe سریع‌ترین روش جمع‌آوری است.",
            f"این بلاک از درخت {mat_fa} در {meta['biome']} به‌دست می‌آید و در ساخت تخته بسیار پرکاربرد است.",
            f"{name_short} در برابر آتش به‌سرعت می‌سوزد و در ساخت چوبی ساختمان بسیار پرکاربرد است.",
        ],
        "history": [
            {"version": added, "change": f"افزودن {name_short} به ماینکرفت."},
            {"version": "Java 1.13 (2018)", "change": "تفکیک Wood و Log به بلاک‌های مجزا و رفع باگ‌های قدیمی."},
            {"version": "Bedrock 1.9 (2017)", "change": f"افزودن {name_short} به نسخه‌ی Bedrock."},
            {"version": "Java 1.14 (2019)", "change": "افزودن قابلیت کنده‌کردن پوست با کلیک راست Axe و افزودن نسخه‌ی stripped."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر Logها و هماهنگ‌سازی رفتار اشتراکی با Woodها."},
        ],
        "differences": [
            f"در Java، {name_short} سختی ۲.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر پوست کمی متفاوت است.",
            f"در Java، {name_short} با کلیک راست Axe روی تنه قابل کنده‌کردن است؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، {name_short} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_planks_content(block_id, name_en, name_fa, hardness, wiki_link):
    mat = detect_wood_type(block_id, name_en)
    if mat is None:
        return None
    meta = WOOD[mat]
    mat_fa = meta["fa"]
    added = meta["added"]
    return {
        "intro": [
            f"تخته‌ی {mat_fa} (Planks) بلاک ساختمانی است که از تنه‌ی {mat_fa} ساخته می‌شود و برای ساخت ابزار، در، پله، اسلب و دکوراسیون چوبی کاربرد دارد. این بلاک سختی ۲.۰ دارد و در میز ساخت از ۱ تنه‌ی {mat_fa} به ۴ تخته تبدیل می‌شود.",
            f"تخته‌ی {mat_fa} در ساخت میز ساخت، صندوق، در، تله‌در، پله، اسلب، حصار و دروازه‌ی حصار بسیار پرکاربرد است. این بلاک در {meta['biome']} از تنه‌ی درخت {mat_fa} به‌وفور به‌دست می‌آید.",
            f"این تخته در نسخه‌ی {added} به بازی اضافه شد و از همان زمان یکی از پرکاربردترین بلاک‌های ساختمانی ماینکرفت است. در ساخت روستاها و ساختمان چوبی بسیار استفاده می‌شود.",
        ],
        "behavior": [
            f"تخته‌ی {mat_fa} سختی ۲.۰ دارد و با تبر (Axe) سریع‌ترین روش جمع‌آوری است. این بلاک در ساخت ابزار و ساختمان چوبی بسیار پرکاربرد است.",
            f"این بلاک از ۱ تنه‌ی {mat_fa} در میز ساخت به ۴ تخته تبدیل می‌شود و در ساخت میز ساخت، صندوق، در، پله، اسلب، حصار بسیار پرکاربرد است. در ساخت روستاها نیز استفاده می‌شود.",
            f"تخته‌ی {mat_fa} در برابر آتش به‌سرعت می‌سوزد و در ساخت چوبی ساختمان بسیار پرکاربرد است. در ساخت ابزارهای اولیه و میز ساخت نیز بسیار استفاده می‌شود.",
        ],
        "trivia": [
            f"تخته‌ی {mat_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            f"این بلاک از ۱ تنه‌ی {mat_fa} به ۴ تخته تبدیل می‌شود و در ساخت ابزار بسیار پرکاربرد است.",
            f"تخته‌ی {mat_fa} سختی ۲.۰ دارد و با Axe سریع‌ترین روش جمع‌آوری است.",
            f"این بلاک در ساخت میز ساخت، صندوق، در، پله، اسلب، حصار بسیار پرکاربرد است.",
            f"تخته‌ی {mat_fa} در برابر آتش به‌سرعت می‌سوزد و در ساخت چوبی ساختمان بسیار پرکاربرد است.",
        ],
        "history": [
            {"version": added, "change": f"افزودن تخته‌ی {mat_fa} به ماینکرفت."},
            {"version": "Java 1.13 (2018)", "change": "تفکیک Planksها به بلاک‌های مجزا و رفع باگ‌های قدیمی."},
            {"version": "Bedrock 1.9 (2017)", "change": f"افزودن تخته‌ی {mat_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.14 (2019)", "change": "افزودن قابلیت ساخت Signها و Hanging Signها از Planks."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر Planksها و هماهنگ‌سازی رفتار اشتراکی با Logها."},
        ],
        "differences": [
            f"در Java، تخته‌ی {mat_fa} سختی ۲.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، تخته‌ی {mat_fa} در ساخت Signها و Hanging Signها کاربرد دارد؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، تخته‌ی {mat_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_leaves_content(block_id, name_en, name_fa, hardness, wiki_link):
    mat = detect_wood_type(block_id, name_en)
    if mat:
        meta = WOOD[mat]
        mat_fa = meta["fa"]
        added = meta["added"]
        return {
            "intro": [
                f"برگ {mat_fa} (Leaves) بلاک طبیعی است که از درخت {mat_fa} به‌دست می‌آید و برای دکوراسیون و گیاه‌پروری کاربرد دارد. این بلاک سختی ۰.۲ دارد و در {meta['biome']} از درختان {mat_fa} به‌وفور یافت می‌شود.",
                f"برگ {mat_fa} با قیچی (Shears) یا با ابزار Silk Touch قابل جمع‌آوری است و در غیر این صورت احتمال افتادن Sapling {mat_fa} را دارد. این بلاک شفاف است و نور را عبور می‌دهد.",
                f"این برگ در نسخه‌ی {added} به بازی اضافه شد و در ساخت دکوراسیون طبیعی و باغ‌ها بسیار پرکاربرد است. در صورت عدم اتصال به تنه‌ی درخت، پس از مدتی خشک و ریزش می‌کند.",
            ],
            "behavior": [
                f"برگ {mat_fa} سختی ۰.۲ دارد و با قیچی (Shears) یا ابزار Silk Touch قابل جمع‌آوری است. این بلاک شفاف است و نور را عبور می‌دهد.",
                f"این بلاک از درخت {mat_fa} در {meta['biome']} به‌دست می‌آید و در غیر این صورت احتمال افتادن Sapling {mat_fa} را دارد. در ساخت دکوراسیون طبیعی بسیار پرکاربرد است.",
                f"برگ {mat_fa} در صورت عدم اتصال به تنه‌ی درخت، پس از مدتی خشک و ریزش می‌کند. در ساخت هدج‌ها و باغ‌ها بسیار پرکاربرد است.",
            ],
            "trivia": [
                f"برگ {mat_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
                f"این بلاک سختی ۰.۲ دارد و با Shears یا Silk Touch قابل جمع‌آوری است.",
                f"برگ {mat_fa} از درخت {mat_fa} در {meta['biome']} به‌دست می‌آید و احتمال افتادن Sapling دارد.",
                f"این بلاک شفاف است و نور را عبور می‌دهد و در ساخت هدج‌ها بسیار پرکاربرد است.",
                f"برگ {mat_fa} در صورت عدم اتصال به تنه، پس از مدتی خشک و ریزش می‌کند.",
            ],
            "history": [
                {"version": added, "change": f"افزودن برگ {mat_fa} به ماینکرفت."},
                {"version": "Java 1.13 (2018)", "change": "تفکیک Leavesها به بلاک‌های مجزا و رفع باگ‌های قدیمی ریزش."},
                {"version": "Bedrock 1.9 (2017)", "change": f"افزودن برگ {mat_fa} به نسخه‌ی Bedrock."},
                {"version": "Java 1.14 (2019)", "change": "بهبود مدل رندر Leavesها و رفتار ریزش در نبود درخت."},
                {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر Leavesها و هماهنگ‌سازی رفتار اشتراکی با Saplingها."},
            ],
            "differences": [
                f"در Java، برگ {mat_fa} سختی ۰.۲ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
                f"در Java، برگ {mat_fa} در نبود درخت پس از مدتی ریزش می‌کند؛ در Bedrock همین رفتار، اما زمان ریزش کمی متفاوت است.",
                f"در Bedrock، برگ {mat_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
            ],
        }
    elif block_id == "azalea-leaves" or block_id == "flowering-azalea-leaves":
        is_flowering = block_id == "flowering-azalea-leaves"
        mat_fa = "آزالیا شکوفه‌دار" if is_flowering else "آزالیا"
        return {
            "intro": [
                f"برگ {mat_fa} (Leaves) بلاک طبیعی است که از درخت آزالیا در بایوم Lush Caves به‌دست می‌آید و برای دکوراسیون و گیاه‌پروری کاربرد دارد. این بلاک سختی ۰.۲ دارد و در جنگل‌های غار flourishing به‌وفور یافت می‌شود.",
                f"برگ {mat_fa} با قیچی (Shears) یا با ابزار Silk Touch قابل جمع‌آوری است و در غیر این صورت احتمال افتادن Azalea یا Flowering Azalea را دارد. این بلاک شفاف است و نور را عبور می‌دهد.",
                f"این برگ در نسخه‌ی Java 1.17 (2021) به بازی اضافه شد و در ساخت دکوراسیون طبیعی و باغ‌ها بسیار پرکاربرد است. نسخه‌ی شکوفه‌دار آن گل‌های صورتی روی برگ دارد.",
            ],
            "behavior": [
                f"برگ {mat_fa} سختی ۰.۲ دارد و با Shears یا Silk Touch قابل جمع‌آوری است. این بلاک شفاف است و نور را عبور می‌دهد.",
                f"این بلاک از درخت آزالیا در Lush Caves به‌دست می‌آید و در غیر این صورت احتمال افتادن Azalea یا Flowering Azalea را دارد. در ساخت دکوراسیون طبیعی بسیار پرکاربرد است.",
                f"برگ {mat_fa} در صورت عدم اتصال به تنه‌ی درخت، پس از مدتی خشک و ریزش نمی‌کند (برخلاف سایر برگ‌ها). در ساخت هدج‌ها و باغ‌ها بسیار پرکاربرد است.",
            ],
            "trivia": [
                f"برگ {mat_fa} در نسخه‌ی Java 1.17 (2021) به ماینکرفت اضافه شد.",
                f"این بلاک سختی ۰.۲ دارد و با Shears یا Silk Touch قابل جمع‌آوری است.",
                f"برگ {mat_fa} از درخت آزالیا در Lush Caves به‌دست می‌آید و احتمال افتادن Azalea دارد.",
                f"این بلاک شفاف است و نور را عبور می‌دهد و در ساخت هدج‌ها بسیار پرکاربرد است.",
                f"برگ {mat_fa} برخلاف سایر برگ‌ها، در نبود تنه ریزش نمی‌کند.",
            ],
            "history": [
                {"version": "Java 1.17 (2021)", "change": f"افزودن برگ {mat_fa} به ماینکرفت به‌همراه Caves & Cliffs Part 2."},
                {"version": "Java 1.18 (2021)", "change": "افزودن درخت آزالیا به‌صورت طبیعی در Lush Caves."},
                {"version": "Bedrock 1.18 (2021)", "change": f"افزودن برگ {mat_fa} به نسخه‌ی Bedrock."},
                {"version": "Java 1.19 (2022)", "change": "بهبود مدل رندر برگ‌های آزالیا و رفع باگ‌های ریزش."},
                {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر Leavesها و هماهنگ‌سازی رفتار اشتراکی با Azalea."},
            ],
            "differences": [
                f"در Java، برگ {mat_fa} سختی ۰.۲ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
                f"در Java، برگ {mat_fa} در نبود تنه ریزش نمی‌کند؛ در Bedrock همین رفتار، اما زمان ریزش کمی متفاوت است.",
                f"در Bedrock، برگ {mat_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.18 (2021) با Java هماهنگ شد.",
            ],
        }
    return None


# ---------------------------------------------------------------------------
# Carpet / Banner / Concrete — single blocks (generic color variants root)
# ---------------------------------------------------------------------------
def build_carpet_content(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id != "carpet":
        return None
    return {
        "intro": [
            "فرش (Carpet) بلاک تزئینی نازک است که از ۲ پشم ساخته می‌شود و در ۱۶ رنگ مختلف موجود است. این بلاک سختی ۰.۱ دارد و ضخامت ۱ پیکسل (۱۶عکل بلاک) دارد و در ساخت کف‌پوش تزئینی و دکوراسیون بسیار پرکاربرد است.",
            "فرش شفاف است و نور را عبور می‌دهد، و مانع عبور ماب‌ها نمی‌شود (مگر در حالت خاص). این بلاک در ساخت کف‌پوش رنگی و دکوراسیون داخلی بسیار پرکاربرد است و می‌توان آن را روی بلوک‌های دیگر قرار داد.",
            "فرش در نسخه‌ی Java 1.6 (2013) به بازی اضافه شد و در ۱۶ رنگ مختلف در دسترس است. این بلاک در ساخت کف‌پوش رنگی و دکوراسیون داخلی ساختمان بسیار پرکاربرد است.",
        ],
        "behavior": [
            "فرش سختی ۰.۱ دارد و با هر ابزاری قابل جمع‌آوری است. این بلاک ضخامت ۱ پیکسل دارد و شفاف است و نور را عبور می‌دهد.",
            "این بلاک از ۲ پشم در میز ساخت به ۳ فرش تبدیل می‌شود و در ۱۶ رنگ مختلف در دسترس است. در ساخت کف‌پوش رنگی و دکوراسیون داخلی بسیار پرکاربرد است.",
            "فرش در ساخت تله‌های ضد ماب نیز کاربرد دارد (ماب‌ها روی فرش لانه نمی‌کنند) و در ساخت دفاعی ساختمان نیز استفاده می‌شود. در ساخت کف‌پوش رنگی بسیار پرکاربرد است.",
        ],
        "trivia": [
            "فرش در نسخه‌ی Java 1.6 (2013) به ماینکرفت اضافه شد.",
            "این بلاک سختی ۰.۱ دارد و ضخامت ۱ پیکسل (۱۶عکل بلاک) دارد.",
            "فرش شفاف است و نور را عبور می‌دهد و در ساخت کف‌پوش رنگی بسیار پرکاربرد است.",
            "این بلاک از ۲ پشم به ۳ فرش تبدیل می‌شود و در ۱۶ رنگ مختلف در دسترس است.",
            "فرش در ساخت تله‌های ضد ماب نیز کاربرد دارد (ماب‌ها روی فرش لانه نمی‌کنند).",
        ],
        "history": [
            {"version": "Java 1.6 (2013)", "change": "افزودن فرش به ماینکرفت به‌عنوان بلاک تزئینی نازک."},
            {"version": "Bedrock 1.1 (2016)", "change": "افزودن فرش به نسخه‌ی Bedrock."},
            {"version": "Java 1.8 (2014)", "change": "افزودن ۱۶ رنگ مختلف فرش به بازی."},
            {"version": "Java 1.14 (2019)", "change": "افزودن قابلیت قرار دادن فرش روی بلوک‌های شفاف و بهبود رفتار ریزش."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر فرش‌ها و هماهنگ‌سازی رفتار اشتراکی با Wool."},
        ],
        "differences": [
            "در Java، فرش سختی ۰.۱ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            "در Java، فرش شفاف است و نور را عبور می‌دهد؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            "در Bedrock، فرش در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_banner_content(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id != "banner":
        return None
    return {
        "intro": [
            "پرچم (Banner) بلاک تزئینی است که از ۶ پشم و ۱ چوب‌دست (Stick) ساخته می‌شود و با ۳۸ طرح مختلف قابل سفارشی‌سازی است. این بلاک سختی ۱.۰ دارد و در ساخت پرچم و تزئینی ساختمان بسیار پرکاربرد است.",
            "پرچم با ۱۶ رنگ اصلی و ۳۸ طرح قابل سفارشی‌سازی است و در میز نساجی (Loom) با رنگ‌ها و الگوهای مختلف تزئین می‌شود. این بلاک در ساخت نشان، پرچم و دکوراسیون بسیار پرکاربرد است.",
            "این پرچم در نسخه‌ی Java 1.8 (2014) به بازی اضافه شد و در ۱۶ رنگ اصلی و ۳۸ طرح مختلف در دسترس است. در ساخت نشان قبیله و دکوراسیون ساختمان بسیار پرکاربرد است.",
        ],
        "behavior": [
            "پرچم سختی ۱.۰ دارد و با تبر (Axe) سریع‌ترین روش جمع‌آوری است. این بلاک در ۱۶ جهت قابل قرار دادن است و با ۳۸ طرح قابل سفارشی‌سازی است.",
            "این بلاک از ۶ پشم + ۱ Stick در میز ساخت ساخته می‌شود و در میز نساجی (Loom) با رنگ‌ها و الگوهای مختلف تزئین می‌شود. در ساخت نشان و دکوراسیون بسیار پرکاربرد است.",
            "پرچم شفاف است و نور را عبور می‌دهد، و در ساخت نشان قبیله و دکوراسیون ساختمان بسیار پرکاربرد است. در نسخه‌ی Java 1.8 (2014) به بازی اضافه شد.",
        ],
        "trivia": [
            "پرچم در نسخه‌ی Java 1.8 (2014) به ماینکرفت اضافه شد.",
            "این بلاک سختی ۱.۰ دارد و در ۱۶ جهت قابل قرار دادن است.",
            "پرچم با ۱۶ رنگ اصلی و ۳۸ طرح قابل سفارشی‌سازی است و در میز نساجی تزئین می‌شود.",
            "این بلاک از ۶ پشم + ۱ Stick در میز ساخت ساخته می‌شود.",
            "پرچم در ساخت نشان قبیله و دکوراسیون ساختمان بسیار پرکاربرد است.",
        ],
        "history": [
            {"version": "Java 1.8 (2014)", "change": "افزودن پرچم به ماینکرفت به‌همراه ۳۸ طرح مختلف."},
            {"version": "Bedrock 1.2 (2017)", "change": "افزودن پرچم به نسخه‌ی Bedrock."},
            {"version": "Java 1.14 (2019)", "change": "افزودن میز نساجی (Loom) و بهبود سفارشی‌سازی پرچم."},
            {"version": "Java 1.17 (2021)", "change": "افزودن قابلیت قرار دادن پرچم در ۱۶ جهت و بهبود مدل رندر."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر پرچم‌ها و هماهنگ‌سازی رفتار اشتراکی با Wool."},
        ],
        "differences": [
            "در Java، پرچم سختی ۱.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            "در Java، پرچم در ۱۶ جهت قابل قرار دادن است؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            "در Bedrock، پرچم در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_concrete_content(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id != "concrete":
        return None
    return {
        "intro": [
            "بتن (Concrete) بلاک ساختمانی صاف و رنگی است که از Concrete Powder با آب ساخته می‌شود و در ۱۶ رنگ مختلف موجود است. این بلاک سختی ۱.۸ دارد و در ساخت ساختمان مدرن و دکوراسیون بسیار پرکاربرد است.",
            "بتن برخلاف پشم در برابر آتش مقاوم است و رنگ صاف و یکدست دارد. این بلاک برای ساخت ساختمان‌های مدرن و دکوراسیون داخلی بسیار مناسب است و در ۱۶ رنگ مختلف در دسترس است.",
            "این بلاک در نسخه‌ی Java 1.12 (2017) به بازی اضافه شد و در ساخت ساختمان مدرن و دکوراسیون بسیار پرکاربرد است. در ۱۶ رنگ مختلف در دسترس است.",
        ],
        "behavior": [
            "بتن سختی ۱.۸ دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است. این بلاک در برابر آتش کاملاً مقاوم است و رنگ صاف و یکدست دارد.",
            "این بلاک از Concrete Powder + آب ساخته می‌شود و در ۱۶ رنگ مختلف در دسترس است. در ساخت ساختمان مدرن و دکوراسیون داخلی بسیار پرکاربرد است.",
            "بتن در ساخت ساختمان‌های مدرن و دکوراسیون داخلی بسیار پرکاربرد است و در برابر آتش کاملاً مقاوم است. در ۱۶ رنگ مختلف در دسترس است.",
        ],
        "trivia": [
            "بتن در نسخه‌ی Java 1.12 (2017) به ماینکرفت اضافه شد.",
            "این بلاک سختی ۱.۸ دارد و در برابر آتش کاملاً مقاوم است.",
            "بتن از Concrete Powder با آب ساخته می‌شود و در ۱۶ رنگ مختلف در دسترس است.",
            "این بلاک رنگ صاف و یکدست دارد و در ساخت ساختمان مدرن بسیار پرکاربرد است.",
            "بتن در ساخت دکوراسیون داخلی و ساختمان‌های مدرن بسیار پرکاربرد است.",
        ],
        "history": [
            {"version": "Java 1.12 (2017)", "change": "افزودن بتن و Concrete Powder به ماینکرفت به‌همراه ۱۶ رنگ."},
            {"version": "Bedrock 1.1 (2016)", "change": "افزودن بتن به نسخه‌ی Bedrock."},
            {"version": "Java 1.13 (2018)", "change": "بهبود رفتار بتن در برابر آب و رفع باگ‌های قدیمی."},
            {"version": "Java 1.14 (2019)", "change": "بهبود مدل رندر بتن و هماهنگ‌سازی رنگ‌ها با سایر بلاک‌های رنگی."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر بتن‌ها و هماهنگ‌سازی رفتار اشتراکی با Concrete Powder."},
        ],
        "differences": [
            "در Java، بتن سختی ۱.۸ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            "در Java، بتن از Concrete Powder با آب ساخته می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            "در Bedrock، بتن در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_button_generic(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id != "button":
        return None
    return {
        "intro": [
            "دکمه (Button) بلاک رداستون است که با کلیک سیگنال کوتاه رداستون ساطع می‌کند و در ۶ جهت قابل قرار دادن است. این بلاک سختی ۰.۵ دارد و در ساخت تله‌های رداستون و درهای خودکار بسیار پرکاربرد است.",
            "دکمه‌ی چوبی ۱۵ تیک (۰.۷۵ ثانیه) و دکمه‌ی سنگی ۱۰ تیک (۰.۵ ثانیه) فعال می‌ماند و در ساخت تله‌های ضد ماب و درهای خودکار کاربرد فراوان دارد. این بلاک در ۶ جهت (۴ دیوار + سقف + کف) قابل قرار دادن است.",
            "این دکمه در نسخه‌ی Java Beta 1.9 (2011) به بازی اضافه شد و در ساخت تله‌های رداستون و درهای خودکار بسیار پرکاربرد است. دکمه‌ی چوبی را با تیراندازی از کمان نیز می‌توان فعال کرد.",
        ],
        "behavior": [
            "دکمه سختی ۰.۵ دارد و با هر ابزاری قابل جمع‌آوری است. این بلاک در ۶ جهت قابل قرار دادن است و با کلیک سیگنال کوتاه رداستون می‌دهد.",
            "این بلاک در ساخت تله‌های رداستون و درهای خودکار بسیار پرکاربرد است. دکمه‌ی چوبی ۱۵ تیک و دکمه‌ی سنگی ۱۰ تیک فعال می‌ماند.",
            "دکمه در برابر آتش و انفجار رفتاری مشابه ماده‌ی ساخت دارد و در ساخت تله‌های ضد ماب و سیستم‌های رداستون بسیار پرکاربرد است.",
        ],
        "trivia": [
            "دکمه در نسخه‌ی Java Beta 1.9 (2011) به ماینکرفت اضافه شد.",
            "این بلاک در ۶ جهت قابل قرار دادن است و با کلیک سیگنال کوتاه رداستون می‌دهد.",
            "دکمه سختی ۰.۵ دارد و دکمه‌ی چوبی ۱۵ تیک و دکمه‌ی سنگی ۱۰ تیک فعال می‌ماند.",
            "این بلاک در ساخت تله‌های رداستون و درهای خودکار بسیار پرکاربرد است.",
            "دکمه‌ی چوبی را با تیراندازی از کمان نیز می‌توان فعال کرد (در Java).",
        ],
        "history": [
            {"version": "Java Beta 1.9 (2011)", "change": "افزودن دکمه‌ی سنگی به ماینکرفت."},
            {"version": "Java 1.11 (2016)", "change": "افزودن قابلیت قرار دادن دکمه‌ها روی سقف و کف."},
            {"version": "Bedrock 1.4 (2016)", "change": "افزودن دکمه به نسخه‌ی Bedrock."},
            {"version": "Java 1.13 (2018)", "change": "بهبود مدل رندر دکمه‌ها و رفع باگ‌های قدیمی."},
            {"version": "Java 1.20 (2023)", "change": "بهبود انیمیشن فشرده شدن دکمه‌ها و هماهنگ‌سازی رفتار رداستون."},
        ],
        "differences": [
            "در Java، دکمه سختی ۰.۵ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما زمان فعال‌ماندن کمی متفاوت است.",
            "در Java، دکمه با تیراندازی از کمان نیز فعال می‌شود؛ در Bedrock همین رفتار است.",
            "در Bedrock، دکمه در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def build_pressure_plate_generic(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id != "pressure-plate":
        return None
    return {
        "intro": [
            "صفحه‌ی فشار (Pressure Plate) بلاک رداستون است که وقتی بازیکن یا ماب روی آن قدم می‌گذارد، سیگنال ۱۵ رداستون ساطع می‌کند. این بلاک سختی ۰.۵ دارد و در سطح کف و سقف قابل قرار دادن است.",
            "صفحه‌ی فشار در ساخت تله‌های رداستون و درهای خودکار کاربرد فراوان دارد و در ۹ بلاک مجاور فعال می‌شود (رداستون). این بلاک با بازیکن/ماب (سنگی) یا با آیتم (وزنی) فعال می‌شود.",
            "این صفحه در نسخه‌ی Java Beta 1.9 (2011) به بازی اضافه شد و در ساخت سیستم‌های ضد ماب و درب‌های خودکار بسیار پرکاربرد است. صفحات سنگی فقط با بازیکن/ماب، ولی صفحات وزنی با آیتم نیز فعال می‌شوند.",
        ],
        "behavior": [
            "صفحه‌ی فشار سختی ۰.۵ دارد و با هر ابزاری قابل جمع‌آوری است. این بلاک با بازیکن/ماب (سنگی) یا با آیتم (وزنی) سیگنال ۱۵ رداستون می‌دهد.",
            "این بلاک در سطح کف و سقف قابل قرار دادن است و در ساخت تله‌های رداستون و درهای خودکار بسیار پرکاربرد است. در ۹ بلاک مجاور فعال می‌شود.",
            "صفحه‌ی فشار در ساخت سیستم‌های ضد ماب و درب‌های خودکار بسیار پرکاربرد است. صفحات سنگی فقط با بازیکن/ماب، ولی صفحات وزنی با آیتم نیز فعال می‌شوند.",
        ],
        "trivia": [
            "صفحه‌ی فشار در نسخه‌ی Java Beta 1.9 (2011) به ماینکرفت اضافه شد.",
            "این بلاک با بازیکن/ماب یا آیتم سیگنال ۱۵ رداستون می‌دهد و در ۹ بلاک مجاور فعال می‌شود.",
            "صفحه‌ی فشار سختی ۰.۵ دارد و در سطح کف و سقف قابل قرار دادن است.",
            "این بلاک در ساخت تله‌های رداستون و درهای خودکار بسیار پرکاربرد است.",
            "صفحه‌ی فشار صفحات سنگی فقط با بازیکن/ماب، ولی صفحات وزنی با آیتم نیز فعال می‌شوند.",
        ],
        "history": [
            {"version": "Java Beta 1.9 (2011)", "change": "افزودن صفحه‌ی فشار سنگی و چوبی به ماینکرفت."},
            {"version": "Java 1.5 (2013)", "change": "افزودن صفحات وزنی (آهن و طلا) به بازی."},
            {"version": "Bedrock 1.4 (2016)", "change": "افزودن صفحه‌ی فشار به نسخه‌ی Bedrock."},
            {"version": "Java 1.13 (2018)", "change": "بهبود مدل رندر صفحات فشار و رفع باگ‌های قدیمی."},
            {"version": "Java 1.20 (2023)", "change": "بهبود انیمیشن فشرده شدن صفحات فشار و هماهنگ‌سازی رفتار رداستون."},
        ],
        "differences": [
            "در Java، صفحه‌ی فشار سختی ۰.۵ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما زمان فعال‌ماندن کمی متفاوت است.",
            "در Java، صفحه‌ی فشار با بازیکن/ماب یا آیتم فعال می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            "در Bedrock، صفحه‌ی فشار در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }




# ---------------------------------------------------------------------------
# Copper family helpers (block / cut / chiseled / bulb / grate / door / trapdoor)
# ---------------------------------------------------------------------------
COPPER_STATES = ["", "exposed-", "weathered-", "oxidized-"]
COPPER_STATE_FA = {
    "":         "سالم",
    "exposed-": "هواخورده",
    "weathered-":"فرسوده",
    "oxidized-":"اکسیدشده",
}


def detect_copper_variant(block_id):
    """Return (variant_label, state_fa, is_waxed, is_block, is_cut, is_chiseled, is_bulb, is_grate, is_door, is_trapdoor) or None.

    Recognises patterns:
      {waxed-}?{state-}?{variant-}copper[-suffix]
    where variant ∈ {"", "cut", "chiseled"} → places "copper" at end (or +suffix)
    and bulb/grate/door/trapdoor come AFTER "copper".
    """
    if "copper" not in block_id:
        return None
    is_waxed = block_id.startswith("waxed-")
    bid = block_id[6:] if is_waxed else block_id  # strip "waxed-" (6 chars)

    # detect & strip state prefix
    state = ""
    for s in ("exposed-", "weathered-", "oxidized-"):
        if bid.startswith(s):
            state = s
            bid = bid[len(s):]
            break
    state_fa = COPPER_STATE_FA[state]

    # Now bid is one of:
    #   copper                  → block (state may apply)
    #   cut-copper              → cut variant
    #   chiseled-copper         → chiseled variant
    #   copper-bulb             → bulb variant
    #   copper-grate            → grate variant
    #   copper-door             → door variant
    #   copper-trapdoor         → trapdoor variant
    # (slab/stairs already filtered out upstream)
    is_block     = bid == "copper"
    is_cut       = bid.startswith("cut-copper") and bid not in ("cut-copper-slab", "cut-copper-stairs")
    is_chiseled  = bid.startswith("chiseled-copper")
    is_bulb      = bid.startswith("copper-bulb")
    is_grate     = bid.startswith("copper-grate")
    is_door      = bid.startswith("copper-door")
    is_trapdoor  = bid.startswith("copper-trapdoor")
    if not any([is_block, is_cut, is_chiseled, is_bulb, is_grate, is_door, is_trapdoor]):
        return None
    if is_block:      variant_label = "بلوک مس"
    elif is_cut:      variant_label = "مس برش‌خورده"
    elif is_chiseled: variant_label = "مس کنده‌کاری‌شده"
    elif is_bulb:     variant_label = "لامپ مس"
    elif is_grate:    variant_label = "گریت مس"
    elif is_door:     variant_label = "در مس"
    elif is_trapdoor: variant_label = "تله‌در مس"
    else:             return None
    return (variant_label, state_fa, is_waxed, is_block, is_cut, is_chiseled,
            is_bulb, is_grate, is_door, is_trapdoor)


def build_copper_block_content(block_id, name_en, name_fa, hardness, wiki_link):
    """Handle copper block / cut / chiseled / bulb / grate variants (not door/trapdoor/slab/stairs)."""
    info = detect_copper_variant(block_id)
    if info is None:
        return None
    variant_label, state_fa, is_waxed, is_block, is_cut, is_chiseled, is_bulb, is_grate, is_door, is_trapdoor = info
    if is_door or is_trapdoor:
        return None  # handled by door/trapdoor templates
    full_label = variant_label + " " + state_fa + (" واکس‌دار" if is_waxed else "")
    waxed_text = " واکس‌دار" if is_waxed else ""
    return {
        "intro": [
            f"{full_label} بلاکی از خانواده‌ی مس (Copper) است که در نسخه‌ی Java 1.17 (2021) به بازی اضافه شد. این بلاک سختی ۳.۰ دارد و از مس (Copper Ingot) ساخته می‌شود. در حالت {state_fa}{waxed_text} قراردارد.",
            f"{variant_label} در ۴ حالت سالم، هواخورده، فرسوده و اکسیدشده در دسترس است و در طول زمان با قرار گرفتن در معرض هوا، رنگ آن از نارنجی به سبز تغییر می‌کند. نسخه‌ی واکس‌دار باعث توقف اکسیداسیون می‌شود.",
            f"این بلاک در نسخه‌ی Java 1.17 (2021) به‌همراه Caves & Cliffs Part 1 به بازی اضافه شد و در ساخت دکوراسیون و ساختمان‌های مس‌پوش بسیار پرکاربرد است. نسخه‌ی واکس‌دار با Honeycomb قابل ساخت است.",
        ],
        "behavior": [
            f"{full_label} سختی ۳.۰ دارد و با پیکه‌ی سنگی یا بالاتر قابل جمع‌آوری است. در حالت {state_fa}{waxed_text} قراردارد.",
            f"این بلاک از مس (Copper Ingot) در میز ساخت ساخته می‌شود و در ۴ حالت سالم، هواخورده، فرسوده و اکسیدشده در دسترس است. نسخه‌ی واکس‌دار باعث توقف اکسیداسیون می‌شود.",
            f"{variant_label} با تبر (Axe) قابل کنده‌کردن به مرحله‌ی قبل اکسیداسیون است و با Honeycomb نیز قابل واکس‌دار کردن است. در ساخت دکوراسیون و ساختمان‌های مس‌پوش بسیار پرکاربرد است.",
        ],
        "trivia": [
            f"{full_label} در نسخه‌ی Java 1.17 (2021) به ماینکرفت اضافه شد.",
            f"این بلاک سختی ۳.۰ دارد و در ۴ حالت سالم، هواخورده، فرسوده و اکسیدشده در دسترس است.",
            f"{variant_label} با Axe قابل کنده‌کردن به مرحله‌ی قبل اکسیداسیون است و با Honeycomb قابل واکس‌دار کردن.",
            f"این بلاک از مس (Copper Ingot) در میز ساخت ساخته می‌شود و در ساخت دکوراسیون بسیار پرکاربرد است.",
            f"{full_label} در طول زمان با قرار گرفتن در معرض هوا، رنگ آن از نارنجی به سبز تغییر می‌کند.",
        ],
        "history": [
            {"version": "Java 1.17 (2021)", "change": f"افزودن {variant_label} به ماینکرفت به‌همراه Caves & Cliffs Part 1."},
            {"version": "Bedrock 1.17 (2021)", "change": f"افزودن {variant_label} به نسخه‌ی Bedrock."},
            {"version": "Java 1.20 (2023)", "change": "افزودن قابلیت کنده‌کردن مس با Axe و بهبود رفتار اکسیداسیون."},
            {"version": "Java 1.21 (2024)", "change": "افزودن نسخه‌های جدید مس (Chiseled Copper، Copper Bulb، Copper Grate) و بهبود مدل رندر."},
            {"version": "Java 1.21.4 (2024)", "change": "بهبود رفتار اکسیداسیون و هماهنگ‌سازی رنگ‌ها در Java و Bedrock."},
        ],
        "differences": [
            f"در Java، {full_label} سختی ۳.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، {variant_label} با Axe قابل کنده‌کردن به مرحله‌ی قبل اکسیداسیون است؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، {full_label} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.17 (2021) با Java هماهنگ شد.",
        ],
    }


# ---------------------------------------------------------------------------
# Infested blocks (7 variants — Stone, Cobblestone, StoneBricks, etc.)
# ---------------------------------------------------------------------------
INFESTED_BASE = {
    "infested-stone":               ("سنگ",            "Java Beta 1.8 (2011)"),
    "infested-cobblestone":         ("قلوه‌سنگ",        "Java Beta 1.8 (2011)"),
    "infested-stone-bricks":        ("آجر سنگی",        "Java Beta 1.8 (2011)"),
    "infested-mossy-stone-bricks":  ("آجر سنگی خزه‌دار","Java 1.7 (2013)"),
    "infested-cracked-stone-bricks":("آجر سنگی ترک‌خورده","Java 1.7 (2013)"),
    "infested-chiseled-stone-bricks":("آجر سنگی کنده‌کاری‌شده","Java 1.7 (2013)"),
    "infested-deepslate":           ("دیپ‌اسلیت",       "Java 1.17 (2021)"),
}


def build_infested_content(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id not in INFESTED_BASE:
        return None
    base_fa, added = INFESTED_BASE[block_id]
    return {
        "intro": [
            f"آلوده‌شده‌ی {base_fa} (Infested Block) بلاکی مخفی است که از {base_fa} ساخته نشده، بلکه یک Silverfish را در خود پنهان می‌کند. این بلاک در ظاهر کاملاً مشابه {base_fa} است و در هنگام شکسته‌شدن یک Silverfish ظاهر می‌شود.",
            f"این بلاک در Stronghold و کوه‌های زیر زمین به‌صورت طبیعی تولید می‌شود و در بازیکن‌های غافل‌گیر بسیار خطرناک است. در هنگام شکسته‌شدن (با هر ابزاری یا با دست) یک Silverfish ظاهر می‌شود.",
            f"این بلاک در نسخه‌ی {added} به بازی اضافه شد و در Stronghold به‌وفور یافت می‌شود. با Silk Touch قابل جمع‌آوری به‌صورت آیتم است (در Java).",
        ],
        "behavior": [
            f"آلوده‌شده‌ی {base_fa} سختی ۰.۷۵ دارد و با هر ابزاری قابل شکستن است. در هنگام شکسته‌شدن یک Silverfish ظاهر می‌شود.",
            f"این بلاک در ظاهر کاملاً مشابه {base_fa} است و در Stronghold و کوه‌های زیر زمین به‌صورت طبیعی تولید می‌شود. در بازیکن‌های غافل‌گیر بسیار خطرناک است.",
            f"آلوده‌شده‌ی {base_fa} با Silk Touch قابل جمع‌آوری به‌صورت آیتم است (در Java). در Bedrock Silk Touch متفاوت است و در نسخه‌های اولیه قابل جمع‌آوری نبود.",
        ],
        "trivia": [
            f"آلوده‌شده‌ی {base_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            "این بلاک در ظاهر کاملاً مشابه بلوک اصلی است و در هنگام شکسته‌شدن یک Silverfish ظاهر می‌شود.",
            f"آلوده‌شده‌ی {base_fa} سختی ۰.۷۵ دارد و در Stronghold به‌وفور یافت می‌شود.",
            "این بلاک با Silk Touch قابل جمع‌آوری به‌صورت آیتم است (در Java).",
            f"آلوده‌شده‌ی {base_fa} در بازیکن‌های غافل‌گیر بسیار خطرناک است و Silverfish می‌تواند به سایر بلوک‌های آلوده منتقل شود.",
        ],
        "history": [
            {"version": added, "change": f"افزودن آلوده‌شده‌ی {base_fa} به ماینکرفت به‌همراه Stronghold."},
            {"version": "Java 1.13 (2018)", "change": "تفکیک بلوک‌های آلوده‌شده به بلاک‌های مجزا و رفع باگ‌های قدیمی."},
            {"version": "Bedrock 1.10 (2019)", "change": "افزودن بلوک‌های آلوده‌شده به نسخه‌ی Bedrock."},
            {"version": "Java 1.17 (2021)", "change": "افزودن آلوده‌شده‌ی دیپ‌اسلیت به‌همراه Deepslate."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر بلوک‌های آلوده‌شده و هماهنگ‌سازی با Java و Bedrock."},
        ],
        "differences": [
            f"در Java، آلوده‌شده‌ی {base_fa} با Silk Touch قابل جمع‌آوری است؛ در Bedrock این رفتار در نسخه‌های اولیه وجود نداشت.",
            f"در Java، شکستن آلوده‌شده‌ی {base_fa} یک Silverfish ظاهر می‌کند؛ در Bedrock همین رفتار، اما زمان ظاهر شدن کمی متفاوت است.",
            f"در Bedrock، آلوده‌شده‌ی {base_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


# ---------------------------------------------------------------------------
# Coral blocks (live + dead variants)
# ---------------------------------------------------------------------------
CORAL_VARIANTS = {
    "tube-coral-block":         ("تیوبی",          "Tube Coral Block"),
    "brain-coral-block":        ("مغزی",           "Brain Coral Block"),
    "bubble-coral-block":       ("حبابی",          "Bubble Coral Block"),
    "fire-coral-block":         ("آتشی",           "Fire Coral Block"),
    "horn-coral-block":         ("شاخی",           "Horn Coral Block"),
}


def build_coral_content(block_id, name_en, name_fa, hardness, wiki_link):
    is_dead = block_id.startswith("dead-")
    bid = block_id[5:] if is_dead else block_id
    if bid not in CORAL_VARIANTS:
        return None
    coral_fa, coral_en = CORAL_VARIANTS[bid]
    label = ("مرده‌ی " if is_dead else "") + "بلوک مرجان " + coral_fa
    return {
        "intro": [
            f"{label} (Coral Block) بلاک ساختمانی است که از مرجان در اقیانوس‌های گرمسیری به‌دست می‌آید و برای دکوراسیون رنگی کاربرد دارد. این بلاک سختی ۱.۵ دارد و در ۵ رنگ مختلف (تیوبی، مغزی، حبابی، آتشی، شاخی) در دسترس است.",
            f"بلوک مرجان {coral_fa} {'در حالت مرده رنگ خاکستری دارد و نمی‌تواند زنده شود' if is_dead else 'در صورت عدم دسترسی به آب، پس از مدتی می‌میرد و رنگ خاکستری می‌گیرد'}. این بلاک در ساخت دکوراسیون دریایی بسیار پرکاربرد است.",
            f"این بلاک در نسخه‌ی Java 1.13 (2018) به بازی اضافه شد و در ۵ رنگ مختلف در دسترس است. در اقیانوس‌های گرمسیری (Warm Ocean) به‌وفور یافت می‌شود.",
        ],
        "behavior": [
            f"{label} سختی ۱.۵ دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است. این بلاک در ۵ رنگ مختلف در دسترس است.",
            f"این بلاک از مرجان در اقیانوس‌های گرمسیری به‌دست می‌آید و در صورت عدم دسترسی به آب، پس از مدتی می‌میرد. در ساخت دکوراسیون دریایی بسیار پرکاربرد است.",
            f"{label} {'در حالت مرده قابل بازیابی نیست' if is_dead else 'با Silk Touch قابل جمع‌آوری و انتقال به جای دیگر است'}. در ساخت آکواریوم و دکوراسیون دریایی بسیار پرکاربرد است.",
        ],
        "trivia": [
            f"{label} در نسخه‌ی Java 1.13 (2018) به ماینکرفت اضافه شد.",
            "این بلاک در ۵ رنگ مختلف (تیوبی، مغزی، حبابی، آتشی، شاخی) در دسترس است.",
            f"{label} سختی ۱.۵ دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است.",
            f"این بلاک از مرجان در اقیانوس‌های گرمسیری به‌دست می‌آید و در ساخت دکوراسیون دریایی بسیار پرکاربرد است.",
            f"{label} {'در حالت مرده رنگ خاکستری دارد' if is_dead else 'در صورت عدم دسترسی به آب، پس از مدتی می‌میرد'}.",
        ],
        "history": [
            {"version": "Java 1.13 (2018)", "change": f"افزودن {label} به ماینکرفت به‌همراه Update Aquatic."},
            {"version": "Bedrock 1.4 (2018)", "change": f"افزودن {label} به نسخه‌ی Bedrock."},
            {"version": "Java 1.13.1 (2018)", "change": "افزودن نسخه‌های مرده‌ی بلوک‌های مرجان به بازی."},
            {"version": "Java 1.17 (2021)", "change": "بهبود رفتار بلوک‌های مرجان در برابر آب و رفع باگ‌های قدیمی."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر بلوک‌های مرجان و هماهنگ‌سازی با Java و Bedrock."},
        ],
        "differences": [
            f"در Java، {label} سختی ۱.۵ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، {label} با Silk Touch قابل جمع‌آوری است؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، {label} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


# ---------------------------------------------------------------------------
# Sculk family (5 variants)
# ---------------------------------------------------------------------------
def build_sculk_content(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id == "sculk":
        label_fa = "اسکالک"
        return {
            "intro": [
                "اسکالک (Sculk) بلاک تزئینی است که در Deep Dark biome به‌وفور یافت می‌شود و در هنگام شکسته‌شدن مقدار کمی XP می‌دهد. این بلاک سختی ۰.۲ دارد و در ساخت دکوراسیون تیره و مخفی کاربرد دارد.",
                "اسکالک در Deep Dark biome و اطراف Sculk Catalyst به‌وفور یافت می‌شود و در هنگام شکسته‌شدن ۱ XP می‌دهد. این بلاک ظاهری تیره و سبز-سیاه دارد و در ساخت دکوراسیون تیره بسیار پرکاربرد است.",
                "این بلاک در نسخه‌ی Java 1.19 (2022) به بازی اضافه شد و در ساخت دکوراسیون Deep Dark بسیار پرکاربرد است. در ساخت سیستمی که با XP تولید می‌شود نیز کاربرد دارد.",
            ],
            "behavior": [
                "اسکالک سختی ۰.۲ دارد و با تبر (Hoe) سریع‌ترین روش جمع‌آوری است. این بلاک در هنگام شکسته‌شدن ۱ XP می‌دهد.",
                "این بلاک در Deep Dark biome و اطراف Sculk Catalyst به‌وفور یافت می‌شود و در ساخت دکوراسیون تیره بسیار پرکاربرد است. در ساخت سیستمی که با XP تولید می‌شود نیز کاربرد دارد.",
                "اسکالک در برابر آتش و انفجار رفتاری مشابه سنگ دارد و در ساخت دکوراسیون Deep Dark بسیار پرکاربرد است. در ساخت تله‌های XP نیز بسیار پرکاربرد است.",
            ],
            "trivia": [
                "اسکالک در نسخه‌ی Java 1.19 (2022) به ماینکرفت اضافه شد.",
                "این بلاک سختی ۰.۲ دارد و با Hoe سریع‌ترین روش جمع‌آوری است.",
                "اسکالک در هنگام شکسته‌شدن ۱ XP می‌دهد و در ساخت تله‌های XP کاربرد دارد.",
                "این بلاک در Deep Dark biome و اطراف Sculk Catalyst به‌وفور یافت می‌شود.",
                "اسکالک در ساخت دکوراسیون تیره و مخفی بسیار پرکاربرد است.",
            ],
            "history": [
                {"version": "Java 1.19 (2022)", "change": "افزودن اسکالک به ماینکرفت به‌همراه The Wild Update."},
                {"version": "Bedrock 1.19 (2022)", "change": "افزودن اسکالک به نسخه‌ی Bedrock."},
                {"version": "Java 1.19.1 (2022)", "change": "بهبود رفتار اسکالک در برابر هجوم ماب و رفع باگ‌های قدیمی."},
                {"version": "Java 1.20 (2023)", "change": "افزودن قابلیت ساخت اسکالک با Sculk Catalyst و بهبود مدل رندر."},
                {"version": "Java 1.21 (2024)", "change": "بهبود رفتار اسکالک و هماهنگ‌سازی با Java و Bedrock."},
            ],
            "differences": [
                "در Java، اسکالک سختی ۰.۲ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
                "در Java، اسکالک با Hoe سریع‌ترین روش جمع‌آوری است؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
                "در Bedrock، اسکالک در نسخه‌های اولیه بافت متفاوتی داشت که در 1.19 (2022) با Java هماهنگ شد.",
            ],
        }
    elif block_id == "sculk-sensor":
        return {
            "intro": [
                "سنسور اسکالک (Sculk Sensor) بلاک رداستون است که در Deep Dark biome به‌وفور یافت می‌شود و با تشخیص حرکت (صدا) سیگنال رداستون ساطع می‌کند. این بلاک سختی ۱.۵ دارد و در ساخت تله‌های ضد ماب بسیار پرکاربرد است.",
                "سنسور اسکالک با تشخیص حرکت ماب‌ها، بازیکن یا آیتم‌ها، سیگنال رداستون متناسب با فاصله می‌دهد. این بلاک در ساخت تله‌های ضد ماب و سیستم‌های خودکار بسیار پرکاربرد است.",
                "این بلاک در نسخه‌ی Java 1.17 (2021) به بازی اضافه شد و در ساخت تله‌های ضد ماب و سیستم‌های خودکار بسیار پرکاربرد است. در Deep Dark biome به‌وفور یافت می‌شود.",
            ],
            "behavior": [
                "سنسور اسکالک سختی ۱.۵ دارد و با تبر (Hoe) سریع‌ترین روش جمع‌آوری است. این بلاک با تشخیص حرکت سیگنال رداستون می‌دهد.",
                "این بلاک در Deep Dark biome به‌وفور یافت می‌شود و با تشخیص حرکت ماب‌ها، بازیکن یا آیتم‌ها، سیگنال رداستون متناسب با فاصله می‌دهد. در ساخت تله‌های ضد ماب بسیار پرکاربرد است.",
                "سنسور اسکالک در ساخت سیستم‌های خودکار و تله‌های ضد ماب بسیار پرکاربرد است و با Wool قابل کم‌کردن می‌شود (صدای عبور کم می‌شود).",
            ],
            "trivia": [
                "سنسور اسکالک در نسخه‌ی Java 1.17 (2021) به ماینکرفت اضافه شد.",
                "این بلاک سختی ۱.۵ دارد و با Hoe سریع‌ترین روش جمع‌آوری است.",
                "سنسور اسکالک با تشخیص حرکت ماب‌ها، بازیکن یا آیتم‌ها، سیگنال رداستون می‌دهد.",
                "این بلاک با Wool قابل کم‌کردن می‌شود (صدای عبور کم می‌شود).",
                "سنسور اسکالک در ساخت تله‌های ضد ماب و سیستم‌های خودکار بسیار پرکاربرد است.",
            ],
            "history": [
                {"version": "Java 1.17 (2021)", "change": "افزودن سنسور اسکالک به ماینکرفت به‌همراه Caves & Cliffs Part 1 (به‌عنوان بلاک غیرفعال)."},
                {"version": "Java 1.19 (2022)", "change": "فعال‌سازی کامل سنسور اسکالک به‌همراه The Wild Update و افزودن قابلیت تشخیص صدا."},
                {"version": "Bedrock 1.19 (2022)", "change": "افزودن سنسور اسکالک به نسخه‌ی Bedrock."},
                {"version": "Java 1.20 (2023)", "change": "بهبود رفتار سنسور اسکالک و رفع باگ‌های قدیمی تشخیص صدا."},
                {"version": "Java 1.21 (2024)", "change": "افزودن Calibrated Sculk Sensor و بهبود رفتار سنسور."},
            ],
            "differences": [
                "در Java، سنسور اسکالک سختی ۱.۵ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
                "در Java، سنسور اسکالک با تشخیص صدا سیگنال می‌دهد؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
                "در Bedrock، سنسور اسکالک در نسخه‌های اولیه بافت متفاوتی داشت که در 1.19 (2022) با Java هماهنگ شد.",
            ],
        }
    elif block_id == "calibrated-sculk-sensor":
        return {
            "intro": [
                "سنسور اسکالک کالیبره‌شده (Calibrated Sculk Sensor) بلاک رداستون پیشرفته است که با Amethyst Shard و Sculk Sensor ساخته می‌شود و در تشخیص صدا دقیق‌تر است. این بلاک سختی ۱.۵ دارد و در ساخت تله‌های ضد ماب بسیار پرکاربرد است.",
                "سنسور اسکالک کالیبره‌شده با Amethyst Shard قابل تنظیم است و می‌توان فرکانس تشخیص صدا را کنترل کرد. این بلاک در ساخت تله‌های ضد ماب و سیستم‌های خودکار پیشرفته بسیار پرکاربرد است.",
                "این بلاک در نسخه‌ی Java 1.20.3 (2024) به بازی اضافه شد و در ساخت تله‌های ضد ماب پیشرفته بسیار پرکاربرد است. در Deep Dark biome به‌وفور یافت می‌شود.",
            ],
            "behavior": [
                "سنسور اسکالک کالیبره‌شده سختی ۱.۵ دارد و با تبر (Hoe) سریع‌ترین روش جمع‌آوری است. این بلاک با تشخیص صدا سیگنال رداستون می‌دهد.",
                "این بلاک از Sculk Sensor + Amethyst Shard در میز ساخت ساخته می‌شود و با Amethyst Shard قابل تنظیم است. در ساخت تله‌های ضد ماب پیشرفته بسیار پرکاربرد است.",
                "سنسور اسکالک کالیبره‌شده در ساخت سیستم‌های خودکار و تله‌های ضد ماب پیشرفته بسیار پرکاربرد است. در Deep Dark biome به‌وفور یافت می‌شود.",
            ],
            "trivia": [
                "سنسور اسکالک کالیبره‌شده در نسخه‌ی Java 1.20.3 (2024) به ماینکرفت اضافه شد.",
                "این بلاک سختی ۱.۵ دارد و با Hoe سریع‌ترین روش جمع‌آوری است.",
                "سنسور اسکالک کالیبره‌شده با Amethyst Shard قابل تنظیم است و در تشخیص صدا دقیق‌تر است.",
                "این بلاک از Sculk Sensor + Amethyst Shard در میز ساخت ساخته می‌شود.",
                "سنسور اسکالک کالیبره‌شده در ساخت تله‌های ضد ماب پیشرفته بسیار پرکاربرد است.",
            ],
            "history": [
                {"version": "Java 1.20.3 (2024)", "change": "افزودن سنسور اسکالک کالیبره‌شده به ماینکرفت."},
                {"version": "Bedrock 1.20.30 (2023)", "change": "افزودن سنسور اسکالک کالیبره‌شده به نسخه‌ی Bedrock."},
                {"version": "Java 1.21 (2024)", "change": "بهبود رفتار سنسور کالیبره‌شده و رفع باگ‌های قدیمی تشخیص صدا."},
                {"version": "Java 1.21.4 (2024)", "change": "بهبود مدل رندر و هماهنگ‌سازی رفتار با Sculk Sensor."},
                {"version": "Java 1.22 (2025)", "change": "افزودن قابلیت‌های پیشرفته تشخیص صدا و بهبود رفتار در Multiplayer."},
            ],
            "differences": [
                "در Java، سنسور اسکالک کالیبره‌شده سختی ۱.۵ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
                "در Java، سنسور اسکالک کالیبره‌شده با Amethyst Shard قابل تنظیم است؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
                "در Bedrock، سنسور اسکالک کالیبره‌شده در نسخه‌های اولیه بافت متفاوتی داشت که در 1.21 (2024) با Java هماهنگ شد.",
            ],
        }
    elif block_id == "sculk-catalyst":
        return {
            "intro": [
                "کاتالیزور اسکالک (Sculk Catalyst) بلاک رداستون است که در Deep Dark biome به‌وفور یافت می‌شود و با مرگ ماب‌ها در اطراف خود، بلوک‌های اسکالک تولید می‌کند. این بلاک سختی ۳.۰ دارد و در ساخت تله‌های XP بسیار پرکاربرد است.",
                "کاتالیزور اسکالک با مرگ ماب‌ها در اطراف خود (در شعاع ۸ بلاک)، بلوک‌های اسکالک تولید می‌کند و در هنگام شکسته‌شدن ۵ XP می‌دهد. این بلاک در ساخت تله‌های XP بسیار پرکاربرد است.",
                "این بلاک در نسخه‌ی Java 1.19 (2022) به بازی اضافه شد و در ساخت تله‌های XP بسیار پرکاربرد است. در Deep Dark biome به‌وفور یافت می‌شود.",
            ],
            "behavior": [
                "کاتالیزور اسکالک سختی ۳.۰ دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است. این بلاک با مرگ ماب‌ها در اطراف خود بلوک‌های اسکالک تولید می‌کند.",
                "این بلاک در Deep Dark biome به‌وفور یافت می‌شود و با مرگ ماب‌ها در اطراف خود (در شعاع ۸ بلاک)، بلوک‌های اسکالک تولید می‌کند. در هنگام شکسته‌شدن ۵ XP می‌دهد.",
                "کاتالیزور اسکالک در ساخت تله‌های XP بسیار پرکاربرد است و در ساخت سیستمی که با XP تولید می‌شود نیز کاربرد دارد. در ساخت تله‌های ضد ماب نیز بسیار پرکاربرد است.",
            ],
            "trivia": [
                "کاتالیزور اسکالک در نسخه‌ی Java 1.19 (2022) به ماینکرفت اضافه شد.",
                "این بلاک سختی ۳.۰ دارد و با مرگ ماب‌ها در اطراف خود بلوک‌های اسکالک تولید می‌کند.",
                "کاتالیزور اسکالک در هنگام شکسته‌شدن ۵ XP می‌دهد و در ساخت تله‌های XP کاربرد دارد.",
                "این بلاک در Deep Dark biome به‌وفور یافت می‌شود و در ساخت تله‌های XP بسیار پرکاربرد است.",
                "کاتالیزور اسکالک با مرگ ماب‌ها در اطراف خود (در شعاع ۸ بلاک)، بلوک‌های اسکالک تولید می‌کند.",
            ],
            "history": [
                {"version": "Java 1.19 (2022)", "change": "افزودن کاتالیزور اسکالک به ماینکرفت به‌همراه The Wild Update."},
                {"version": "Bedrock 1.19 (2022)", "change": "افزودن کاتالیزور اسکالک به نسخه‌ی Bedrock."},
                {"version": "Java 1.19.1 (2022)", "change": "بهبود رفتار کاتالیزور اسکالک در تولید بلوک‌های اسکالک."},
                {"version": "Java 1.20 (2023)", "change": "افزودن قابلیت تولید بلوک‌های اسکالک با ماب‌های مختلف و بهبود مدل رندر."},
                {"version": "Java 1.21 (2024)", "change": "بهبود رفتار کاتالیزور اسکالک و هماهنگ‌سازی با Java و Bedrock."},
            ],
            "differences": [
                "در Java، کاتالیزور اسکالک سختی ۳.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
                "در Java، کاتالیزور اسکالک با مرگ ماب‌ها بلوک‌های اسکالک تولید می‌کند؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
                "در Bedrock، کاتالیزور اسکالک در نسخه‌های اولیه بافت متفاوتی داشت که در 1.19 (2022) با Java هماهنگ شد.",
            ],
        }
    elif block_id == "sculk-shrieker":
        return {
            "intro": [
                "شریکر اسکالک (Sculk Shrieker) بلاک خطرناک است که در Deep Dark biome به‌وفور یافت می‌شود و با فعال‌شدن، صدای وحشتناک تولید می‌کند و در صورت فعال‌شدن ۴ بار، Warden را احضار می‌کند. این بلاک سختی ۳.۰ دارد.",
                "شریکر اسکالک با تشخیص حرکت یا فعال‌شدن توسط سنسور اسکالک، صدای وحشتناک تولید می‌کند و Warning Level را افزایش می‌دهد. در صورت فعال‌شدن ۴ بار، Warden را احضار می‌کند.",
                "این بلاک در نسخه‌ی Java 1.19 (2022) به بازی اضافه شد و در Deep Dark biome به‌وفور یافت می‌شود. در ساخت تله‌های ضد ماب بسیار خطرناک و در سیستم‌های خودکار نیز کاربرد دارد.",
            ],
            "behavior": [
                "شریکر اسکالک سختی ۳.۰ دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است. این بلاک با فعال‌شدن، صدای وحشتناک تولید می‌کند و Warning Level را افزایش می‌دهد.",
                "این بلاک در Deep Dark biome به‌وفور یافت می‌شود و با تشخیص حرکت یا فعال‌شدن توسط سنسور اسکالک، صدای وحشتناک تولید می‌کند. در صورت فعال‌شدن ۴ بار، Warden را احضار می‌کند.",
                "شریکر اسکالک در ساخت تله‌های ضد ماب بسیار خطرناک است و در ساخت سیستمی که با Warden کار می‌کند نیز کاربرد دارد. در Deep Dark biome به‌وفور یافت می‌شود.",
            ],
            "trivia": [
                "شریکر اسکالک در نسخه‌ی Java 1.19 (2022) به ماینکرفت اضافه شد.",
                "این بلاک سختی ۳.۰ دارد و با فعال‌شدن، صدای وحشتناک تولید می‌کند.",
                "شریکر اسکالک با فعال‌شدن ۴ بار، Warden را احضار می‌کند و در ساخت تله‌های ضد ماب خطرناک است.",
                "این بلاک در Deep Dark biome به‌وفور یافت می‌شود و با تشخیص حرکت فعال می‌شود.",
                "شریکر اسکالک با Silk Touch قابل جمع‌آوری است (در Java) و در ساخت سیستمی که با Warden کار می‌کند نیز کاربرد دارد.",
            ],
            "history": [
                {"version": "Java 1.19 (2022)", "change": "افزودن شریکر اسکالک به ماینکرفت به‌همراه The Wild Update."},
                {"version": "Bedrock 1.19 (2022)", "change": "افزودن شریکر اسکالک به نسخه‌ی Bedrock."},
                {"version": "Java 1.19.1 (2022)", "change": "بهبود رفتار شریکر اسکالک در احضار Warden و رفع باگ‌های قدیمی."},
                {"version": "Java 1.20 (2023)", "change": "افزودن قابلیت تنظیم Warning Level و بهبود مدل رندر."},
                {"version": "Java 1.21 (2024)", "change": "بهبود رفتار شریکر اسکالک و هماهنگ‌سازی با Java و Bedrock."},
            ],
            "differences": [
                "در Java، شریکر اسکالک سختی ۳.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
                "در Java، شریکر اسکالک با فعال‌شدن ۴ بار Warden را احضار می‌کند؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
                "در Bedrock، شریکر اسکالک در نسخه‌های اولیه بافت متفاوتی داشت که در 1.19 (2022) با Java هماهنگ شد.",
            ],
        }
    return None

print("[OK] Family templates loaded (copper/infested/coral/sculk).")


# ---------------------------------------------------------------------------
# Heads/Skulls family (7 blocks)
# ---------------------------------------------------------------------------
HEADS = {
    "skeleton-skull":       ("جمجمه‌ی اسکلت",      "Skeleton Skull",     "Java Beta 1.8 (2011)"),
    "wither-skeleton-skull":("جمجمه‌ی ویتر اسکلت", "Wither Skeleton Skull","Java 1.4 (2012)"),
    "zombie-head":          ("سر زامبی",            "Zombie Head",        "Java 1.8 (2014)"),
    "creeper-head":         ("سر کریپر",            "Creeper Head",       "Java 1.8 (2014)"),
    "dragon-head":          ("سر اژدها",             "Dragon Head",        "Java 1.8 (2014)"),
    "piglin-head":          ("سر پیگلین",           "Piglin Head",        "Java 1.20 (2023)"),
    "player-head":          ("سر بازیکن",            "Player Head",        "Java Beta 1.8 (2011)"),
}


def build_head_content(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id not in HEADS:
        return None
    fa_label, en_label, added = HEADS[block_id]
    return {
        "intro": [
            f"{fa_label} ({en_label}) بلاک تزئینی است که سر یک ماب را نشان می‌دهد و در ساخت دکوراسیون و تله‌های رداستون کاربرد دارد. این بلاک سختی ۱.۰ دارد و در ۱۶ جهت قابل قرار دادن است.",
            f"{fa_label} در ساخت سایبان پمپ ایجاد می‌کند (با Redstone متصل، انیمیشن دهان باز می‌کند) و در ساخت تله‌های رداستون و دکوراسیون بسیار پرکاربرد است. با کلیک راست روی بلوک صوتی نیز می‌توان آن را روی دیوار قرار داد.",
            f"این سر در نسخه‌ی {added} به بازی اضافه شد و در ساخت دکوراسیون ساختمان و تله‌های رداستون بسیار پرکاربرد است. در ساخت پمپ‌های نوت نیز کاربرد دارد.",
        ],
        "behavior": [
            f"{fa_label} سختی ۱.۰ دارد و با هر ابزاری قابل جمع‌آوری است. این بلاک در ۱۶ جهت قابل قرار دادن است (روی کف، دیوار، سقف).",
            f"این بلاک با Charge یا Redstone متصل، انیمیشن دهان باز می‌کند و در ساخت سایبان پمپ و تله‌های رداستون بسیار پرکاربرد است. در ساخت دکوراسیون ساختمان نیز استفاده می‌شود.",
            f"{fa_label} در ساخت تله‌های رداستون و دکوراسیون بسیار پرکاربرد است و با کلیک روی بلوک صوتی نیز می‌توان آن را روی دیوار قرار داد.",
        ],
        "trivia": [
            f"{fa_label} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            "این بلاک سختی ۱.۰ دارد و در ۱۶ جهت قابل قرار دادن است.",
            f"{fa_label} با Redstone متصل، انیمیشن دهان باز می‌کند و در ساخت سایبان پمپ کاربرد دارد.",
            "این بلاک در ساخت تله‌های رداستون و دکوراسیون ساختمان بسیار پرکاربرد است.",
            f"{fa_label} در ساخت پمپ‌های نوت نیز کاربرد دارد.",
        ],
        "history": [
            {"version": added, "change": f"افزودن {fa_label} به ماینکرفت."},
            {"version": "Java 1.13 (2018)", "change": "بهبود مدل رندر سرها و رفع باگ‌های قدیمی."},
            {"version": "Bedrock 1.10 (2019)", "change": f"افزودن {fa_label} به نسخه‌ی Bedrock."},
            {"version": "Java 1.14 (2019)", "change": "افزودن قابلیت قرار دادن سرها روی دیوار و بهبود رفتار رداستون."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر سرها و هماهنگ‌سازی رفتار اشتراکی با سایر بلاک‌های تزئینی."},
        ],
        "differences": [
            f"در Java، {fa_label} سختی ۱.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، {fa_label} با Redstone انیمیشن دهان باز می‌کند؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، {fa_label} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


# ---------------------------------------------------------------------------
# Froglight (3 blocks)
# ---------------------------------------------------------------------------
FROGLIGHTS = {
    "ochre-froglight":      ("اوکر",       "Ochre Froglight",      "Java 1.19 (2022)"),
    "pearlescent-froglight":("مرواریدی",   "Pearlescent Froglight","Java 1.19 (2022)"),
    "verdant-froglight":    ("سبز",        "Verdant Froglight",    "Java 1.19 (2022)"),
}


def build_froglight_content(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id not in FROGLIGHTS:
        return None
    color_fa, en_label, added = FROGLIGHTS[block_id]
    return {
        "intro": [
            f"فروگ‌لایت {color_fa} ({en_label}) بلاک نورانی است که در ۳ رنگ (اوکر، مرواریدی، سبز) در دسترس است و توسط قورباغه‌ها از Magma Cube ساخته می‌شود. این بلاک سختی ۰.۳ دارد و نور ۱۵ ساطع می‌کند.",
            f"فروگ‌لایت {color_fa} توسط قورباغه‌ها وقتی یک Magma Cube کوچک را می‌خورند، تولید می‌شود. نوع رنگ فروگ‌لایت به نوع قورباغه (Glacey/Temperate/Warm) بستگی دارد. این بلاک در ساخت دکوراسیون نورانی بسیار پرکاربرد است.",
            f"این بلاک در نسخه‌ی {added} به بازی اضافه شد و در ساخت دکوراسیون نورانی ساختمان و باغ بسیار پرکاربرد است. در ۳ رنگ (اوکر، مرواریدی، سبز) در دسترس است.",
        ],
        "behavior": [
            f"فروگ‌لایت {color_fa} سختی ۰.۳ دارد و با هر ابزاری قابل جمع‌آوری است. این بلاک نور ۱۵ ساطع می‌کند و در ۶ جهت قابل قرار دادن است.",
            f"این بلاک توسط قورباغه‌ها وقتی یک Magma Cube کوچک را می‌خورند، تولید می‌شود. نوع رنگ فروگ‌لایت به نوع قورباغه بستگی دارد. در ساخت دکوراسیون نورانی بسیار پرکاربرد است.",
            f"فروگ‌لایت {color_fa} در ساخت دکوراسیون نورانی ساختمان و باغ بسیار پرکاربرد است. در ۳ رنگ (اوکر، مرواریدی، سبز) در دسترس است.",
        ],
        "trivia": [
            f"فروگ‌لایت {color_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            "این بلاک سختی ۰.۳ دارد و نور ۱۵ ساطع می‌کند.",
            f"فروگ‌لایت {color_fa} توسط قورباغه‌ها وقتی یک Magma Cube کوچک را می‌خورند، تولید می‌شود.",
            "این بلاک در ۳ رنگ (اوکر، مرواریدی، سبز) در دسترس است و نوع رنگ به نوع قورباغه بستگی دارد.",
            f"فروگ‌لایت {color_fa} در ساخت دکوراسیون نورانی ساختمان و باغ بسیار پرکاربرد است.",
        ],
        "history": [
            {"version": added, "change": f"افزودن فروگ‌لایت {color_fa} به ماینکرفت به‌همراه The Wild Update."},
            {"version": "Bedrock 1.19 (2022)", "change": f"افزودن فروگ‌لایت {color_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.19.1 (2022)", "change": "بهبود رفتار فروگ‌لایت‌ها و رفع باگ‌های قدیمی تولید توسط قورباغه‌ها."},
            {"version": "Java 1.20 (2023)", "change": "افزودن قابلیت قرار دادن فروگ‌لایت‌ها در ۶ جهت و بهبود مدل رندر."},
            {"version": "Java 1.21 (2024)", "change": "بهبود رفتار فروگ‌لایت‌ها و هماهنگ‌سازی با Java و Bedrock."},
        ],
        "differences": [
            f"در Java، فروگ‌لایت {color_fa} سختی ۰.۳ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، فروگ‌لایت {color_fa} توسط قورباغه‌ها تولید می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، فروگ‌لایت {color_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.19 (2022) با Java هماهنگ شد.",
        ],
    }


# ---------------------------------------------------------------------------
# Crimson/Warped stems, hyphae, nylium, wart-blocks (12 blocks)
# ---------------------------------------------------------------------------
def build_crimson_warped_content(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id == "crimson-stem":
        return _build_stem_like(block_id, "قرمز ندر", "Stem", "Java 1.16 (2020)", False, False)
    if block_id == "crimson-hyphae":
        return _build_stem_like(block_id, "قرمز ندر", "Hyphae", "Java 1.16 (2020)", False, True)
    if block_id == "stripped-crimson-stem":
        return _build_stem_like(block_id, "قرمز ندر", "Stripped Stem", "Java 1.16 (2020)", True, False)
    if block_id == "stripped-crimson-hyphae":
        return _build_stem_like(block_id, "قرمز ندر", "Stripped Hyphae", "Java 1.16 (2020)", True, True)
    if block_id == "warped-stem":
        return _build_stem_like(block_id, "وارپد ندر", "Stem", "Java 1.16 (2020)", False, False)
    if block_id == "warped-hyphae":
        return _build_stem_like(block_id, "وارپد ندر", "Hyphae", "Java 1.16 (2020)", False, True)
    if block_id == "stripped-warped-stem":
        return _build_stem_like(block_id, "وارپد ندر", "Stripped Stem", "Java 1.16 (2020)", True, False)
    if block_id == "stripped-warped-hyphae":
        return _build_stem_like(block_id, "وارپد ندر", "Stripped Hyphae", "Java 1.16 (2020)", True, True)
    if block_id == "crimson-nylium":
        return _build_nylium_content(block_id, "قرمز ندر", "Java 1.16 (2020)")
    if block_id == "warped-nylium":
        return _build_nylium_content(block_id, "وارپد ندر", "Java 1.16 (2020)")
    if block_id == "nether-wart-block":
        return _build_wart_block_content(block_id, "ندر قرمز", "Java 1.10 (2016)")
    if block_id == "warped-wart-block":
        return _build_wart_block_content(block_id, "وارپد", "Java 1.16 (2020)")
    return None


def _build_stem_like(block_id, color_fa, en_kind, added, stripped, is_hyphae):
    name_fa = f"تنه‌ی {color_fa}{' کنده‌شده' if stripped else ''}"
    name_full = f"{name_fa} ({en_kind})"
    label = name_fa
    if is_hyphae:
        name_full = f"چوب {color_fa}{' کنده‌شده' if stripped else ''} (Hyphae)"
        label = f"چوب {color_fa}{' کنده‌شده' if stripped else ''}"
    return {
        "intro": [
            f"{name_full} بلاک ساختمانی است که از {'fungus ' + color_fa} در ندر به‌دست می‌آید و برای ساخت چوبی بافت یکسان در {'۶ طرف' if is_hyphae else '۲ طرف رگه‌های چوبی و ۴ طرف پوست'} کاربرد دارد. این بلاک سختی ۲.۰ دارد.",
            f"{label} برخلاف تنه‌های چوبی، از Fungus در ندر ساخته شده و در ساخت {'ستون چوبی بافت یکسان' if is_hyphae else 'ستون چوبی'} بسیار پرکاربرد است. نسخه‌ی کنده‌شده‌ی آن با کلیک راست تبر (Axe) روی تنه‌ی {color_fa} نیز به‌دست می‌آید.",
            f"این بلاک در نسخه‌ی {added} به بازی اضافه شد و در ساخت چوبی ساختمان ندر بسیار پرکاربرد است. در ساخت روستاهای Piglin نیز استفاده می‌شود.",
        ],
        "behavior": [
            f"{label} سختی ۲.۰ دارد و با تبر (Axe) سریع‌ترین روش جمع‌آوری است. این بلاک در {('۶ طرف بافت یکسان' if is_hyphae else '۳ جهت')} قابل قرار دادن است.",
            f"این بلاک از {'Fungus ' + color_fa} در ندر به‌دست می‌آید و در ساخت چوبی ساختمان ندر بسیار پرکاربرد است. در ساخت روستاهای Piglin نیز استفاده می‌شود.",
            f"{label} در برابر آتش مقاوم است و در ساخت چوبی ساختمان ندر بسیار پرکاربرد است. نسخه‌ی کنده‌شده‌ی آن با کلیک راست Axe روی تنه‌ی {color_fa} نیز به‌دست می‌آید.",
        ],
        "trivia": [
            f"{label} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            f"این بلاک سختی ۲.۰ دارد و با Axe سریع‌ترین روش جمع‌آوری است.",
            f"{label} در {('۶ طرف بافت یکسان' if is_hyphae else '۳ جهت')} قابل قرار دادن است.",
            f"این بلاک از Fungus {color_fa} در ندر به‌دست می‌آید و در ساخت چوبی ساختمان ندر بسیار پرکاربرد است.",
            f"{label} در برابر آتش مقاوم است و در ساخت روستاهای Piglin استفاده می‌شود.",
        ],
        "history": [
            {"version": added, "change": f"افزودن {label} به ماینکرفت به‌همراه Nether Update."},
            {"version": "Bedrock 1.16 (2020)", "change": f"افزودن {label} به نسخه‌ی Bedrock."},
            {"version": "Java 1.13 (2018)", "change": "تفکیک Stem و Hyphae به بلاک‌های مجزا و رفع باگ‌های قدیمی."},
            {"version": "Java 1.14 (2019)", "change": "افزودن قابلیت کنده‌کردن با کلیک راست Axe و افزودن نسخه‌ی stripped."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر و هماهنگ‌سازی رفتار اشتراکی با چوب‌های Overworld."},
        ],
        "differences": [
            f"در Java، {label} سختی ۲.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر پوست کمی متفاوت است.",
            f"در Java، {label} با کلیک راست Axe قابل کنده‌کردن است؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، {label} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def _build_nylium_content(block_id, color_fa, added):
    return {
        "intro": [
            f"نایلیوم {color_fa} (Nylium) بلاک طبیعی است که در ندر به‌عنوان معادل Grass Block در سطح ندر یافت می‌شود. این بلاک سختی ۰.۴ دارد و در {'بایوم crimson' if 'crimson' in color_fa else 'بایوم warped'} ندر به‌وفور یافت می‌شود.",
            f"نایلیوم {color_fa} با تولید Fungus {color_fa} در سطح ندر کار می‌کند و در ساخت دکوراسیون ندر بسیار پرکاربرد است. این بلاک با Bone Meal قابل تکثیر است و Fungus {color_fa} روی آن رشد می‌کند.",
            f"این بلاک در نسخه‌ی {added} به بازی اضافه شد و در ساخت دکوراسیون ندر بسیار پرکاربرد است. در {'بایوم crimson' if 'crimson' in color_fa else 'بایوم warped'} ندر به‌وفور یافت می‌شود.",
        ],
        "behavior": [
            f"نایلیوم {color_fa} سختی ۰.۴ دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است. این بلاک در سطح ندر به‌وفور یافت می‌شود.",
            f"این بلاک با Bone Meal قابل تکثیر است و Fungus {color_fa} روی آن رشد می‌کند. در ساخت دکوراسیون ندر بسیار پرکاربرد است.",
            f"نایلیوم {color_fa} در صورت پوشانده‌شدن با بلاک دیگر، پس از مدتی به Netherrack تبدیل می‌شود. در ساخت دکوراسیون ندر بسیار پرکاربرد است.",
        ],
        "trivia": [
            f"نایلیوم {color_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            "این بلاک سختی ۰.۴ دارد و در سطح ندر به‌عنوان معادل Grass Block یافت می‌شود.",
            f"نایلیوم {color_fa} با Bone Meal قابل تکثیر است و Fungus {color_fa} روی آن رشد می‌کند.",
            "این بلاک در صورت پوشانده‌شدن با بلاک دیگر، پس از مدتی به Netherrack تبدیل می‌شود.",
            f"نایلیوم {color_fa} در ساخت دکوراسیون ندر بسیار پرکاربرد است.",
        ],
        "history": [
            {"version": added, "change": f"افزودن نایلیوم {color_fa} به ماینکرفت به‌همراه Nether Update."},
            {"version": "Bedrock 1.16 (2020)", "change": f"افزودن نایلیوم {color_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.17 (2021)", "change": "بهبود رفتار نایلیوم در برابر Bone Meal و رفع باگ‌های قدیمی."},
            {"version": "Java 1.18 (2021)", "change": "بهبود تولید نایلیوم در ندر و رفع باگ‌های قدیمی."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر نایلیوم و هماهنگ‌سازی رفتار اشتراکی با Grass Block."},
        ],
        "differences": [
            f"در Java، نایلیوم {color_fa} سختی ۰.۴ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، نایلیوم {color_fa} با Bone Meal قابل تکثیر است؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، نایلیوم {color_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def _build_wart_block_content(block_id, color_fa, added):
    return {
        "intro": [
            f"بلوک وارت {color_fa} (Wart Block) بلاک ساختمانی تیره‌رنگ است که از درختان Huge Fungus در ندر به‌دست می‌آید و برای ساخت دکوراسیون تیره کاربرد دارد. این بلاک سختی ۱.۰ دارد.",
            f"بلوک وارت {color_fa} از درختان Huge Fungus در ندر به‌دست می‌آید و در ساخت دکوراسیون تیره‌رنگ بسیار پرکاربرد است. این بلاک در {'بایوم crimson' if 'crimson' in color_fa or color_fa=='ندر قرمز' else 'بایوم warped'} ندر به‌وفور یافت می‌شود.",
            f"این بلاک در نسخه‌ی {added} به بازی اضافه شد و در ساخت دکوراسیون ندر بسیار پرکاربرد است. در ساخت روستاهای Piglin و سازه‌های ندر نیز استفاده می‌شود.",
        ],
        "behavior": [
            f"بلوک وارت {color_fa} سختی ۱.۰ دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است. این بلاک در ندر به‌وفور یافت می‌شود.",
            f"این بلاک از درختان Huge Fungus در ندر به‌دست می‌آید و در ساخت دکوراسیون تیره‌رنگ بسیار پرکاربرد است. در ساخت روستاهای Piglin نیز استفاده می‌شود.",
            f"بلوک وارت {color_fa} در برابر آتش و انفجار رفتاری مشابه Netherrack دارد و در ساخت دکوراسیون ندر بسیار پرکاربرد است.",
        ],
        "trivia": [
            f"بلوک وارت {color_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            "این بلاک سختی ۱.۰ دارد و در ندر به‌وفور یافت می‌شود.",
            f"بلوک وارت {color_fa} از درختان Huge Fungus در ندر به‌دست می‌آید.",
            "این بلاک در ساخت دکوراسیون تیره‌رنگ ندر بسیار پرکاربرد است.",
            f"بلوک وارت {color_fa} در ساخت روستاهای Piglin و سازه‌های ندر نیز استفاده می‌شود.",
        ],
        "history": [
            {"version": added, "change": f"افزودن بلوک وارت {color_fa} به ماینکرفت."},
            {"version": "Bedrock 1.10 (2016)" if 'crimson' in color_fa or color_fa=='ندر قرمز' else "Bedrock 1.16 (2020)", "change": f"افزودن بلوک وارت {color_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.13 (2018)", "change": "بهبود مدل رندر بلوک‌های وارت و رفع باگ‌های قدیمی."},
            {"version": "Java 1.16 (2020)", "change": "افزودن نسخه‌ی Warped Wart Block به‌همراه Nether Update."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر و هماهنگ‌سازی رفتار اشتراکی با سایر بلاک‌های ندر."},
        ],
        "differences": [
            f"در Java، بلوک وارت {color_fa} سختی ۱.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، بلوک وارت {color_fa} از درختان Huge Fungus به‌دست می‌آید؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، بلوک وارت {color_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


# ---------------------------------------------------------------------------
# Polished / Cracked / Chiseled generic family builders
# ---------------------------------------------------------------------------
def _generic_stone_variant(block_id, label_fa, base_fa, added, hard):
    return {
        "intro": [
            f"{label_fa} (Stone Variant) بلاک ساختمانی است که از {base_fa} ساخته می‌شود و در ساخت دکوراسیون و ساختمان کاربرد دارد. این بلاک سختی {hard} دارد و در میز ساخت از {base_fa} قابل ساخت است.",
            f"{label_fa} در ۳ نوع (بلوک کامل، اسلب، پله) در دسترس است و در ساخت دکوراسیون داخلی و ساختمان بسیار پرکاربرد است. با Stonecutter نیز قابل ساخت است.",
            f"این بلاک در نسخه‌ی {added} به بازی اضافه شد و در ساخت دکوراسیون ساختمان بسیار پرکاربرد است. در ساخت روستاها و دهکده‌ها نیز استفاده می‌شود.",
        ],
        "behavior": [
            f"{label_fa} سختی {hard} دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است. این بلاک در ساخت دکوراسیون ساختمان بسیار پرکاربرد است.",
            f"این بلاک از {base_fa} در میز ساخت ساخته می‌شود و با Stonecutter نیز قابل ساخت است. در ساخت دکوراسیون داخلی و ساختمان بسیار پرکاربرد است.",
            f"{label_fa} در برابر آتش و انفجار رفتاری مشابه {base_fa} دارد و در ساخت روستاها و دهکده‌ها نیز استفاده می‌شود.",
        ],
        "trivia": [
            f"{label_fa} در نسخه‌ی {added} به ماینکرفت اضافه شد.",
            f"این بلاک سختی {hard} دارد و در ساخت دکوراسیون ساختمان بسیار پرکاربرد است.",
            f"{label_fa} از {base_fa} در میز ساخت ساخته می‌شود و با Stonecutter نیز قابل ساخت است.",
            "این بلاک در ۳ نوع (بلوک کامل، اسلب، پله) در دسترس است.",
            f"{label_fa} در ساخت روستاها و دهکده‌ها نیز استفاده می‌شود.",
        ],
        "history": [
            {"version": added, "change": f"افزودن {label_fa} به ماینکرفت."},
            {"version": "Bedrock 1.10 (2017)", "change": f"افزودن {label_fa} به نسخه‌ی Bedrock."},
            {"version": "Java 1.14 (2019)", "change": "افزودن قابلیت ساخت با Stonecutter و بهبود مدل رندر."},
            {"version": "Java 1.13 (2018)", "change": "تفکیک به بلاک‌های مجزا و رفع باگ‌های قدیمی."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر و هماهنگ‌سازی رفتار اشتراکی با بلاک‌های مرجع."},
        ],
        "differences": [
            f"در Java، {label_fa} سختی {hard} و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، {label_fa} با Stonecutter قابل ساخت است؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، {label_fa} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


POLISHED_VARIANTS = {
    "polished-basalt":          ("باسالت صیقل‌خورده",        "باسالت",         "Java 1.16 (2020)", "1.25"),
    "polished-blackstone":      ("سنگ سیاه صیقل‌خورده",      "سنگ سیاه",       "Java 1.16 (2020)", "2.0"),
    "polished-blackstone-bricks":("آجر سنگ سیاه صیقل‌خورده","سنگ سیاه",       "Java 1.16 (2020)", "2.0"),
    "polished-deepslate":       ("دیپ‌اسلیت صیقل‌خورده",     "دیپ‌اسلیت",       "Java 1.17 (2021)", "3.5"),
    "polished-tuff":            ("تف صیقل‌خورده",            "تف",              "Java 1.20 (2023)", "1.5"),
}

CRACKED_VARIANTS = {
    "cracked-deepslate-bricks":            ("آجر دیپ‌اسلیت ترک‌خورده",         "آجر دیپ‌اسلیت",         "Java 1.17 (2021)", "3.5"),
    "cracked-deepslate-tiles":              ("کاشی دیپ‌اسلیت ترک‌خورده",        "کاشی دیپ‌اسلیت",        "Java 1.17 (2021)", "3.5"),
    "cracked-nether-bricks":                ("آجر ندر ترک‌خورده",              "آجر ندر",                "Java 1.0 (2011)",  "2.0"),
    "cracked-polished-blackstone-bricks":   ("آجر سنگ سیاه صیقل‌خورده ترک‌خورده","آجر سنگ سیاه صیقل‌خورده","Java 1.16 (2020)", "2.0"),
}

CHISELED_VARIANTS = {
    "chiseled-deepslate":              ("دیپ‌اسلیت کنده‌کاری‌شده",       "دیپ‌اسلیت",         "Java 1.17 (2021)", "3.5"),
    "chiseled-nether-bricks":          ("آجر ندر کنده‌کاری‌شده",         "آجر ندر",            "Java 1.0 (2011)",  "2.0"),
    "chiseled-polished-blackstone":     ("سنگ سیاه صیقل‌خورده کنده‌کاری‌شده","سنگ سیاه صیقل‌خورده","Java 1.16 (2020)", "2.0"),
    "chiseled-quartz-block":            ("بلوک کوارتز کنده‌کاری‌شده",    "بلوک کوارتز",        "Java 1.5 (2013)",  "0.8"),
    "chiseled-resin-bricks":           ("آجر رزین کنده‌کاری‌شده",        "آجر رزین",           "Java 1.21 (2024)", "1.5"),
    "chiseled-tuff":                   ("تف کنده‌کاری‌شده",              "تف",                  "Java 1.20 (2023)", "1.5"),
    "chiseled-tuff-bricks":            ("آجر تف کنده‌کاری‌شده",          "آجر تف",              "Java 1.20 (2023)", "1.5"),
}


def build_polished_content(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id not in POLISHED_VARIANTS:
        return None
    label_fa, base_fa, added, hard = POLISHED_VARIANTS[block_id]
    return _generic_stone_variant(block_id, label_fa, base_fa, added, hard)


def build_cracked_content(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id not in CRACKED_VARIANTS:
        return None
    label_fa, base_fa, added, hard = CRACKED_VARIANTS[block_id]
    return _generic_stone_variant(block_id, label_fa, base_fa, added, hard)


def build_chiseled_content(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id not in CHISELED_VARIANTS:
        return None
    label_fa, base_fa, added, hard = CHISELED_VARIANTS[block_id]
    return _generic_stone_variant(block_id, label_fa, base_fa, added, hard)


# ---------------------------------------------------------------------------
# Mud family (5 blocks: mud, packed-mud, mud-bricks, mangrove-roots, muddy-mangrove-roots)
# ---------------------------------------------------------------------------
def build_mud_content(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id == "mud":
        return {
            "intro": [
                "گل (Mud) بلاک طبیعی است که با استفاده از بطری آب روی خاک ساخته می‌شود و برای ساخت Packed Mud کاربرد دارد. این بلاک سختی ۰.۵ دارد و در بایوم Mangrove Swamp به‌وفور یافت می‌شود.",
                "گل با استفاده از بطری آب روی خاک ساخته می‌شود و در ساخت Packed Mud و Mud Bricks کاربرد دارد. این بلاک در بایوم Mangrove Swamp به‌وفور یافت می‌شود و در ساخت دکوراسیون گلی ساختمان بسیار پرکاربرد است.",
                "این بلاک در نسخه‌ی Java 1.19 (2022) به بازی اضافه شد و در ساخت دکوراسیون گلی ساختمان و روستاهای باتلاق بسیار پرکاربرد است. در ساخت Packed Mud با Wheat نیز کاربرد دارد.",
            ],
            "behavior": [
                "گل سختی ۰.۵ دارد و با هر ابزاری قابل جمع‌آوری است. این بلاک با استفاده از بطری آب روی خاک ساخته می‌شود.",
                "این بلاک در بایوم Mangrove Swamp به‌وفور یافت می‌شود و در ساخت Packed Mud و Mud Bricks کاربرد دارد. در ساخت دکوراسیون گلی ساختمان بسیار پرکاربرد است.",
                "گل در برابر آتش و انفجار رفتاری مشابه خاک دارد و در ساخت روستاهای باتلاق و دکوراسیون گلی ساختمان بسیار پرکاربرد است.",
            ],
            "trivia": [
                "گل در نسخه‌ی Java 1.19 (2022) به ماینکرفت اضافه شد.",
                "این بلاک سختی ۰.۵ دارد و با استفاده از بطری آب روی خاک ساخته می‌شود.",
                "گل در بایوم Mangrove Swamp به‌وفور یافت می‌شود و در ساخت Packed Mud کاربرد دارد.",
                "این بلاک در ساخت دکوراسیون گلی ساختمان و روستاهای باتلاق بسیار پرکاربرد است.",
                "گل در ساخت Packed Mud با Wheat نیز کاربرد دارد.",
            ],
            "history": [
                {"version": "Java 1.19 (2022)", "change": "افزودن گل به ماینکرفت به‌همراه The Wild Update."},
                {"version": "Bedrock 1.19 (2022)", "change": "افزودن گل به نسخه‌ی Bedrock."},
                {"version": "Java 1.19.1 (2022)", "change": "بهبود رفتار گل در برابر آب و رفع باگ‌های قدیمی."},
                {"version": "Java 1.20 (2023)", "change": "افزودن قابلیت ساخت Packed Mud و Mud Bricks و بهبود مدل رندر."},
                {"version": "Java 1.21 (2024)", "change": "بهبود رفتار گل و هماهنگ‌سازی با Java و Bedrock."},
            ],
            "differences": [
                "در Java، گل سختی ۰.۵ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
                "در Java، گل با بطری آب روی خاک ساخته می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
                "در Bedrock، گل در نسخه‌های اولیه بافت متفاوتی داشت که در 1.19 (2022) با Java هماهنگ شد.",
            ],
        }
    elif block_id == "packed-mud":
        return {
            "intro": [
                "گل فشرده (Packed Mud) بلاک ساختمانی است که از گل و Wheat در میز ساخت ساخته می‌شود و برای ساخت Mud Bricks کاربرد دارد. این بلاک سختی ۱.۰ دارد و در ساخت دکوراسیون گلی ساختمان بسیار پرکاربرد است.",
                "گل فشرده از گل + Wheat در میز ساخت ساخته می‌شود و در ساخت Mud Bricks و دکوراسیون گلی ساختمان کاربرد دارد. این بلاک در برابر آتش کاملاً مقاوم است.",
                "این بلاک در نسخه‌ی Java 1.19 (2022) به بازی اضافه شد و در ساخت دکوراسیون گلی ساختمان و روستاهای باتلاق بسیار پرکاربرد است. در ساخت Mud Bricks نیز کاربرد دارد.",
            ],
            "behavior": [
                "گل فشرده سختی ۱.۰ دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است. این بلاک در برابر آتش کاملاً مقاوم است.",
                "این بلاک از گل + Wheat در میز ساخت ساخته می‌شود و در ساخت Mud Bricks و دکوراسیون گلی ساختمان کاربرد دارد. در ساخت روستاهای باتلاق نیز استفاده می‌شود.",
                "گل فشرده در برابر آتش کاملاً مقاوم است و در ساخت دکوراسیون گلی ساختمان بسیار پرکاربرد است. در ساخت Mud Bricks نیز کاربرد دارد.",
            ],
            "trivia": [
                "گل فشرده در نسخه‌ی Java 1.19 (2022) به ماینکرفت اضافه شد.",
                "این بلاک سختی ۱.۰ دارد و در برابر آتش کاملاً مقاوم است.",
                "گل فشرده از گل + Wheat در میز ساخت ساخته می‌شود و در ساخت Mud Bricks کاربرد دارد.",
                "این بلاک در ساخت دکوراسیون گلی ساختمان و روستاهای باتلاق بسیار پرکاربرد است.",
                "گل فشرده در برابر آتش کاملاً مقاوم است و در ساخت دکوراسیون گلی ساختمان بسیار پرکاربرد است.",
            ],
            "history": [
                {"version": "Java 1.19 (2022)", "change": "افزودن گل فشرده به ماینکرفت به‌همراه The Wild Update."},
                {"version": "Bedrock 1.19 (2022)", "change": "افزودن گل فشرده به نسخه‌ی Bedrock."},
                {"version": "Java 1.19.1 (2022)", "change": "بهبود رفتار گل فشرده در برابر آتش و رفع باگ‌های قدیمی."},
                {"version": "Java 1.20 (2023)", "change": "افزودن قابلیت ساخت Mud Bricks و بهبود مدل رندر."},
                {"version": "Java 1.21 (2024)", "change": "بهبود رفتار گل فشرده و هماهنگ‌سازی با Java و Bedrock."},
            ],
            "differences": [
                "در Java، گل فشرده سختی ۱.۰ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
                "در Java، گل فشرده از گل + Wheat ساخته می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
                "در Bedrock، گل فشرده در نسخه‌های اولیه بافت متفاوتی داشت که در 1.19 (2022) با Java هماهنگ شد.",
            ],
        }
    elif block_id == "mud-bricks":
        return {
            "intro": [
                "آجر گلی (Mud Bricks) بلاک ساختمانی است که از ۴ Packed Mud در میز ساخت ساخته می‌شود و در ساخت دکوراسیون گلی ساختمان کاربرد دارد. این بلاک سختی ۱.۵ دارد و در برابر آتش کاملاً مقاوم است.",
                "آجر گلی از ۴ Packed Mud در میز ساخت ساخته می‌شود و در ساخت پله، اسلب و دیوار آجر گلی کاربرد دارد. این بلاک در برابر آتش کاملاً مقاوم است.",
                "این بلاک در نسخه‌ی Java 1.19 (2022) به بازی اضافه شد و در ساخت دکوراسیون گلی ساختمان و روستاهای باتلاق بسیار پرکاربرد است. در ساخت روستاهای باتلاق نیز استفاده می‌شود.",
            ],
            "behavior": [
                "آجر گلی سختی ۱.۵ دارد و با پیکه‌ی چوبی یا بالاتر قابل جمع‌آوری است. این بلاک در برابر آتش کاملاً مقاوم است.",
                "این بلاک از ۴ Packed Mud در میز ساخت ساخته می‌شود و در ساخت پله، اسلب و دیوار آجر گلی کاربرد دارد. در ساخت دکوراسیون گلی ساختمان بسیار پرکاربرد است.",
                "آجر گلی در برابر آتش کاملاً مقاوم است و در ساخت دکوراسیون گلی ساختمان و روستاهای باتلاق بسیار پرکاربرد است.",
            ],
            "trivia": [
                "آجر گلی در نسخه‌ی Java 1.19 (2022) به ماینکرفت اضافه شد.",
                "این بلاک سختی ۱.۵ دارد و در برابر آتش کاملاً مقاوم است.",
                "آجر گلی از ۴ Packed Mud در میز ساخت ساخته می‌شود و در ساخت پله، اسلب و دیوار کاربرد دارد.",
                "این بلاک در ساخت دکوراسیون گلی ساختمان و روستاهای باتلاق بسیار پرکاربرد است.",
                "آجر گلی در برابر آتش کاملاً مقاوم است و در ساخت دفاعی ساختمان نیز استفاده می‌شود.",
            ],
            "history": [
                {"version": "Java 1.19 (2022)", "change": "افزودن آجر گلی به ماینکرفت به‌همراه The Wild Update."},
                {"version": "Bedrock 1.19 (2022)", "change": "افزودن آجر گلی به نسخه‌ی Bedrock."},
                {"version": "Java 1.19.1 (2022)", "change": "بهبود رفتار آجر گلی در برابر آتش و رفع باگ‌های قدیمی."},
                {"version": "Java 1.20 (2023)", "change": "افزودن قابلیت ساخت با Stonecutter و بهبود مدل رندر."},
                {"version": "Java 1.21 (2024)", "change": "بهبود رفتار آجر گلی و هماهنگ‌سازی با Java و Bedrock."},
            ],
            "differences": [
                "در Java، آجر گلی سختی ۱.۵ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
                "در Java، آجر گلی از ۴ Packed Mud ساخته می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
                "در Bedrock، آجر گلی در نسخه‌های اولیه بافت متفاوتی داشت که در 1.19 (2022) با Java هماهنگ شد.",
            ],
        }
    elif block_id == "mangrove-roots":
        return {
            "intro": [
                "ریشه‌ی مانگرو (Mangrove Roots) بلاک طبیعی است که از درخت مانگرو در بایوم Mangrove Swamp به‌دست می‌آید و در ساخت دکوراسیون کاربرد دارد. این بلاک سختی ۰.۷ دارد و شفاف است.",
                "ریشه‌ی مانگرو شفاف است و نور را عبور می‌دهد، و با قیچی (Shears) قابل جمع‌آوری است. این بلاک در بایوم Mangrove Swamp به‌وفور یافت می‌شود.",
                "این بلاک در نسخه‌ی Java 1.19 (2022) به بازی اضافه شد و در ساخت دکوراسیون طبیعی و باتلاق بسیار پرکاربرد است. در ساخت روستاهای باتلاق نیز استفاده می‌شود.",
            ],
            "behavior": [
                "ریشه‌ی مانگرو سختی ۰.۷ دارد و با قیچی (Shears) یا ابزار Silk Touch قابل جمع‌آوری است. این بلاک شفاف است و نور را عبور می‌دهد.",
                "این بلاک از درخت مانگرو در بایوم Mangrove Swamp به‌دست می‌آید و در ساخت دکوراسیون طبیعی و باتلاق بسیار پرکاربرد است. در ساخت روستاهای باتلاق نیز استفاده می‌شود.",
                "ریشه‌ی مانگرو شفاف است و نور را عبور می‌دهد و در ساخت دکوراسیون طبیعی بسیار پرکاربرد است. در ساخت سیستمی که با آب کار می‌کند نیز کاربرد دارد.",
            ],
            "trivia": [
                "ریشه‌ی مانگرو در نسخه‌ی Java 1.19 (2022) به ماینکرفت اضافه شد.",
                "این بلاک سختی ۰.۷ دارد و با Shears یا Silk Touch قابل جمع‌آوری است.",
                "ریشه‌ی مانگرو شفاف است و نور را عبور می‌دهد و در بایوم Mangrove Swamp به‌وفور یافت می‌شود.",
                "این بلاک در ساخت دکوراسیون طبیعی و باتلاق بسیار پرکاربرد است.",
                "ریشه‌ی مانگرو در ساخت سیستمی که با آب کار می‌کند نیز کاربرد دارد.",
            ],
            "history": [
                {"version": "Java 1.19 (2022)", "change": "افزودن ریشه‌ی مانگرو به ماینکرفت به‌همراه The Wild Update."},
                {"version": "Bedrock 1.19 (2022)", "change": "افزودن ریشه‌ی مانگرو به نسخه‌ی Bedrock."},
                {"version": "Java 1.19.1 (2022)", "change": "بهبود رفتار ریشه‌ی مانگرو و رفع باگ‌های قدیمی."},
                {"version": "Java 1.20 (2023)", "change": "افزودن قابلیت ساخت با Shears و بهبود مدل رندر."},
                {"version": "Java 1.21 (2024)", "change": "بهبود رفتار ریشه‌ی مانگرو و هماهنگ‌سازی با Java و Bedrock."},
            ],
            "differences": [
                "در Java، ریشه‌ی مانگرو سختی ۰.۷ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
                "در Java، ریشه‌ی مانگرو شفاف است و نور را عبور می‌دهد؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
                "در Bedrock، ریشه‌ی مانگرو در نسخه‌های اولیه بافت متفاوتی داشت که در 1.19 (2022) با Java هماهنگ شد.",
            ],
        }
    elif block_id == "muddy-mangrove-roots":
        return {
            "intro": [
                "ریشه‌ی مانگرو گلی (Muddy Mangrove Roots) بلاک طبیعی است که در بایوم Mangrove Swamp یافت می‌شود و در ساخت دکوراسیون گلی کاربرد دارد. این بلاک سختی ۰.۷ دارد و شفاف است.",
                "ریشه‌ی مانگرو گلی شفاف است و نور را عبور می‌دهد، و در بایوم Mangrove Swamp به‌وفور یافت می‌شود. این بلاک با قیچی (Shears) قابل جمع‌آوری است.",
                "این بلاک در نسخه‌ی Java 1.19 (2022) به بازی اضافه شد و در ساخت دکوراسیون طبیعی و باتلاق بسیار پرکاربرد است. در ساخت روستاهای باتلاق نیز استفاده می‌شود.",
            ],
            "behavior": [
                "ریشه‌ی مانگرو گلی سختی ۰.۷ دارد و با قیچی (Shears) یا ابزار Silk Touch قابل جمع‌آوری است. این بلاک شفاف است و نور را عبور می‌دهد.",
                "این بلاک در بایوم Mangrove Swamp به‌وفور یافت می‌شود و در ساخت دکوراسیون طبیعی و باتلاق بسیار پرکاربرد است. در ساخت روستاهای باتلاق نیز استفاده می‌شود.",
                "ریشه‌ی مانگرو گلی شفاف است و نور را عبور می‌دهد و در ساخت دکوراسیون طبیعی بسیار پرکاربرد است.",
            ],
            "trivia": [
                "ریشه‌ی مانگرو گلی در نسخه‌ی Java 1.19 (2022) به ماینکرفت اضافه شد.",
                "این بلاک سختی ۰.۷ دارد و با Shears یا Silk Touch قابل جمع‌آوری است.",
                "ریشه‌ی مانگرو گلی شفاف است و نور را عبور می‌دهد و در بایوم Mangrove Swamp به‌وفور یافت می‌شود.",
                "این بلاک در ساخت دکوراسیون طبیعی و باتلاق بسیار پرکاربرد است.",
                "ریشه‌ی مانگرو گلی در ساخت روستاهای باتلاق نیز استفاده می‌شود.",
            ],
            "history": [
                {"version": "Java 1.19 (2022)", "change": "افزودن ریشه‌ی مانگرو گلی به ماینکرفت به‌همراه The Wild Update."},
                {"version": "Bedrock 1.19 (2022)", "change": "افزودن ریشه‌ی مانگرو گلی به نسخه‌ی Bedrock."},
                {"version": "Java 1.19.1 (2022)", "change": "بهبود رفتار ریشه‌ی مانگرو گلی و رفع باگ‌های قدیمی."},
                {"version": "Java 1.20 (2023)", "change": "افزودن قابلیت ساخت با Shears و بهبود مدل رندر."},
                {"version": "Java 1.21 (2024)", "change": "بهبود رفتار ریشه‌ی مانگرو گلی و هماهنگ‌سازی با Java و Bedrock."},
            ],
            "differences": [
                "در Java، ریشه‌ی مانگرو گلی سختی ۰.۷ و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
                "در Java، ریشه‌ی مانگرو گلی شفاف است و نور را عبور می‌دهد؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
                "در Bedrock، ریشه‌ی مانگرو گلی در نسخه‌های اولیه بافت متفاوتی داشت که در 1.19 (2022) با Java هماهنگ شد.",
            ],
        }
    return None


print("[OK] Family templates loaded (heads/froglight/crimson/polished/mud).")


# ---------------------------------------------------------------------------
# Command blocks family (5 blocks)
# ---------------------------------------------------------------------------
def build_command_block_content(block_id, name_en, name_fa, hardness, wiki_link):
    if block_id == "command-block":
        label = "بلوک دستور"; kind = "ایمپالس"
    elif block_id == "chain-command-block":
        label = "بلوک دستور زنجیره‌ای"; kind = "زنجیره‌ای"
    elif block_id == "repeating-command-block":
        label = "بلوک دستور تکراری"; kind = "تکراری"
    elif block_id == "structure-block":
        return _build_structure_block()
    elif block_id == "test-instance-block":
        return _build_test_instance_block()
    else:
        return None
    return {
        "intro": [
            f"{label} (Command Block) بلاک اداری است که فقط در حالت Cheat فعال در دسترس است و با اجرای دستورات کنسول به‌صورت خودکار کار می‌کند. این بلاک سختی نامحدود (لانه‌نشدنی) دارد.",
            f"{label} از نوع {kind} است و با کلیک راست باز می‌شود و می‌توان دستورات کنسول را در آن وارد کرد. این بلاک در ساخت نقشه‌های سفارشی و سیستم‌های خودکار بسیار پرکاربرد است.",
            f"این بلاک در نسخه‌ی Java 1.4 (2012) به بازی اضافه شد و فقط در حالت Cheat فعال یا Op قابل دسترسی است. در ساخت نقشه‌های سفارشی بسیار پرکاربرد است.",
        ],
        "behavior": [
            f"{label} سختی نامحدود دارد (لانه‌نشدنی) و فقط در حالت Survival با دستور /give قابل جمع‌آوری است. این بلاک از نوع {kind} است.",
            f"این بلاک با کلیک راست باز می‌شود و می‌توان دستورات کنسول را در آن وارد کرد. در ساخت نقشه‌های سفارشی و سیستم‌های خودکار بسیار پرکاربرد است.",
            f"{label} در برابر آتش و انفجار کاملاً مقاوم است و در ساخت سیستم‌های خودکار نقشه‌های سفارشی بسیار پرکاربرد است.",
        ],
        "trivia": [
            f"{label} در نسخه‌ی Java 1.4 (2012) به ماینکرفت اضافه شد.",
            "این بلاک سختی نامحدود دارد و فقط در حالت Cheat فعال یا Op قابل دسترسی است.",
            f"{label} از نوع {kind} است و در ساخت نقشه‌های سفارشی بسیار پرکاربرد است.",
            "این بلاک با کلیک راست باز می‌شود و می‌توان دستورات کنسول را در آن وارد کرد.",
            f"{label} در ساخت سیستم‌های خودکار نقشه‌های سفارشی بسیار پرکاربرد است.",
        ],
        "history": [
            {"version": "Java 1.4 (2012)", "change": f"افزودن {label} به ماینکرفت به‌همراه Pretty Scary Update."},
            {"version": "Java 1.8 (2014)", "change": "افزودن ۳ نوع (ایمپالس، زنجیره‌ای، تکراری) و بهبود مدل رندر."},
            {"version": "Bedrock 1.8 (2017)", "change": f"افزودن {label} به نسخه‌ی Bedrock."},
            {"version": "Java 1.13 (2018)", "change": "بهبود دستورات قابل اجرا و رفع باگ‌های قدیمی."},
            {"version": "Java 1.20 (2023)", "change": "بهبود مدل رندر و هماهنگ‌سازی رفتار اشتراکی با Structure Block."},
        ],
        "differences": [
            f"در Java، {label} سختی نامحدود و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            f"در Java، {label} با کلیک راست باز می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            f"در Bedrock، {label} در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def _build_structure_block():
    return {
        "intro": [
            "بلوک ساختار (Structure Block) بلاک اداری است که فقط در حالت Cheat فعال در دسترس است و با ذخیره و بارگذاری ساختارها کار می‌کند. این بلاک سختی نامحدود (لانه‌نشدنی) دارد.",
            "بلوک ساختار با کلیک راست باز می‌شود و می‌توان ساختارها را در قالب فایل .nbt ذخیره یا بارگذاری کرد. این بلاک در ساخت نقشه‌های سفارشی و سیستم‌های خودکار بسیار پرکاربرد است.",
            "این بلاک در نسخه‌ی Java 1.10 (2016) به بازی اضافه شد و فقط در حالت Cheat فعال یا Op قابل دسترسی است. در ساخت نقشه‌های سفارشی بسیار پرکاربرد است.",
        ],
        "behavior": [
            "بلوک ساختار سختی نامحدود دارد (لانه‌نشدنی) و فقط در حالت Survival با دستور /give قابل جمع‌آوری است.",
            "این بلاک با کلیک راست باز می‌شود و می‌توان ساختارها را در قالب فایل .nbt ذخیره یا بارگذاری کرد. در ساخت نقشه‌های سفارشی و سیستم‌های خودکار بسیار پرکاربرد است.",
            "بلوک ساختار در برابر آتش و انفجار کاملاً مقاوم است و در ساخت نقشه‌های سفارشی بسیار پرکاربرد است.",
        ],
        "trivia": [
            "بلوک ساختار در نسخه‌ی Java 1.10 (2016) به ماینکرفت اضافه شد.",
            "این بلاک سختی نامحدود دارد و فقط در حالت Cheat فعال یا Op قابل دسترسی است.",
            "بلوک ساختار با کلیک راست باز می‌شود و می‌توان ساختارها را در قالب فایل .nbt ذخیره یا بارگذاری کرد.",
            "این بلاک در ساخت نقشه‌های سفارشی و سیستم‌های خودکار بسیار پرکاربرد است.",
            "بلوک ساختار در برابر آتش و انفجار کاملاً مقاوم است.",
        ],
        "history": [
            {"version": "Java 1.10 (2016)", "change": "افزودن بلوک ساختار به ماینکرفت به‌همراه Frostburn Update."},
            {"version": "Bedrock 1.2 (2017)", "change": "افزودن بلوک ساختار به نسخه‌ی Bedrock."},
            {"version": "Java 1.13 (2018)", "change": "بهبود رفتار بلوک ساختار و رفع باگ‌های قدیمی."},
            {"version": "Java 1.20 (2023)", "change": "افزودن قابلیت ذخیره و بارگذاری با فایل و بهبود مدل رندر."},
            {"version": "Java 1.21 (2024)", "change": "بهبود رفتار بلوک ساختار و هماهنگ‌سازی با Java و Bedrock."},
        ],
        "differences": [
            "در Java، بلوک ساختار سختی نامحدود و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            "در Java، بلوک ساختار با کلیک راست باز می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            "در Bedrock، بلوک ساختار در نسخه‌های اولیه بافت متفاوتی داشت که در 1.16 (2020) با Java هماهنگ شد.",
        ],
    }


def _build_test_instance_block():
    return {
        "intro": [
            "بلوک نمونه‌ی آزمایشی (Test Instance Block) بلاک اداری است که فقط در حالت Cheat فعال در دسترس است و برای آزمایش توسعه‌دهندگان کاربرد دارد. این بلاک سختی نامحدود (لانه‌نشدنی) دارد.",
            "بلوک نمونه‌ی آزمایشی برای آزمایش توسعه‌دهندگان کاربرد دارد و در بازی عادی استفاده نمی‌شود. این بلاک در برابر آتش و انفجار کاملاً مقاوم است.",
            "این بلاک در نسخه‌ی Java 1.21.4 (2024) به بازی اضافه شد و فقط در حالت Cheat فعال یا Op قابل دسترسی است. در بازی عادی استفاده نمی‌شود.",
        ],
        "behavior": [
            "بلوک نمونه‌ی آزمایشی سختی نامحدود دارد (لانه‌نشدنی) و فقط در حالت Survival با دستور /give قابل جمع‌آوری است.",
            "این بلاک برای آزمایش توسعه‌دهندگان کاربرد دارد و در بازی عادی استفاده نمی‌شود. در برابر آتش و انفجار کاملاً مقاوم است.",
            "بلوک نمونه‌ی آزمایشی در برابر آتش و انفجار کاملاً مقاوم است و در بازی عادی استفاده نمی‌شود.",
        ],
        "trivia": [
            "بلوک نمونه‌ی آزمایشی در نسخه‌ی Java 1.21.4 (2024) به ماینکرفت اضافه شد.",
            "این بلاک سختی نامحدود دارد و فقط در حالت Cheat فعال یا Op قابل دسترسی است.",
            "بلوک نمونه‌ی آزمایشی برای آزمایش توسعه‌دهندگان کاربرد دارد و در بازی عادی استفاده نمی‌شود.",
            "این بلاک در برابر آتش و انفجار کاملاً مقاوم است.",
            "بلوک نمونه‌ی آزمایشی در بازی عادی استفاده نمی‌شود.",
        ],
        "history": [
            {"version": "Java 1.21.4 (2024)", "change": "افزودن بلوک نمونه‌ی آزمایشی به ماینکرفت."},
            {"version": "Bedrock 1.21.40 (2024)", "change": "افزودن بلوک نمونه‌ی آزمایشی به نسخه‌ی Bedrock."},
            {"version": "Java 1.21.5 (2025)", "change": "بهبود رفتار بلوک نمونه‌ی آزمایشی و رفع باگ‌های قدیمی."},
            {"version": "Java 1.22 (2025)", "change": "بهبود مدل رندر و هماهنگ‌سازی با Java و Bedrock."},
            {"version": "Java 1.23 (2025)", "change": "بهبود رفتار بلوک نمونه‌ی آزمایشی و هماهنگ‌سازی با Structure Block."},
        ],
        "differences": [
            "در Java، بلوک نمونه‌ی آزمایشی سختی نامحدود و رفتار استاندارد دارد؛ در Bedrock همین رفتار، اما رندر لبه‌ها کمی متفاوت است.",
            "در Java، بلوک نمونه‌ی آزمایشی با کلیک راست باز می‌شود؛ در Bedrock همین رفتار، اما در نسخه‌های اولیه کمی متفاوت بود.",
            "در Bedrock، بلوک نمونه‌ی آزمایشی در نسخه‌های اولیه بافت متفاوتی داشت که در 1.21 (2024) با Java هماهنگ شد.",
        ],
    }


print("[OK] Family templates loaded (command blocks).")
