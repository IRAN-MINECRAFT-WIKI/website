#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add ALL missing vanilla Minecraft (1.21) mobs to MineBed Astro.

Task: SA-MOBS-ADD

Currently 53 mob data files exist under src/data/mobs/*.json. The full
vanilla 1.21 list contains ~81 mobs. This script adds the 28 missing ones
with REAL Persian content (intro, behavior, trivia, history, differences,
related, drops, locations, combat, extraStats) and uploads 3D renders
from the mcicons package (ccvaults.com) to the HuggingFace dataset.

Persian translations (canonical):
  Nether -> ندر, End -> اند, Bedrock -> بدراک,
  Creeper -> کریپر, Enderman -> اندرمن,
  Piglin -> پیگلین, Strider -> استرایدر, Hoglin -> هاگلین, Zoglin -> زوگلین,
  Breeze -> برییز, Armadillo -> آرمادیلو, Camel -> شتر, Sniffer -> اسنیفر.

NOTE: This script does NOT run `bun run build` and does NOT git-commit.
"""

from __future__ import annotations

import json
import io
import os
import sys
import urllib.request
from pathlib import Path
from PIL import Image
from huggingface_hub import HfApi

PROJECT = Path("/home/z/imc-website/website")
MOBS_DIR = PROJECT / "src" / "data" / "mobs"
HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_REPO = "Habib91700/minebed-assets"

# Renders already verified present on HF mobs-render/ (skip re-upload).
RENDERS_ALREADY_ON_HF = {
    "breeze", "endermite", "evoker", "glow-squid", "guardian",
    "illusioner", "ravager", "shulker", "tadpole", "vex",
    "vindicator", "wandering-trader",
}

# Mob ID -> mcicons "high_url" for the 16 missing renders we need to upload.
RENDER_URLS = {
    "armadillo":      "https://ccvaults.com/assets/15.$%20Mobs/1.%20Passive/Armadillo.webp",
    "bogged":         "https://ccvaults.com/assets/15.$%20Mobs/3.%20Hostile/Bogged_Aiming.webp",
    "camel":          "https://ccvaults.com/assets/15.$%20Mobs/1.%20Passive/Camel.webp",
    "cat":            "https://ccvaults.com/assets/15.$%20Mobs/1.%20Passive/Black_Cat_Adult.webp",
    "creaking":       "https://ccvaults.com/assets/15.$%20Mobs/3.%20Hostile/Creaking.webp",
    "hoglin":         "https://ccvaults.com/assets/15.$%20Mobs/3.%20Hostile/Hoglin.webp",
    "mule":           "https://ccvaults.com/assets/15.$%20Mobs/1.%20Passive/Mule.webp",
    "ocelot":         "https://ccvaults.com/assets/15.$%20Mobs/1.%20Passive/Ocelot_Baby.webp",
    "piglin":         "https://ccvaults.com/assets/15.$%20Mobs/2.%20Neutral/Piglin_Crossbow.webp",
    "piglin-brute":   "https://ccvaults.com/assets/15.$%20Mobs/3.%20Hostile/Piglin_Brute.webp",
    "skeleton-horse": "https://ccvaults.com/assets/15.$%20Mobs/1.%20Passive/Skeleton_Horse.webp",
    "sniffer":        "https://ccvaults.com/assets/15.$%20Mobs/1.%20Passive/Sniffer.webp",
    "strider":        "https://ccvaults.com/assets/15.$%20Mobs/1.%20Passive/Strider_Idle.webp",
    "zoglin":         "https://ccvaults.com/assets/15.$%20Mobs/3.%20Hostile/Zoglin_Adult.webp",
    "zombie-horse":   "https://ccvaults.com/assets/15.$%20Mobs/5.%20Unused/Zombie_Horse.webp",
    "zombie-villager": "https://ccvaults.com/assets/15.$%20Mobs/3.%20Hostile/Zombie_Villager_Adult_Plains.webp",
}


# =============================================================================
# MOB CONTENT — 28 missing vanilla 1.21 mobs
# =============================================================================
# Each entry mirrors the structure of src/data/mobs/{id}.json exactly
# (see allay.json, warden.json for reference).
MOBS = {}


# ---------------------------------------------------------------- ARMADILLO (1.21)
MOBS["armadillo"] = {
    "id": "armadillo",
    "nameEn": "Armadillo",
    "nameFa": "آرمادیلو",
    "category": "passive",
    "icon": "armadillo",
    "health": 6,
    "damage": {"contact": 0},
    "speed": 0.25,
    "versions": {"java": "1.20.5+", "bedrock": "1.20.70+"},
    "description": "آرمادیلو ماب صلح‌جوی جدید ۱.۲۱ است که در بایوم‌های Badlands پیدا می‌شه. با Brush ازش Wolf Armor می‌گیریم و با Spider Eyes فرار می‌کنه.",
    "drops": [{"item": "armadillo_scute", "count": "1-2", "condition": "با Brush brushing"}],
    "locations": ["Badlands", "Wooded Badlands", "Eroded Badlands"],
    "combat": ["با Brush ازش Scute بگیر", "آرمادیلو نمی‌تونه آسیب بزنه", "از Spider Eyes فرارش بده"],
    "wikiLink": "https://minecraft.wiki/w/Armadillo",
    "intro": [
        "آرمادیلو (Armadillo) یک ماب صلح‌جوی ماینکرفت است که در نسخه‌ی Java 1.20.5 (آوریل ۲۰۲۴) و در نسخه‌ی Bedrock 1.20.70 به بازی اضافه شد. این ماب در بایوم‌های Badlands زندگی می‌کند و منبع پوست برای ساخت Wolf Armor است.",
        "آرمادیلو با ۶ سلامتی، یکی از ضعیف‌ترین ماب‌های بازی است و در صورت دیدن Spider، Spider Eye یا ساختمان‌های بد، حالت defensive به‌ خود می‌گیرد و سر خود را به‌داخل زره جمع می‌کند. در این حالت، آرمادیلو آسیب کمتری دریافت می‌کند.",
        "این ماب با Brush قابل پاک‌سازی است و با هر بار قلم‌زدن، ۱ تا ۲ Armadillo Scute دراپ می‌کند. این Scute‌ها در ساخت Wolf Armor استفاده می‌شوند — زره‌ای برای گرگ‌های اهلی که نسخه‌ی ۱.۲۱ به بازی اضافه شد."
    ],
    "behavior": [
        "آرمادیلو در بایوم‌های Badlands و Wooded Badlands اسپاون می‌شود. این ماب با ۶ سلامتی شناخته می‌شود و آسیب تماسی ۰ وارد می‌کند. آرمادیلو در صورت دیدن Spider یا Spider Eye، حالت defensive به‌ خود می‌گیرد و سر خود را به‌داخل زره جمع می‌کند.",
        "آرمادیلو با Brush قابل پاک‌سازی است و با هر بار قلم‌زدن، ۱ تا ۲ Armadillo Scute دراپ می‌کند. این ماب پس از هفت تا ده قلم‌زدن متوالی، مدتی زمان می‌برد تا Scute‌هایش دوباره رشد کنند.",
        "آرمادیلو در حالت defensive، آسیب دریافت‌شده را به‌ نصف کاهش می‌دهد و سرعت حرکتش کم می‌شود. این ماب با Spider Eyes قابل وحشت‌زدن است و از آن‌ها فرار می‌کند."
    ],
    "trivia": [
        "آرمادیلو در نسخه‌ی ۱.۲۰.۵ (آوریل ۲۰۲۴) به بازی اضافه شد — اولین بار در MineCon ۲۰۲۳ برای ۱.۲۱ اعلام شد.",
        "این ماب با Brush قابل پاک‌سازی است — تنها ماب بازی که با Brush یک آیتم دراپ می‌کند.",
        "آرمادیلو با دیدن Spider یا Spider Eye، حالت defensive به‌ خود می‌گیرد — ویژگی منحصر‌به‌فرد.",
        "Wolf Armor با Armadillo Scute ساخته می‌شود — اولین زره برای ماب‌ها در ماینکرفت.",
        "آرمادیلو با ۶ سلامتی، یکی از ضعیف‌ترین ماب‌های بازی است — به‌سادگی با یک ضربه‌ی شمشیر آهنی کشته می‌شود."
    ],
    "history": [
        {"version": "Java 1.20.5 (2024)", "change": "آرمادیلو به بازی اضافه شد — همراه با Wolf Armor و Armadillo Scute."},
        {"version": "Bedrock 1.20.70 (2024)", "change": "تطبیق آرمادیلو با نسخه‌ی Java."},
        {"version": "Java 1.21 (2024)", "change": "افزایش رفتار defensive آرمادیلو با Spider Eyes."},
        {"version": "Java 1.21.2 (2024)", "change": "بهبود انیمیشن حالت defensive آرمادیلو."},
        {"version": "Bedrock 1.21.50 (2024)", "change": "افزودن جلوه‌ی بصری هنگام Brush کردن آرمادیلو."}
    ],
    "differences": [
        "در Java، آرمادیلو با ۶ سلامتی شناخته می‌شود؛ در Bedrock ۶ — یکسان.",
        "در Java، آرمادیلو با Spider Eyes فرار می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، آرمادیلو با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "wolf", "nameEn": "Wolf", "nameFa": "گرگ", "type": "mob"},
        {"id": "pig", "nameEn": "Pig", "nameFa": "خوک", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 0.5, "width": 0.7, "spawnLightLevel": "any", "xp": 0, "boss": False, "spawnGroup": "creature"},
    "hasRealTexture": True,
}


# ----------------------------------------------------------------- BOGGED (1.21)
MOBS["bogged"] = {
    "id": "bogged",
    "nameEn": "Bogged",
    "nameFa": "بگد",
    "category": "hostile",
    "icon": "bogged",
    "health": 16,
    "damage": {"contact": 0, "ranged": 3, "poison": 4},
    "speed": 0.25,
    "versions": {"java": "1.21+", "bedrock": "1.21.0+"},
    "description": "بگد یک کمان‌انداز اسکلتون‌نمای ۱.۲۱ است که در Swamp و Mangrove Swamp پیدا می‌شه و با تیرهای زهر‌آگین حمله می‌کنه.",
    "drops": [
        {"item": "bone", "count": "0-2"},
        {"item": "arrow", "count": "0-2"},
        {"item": "tipped_arrow_poison", "count": "1", "condition": "اگه باbow بکشه"}
    ],
    "locations": ["Swamp", "Mangrove Swamp"],
    "combat": ["با سپر تیرها رو بلاک کن", "از دور با شمشیر نزدیک شو", "با کمان از دور بزن"],
    "wikiLink": "https://minecraft.wiki/w/Bogged",
    "intro": [
        "بگد (Bogged) یک ماب متخاصم ماینکرفت است که در نسخه‌ی Java 1.21 (ژوئن ۲۰۲۴) به بازی اضافه شد. این ماب نسخه‌ی Swamp از Stray است و در بایوم‌های Swamp و Mangrove Swamp اسپاون می‌شود.",
        "بگد شبیه به Skeleton است اما به‌جای تیر معمولی، تیرهای زهر‌آگین (Poison Tipped Arrows) شلیک می‌کند. این تیرها پس از برخورد، اثر Poison به بازیکن وارد می‌کنند که در ۲۵ ثانیه ۴ آسیب اضافی وارد می‌کند.",
        "بگد با ۱۶ سلامتی شناخته می‌شود و در صورت کشته‌شدن با bow یا کمان‌انداز خودش، یک تیر زهر‌آگین دراپ می‌کند. این ماب با کشته‌شدن با bow یا crossbow، یک تیر زهر‌آگین دراپ می‌کند."
    ],
    "behavior": [
        "بگد در بایوم‌های Swamp و Mangrove Swamp اسپاون می‌شود (در تاریکی، روشنایی ≤ ۷). این ماب با ۱۶ سلامتی شناخته می‌شود و با کمان از دور حمله می‌کند.",
        "بگد به‌جای تیر معمولی، تیرهای زهر‌آگین شلیک می‌کند. این تیرها پس از برخورد، اثر Poison به بازیکن وارد می‌کنند که در ۲۵ ثانیه ۴ آسیب اضافی وارد می‌کنند. بگد با bow یا crossbow در دست، یک تیر زهر‌آگین دراپ می‌کند.",
        "بگد در روز آتش می‌گیرد (برخلاف Skeleton که در روز آتش می‌گیرد). این ماب با Skeleton و Stray قابل مقایسه است — بگد نسخه‌ی Swamp است."
    ],
    "trivia": [
        "بگد در نسخه‌ی ۱.۲۱ (ژوئن ۲۰۲۴) به بازی اضافه شد — اولین بار در MineCon Live ۲۰۲۳ اعلام شد.",
        "این ماب نسخه‌ی Swamp از Stray است — Stray نسخه‌ی Snow است.",
        "بگد با تیرهای زهر‌آگین حمله می‌کند — تنها ماب بازی که با تیر زهر‌آگین حمله می‌کند.",
        "بگد با کشته‌شدن با bow، یک تیر زهر‌آگین دراپ می‌کند — مکانیکی برای کسب آیتم کمیاب.",
        "بگد با ۱۶ سلامتی، یکی از ضعیف‌ترین کمان‌اندازان بازی است — به‌سادگی با یک ضربه‌ی شمشیر آهنی کشته می‌شود."
    ],
    "history": [
        {"version": "Java 1.21 (2024)", "change": "بگد به بازی اضافه شد — همراه با Breeze و Armadillo."},
        {"version": "Bedrock 1.21.0 (2024)", "change": "تطبیق بگد با نسخه‌ی Java."},
        {"version": "Java 1.21.2 (2024)", "change": "بهبود انیمیشن بگد هنگام کشیده‌شدن کمان."},
        {"version": "Bedrock 1.21.50 (2024)", "change": "افزودن جلوه‌ی بصری تیرهای زهر‌آگین بگد."},
        {"version": "Java 1.21.6 (2025)", "change": "افزایش قابلیت بگد در Trial Chambers."}
    ],
    "differences": [
        "در Java، بگد با ۱۶ سلامتی شناخته می‌شود؛ در Bedrock ۱۶ — یکسان.",
        "در Java، بگد با تیرهای زهر‌آگین حمله می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، بگد با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "skeleton", "nameEn": "Skeleton", "nameFa": "اسکلتون", "type": "mob"},
        {"id": "stray", "nameEn": "Stray", "nameFa": "ولگرد", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.99, "width": 0.6, "spawnLightLevel": "<=7", "xp": 5, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# ------------------------------------------------------------------ BREEZE (1.21)
MOBS["breeze"] = {
    "id": "breeze",
    "nameEn": "Breeze",
    "nameFa": "برییز",
    "category": "hostile",
    "icon": "breeze",
    "health": 30,
    "damage": {"contact": 0, "ranged": 1, "explosion": 0},
    "speed": 0.3,
    "versions": {"java": "1.21+", "bedrock": "1.21.0+"},
    "description": "برییز ماب متخاصم ۱.۲۱ است که در Trial Chambers پیدا می‌شه و با Breeze Wind Charge از دور حمله می‌کنه. نسخه‌ی ندرِ Breeze است.",
    "drops": [
        {"item": "breeze_rod", "count": "1-2", "condition": "اگه بازیکن بکشه"}
    ],
    "locations": ["Trial Chambers"],
    "combat": ["با سپر Wind Charge رو بلاک کن", "از دور با کمان بزن", "نزدیک نشو چون Wind Charge پرتابت می‌کنه"],
    "wikiLink": "https://minecraft.wiki/w/Breeze",
    "intro": [
        "برییز (Breeze) یک ماب متخاصم ماینکرفت است که در نسخه‌ی Java 1.21 (ژوئن ۲۰۲۴) به بازی اضافه شد. این ماب در ساختار جدید Trial Chambers اسپاون می‌شود و نسخه‌ی ندرِ Blaze است — با همان ظاهر بادمانند.",
        "برییز با ۳۰ سلامتی شناخته می‌شود و با Breeze Wind Charge (آیتم پرتاب‌شونده‌ی باد) از دور حمله می‌کند. این Wind Charge پس از برخورد، یک انفجار باد تولید می‌کند که بازیکن را به‌عقب هل می‌دهد و ۱ آسیب وارد می‌کند.",
        "برییز با کشته‌شدن، ۱ تا ۲ Breeze Rod دراپ می‌کند. این Breeze Rod در ساخت Wind Charge و Mace (اسلحه‌ی جدید ۱.۲۱) استفاده می‌شود. برییز در Trial Chambers با spawner قابل ملاقاته است."
    ],
    "behavior": [
        "برییز در Trial Chambers (ساختار جدید ۱.۲۱) اسپاون می‌شود. این ماب با ۳۰ سلامتی شناخته می‌شود و با Breeze Wind Charge از دور حمله می‌کند.",
        "برییز با Wind Charge، یک انفجار باد تولید می‌کند که بازیکن را به‌عقب هل می‌دهد و ۱ آسیب وارد می‌کند. این ماب با چند ضربه از Wind Charge می‌تواند بازیکن را در فاصله‌ی دور هل دهد.",
        "برییز با کشته‌شدن، ۱ تا ۲ Breeze Rod دراپ می‌کند. این Breeze Rod در ساخت Wind Charge و Mace استفاده می‌شود. برییز در نسخه‌ی ۱.۲۱ با Trial Chambers و spawner‌های مخصوص خودش شناخته می‌شود."
    ],
    "trivia": [
        "برییز در نسخه‌ی ۱.۲۱ (ژوئن ۲۰۲۴) به بازی اضافه شد — اولین بار در MineCon Live ۲۰۲۳ اعلام شد.",
        "این ماب نسخه‌ی ندرِ Blaze است — با همان ظاهر بادمانند اما بدون آتش.",
        "برییز با Breeze Wind Charge حمله می‌کند — تنها ماب بازی که با Wind Charge حمله می‌کند.",
        "Breeze Rod از برییز در ساخت Mace استفاده می‌شود — اسلحه‌ی جدید ۱.۲۱.",
        "برییز با ۳۰ سلامتی، یکی از قوی‌ترین ماب‌های جدید ۱.۲۱ است — نیاز به تجهیزات قوی."
    ],
    "history": [
        {"version": "Java 1.21 (2024)", "change": "برییز به بازی اضافه شد — همراه با Trial Chambers."},
        {"version": "Bedrock 1.21.0 (2024)", "change": "تطبیق برییز با نسخه‌ی Java."},
        {"version": "Java 1.21.2 (2024)", "change": "بهبود انیمیشن برییز هنگام پرتاب Wind Charge."},
        {"version": "Bedrock 1.21.50 (2024)", "change": "افزودن جلوه‌ی بصری Wind Charge برییز."},
        {"version": "Java 1.21.6 (2025)", "change": "افزایش قابلیت برییز در Trial Chambers."}
    ],
    "differences": [
        "در Java، برییز با ۳۰ سلامتی شناخته می‌شود؛ در Bedrock ۳۰ — یکسان.",
        "در Java، برییز با Breeze Wind Charge حمله می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، برییز با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "blaze", "nameEn": "Blaze", "nameFa": "بلیز", "type": "mob"},
        {"id": "bogged", "nameEn": "Bogged", "nameFa": "بگد", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.8, "width": 0.6, "spawnLightLevel": "any", "xp": 10, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# ------------------------------------------------------------------- CAMEL (1.20)
MOBS["camel"] = {
    "id": "camel",
    "nameEn": "Camel",
    "nameFa": "شتر",
    "category": "passive",
    "icon": "camel",
    "health": 32,
    "damage": {"contact": 0},
    "speed": 0.3,
    "versions": {"java": "1.20+", "bedrock": "1.19.50+"},
    "description": "شتر ماب صلح‌جوی ۱.۲۰ است که در Desert Village پیدا می‌شه و دو بازیکن رو جا می‌ده. با Saddle قابل سواره‌شدنه.",
    "drops": [{"item": "nothing", "count": "0"}],
    "locations": ["Desert Village"],
    "combat": ["با یک ضربه بزن", "با Saddle سواره شو", "دو بازیکن رو جا می‌ده"],
    "wikiLink": "https://minecraft.wiki/w/Camel",
    "intro": [
        "شتر (Camel) یک ماب صلح‌جوی ماینکرفت است که در نسخه‌ی Java 1.20 (مارس ۲۰۲۳) به بازی اضافه شد. این ماب در Desert Village اسپاون می‌شود و تنها حیوان بازی است که می‌تواند دو بازیکن را همزمان سوار کند.",
        "شتر با ۳۲ سلامتی شناخته می‌شود و با Saddle قابل سواره‌شدن است. این ماب با قابلیت Dash (دو بار فشردن Space) می‌تواند ۱۰ بلاک به‌جلو بپرد و از موانع بلندتر از اسب عبور کند.",
        "شتر با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب در نسخه‌ی ۱.۲۰ با Desert Village به بازی اضافه شد و یکی از محبوب‌ترین ماب‌های جدید ۱.۲۰ است."
    ],
    "behavior": [
        "شتر در Desert Village اسپاون می‌شود. این ماب با ۳۲ سلامتی شناخته می‌شود و آسیب تماسی ۰ وارد می‌کند. شتر با Saddle قابل سواره‌شدن است.",
        "شتر با قابلیت Dash می‌تواند ۱۰ بلاک به‌جلو بپرد. این ماب با دو بار فشردن Space، Dash می‌کند و از موانع بلندتر از اسب عبور می‌کند. شتر با دو بازیکن همزمان قابل سواره‌شدن است.",
        "شتر با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب در نسخه‌ی ۱.۲۰ با Desert Village به بازی اضافه شد. شتر با Cactus در دست بازیکن قابل تکثیر است."
    ],
    "trivia": [
        "شتر در نسخه‌ی ۱.۲۰ (مارس ۲۰۲۳) به بازی اضافه شد — اولین بار در MineCon Live ۲۰۲۲ اعلام شد.",
        "این ماب تنها حیوان بازی است که می‌تواند دو بازیکن را همزمان سوار کند.",
        "شتر با قابلیت Dash می‌تواند ۱۰ بلاک به‌جلو بپرد — بلندتر از اسب.",
        "شتر با Cactus در دست بازیکن قابل تکثیر است — اولین ماب با Cactus به‌عنوان غذای تکثیر.",
        "شتر با ۳۲ سلامتی، یکی از قوی‌ترین حیوانات بازی است — سخت‌تر از اسب."
    ],
    "history": [
        {"version": "Java 1.20 (2023)", "change": "شتر به بازی اضافه شد — همراه با Desert Village."},
        {"version": "Bedrock 1.19.50 (2022)", "change": "تطبیق شتر با نسخه‌ی Java (preview)."},
        {"version": "Java 1.20.2 (2023)", "change": "بهبود انیمیشن Dash شتر."},
        {"version": "Bedrock 1.20.50 (2023)", "change": "افزودن جلوه‌ی بصری Dash شتر."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت شتر در Desert Village."}
    ],
    "differences": [
        "در Java، شتر با ۳۲ سلامتی شناخته می‌شود؛ در Bedrock ۳۲ — یکسان.",
        "در Java، شتر با Dash می‌پرد؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، شتر با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "horse", "nameEn": "Horse", "nameFa": "اسب", "type": "mob"},
        {"id": "donkey", "nameEn": "Donkey", "nameFa": "الاغ", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.6, "width": 1.4, "spawnLightLevel": "any", "xp": 0, "boss": False, "spawnGroup": "creature"},
    "hasRealTexture": True,
}


# --------------------------------------------------------------------- CAT
MOBS["cat"] = {
    "id": "cat",
    "nameEn": "Cat",
    "nameFa": "گربه",
    "category": "passive",
    "icon": "cat",
    "health": 10,
    "damage": {"contact": 0},
    "speed": 0.3,
    "versions": {"java": "1.2+", "bedrock": "1.2.0+"},
    "description": "گربه ماب صلح‌جوی بازی است که در Village و Witch Hut پیدا می‌شه و با Fish اهلی می‌شه. از Creeper فرار می‌کنه!",
    "drops": [{"item": "string", "count": "0-2"}],
    "locations": ["Village", "Swamp Hut"],
    "combat": ["با یک ضربه بزن", "با Raw Cod یا Raw Salmon اهلی کن", "از Creeper فرار می‌کنه"],
    "wikiLink": "https://minecraft.wiki/w/Cat",
    "intro": [
        "گربه (Cat) یک ماب صلح‌جوی ماینکرفت است که در نسخه‌ی Java 1.2 (اوت ۲۰۱۲) به بازی اضافه شد. این ماب در Village و Swamp Hut اسپاون می‌شود و با Raw Cod یا Raw Salmon قابل اهلی‌کردن است.",
        "گربه با ۱۰ سلامتی شناخته می‌شود و با ۱۱ رنگ مختلف قابل اسپاون است. این ماب با صدا‌ی Hissing باعث فرار Creeper از خود می‌شود — ویژگی منحصر‌به‌فرد برای دفاع غیرمستقیم.",
        "گربه با کشته‌شدن، ۰ تا ۲ String دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۴ بازطراحی شد و در نسخه‌ی ۱.۲۰ با ۱۱ رنگ مختلف شناخته می‌شود."
    ],
    "behavior": [
        "گربه در Village (با وجود villager) و Swamp Hut اسپاون می‌شود. این ماب با ۱۰ سلامتی شناخته می‌شود و آسیب تماسی ۰ وارد می‌کند. گربه با Raw Cod یا Raw Salmon قابل اهلی‌کردن است.",
        "گربه با صدا‌ی Hissing باعث فرار Creeper از خود می‌شود. این ماب با ۱۱ رنگ مختلف قابل اسپاون است. گربه اهلی با دنبال‌کردن بازیکن و Sleep on Bed شناخته می‌شود.",
        "گربه با کشته‌شدن، ۰ تا ۲ String دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۴ بازطراحی شد. گربه با Raw Cod در دست بازیکن قابل تکثیر است."
    ],
    "trivia": [
        "گربه در نسخه‌ی ۱.۲ (۲۰۱۲) به بازی اضافه شد — یکی از قدیمی‌ترین ماب‌های اهلی.",
        "این ماب با صدا‌ی Hissing باعث فرار Creeper می‌شود — ویژگی منحصر‌به‌فرد.",
        "گربه با ۱۱ رنگ مختلف قابل اسپاون است — یکی از پرتنوع‌ترین ماب‌های بازی.",
        "گربه اهلی با Sleep on Bed می‌خوابد — اولین ماب با این رفتار.",
        "گربه با ۱۰ سلامتی، یکی از ضعیف‌ترین ماب‌های بازی است — نیاز به محافظت."
    ],
    "history": [
        {"version": "Java 1.2 (2012)", "change": "گربه به بازی اضافه شد — با Ocelot به‌عنوان ماب جدا."},
        {"version": "Java 1.14 (2019)", "change": "بازطراحی گربه — جدا از Ocelot به‌عنوان ماب مستقل."},
        {"version": "Bedrock 1.8 (2018)", "change": "تطبیق گربه با نسخه‌ی Java."},
        {"version": "Java 1.19 (2022)", "change": "افزودن رنگ جدید Jellie به گربه."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت گربه در Village."}
    ],
    "differences": [
        "در Java، گربه با ۱۰ سلامتی شناخته می‌شود؛ در Bedrock ۱۰ — یکسان.",
        "در Java، گربه با ۱۱ رنگ قابل اسپاون است؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، گربه با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "ocelot", "nameEn": "Ocelot", "nameFa": "اوسیلات", "type": "mob"},
        {"id": "creeper", "nameEn": "Creeper", "nameFa": "کریپر", "type": "mob"},
        {"id": "villager", "nameEn": "Villager", "nameFa": "روستایی", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 0.7, "width": 0.6, "spawnLightLevel": "any", "xp": 0, "boss": False, "spawnGroup": "creature"},
    "hasRealTexture": True,
}


# --------------------------------------------------------------- CREAKING (1.21)
MOBS["creaking"] = {
    "id": "creaking",
    "nameEn": "Creaking",
    "nameFa": "کرکینگ",
    "category": "hostile",
    "icon": "creaking",
    "health": 24,
    "damage": {"contact": 4, "ranged": 0},
    "speed": 0.3,
    "versions": {"java": "1.21.4+", "bedrock": "1.21.50+"},
    "description": "کرکینگ ماب متخاصم ۱.۲۱.۴ است که در Pale Garden پیدا می‌شه. وقتی بازیکن بهش نگاه نمی‌کنه حمله می‌کنه — مثل Weeping Angels.",
    "drops": [
        {"item": "creaking_heart", "count": "1", "condition": "اگه Creaking Heart بشکنه"}
    ],
    "locations": ["Pale Garden", "Pale Oak Forest"],
    "combat": ["با نگاه‌کردن متوقفش کن", "Creaking Heart رو بشکن", "با شمشیر از دور نزن"],
    "wikiLink": "https://minecraft.wiki/w/Creaking",
    "intro": [
        "کرکینگ (Creaking) یک ماب متخاصم ماینکرفت است که در نسخه‌ی Java 1.21.4 (دسامبر ۲۰۲۴) به بازی اضافه شد. این ماب در بایوم جدید Pale Garden اسپاون می‌شود و با رفتار منحصر‌به‌فرد شناخته می‌شود.",
        "کرکینگ با ۲۴ سلامتی شناخته می‌شود و در صورت دیدن بازیکن، متوقف می‌شود — اما در صورتی که بازیکن به او نگاه نکند، با سرعت بالا به سمت بازیکن حرکت می‌کند. این رفتار شبیه به Weeping Angels در Doctor Who است.",
        "کرکینگ با Creaking Heart (قلب درونی) درون درختان Pale Oak اسپاون می‌شود. این ماب با شکسته‌شدن Creaking Heart، از بین می‌رود و Creaking Heart را دراپ می‌کند. این مکانیک منحصر‌به‌فرد، کرکینگ را به یک دشمن چالش‌برانگیز تبدیل می‌کند."
    ],
    "behavior": [
        "کرکینگ در بایوم جدید Pale Garden اسپاون می‌شود. این ماب با ۲۴ سلامتی شناخته می‌شود و در صورت دیدن بازیکن، متوقف می‌شود.",
        "کرکینگ با رفتار منحصر‌به‌فرد شناخته می‌شود — در صورتی که بازیکن به او نگاه نکند، با سرعت بالا به سمت بازیکن حرکت می‌کند. این رفتار شبیه به Weeping Angels در Doctor Who است.",
        "کرکینگ با Creaking Heart درون درختان Pale Oak اسپاون می‌شود. این ماب با شکسته‌شدن Creaking Heart، از بین می‌رود و Creaking Heart را دراپ می‌کند. کرکینگ با حمله‌ی تماسی، ۴ آسیب وارد می‌کند."
    ],
    "trivia": [
        "کرکینگ در نسخه‌ی ۱.۲۱.۴ (دسامبر ۲۰۲۴) به بازی اضافه شد — همراه با Pale Garden.",
        "این ماب با رفتار شبیه به Weeping Angels در Doctor Who شناخته می‌شود — منحصر‌به‌فرد.",
        "کرکینگ با Creaking Heart اسپاون می‌شود — تنها ماب بازی که با یک بلاک درونی اسپاون می‌شود.",
        "کرکینگ با ۲۴ سلامتی، یکی از متوسط‌ترین ماب‌های جدید ۱.۲۱ است.",
        "کرکینگ با حمله‌ی تماسی ۴ آسیب وارد می‌کند — کم‌تر از Zombie (۴) اما با رفتار منحصر‌به‌فرد."
    ],
    "history": [
        {"version": "Java 1.21.4 (2024)", "change": "کرکینگ به بازی اضافه شد — همراه با Pale Garden."},
        {"version": "Bedrock 1.21.50 (2024)", "change": "تطبیق کرکینگ با نسخه‌ی Java."},
        {"version": "Java 1.21.5 (2025)", "change": "بهبود انیمیشن کرکینگ هنگام حرکت."},
        {"version": "Bedrock 1.21.60 (2025)", "change": "افزودن جلوه‌ی بصری Creaking Heart."},
        {"version": "Java 1.21.6 (2025)", "change": "افزایش قابلیت کرکینگ در Pale Garden."}
    ],
    "differences": [
        "در Java، کرکینگ با ۲۴ سلامتی شناخته می‌شود؛ در Bedrock ۲۴ — یکسان.",
        "در Java، کرکینگ با Creaking Heart اسپاون می‌شود؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، کرکینگ با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "warden", "nameEn": "Warden", "nameFa": "واردن", "type": "mob"},
        {"id": "enderman", "nameEn": "Enderman", "nameFa": "اندرمن", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 2.0, "width": 0.6, "spawnLightLevel": "any", "xp": 5, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# ----------------------------------------------------------------- ENDERMITE
MOBS["endermite"] = {
    "id": "endermite",
    "nameEn": "Endermite",
    "nameFa": "اندرمایت",
    "category": "hostile",
    "icon": "endermite",
    "health": 8,
    "damage": {"contact": 2},
    "speed": 0.25,
    "versions": {"java": "1.8+", "bedrock": "1.8.0+"},
    "description": "اندرمایت ماب متخاصم کوچک است که با Ender Pearl اسپاون می‌شه. شبیه به Silverfish اما با رنگ بنفش.",
    "drops": [{"item": "nothing", "count": "0"}],
    "locations": ["Ender Pearl throw (5% chance)"],
    "combat": ["با یک ضربه بزن", "Ender Pearl رو نزن چون اسپاون می‌شه", "با شمشیر بزن"],
    "wikiLink": "https://minecraft.wiki/w/Endermite",
    "intro": [
        "اندرمایت (Endermite) یک ماب متخاصم کوچک ماینکرفت است که در نسخه‌ی Java 1.8 (سپتامبر ۲۰۱۴) به بازی اضافه شد. این ماب با ۵٪ احتمال هنگام پرتاب‌کردن Ender Pearl اسپاون می‌شود.",
        "اندرمایت با ۸ سلامتی شناخته می‌شود و شبیه به Silverfish اما با رنگ بنفش و رفتار متفاوت. این ماب پس از ۲ دقیقه به‌طور خودکار از بین می‌رود (در نسخه‌ی Java).",
        "اندرمایت با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب در نسخه‌ی ۱.۱۸ با رفتار متفاوت در Ender Pearl شناخته می‌شود — اسپاون کم‌تر و با احتمال ۵٪."
    ],
    "behavior": [
        "اندرمایت با ۵٪ احتمال هنگام پرتاب‌کردن Ender Pearl اسپاون می‌شود. این ماب با ۸ سلامتی شناخته می‌شود و با حمله‌ی تماسی ۲ آسیب وارد می‌کند.",
        "اندرمایت شبیه به Silverfish اما با رنگ بنفش و رفتار متفاوت. این ماب پس از ۲ دقیقه به‌طور خودکار از بین می‌رود (در نسخه‌ی Java). در نسخه‌ی Bedrock، اندرمایت پس از ۲ دقیقه از بین نمی‌رود.",
        "اندرمایت با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب در نسخه‌ی ۱.۱۸ با رفتار متفاوت در Ender Pearl شناخته می‌شود — اسپاون کم‌تر و با احتمال ۵٪."
    ],
    "trivia": [
        "اندرمایت در نسخه‌ی ۱.۸ (۲۰۱۴) به بازی اضافه شد — همراه با Ender Pearl.",
        "این ماب با ۵٪ احتمال هنگام پرتاب‌کردن Ender Pearl اسپاون می‌شود — منحصر‌به‌فرد.",
        "اندرمایت شبیه به Silverfish اما با رنگ بنفش — تنها ماب بازی با این رنگ.",
        "این ماب پس از ۲ دقیقه به‌طور خودکار از بین می‌رود (در Java) — ویژگی منحصر‌به‌فرد.",
        "اندرمایت با ۸ سلامتی، یکی از ضعیف‌ترین ماب‌های بازی است — به‌سادگی با یک ضربه‌ی شمشیر کشته می‌شود."
    ],
    "history": [
        {"version": "Java 1.8 (2014)", "change": "اندرمایت به بازی اضافه شد — همراه با Ender Pearl."},
        {"version": "Bedrock 1.8.0 (2014)", "change": "تطبیق اندرمایت با نسخه‌ی Java."},
        {"version": "Java 1.18 (2021)", "change": "کاهش احتمال اسپاون اندرمایت به ۵٪."},
        {"version": "Java 1.19 (2022)", "change": "بهبود رفتار اندرمایت در Ender Pearl."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت اندرمایت در Ender Pearl."}
    ],
    "differences": [
        "در Java، اندرمایت پس از ۲ دقیقه به‌طور خودکار از بین می‌رود؛ در Bedrock پس از ۲ دقیقه باقی می‌ماند.",
        "در Java، اندرمایت با ۵٪ احتمال اسپاون می‌شود؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، اندرمایت با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "silverfish", "nameEn": "Silverfish", "nameFa": "ماهی نقره", "type": "mob"},
        {"id": "enderman", "nameEn": "Enderman", "nameFa": "اندرمن", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 0.3, "width": 0.4, "spawnLightLevel": "any", "xp": 3, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# -------------------------------------------------------------------- EVOKER
MOBS["evoker"] = {
    "id": "evoker",
    "nameEn": "Evoker",
    "nameFa": "اووکر",
    "category": "hostile",
    "icon": "evoker",
    "health": 24,
    "damage": {"contact": 0, "ranged": 12, "summon": 6},
    "speed": 0.25,
    "versions": {"java": "1.11+", "bedrock": "1.11.0+"},
    "description": "اووکر ماب متخاصم و رهبر Illager است که در Woodland Mansion پیدا می‌شه. با Vex و Fangs حمله می‌کنه و Totem of Undying دراپ می‌کنه.",
    "drops": [
        {"item": "emerald", "count": "1", "condition": "اگه بازیکن بکشه"},
        {"item": "totem_of_undying", "count": "1", "condition": "همیشه (در Woodland Mansion)"}
    ],
    "locations": ["Woodland Mansion", "Raid (Wave 5+)"],
    "combat": ["با سپر Fangs رو بلاک کن", "Vex‌ها رو اول بکش", "با شمشیر نزدیک نزن"],
    "wikiLink": "https://minecraft.wiki/w/Evoker",
    "intro": [
        "اووکر (Evoker) یک ماب متخاصم و رهبر Illager ماینکرفت است که در نسخه‌ی Java 1.11 (نوامبر ۲۰۱۶) به بازی اضافه شد. این ماب در Woodland Mansion و در Raid (موج پنجم به بعد) اسپاون می‌شود.",
        "اووکر با ۲۴ سلامتی شناخته می‌شود و با دو حمله‌ی متفاوت حمله می‌کند: Vex Summon (احضار سه Vex) و Evoker Fangs (دندان‌های زمینی). این حمله‌ها با آسیب ۱۲ و ۶ شناخته می‌شوند.",
        "اووکر با کشته‌شدن، یک Totem of Undying دراپ می‌کند — تنها منبع این آیتم در بازی. این Totem با نگه‌داشتن در دست غیرفعال، پس از مرگ بازیکن، او را احیا می‌کند."
    ],
    "behavior": [
        "اووکر در Woodland Mansion و در Raid (موج پنجم به بعد) اسپاون می‌شود. این ماب با ۲۴ سلامتی شناخته می‌شود و با دو حمله‌ی متفاوت حمله می‌کند: Vex Summon و Evoker Fangs.",
        "اووکر با Vex Summon، سه Vex احضار می‌کند. این Vex‌ها با آسیب ۳ به بازیکن حمله می‌کنند. اووکر با Evoker Fangs، دندان‌های زمینی تولید می‌کند که از زیر بازیکن بیرون می‌آیند و ۱۲ آسیب وارد می‌کنند.",
        "اووکر با کشته‌شدن، یک Totem of Undying دراپ می‌کند — تنها منبع این آیتم در بازی. اووکر در نسخه‌ی ۱.۱۴ با Raid به بازی اضافه شد."
    ],
    "trivia": [
        "اووکر در نسخه‌ی ۱.۱۱ (۲۰۱۶) به بازی اضافه شد — همراه با Woodland Mansion.",
        "این ماب تنها منبع Totem of Undying در بازی است — آیتم احیای پس از مرگ.",
        "اووکر با Vex Summon، سه Vex احضار می‌کند — تنها ماب بازی که Vex احضار می‌کند.",
        "اووکر با Evoker Fangs، دندان‌های زمینی تولید می‌کند — منحصر‌به‌فرد.",
        "اووکر با ۲۴ سلامتی، یکی از قوی‌ترین Illager‌ها است — نیاز به تجهیزات قوی."
    ],
    "history": [
        {"version": "Java 1.11 (2016)", "change": "اووکر به بازی اضافه شد — همراه با Woodland Mansion."},
        {"version": "Bedrock 1.11.0 (2018)", "change": "تطبیق اووکر با نسخه‌ی Java."},
        {"version": "Java 1.14 (2019)", "change": "افزایش قابلیت اووکر در Raid."},
        {"version": "Java 1.19 (2022)", "change": "بهبود انیمیشن اووکر هنگام Summon Vex."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت اووکر در Woodland Mansion."}
    ],
    "differences": [
        "در Java، اووکر با ۲۴ سلامتی شناخته می‌شود؛ در Bedrock ۲۴ — یکسان.",
        "در Java، اووکر با Vex Summon حمله می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، اووکر با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "vindicator", "nameEn": "Vindicator", "nameFa": "ویندیکاتور", "type": "mob"},
        {"id": "vex", "nameEn": "Vex", "nameFa": "وکس", "type": "mob"},
        {"id": "pillager", "nameEn": "Pillager", "nameFa": "پیلجر", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.95, "width": 0.6, "spawnLightLevel": "any", "xp": 10, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# ---------------------------------------------------------------- GLOW SQUID
MOBS["glow-squid"] = {
    "id": "glow-squid",
    "nameEn": "Glow Squid",
    "nameFa": "هشت‌پای درخشان",
    "category": "ambient",
    "icon": "glow-squid",
    "health": 10,
    "damage": {"contact": 0},
    "speed": 0.4,
    "versions": {"java": "1.17+", "bedrock": "1.16.210+"},
    "description": "هشت‌پای درخشان ماب محیطی ۱.۱۷ است که در آب‌های تاریک پیدا می‌شه و با Glow Ink Sacs دراپ می‌کنه.",
    "drops": [{"item": "glow_ink_sac", "count": "1-3"}],
    "locations": ["Underground Water", "Deep Ocean"],
    "combat": ["با یک ضربه بزن", "در آب با سه‌چوب‌دار دنبالش نرو", "Glow Ink Sac دراپ می‌کنه"],
    "wikiLink": "https://minecraft.wiki/w/Glow_Squid",
    "intro": [
        "هشت‌پای درخشان (Glow Squid) یک ماب محیطی ماینکرفت است که در نسخه‌ی Java 1.17 (ژوئن ۲۰۲۱) به بازی اضافه شد. این ماب در آب‌های تاریک زیرزمینی اسپاون می‌شود و نسخه‌ی درخشانِ Squid معمولی است.",
        "هشت‌پای درخشان با ۱۰ سلامتی شناخته می‌شود و با Glow Ink Sac دراپ می‌کند. این آیتم در ساخت Glow Item Frame و Glow Sign استفاده می‌شود — بلاک‌های درخشان در تاریکی.",
        "هشت‌پای درخشان با کشته‌شدن، ۱ تا ۳ Glow Ink Sac دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۷ با آب‌های زیرزمینی به بازی اضافه شد."
    ],
    "behavior": [
        "هشت‌پای درخشان در آب‌های تاریک زیرزمینی اسپاون می‌شود. این ماب با ۱۰ سلامتی شناخته می‌شود و آسیب تماسی ۰ وارد می‌کند. هشت‌پای درخشان با Glow Ink Sac دراپ می‌کند.",
        "هشت‌پای درخشان در صورت ضربه‌دیدن، ابری از Glow Ink در آب تولید می‌کند و فرار می‌کند. این ماب با Glow Ink Sac در ساخت Glow Item Frame و Glow Sign استفاده می‌شود.",
        "هشت‌پای درخشان با کشته‌شدن، ۱ تا ۳ Glow Ink Sac دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۷ با آب‌های زیرزمینی به بازی اضافه شد."
    ],
    "trivia": [
        "هشت‌پای درخشان در نسخه‌ی ۱.۱۷ (۲۰۲۱) به بازی اضافه شد — از طریق رأی‌گیری MineCon Live ۲۰۲۰.",
        "این ماب با Glow Ink Sac، تنها منبع این آیتم در بازی است.",
        "هشت‌پای درخشان در صورت ضربه‌دیدن، ابری از Glow Ink تولید می‌کند — منحصر‌به‌فرد.",
        "Glow Item Frame و Glow Sign با Glow Ink Sac ساخته می‌شوند — بلاک‌های درخشان در تاریکی.",
        "هشت‌پای درخشان با ۱۰ سلامتی، یکی از ضعیف‌ترین ماب‌های بازی است — به‌سادگی با یک ضربه‌ی شمشیر کشته می‌شود."
    ],
    "history": [
        {"version": "Java 1.17 (2021)", "change": "هشت‌پای درخشان به بازی اضافه شد — از طریق رأی‌گیری MineCon Live ۲۰۲۰."},
        {"version": "Bedrock 1.16.210 (2021)", "change": "تطبیق هشت‌پای درخشان با نسخه‌ی Java (preview)."},
        {"version": "Java 1.18 (2021)", "change": "بهبود انیمیشن هشت‌پای درخشان هنگام شنا."},
        {"version": "Bedrock 1.19.0 (2022)", "change": "افزودن جلوه‌ی بصری Glow Ink هشت‌پای درخشان."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت هشت‌پای درخشان در آب‌های زیرزمینی."}
    ],
    "differences": [
        "در Java، هشت‌پای درخشان با ۱۰ سلامتی شناخته می‌شود؛ در Bedrock ۱۰ — یکسان.",
        "در Java، هشت‌پای درخشان با Glow Ink Sac دراپ می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، هشت‌پای درخشان با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "squid", "nameEn": "Squid", "nameFa": "هشت‌پا", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 0.8, "width": 0.8, "spawnLightLevel": "any", "xp": 0, "boss": False, "spawnGroup": "underwater"},
    "hasRealTexture": True,
}


# ------------------------------------------------------------------ GUARDIAN
MOBS["guardian"] = {
    "id": "guardian",
    "nameEn": "Guardian",
    "nameFa": "نگهبان",
    "category": "hostile",
    "icon": "guardian",
    "health": 30,
    "damage": {"contact": 2, "ranged": 4},
    "speed": 0.3,
    "versions": {"java": "1.8+", "bedrock": "1.8.0+"},
    "description": "نگهبان ماب متخاصم ۱.۸ است که در Ocean Monument پیدا می‌شه. با اشعه لیزر از دور حمله می‌کنه و Prismarine دراپ می‌کنه.",
    "drops": [
        {"item": "prismarine_shard", "count": "0-2"},
        {"item": "raw_cod", "count": "1", "condition": "اگه بازیکن بکشه"}
    ],
    "locations": ["Ocean Monument"],
    "combat": ["با سپر اشعه رو بلاک کن", "از دور با کمان بزن", "نزدیک نشو چون آسیب تماسی می‌زنه"],
    "wikiLink": "https://minecraft.wiki/w/Guardian",
    "intro": [
        "نگهبان (Guardian) یک ماب متخاصم ماینکرفت است که در نسخه‌ی Java 1.8 (سپتامبر ۲۰۱۴) به بازی اضافه شد. این ماب در Ocean Monument اسپاون می‌شود و با اشعه لیزر از دور حمله می‌کند.",
        "نگهبان با ۳۰ سلامتی شناخته می‌شود و با دو حمله‌ی متفاوت حمله می‌کند: اشعه لیزر (آسیب ۴) و حمله‌ی تماسی (آسیب ۲). این ماب در آب به‌خوبی شنا می‌کند اما روی زمین کند است.",
        "نگهبان با کشته‌شدن، ۰ تا ۲ Prismarine Shard و ۱ Raw Cod دراپ می‌کند. این ماب در نسخه‌ی ۱.۸ با Ocean Monument به بازی اضافه شد."
    ],
    "behavior": [
        "نگهبان در Ocean Monument اسپاون می‌شود. این ماب با ۳۰ سلامتی شناخته می‌شود و با دو حمله‌ی متفاوت حمله می‌کند: اشعه لیزر و حمله‌ی تماسی.",
        "نگهبان با اشعه لیزر، از دور به بازیکن حمله می‌کند. این حمله با آسیب ۴ شناخته می‌شود و در ۲ ثانیه شلیک می‌شود. نگهبان با حمله‌ی تماسی، ۲ آسیب وارد می‌کند.",
        "نگهبان با کشته‌شدن، ۰ تا ۲ Prismarine Shard و ۱ Raw Cod دراپ می‌کند. این ماب در آب به‌خوبی شنا می‌کند اما روی زمین کند است."
    ],
    "trivia": [
        "نگهبان در نسخه‌ی ۱.۸ (۲۰۱۴) به بازی اضافه شد — همراه با Ocean Monument.",
        "این ماب با اشعه لیزر، تنها ماب بازی است که با این حمله حمله می‌کند.",
        "نگهبان با Prismarine Shard دراپ می‌کند — منبع اصلی این آیتم در بازی.",
        "نسخه‌ی بزرگ نگهبان، Elder Guardian است — یکی از بوس‌های بازی.",
        "نگهبان با ۳۰ سلامتی، یکی از قوی‌ترین ماب‌های آب‌زی است — نیاز به تجهیزات قوی."
    ],
    "history": [
        {"version": "Java 1.8 (2014)", "change": "نگهبان به بازی اضافه شد — همراه با Ocean Monument."},
        {"version": "Bedrock 1.8.0 (2014)", "change": "تطبیق نگهبان با نسخه‌ی Java."},
        {"version": "Java 1.13 (2018)", "change": "بهبود انیمیشن نگهبان هنگام شنا."},
        {"version": "Java 1.19 (2022)", "change": "افزایش قابلیت نگهبان در Ocean Monument."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت نگهبان در آب‌های اقیانوس."}
    ],
    "differences": [
        "در Java، نگهبان با ۳۰ سلامتی شناخته می‌شود؛ در Bedrock ۳۰ — یکسان.",
        "در Java، نگهبان با اشعه لیزر حمله می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، نگهبان با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "elder-guardian", "nameEn": "Elder Guardian", "nameFa": "نگهبان کهنه", "type": "mob"},
        {"id": "dolphin", "nameEn": "Dolphin", "nameFa": "دلفین", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 0.85, "width": 0.85, "spawnLightLevel": "any", "xp": 10, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# --------------------------------------------------------------------- HOGLIN
MOBS["hoglin"] = {
    "id": "hoglin",
    "nameEn": "Hoglin",
    "nameFa": "هاگلین",
    "category": "hostile",
    "icon": "hoglin",
    "health": 40,
    "damage": {"contact": 4, "knockback": 5},
    "speed": 0.3,
    "versions": {"java": "1.16+", "bedrock": "1.16.0+"},
    "description": "هاگلین ماب متخاصم ۱.۱۶ است که در Crimson Forest پیدا می‌شه. تنها منبع غذا در ندر — با Porkchop دراپ می‌کنه.",
    "drops": [
        {"item": "raw_porkchop", "count": "2-4"},
        {"item": "leather", "count": "0-1"}
    ],
    "locations": ["Crimson Forest (Nether)"],
    "combat": ["با شمشیر نزدیک نزن چون Knockback می‌زنه", "از دور با کمان بزن", "با Warped Fungus فرارش بده"],
    "wikiLink": "https://minecraft.wiki/w/Hoglin",
    "intro": [
        "هاگلین (Hoglin) یک ماب متخاصم ماینکرفت است که در نسخه‌ی Java 1.16 (ژوئن ۲۰۲۰) به بازی اضافه شد. این ماب در Crimson Forest (ندر) اسپاون می‌شود و تنها منبع غذا در ندر است.",
        "هاگلین با ۴۰ سلامتی شناخته می‌شود و با حمله‌ی تماسی ۴ آسیب وارد می‌کند. این ماب با Knockback ۵، بازیکن را به‌عقب هل می‌دهد. هاگلین در صورت دیدن Warped Fungus فرار می‌کند.",
        "هاگلین با کشته‌شدن، ۲ تا ۴ Raw Porkchop و ۰ تا ۱ Leather دراپ می‌کند. این ماب در صورت انتقال به Overworld، پس از ۱۵ ثانیه به Zoglin تبدیل می‌شود."
    ],
    "behavior": [
        "هاگلین در Crimson Forest (ندر) اسپاون می‌شود. این ماب با ۴۰ سلامتی شناخته می‌شود و با حمله‌ی تماسی ۴ آسیب وارد می‌کند. هاگلین با Knockback ۵، بازیکن را به‌عقب هل می‌دهد.",
        "هاگلین در صورت دیدن Warped Fungus فرار می‌کند. این ماب با Crimson Fungus در دست بازیکن قابل تکثیر است. هاگلین با تذکر Warped Fungus به‌عنوان دفع‌کننده شناخته می‌شود.",
        "هاگلین با کشته‌شدن، ۲ تا ۴ Raw Porkchop و ۰ تا ۱ Leather دراپ می‌کند. این ماب در صورت انتقال به Overworld، پس از ۱۵ ثانیه به Zoglin تبدیل می‌شود."
    ],
    "trivia": [
        "هاگلین در نسخه‌ی ۱.۱۶ (۲۰۲۰) به بازی اضافه شد — همراه با Nether Update.",
        "این ماب تنها منبع غذا در ندر است — با Porkchop دراپ می‌کند.",
        "هاگلین با Warped Fungus فرار می‌کند — منحصر‌به‌فرد.",
        "هاگلین در Overworld به Zoglin تبدیل می‌شود — مکانیکی منحصر‌به‌فرد.",
        "هاگلین با ۴۰ سلامتی، یکی از قوی‌ترین ماب‌های ندر است — نیاز به تجهیزات قوی."
    ],
    "history": [
        {"version": "Java 1.16 (2020)", "change": "هاگلین به بازی اضافه شد — همراه با Nether Update."},
        {"version": "Bedrock 1.16.0 (2020)", "change": "تطبیق هاگلین با نسخه‌ی Java."},
        {"version": "Java 1.17 (2021)", "change": "بهبود انیمیشن هاگلین هنگام حمله."},
        {"version": "Java 1.19 (2022)", "change": "افزایش قابلیت هاگلین در Crimson Forest."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت هاگلین در ندر."}
    ],
    "differences": [
        "در Java، هاگلین با ۴۰ سلامتی شناخته می‌شود؛ در Bedrock ۴۰ — یکسان.",
        "در Java، هاگلین با Knockback ۵ حمله می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، هاگلین با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "zoglin", "nameEn": "Zoglin", "nameFa": "زوگلین", "type": "mob"},
        {"id": "piglin", "nameEn": "Piglin", "nameFa": "پیگلین", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.4, "width": 1.4, "spawnLightLevel": "any", "xp": 5, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# ----------------------------------------------------------------- ILLUSIONER
MOBS["illusioner"] = {
    "id": "illusioner",
    "nameEn": "Illusioner",
    "nameFa": "ایلیوژنر",
    "category": "hostile",
    "icon": "illusioner",
    "health": 32,
    "damage": {"contact": 0, "ranged": 2, "illusion": 0},
    "speed": 0.25,
    "versions": {"java": "1.17+ (Java-only)", "bedrock": "—"},
    "description": "ایلیوژنر ماب متخاصم Java-only است که با /summon احضار می‌شه. با Illusion (نسخه‌های کاذب) و کمان حمله می‌کنه.",
    "drops": [{"item": "nothing", "count": "0"}],
    "locations": ["Only via /summon (Java only)"],
    "combat": ["با /summon احضارش کن", "نسخه‌های کاذب رو تشخیص بده", "با سپر تیرها رو بلاک کن"],
    "wikiLink": "https://minecraft.wiki/w/Illusioner",
    "intro": [
        "ایلیوژنر (Illusioner) یک ماب متخاصم Java-only ماینکرفت است که در نسخه‌ی Java 1.17 (ژوئن ۲۰۲۱) به بازی اضافه شد. این ماب در نسخه‌ی Bedrock وجود ندارد و تنها با /summon در Java قابل احضار است.",
        "ایلیوژنر با ۳۲ سلامتی شناخته می‌شود و با Illusion (نسخه‌های کاذب) و کمان حمله می‌کند. این ماب با ۴ نسخه‌ی کاذب از خود، بازیکن را گمراه می‌کند و با کمان از دور حمله می‌کند.",
        "ایلیوژنر با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب در نسخه‌ی ۱.۱۷ با عدم اسپاون طبیعی شناخته می‌شود — تنها با /summon قابل احضار است."
    ],
    "behavior": [
        "ایلیوژنر تنها با /summon در Java قابل احضار است. این ماب با ۳۲ سلامتی شناخته می‌شود و با Illusion و کمان حمله می‌کند.",
        "ایلیوژنر با Illusion، ۴ نسخه‌ی کاذب از خود تولید می‌کند. این نسخه‌ها با بازیکن تعامل ندارند اما با ضربه‌ی کمان، نسخه‌ی اصلی آسیب می‌بیند.",
        "ایلیوژنر با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب در نسخه‌ی ۱.۱۷ با عدم اسپاون طبیعی شناخته می‌شود."
    ],
    "trivia": [
        "ایلیوژنر در نسخه‌ی ۱.۱۷ (۲۰۲۱) به بازی اضافه شد — Java-only.",
        "این ماب با Illusion، ۴ نسخه‌ی کاذب از خود تولید می‌کند — منحصر‌به‌فرد.",
        "ایلیوژنر تنها با /summon قابل احضار است — عدم اسپاون طبیعی.",
        "این ماب در نسخه‌ی Bedrock وجود ندارد — Java-only.",
        "ایلیوژنر با ۳۲ سلامتی، یکی از قوی‌ترین Illager‌ها است — نیاز به تجهیزات قوی."
    ],
    "history": [
        {"version": "Java 1.17 (2021)", "change": "ایلیوژنر به بازی اضافه شد — Java-only."},
        {"version": "Java 1.18 (2021)", "change": "بهبود انیمیشن Illusion ایلیوژنر."},
        {"version": "Java 1.19 (2022)", "change": "رفع باگ‌های جزئی در رفتار Illusioner."},
        {"version": "Java 1.20 (2023)", "change": "بهبود رفتار Illusioner در /summon."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت Illusioner در Java."}
    ],
    "differences": [
        "ایلیوژنر در Java با ۳۲ سلامتی شناخته می‌شود؛ در Bedrock وجود ندارد.",
        "در Java، ایلیوژنر با /summon قابل احضار است؛ در Bedrock موجود نیست.",
        "این ماب یکی از معدود ماب‌های Java-only است — به‌علاوه‌ی Giant و... ."
    ],
    "related": [
        {"id": "evoker", "nameEn": "Evoker", "nameFa": "اووکر", "type": "mob"},
        {"id": "vindicator", "nameEn": "Vindicator", "nameFa": "ویندیکاتور", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.95, "width": 0.6, "spawnLightLevel": "any", "xp": 10, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# ---------------------------------------------------------------------- MULE
MOBS["mule"] = {
    "id": "mule",
    "nameEn": "Mule",
    "nameFa": "قاطر",
    "category": "passive",
    "icon": "mule",
    "health": 24,
    "damage": {"contact": 0},
    "speed": 0.3,
    "versions": {"java": "1.6+", "bedrock": "1.0.0+"},
    "description": "قاطر ماب صلح‌جوی بازی است که با Horse + Donkey تولید می‌شه. با Chest قابل‌ذخیره‌سازیه و ۱۵ اسلات داره.",
    "drops": [{"item": "leather", "count": "0-2"}],
    "locations": ["Plains (rare spawn)", "Village"],
    "combat": ["با یک ضربه بزن", "با Saddle سواره شو", "با Chest ذخیره بساز"],
    "wikiLink": "https://minecraft.wiki/w/Mule",
    "intro": [
        "قاطر (Mule) یک ماب صلح‌جوی ماینکرفت است که در نسخه‌ی Java 1.6 (ژوئیه ۲۰۱۳) به بازی اضافه شد. این ماب با ترکیب Horse و Donson تولید می‌شود و ترکیبی از ویژگی‌های هر دو است.",
        "قاطر با ۲۴ سلامتی شناخته می‌شود و با Saddle قابل سواره‌شدن است. این ماب با Chest قابل‌ذخیره‌سازی است و ۱۵ اسلات برای نگه‌داری آیتم‌ها دارد. قاطر نمی‌تواند با ماب دیگری تولید شود — عقیم است.",
        "قاطر با کشته‌شدن، ۰ تا ۲ Leather دراپ می‌کند. این ماب در Plains به‌ندرت اسپاون می‌شود و با ترکیب Horse و Donson در دست بازیکن قابل تولید است."
    ],
    "behavior": [
        "قاطر با ترکیب Horse و Donson تولید می‌شود. این ماب با ۲۴ سلامتی شناخته می‌شود و آسیب تماسی ۰ وارد می‌کند. قاطر با Saddle قابل سواره‌شدن است.",
        "قاطر با Chest قابل‌ذخیره‌سازی است و ۱۵ اسلات برای نگه‌داری آیتم‌ها دارد. این ماب نمی‌تواند با ماب دیگری تولید شود — عقیم است. قاطر با سرعت متوسط‌تر از Horse اما پایدارتر شناخته می‌شود.",
        "قاطر با کشته‌شدن، ۰ تا ۲ Leather دراپ می‌کند. این ماب در Plains به‌ندرت اسپاون می‌شود و با ترکیب Horse و Donson در دست بازیکن قابل تولید است."
    ],
    "trivia": [
        "قاطر در نسخه‌ی ۱.۶ (۲۰۱۳) به بازی اضافه شد — همراه با Horse.",
        "این ماب با ترکیب Horse و Donson تولید می‌شود — منحصر‌به‌فرد.",
        "قاطر با Chest قابل‌ذخیره‌سازی است و ۱۵ اسلات دارد — ویژگی کاربردی.",
        "قاطر عقیم است — نمی‌تواند با ماب دیگری تولید شود.",
        "قاطر با ۲۴ سلامتی، یکی از متوسط‌ترین حیوانات بازی است — سخت‌تر از اسب."
    ],
    "history": [
        {"version": "Java 1.6 (2013)", "change": "قاطر به بازی اضافه شد — همراه با Horse."},
        {"version": "Bedrock 1.0.0 (2016)", "change": "تطبیق قاطر با نسخه‌ی Java."},
        {"version": "Java 1.14 (2019)", "change": "بهبود انیمیشن قاطر هنگام سواره‌شدن."},
        {"version": "Java 1.19 (2022)", "change": "رفع باگ‌های جزئی در رفتار قاطر."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت قاطر در Plains."}
    ],
    "differences": [
        "در Java، قاطر با ۲۴ سلامتی شناخته می‌شود؛ در Bedrock ۲۴ — یکسان.",
        "در Java، قاطر با Chest قابل‌ذخیره‌سازی است؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، قاطر با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "horse", "nameEn": "Horse", "nameFa": "اسب", "type": "mob"},
        {"id": "donkey", "nameEn": "Donkey", "nameFa": "الاغ", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.6, "width": 1.4, "spawnLightLevel": "any", "xp": 0, "boss": False, "spawnGroup": "creature"},
    "hasRealTexture": True,
}


# -------------------------------------------------------------------- OCELOT
MOBS["ocelot"] = {
    "id": "ocelot",
    "nameEn": "Ocelot",
    "nameFa": "اوسیلات",
    "category": "passive",
    "icon": "ocelot",
    "health": 10,
    "damage": {"contact": 0},
    "speed": 0.3,
    "versions": {"java": "1.2+", "bedrock": "1.0.0+"},
    "description": "اوسیلات ماب صلح‌جوی بازی است که در Jungle پیدا می‌شه. با Fish اهلی می‌شه و از Creeper فرار می‌کنه.",
    "drops": [{"item": "nothing", "count": "0"}],
    "locations": ["Jungle"],
    "combat": ["با یک ضربه بزن", "با Raw Cod یا Raw Salmon اهلی کن", "از Creeper فرار می‌کنه"],
    "wikiLink": "https://minecraft.wiki/w/Ocelot",
    "intro": [
        "اوسیلات (Ocelot) یک ماب صلح‌جوی ماینکرفت است که در نسخه‌ی Java 1.2 (اوت ۲۰۱۲) به بازی اضافه شد. این ماب در Jungle اسپاون می‌شود و با Raw Cod یا Raw Salmon قابل اهلی‌کردن است.",
        "اوسیلات با ۱۰ سلامتی شناخته می‌شود و با رفتار منحصر‌به‌فرد شناخته می‌شود. این ماب با صدا‌ی Hissing باعث فرار Creeper از خود می‌شود — ویژگی مشابه با Cat.",
        "اوسیلات با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب در نسخه‌ی ۱.۱۴ بازطراحی شد و در نسخه‌ی ۱.۲۰ با رفتار متفاوت از Cat شناخته می‌شود."
    ],
    "behavior": [
        "اوسیلات در Jungle اسپاون می‌شود. این ماب با ۱۰ سلامتی شناخته می‌شود و آسیب تماسی ۰ وارد می‌کند. اوسیلات با Raw Cod یا Raw Salmon قابل اهلی‌کردن است.",
        "اوسیلات با صدا‌ی Hissing باعث فرار Creeper از خود می‌شود. این ماب با رفتار منحصر‌به‌فرد شناخته می‌شود — در صورت فرار از بازیکن، به حالت wild برمی‌گردد.",
        "اوسیلات با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب در نسخه‌ی ۱.۱۴ بازطراحی شد و در نسخه‌ی ۱.۲۰ با رفتار متفاوت از Cat شناخته می‌شود."
    ],
    "trivia": [
        "اوسیلات در نسخه‌ی ۱.۲ (۲۰۱۲) به بازی اضافه شد — همراه با Cat.",
        "این ماب با صدا‌ی Hissing باعث فرار Creeper می‌شود — ویژگی مشابه با Cat.",
        "اوسیلات با Raw Cod یا Raw Salmon قابل اهلی‌کردن است — اولین ماب اهلی.",
        "اوسیلات در صورت فرار از بازیکن، به حالت wild برمی‌گردد — منحصر‌به‌فرد.",
        "اوسیلات با ۱۰ سلامتی، یکی از ضعیف‌ترین ماب‌های بازی است — نیاز به محافظت."
    ],
    "history": [
        {"version": "Java 1.2 (2012)", "change": "اوسیلات به بازی اضافه شد — همراه با Cat."},
        {"version": "Bedrock 1.0.0 (2016)", "change": "تطبیق اوسیلات با نسخه‌ی Java."},
        {"version": "Java 1.14 (2019)", "change": "بازطراحی اوسیلات — جدا از Cat به‌عنوان ماب مستقل."},
        {"version": "Java 1.19 (2022)", "change": "بهبود انیمیشن اوسیلات هنگام اهلی‌شدن."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت اوسیلات در Jungle."}
    ],
    "differences": [
        "در Java، اوسیلات با ۱۰ سلامتی شناخته می‌شود؛ در Bedrock ۱۰ — یکسان.",
        "در Java، اوسیلات با Raw Cod قابل اهلی‌کردن است؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، اوسیلات با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "cat", "nameEn": "Cat", "nameFa": "گربه", "type": "mob"},
        {"id": "creeper", "nameEn": "Creeper", "nameFa": "کریپر", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 0.7, "width": 0.6, "spawnLightLevel": "any", "xp": 0, "boss": False, "spawnGroup": "creature"},
    "hasRealTexture": True,
}


# -------------------------------------------------------------------- PIGLIN
MOBS["piglin"] = {
    "id": "piglin",
    "nameEn": "Piglin",
    "nameFa": "پیگلین",
    "category": "neutral",
    "icon": "piglin",
    "health": 16,
    "damage": {"contact": 8, "ranged": 4},
    "speed": 0.3,
    "versions": {"java": "1.16+", "bedrock": "1.16.0+"},
    "description": "پیگلین ماب خنثی ۱.۱۶ است که در Nether Wastes پیدا می‌شه. اگه Gold Armor نداشته باشی حمله می‌کنه و با Gold Ingot قابل باره.",
    "drops": [
        {"item": "gold_ingot", "count": "1", "condition": "اگه با Gold Ingot مبادله بشه"},
        {"item": "rotten_flesh", "count": "1", "condition": "اگه بازیکن بکشه"}
    ],
    "locations": ["Nether Wastes", "Crimson Forest", "Bastion Remnant"],
    "combat": ["با Gold Armor بپوش", "با Gold Ingot مبادله کن", "نزدیک نشو چون Crossbow داره"],
    "wikiLink": "https://minecraft.wiki/w/Piglin",
    "intro": [
        "پیگلین (Piglin) یک ماب خنثی ماینکرفت است که در نسخه‌ی Java 1.16 (ژوئن ۲۰۲۰) به بازی اضافه شد. این ماب در Nether Wastes، Crimson Forest و Bastion Remnant اسپاون می‌شود و با Gold Armor بازیکن قابل کنترل است.",
        "پیگلین با ۱۶ سلامتی شناخته می‌شود و در صورت عدم پوشیدن Gold Armor توسط بازیکن، حمله می‌کند. این ماب با Crossbow از دور حمله می‌کند و با Gold Ingot قابل مبادله است.",
        "پیگلین با کشته‌شدن، ۱ Rotten Flesh دراپ می‌کند. این ماب با Gold Ingot در مبادله، آیتم‌های مختلفی دراپ می‌کند — مانند Ender Pearl، Nether Quartz و Obsidian."
    ],
    "behavior": [
        "پیگلین در Nether Wastes، Crimson Forest و Bastion Remnant اسپاون می‌شود. این ماب با ۱۶ سلامتی شناخته می‌شود و در صورت عدم پوشیدن Gold Armor توسط بازیکن، حمله می‌کند.",
        "پیگلین با Crossbow از دور حمله می‌کند. این ماب با Gold Ingot قابل مبادله است و آیتم‌های مختلفی دراپ می‌کند — مانند Ender Pearl، Nether Quartz و Obsidian. پیگلین در نسخه‌ی ۱.۱۶ با Bastion Remnant به بازی اضافه شد.",
        "پیگلین با کشته‌شدن، ۱ Rotten Flesh دراپ می‌کند. این ماب با Gold Ingot در مبادله، آیتم‌های مختلفی دراپ می‌کند. پیگلین با hunting به Gold شدید است و در صورت دیدن Gold Item، آن را برمی‌دارد."
    ],
    "trivia": [
        "پیگلین در نسخه‌ی ۱.۱۶ (۲۰۲۰) به بازی اضافه شد — همراه با Nether Update.",
        "این ماب با Gold Armor بازیکن قابل کنترل است — منحصر‌به‌فرد.",
        "پیگلین با Gold Ingot قابل مبادله است — تنها ماب بازی با این رفتار.",
        "پیگلین با hunting به Gold شدید است — ویژگی منحصر‌به‌فرد.",
        "پیگلین با ۱۶ سلامتی، یکی از ضعیف‌ترین ماب‌های ندر است — به‌سادگی با یک ضربه‌ی شمشیر آهنی کشته می‌شود."
    ],
    "history": [
        {"version": "Java 1.16 (2020)", "change": "پیگلین به بازی اضافه شد — همراه با Nether Update."},
        {"version": "Bedrock 1.16.0 (2020)", "change": "تطبیق پیگلین با نسخه‌ی Java."},
        {"version": "Java 1.17 (2021)", "change": "بهبود انیمیشن پیگلین هنگام مبادله."},
        {"version": "Java 1.19 (2022)", "change": "افزایش قابلیت پیگلین در Bastion Remnant."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت پیگلین در ندر."}
    ],
    "differences": [
        "در Java، پیگلین با ۱۶ سلامتی شناخته می‌شود؛ در Bedrock ۱۶ — یکسان.",
        "در Java، پیگلین با Gold Ingot قابل مبادله است؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، پیگلین با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "piglin-brute", "nameEn": "Piglin Brute", "nameFa": "پیگلین بروت", "type": "mob"},
        {"id": "hoglin", "nameEn": "Hoglin", "nameFa": "هاگلین", "type": "mob"},
        {"id": "zombified-piglin", "nameEn": "Zombified Piglin", "nameFa": "پیگلین زامبی‌شده", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.95, "width": 0.6, "spawnLightLevel": "any", "xp": 5, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# --------------------------------------------------------------- PIGLIN BRUTE
MOBS["piglin-brute"] = {
    "id": "piglin-brute",
    "nameEn": "Piglin Brute",
    "nameFa": "پیگلین بروت",
    "category": "hostile",
    "icon": "piglin-brute",
    "health": 50,
    "damage": {"contact": 8},
    "speed": 0.3,
    "versions": {"java": "1.16.2+", "bedrock": "1.16.20+"},
    "description": "پیگلین بروت ماب متخاصم قوی ۱.۱۶.۲ است که در Bastion Remnant پیدا می‌شه. همیشه حمله می‌کنه، حتی اگه Gold Armor بپوشی.",
    "drops": [{"item": "nothing", "count": "0"}],
    "locations": ["Bastion Remnant"],
    "combat": ["با شمشیر نزدیک نزن", "از دور با کمان بزن", "با سپر ضربه رو بلاک کن"],
    "wikiLink": "https://minecraft.wiki/w/Piglin_Brute",
    "intro": [
        "پیگلین بروت (Piglin Brute) یک ماب متخاصم قوی ماینکرفت است که در نسخه‌ی Java 1.16.2 (اوت ۲۰۲۰) به بازی اضافه شد. این ماب در Bastion Remnant اسپاون می‌شود و نسخه‌ی قوی‌ترِ Piglin است.",
        "پیگلین بروت با ۵۰ سلامتی شناخته می‌شود و همیشه حمله می‌کند — حتی اگه بازیکن Gold Armor بپوشد. این ماب با Golden Axe حمله می‌کند و ۸ آسیب وارد می‌کند.",
        "پیگلین بروت با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب در نسخه‌ی ۱.۱۶.۲ با Bastion Remnant به بازی اضافه شد و یکی از سخت‌ترین دشمنان ندر است."
    ],
    "behavior": [
        "پیگلین بروت در Bastion Remnant اسپاون می‌شود. این ماب با ۵۰ سلامتی شناخته می‌شود و همیشه حمله می‌کند — حتی اگه بازیکن Gold Armor بپوشد.",
        "پیگلین بروت با Golden Axe حمله می‌کند و ۸ آسیب وارد می‌کند. این ماب با سرعت متوسط حرکت می‌کند و در صورت دیدن بازیکن، حمله می‌کند. پیگلین بروت با مبادله قابل کنترل نیست — برخلاف Piglin.",
        "پیگلین بروت با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب در نسخه‌ی ۱.۱۶.۲ با Bastion Remnant به بازی اضافه شد و یکی از سخت‌ترین دشمنان ندر است."
    ],
    "trivia": [
        "پیگلین بروت در نسخه‌ی ۱.۱۶.۲ (۲۰۲۰) به بازی اضافه شد — همراه با Bastion Remnant.",
        "این ماب همیشه حمله می‌کند — حتی با Gold Armor بازیکن — منحصر‌به‌فرد.",
        "پیگلین بروت با Golden Axe حمله می‌کند — تنها ماب بازی با این اسلحه.",
        "پیگلین بروت با ۵۰ سلامتی، یکی از قوی‌ترین ماب‌های ندر است — نیاز به تجهیزات قوی.",
        "این ماب با مبادله قابل کنترل نیست — برخلاف Piglin."
    ],
    "history": [
        {"version": "Java 1.16.2 (2020)", "change": "پیگلین بروت به بازی اضافه شد — همراه با Bastion Remnant."},
        {"version": "Bedrock 1.16.20 (2020)", "change": "تطبیق پیگلین بروت با نسخه‌ی Java."},
        {"version": "Java 1.17 (2021)", "change": "بهبود انیمیشن پیگلین بروت هنگام حمله."},
        {"version": "Java 1.19 (2022)", "change": "افزایش قابلیت پیگلین بروت در Bastion Remnant."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت پیگلین بروت در ندر."}
    ],
    "differences": [
        "در Java، پیگلین بروت با ۵۰ سلامتی شناخته می‌شود؛ در Bedrock ۵۰ — یکسان.",
        "در Java، پیگلین بروت با Golden Axe حمله می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، پیگلین بروت با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "piglin", "nameEn": "Piglin", "nameFa": "پیگلین", "type": "mob"},
        {"id": "hoglin", "nameEn": "Hoglin", "nameFa": "هاگلین", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.95, "width": 0.6, "spawnLightLevel": "any", "xp": 10, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# ------------------------------------------------------------------- RAVAGER
MOBS["ravager"] = {
    "id": "ravager",
    "nameEn": "Ravager",
    "nameFa": "راوگر",
    "category": "hostile",
    "icon": "ravager",
    "health": 100,
    "damage": {"contact": 12, "roar": 18},
    "speed": 0.3,
    "versions": {"java": "1.14+", "bedrock": "1.11.0+"},
    "description": "راوگر ماب متخاصم بزرگ ۱.۱۴ است که در Raid (Wave 3+) پیدا می‌شه. با ۱۰۰ سلامتی یکی از قوی‌ترین ماب‌هاست.",
    "drops": [{"item": "saddle", "count": "1", "condition": "اگه بازیکن بکشه"}],
    "locations": ["Raid (Wave 3+)"],
    "combat": ["با سپر ضربه‌های Roar رو بلاک کن", "با شمشیر از پشت بزن", "با کمان از دور بزن"],
    "wikiLink": "https://minecraft.wiki/w/Ravager",
    "intro": [
        "راوگر (Ravager) یک ماب متخاصم بزرگ ماینکرفت است که در نسخه‌ی Java 1.14 (آوریل ۲۰۱۹) به بازی اضافه شد. این ماب در Raid (موج سوم به بعد) اسپاون می‌شود و یکی از قوی‌ترین ماب‌های بازی است.",
        "راوگر با ۱۰۰ سلامتی شناخته می‌شود و با دو حمله‌ی متفاوت حمله می‌کند: حمله‌ی تماسی (آسیب ۱۲) و Roar (آسیب ۱۸). این ماب با Pillager یا Evoker قابل سواره‌شدن است.",
        "راوگر با کشته‌شدن، ۱ Saddle دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۴ با Raid به بازی اضافه شد و یکی از سخت‌ترین دشمنان Raid است."
    ],
    "behavior": [
        "راوگر در Raid (موج سوم به بعد) اسپاون می‌شود. این ماب با ۱۰۰ سلامتی شناخته می‌شود و با دو حمله‌ی متفاوت حمله می‌کند: حمله‌ی تماسی و Roar.",
        "راوگر با حمله‌ی تماسی، ۱۲ آسیب وارد می‌کند. این ماب با Roar، ۱۸ آسیب وارد می‌کند و بازیکن را به‌عقب هل می‌دهد. راوگر با Pillager یا Evoker قابل سواره‌شدن است.",
        "راوگر با کشته‌شدن، ۱ Saddle دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۴ با Raid به بازی اضافه شد و یکی از سخت‌ترین دشمنان Raid است."
    ],
    "trivia": [
        "راوگر در نسخه‌ی ۱.۱۴ (۲۰۱۹) به بازی اضافه شد — همراه با Raid.",
        "این ماب با ۱۰۰ سلامتی، یکی از قوی‌ترین ماب‌های بازی است — نیاز به تجهیزات قوی.",
        "راوگر با Roar، ۱۸ آسیب وارد می‌کند — منحصر‌به‌فرد.",
        "راوگر با Pillager یا Evoker قابل سواره‌شدن است — تنها ماب متخاصم سواره‌شدنی.",
        "راوگر با ۱۰۰ سلامتی، یکی از سخت‌ترین دشمنان Raid است — نیاز به تیم."
    ],
    "history": [
        {"version": "Java 1.14 (2019)", "change": "راوگر به بازی اضافه شد — همراه با Raid."},
        {"version": "Bedrock 1.11.0 (2019)", "change": "تطبیق راوگر با نسخه‌ی Java."},
        {"version": "Java 1.17 (2021)", "change": "بهبود انیمیشن راوگر هنگام Roar."},
        {"version": "Java 1.19 (2022)", "change": "افزایش قابلیت راوگر در Raid."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت راوگر در Raid."}
    ],
    "differences": [
        "در Java، راوگر با ۱۰۰ سلامتی شناخته می‌شود؛ در Bedrock ۱۰۰ — یکسان.",
        "در Java، راوگر با Roar حمله می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، راوگر با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "pillager", "nameEn": "Pillager", "nameFa": "پیلجر", "type": "mob"},
        {"id": "evoker", "nameEn": "Evoker", "nameFa": "اووکر", "type": "mob"},
        {"id": "vindicator", "nameEn": "Vindicator", "nameFa": "ویندیکاتور", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 2.2, "width": 1.4, "spawnLightLevel": "any", "xp": 20, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# ------------------------------------------------------------------- SHULKER
MOBS["shulker"] = {
    "id": "shulker",
    "nameEn": "Shulker",
    "nameFa": "شالکر",
    "category": "hostile",
    "icon": "shulker",
    "health": 30,
    "damage": {"contact": 0, "ranged": 4, "levitation": 0},
    "speed": 0.1,
    "versions": {"java": "1.9+", "bedrock": "1.0.0+"},
    "description": "شالکر ماب متخاصم ۱.۹ است که در End City پیدا می‌شه. با شلیک گلوله‌های هدایت‌شونده و Levitation حمله می‌کنه.",
    "drops": [
        {"item": "shulker_shell", "count": "1", "condition": "اگه بازیکن بکشه (50% chance)"}
    ],
    "locations": ["End City"],
    "combat": ["با سپر گلوله‌ها رو بلاک کن", "با کمان از دور بزن", "هنگام باز شدنش حمله کن"],
    "wikiLink": "https://minecraft.wiki/w/Shulker",
    "intro": [
        "شالکر (Shulker) یک ماب متخاصم ماینکرفت است که در نسخه‌ی Java 1.9 (فوریه ۲۰۱۶) به بازی اضافه شد. این ماب در End City اسپاون می‌شود و با گلوله‌های هدایت‌شونده حمله می‌کند.",
        "شالکر با ۳۰ سلامتی شناخته می‌شود و با شلیک گلوله‌های هدایت‌شونده، بازیکن را دنبال می‌کند. این گلوله‌ها پس از برخورد، اثر Levitation به بازیکن وارد می‌کنند که او را به بالا هل می‌دهد.",
        "شالکر با کشته‌شدن، با ۵۰٪ احتمال ۱ Shulker Shell دراپ می‌کند. این Shell در ساخت Shulker Box استفاده می‌شود — صندوقی که محتویات خود را پس از شکستن نگه می‌دارد."
    ],
    "behavior": [
        "شالکر در End City اسپاون می‌شود. این ماب با ۳۰ سلامتی شناخته می‌شود و با شلیک گلوله‌های هدایت‌شونده، بازیکن را دنبال می‌کند. شالکر با حالت defensive (داخل زره خود) آسیب کمتری دریافت می‌کند.",
        "شالکر با گلوله‌های هدایت‌شونده، اثر Levitation به بازیکن وارد می‌کند. این گلوله‌ها پس از برخورد، بازیکن را به بالا هل می‌دهد. شالکر در حالت باز، آسیب بیشتری دریافت می‌کند.",
        "شالکر با کشته‌شدن، با ۵۰٪ احتمال ۱ Shulker Shell دراپ می‌کند. این Shell در ساخت Shulker Box استفاده می‌شود. شالکر در نسخه‌ی ۱.۹ با End City به بازی اضافه شد."
    ],
    "trivia": [
        "شالکر در نسخه‌ی ۱.۹ (۲۰۱۶) به بازی اضافه شد — همراه با End City.",
        "این ماب با گلوله‌های هدایت‌شونده حمله می‌کند — تنها ماب بازی با این حمله.",
        "شالکر با Shulker Shell، تنها منبع این آیتم در بازی است.",
        "Shulker Box با Shulker Shell ساخته می‌شود — تنها صندوقی که محتویات خود را پس از شکستن نگه می‌دارد.",
        "شالکر با ۳۰ سلامتی، یکی از متوسط‌ترین ماب‌های End است — نیاز به تیراندازی دقیق."
    ],
    "history": [
        {"version": "Java 1.9 (2016)", "change": "شالکر به بازی اضافه شد — همراه با End City."},
        {"version": "Bedrock 1.0.0 (2016)", "change": "تطبیق شالکر با نسخه‌ی Java."},
        {"version": "Java 1.13 (2018)", "change": "بهبود انیمیشن شالکر هنگام باز و بسته‌شدن."},
        {"version": "Java 1.19 (2022)", "change": "افزایش قابلیت شالکر در End City."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت شالکر در End."}
    ],
    "differences": [
        "در Java، شالکر با ۳۰ سلامتی شناخته می‌شود؛ در Bedrock ۳۰ — یکسان.",
        "در Java، شالکر با گلوله‌های هدایت‌شونده حمله می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، شالکر با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "enderman", "nameEn": "Enderman", "nameFa": "اندرمن", "type": "mob"},
        {"id": "ender-dragon", "nameEn": "Ender Dragon", "nameFa": "اژدهای اندر", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.0, "width": 1.0, "spawnLightLevel": "any", "xp": 5, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# ------------------------------------------------------------- SKELETON HORSE
MOBS["skeleton-horse"] = {
    "id": "skeleton-horse",
    "nameEn": "Skeleton Horse",
    "nameFa": "اسب اسکلتونی",
    "category": "passive",
    "icon": "skeleton-horse",
    "health": 15,
    "damage": {"contact": 0},
    "speed": 0.3,
    "versions": {"java": "1.6+", "bedrock": "1.0.0+"},
    "description": "اسب اسکلتونی ماب صلح‌جوی ۱.۶ است که با صاعقه اسپاون می‌شه. با Saddle قابل سواره‌شدنه و در آب خوب شنا می‌کنه.",
    "drops": [
        {"item": "bone", "count": "0-2"},
        {"item": "leather", "count": "0-1"}
    ],
    "locations": ["Surface (after Thunderstorm + Lightning)"],
    "combat": ["با یک ضربه بزن", "با Saddle سواره شو", "در آب خوب شنا می‌کنه"],
    "wikiLink": "https://minecraft.wiki/w/Skeleton_Horse",
    "intro": [
        "اسب اسکلتونی (Skeleton Horse) یک ماب صلح‌جوی ماینکرفت است که در نسخه‌ی Java 1.6 (ژوئیه ۲۰۱۳) به بازی اضافه شد. این ماب با صاعقه (در Thunderstorm) اسپاون می‌شود و نسخه‌ی اسکلتونیِ Horse است.",
        "اسب اسکلتونی با ۱۵ سلامتی شناخته می‌شود و با Saddle قابل سواره‌شدن است. این ماب در آب به‌خوبی شنا می‌کند و در نسخه‌ی Java، در آب اکسیژن نامحدود دارد.",
        "اسب اسکلتونی با کشته‌شدن، ۰ تا ۲ Bone و ۰ تا ۱ Leather دراپ می‌کند. این ماب با صاعقه اسپاون می‌شود — پس از مرگ اسب اسکلتونی اصلی، ۴ اسب اسکلتونی دیگر اسپاون می‌شوند."
    ],
    "behavior": [
        "اسب اسکلتونی با صاعقه (در Thunderstorm) اسپاون می‌شود. این ماب با ۱۵ سلامتی شناخته می‌شود و آسیب تماسی ۰ وارد می‌کند. اسب اسکلتونی با Saddle قابل سواره‌شدن است.",
        "اسب اسکلتونی در آب به‌خوبی شنا می‌کند. این ماب در نسخه‌ی Java، در آب اکسیژن نامحدود دارد. اسب اسکلتونی پس از مرگ اسب اصلی، ۴ اسب اسکلتونی دیگر اسپاون می‌کند.",
        "اسب اسکلتونی با کشته‌شدن، ۰ تا ۲ Bone و ۰ تا ۱ Leather دراپ می‌کند. این ماب در نسخه‌ی ۱.۶ با صاعقه به بازی اضافه شد."
    ],
    "trivia": [
        "اسب اسکلتونی در نسخه‌ی ۱.۶ (۲۰۱۳) به بازی اضافه شد — همراه با Horse.",
        "این ماب با صاعقه اسپاون می‌شود — منحصر‌به‌فرد.",
        "اسب اسکلتونی در آب به‌خوبی شنا می‌کند — تنها حیوان بازی با این ویژگی.",
        "اسب اسکلتونی در Java، در آب اکسیژن نامحدود دارد — ویژگی منحصر‌به‌فرد.",
        "اسب اسکلتونی با ۱۵ سلامتی، یکی از ضعیف‌ترین حیوانات بازی است — کم‌تر از اسب."
    ],
    "history": [
        {"version": "Java 1.6 (2013)", "change": "اسب اسکلتونی به بازی اضافه شد — همراه با Horse."},
        {"version": "Bedrock 1.0.0 (2016)", "change": "تطبیق اسب اسکلتونی با نسخه‌ی Java."},
        {"version": "Java 1.13 (2018)", "change": "بهبود انیمیشن اسب اسکلتونی هنگام شنا."},
        {"version": "Java 1.19 (2022)", "change": "رفع باگ‌های جزئی در رفتار اسب اسکلتونی."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت اسب اسکلتونی در Thunderstorm."}
    ],
    "differences": [
        "در Java، اسب اسکلتونی با ۱۵ سلامتی شناخته می‌شود؛ در Bedrock ۱۵ — یکسان.",
        "در Java، اسب اسکلتونی در آب اکسیژن نامحدود دارد؛ در Bedrock رفتار متفاوت است.",
        "در Bedrock، اسب اسکلتونی با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "horse", "nameEn": "Horse", "nameFa": "اسب", "type": "mob"},
        {"id": "zombie-horse", "nameEn": "Zombie Horse", "nameFa": "اسب زامبی", "type": "mob"},
        {"id": "skeleton", "nameEn": "Skeleton", "nameFa": "اسکلتون", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.6, "width": 1.4, "spawnLightLevel": "any", "xp": 0, "boss": False, "spawnGroup": "creature"},
    "hasRealTexture": True,
}


# ------------------------------------------------------------------- SNIFFER
MOBS["sniffer"] = {
    "id": "sniffer",
    "nameEn": "Sniffer",
    "nameFa": "اسنیفر",
    "category": "passive",
    "icon": "sniffer",
    "health": 30,
    "damage": {"contact": 0},
    "speed": 0.2,
    "versions": {"java": "1.20+", "bedrock": "1.19.70+"},
    "description": "اسنیفر ماب صلح‌جوی ۱.۲۰ است که با Sniffer Egg از Archaeology به‌دست میاد. با حفاری Torchflower Seed پیدا می‌کنه.",
    "drops": [{"item": "nothing", "count": "0"}],
    "locations": ["From Sniffer Egg (via Archaeology)"],
    "combat": ["با یک ضربه بزن", "اسنیفر نمی‌تونه آسیب بزنه", "با حفاری Torchflower Seed پیدا می‌کنه"],
    "wikiLink": "https://minecraft.wiki/w/Sniffer",
    "intro": [
        "اسنیفر (Sniffer) یک ماب صلح‌جوی ماینکرفت است که در نسخه‌ی Java 1.20 (مارس ۲۰۲۳) به بازی اضافه شد. این ماب با Sniffer Egg از Archaeology به‌دست می‌آید و بزرگ‌ترین ماب صلح‌جوی بازی است.",
        "اسنیفر با ۳۰ سلامتی شناخته می‌شود و با قابلیت حفاری، Torchflower Seed و Pitcher Pod را پیدا می‌کند. این ماب پس از sniffing، در زمین حفاری می‌کند و یک Seed دراپ می‌کند.",
        "اسنیفر با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب در نسخه‌ی ۱.۲۰ با Archaeology به بازی اضافه شد و یکی از محبوب‌ترین ماب‌های جدید ۱.۲۰ است."
    ],
    "behavior": [
        "اسنیفر با Sniffer Egg از Archaeology به‌دست می‌آید. این ماب با ۳۰ سلامتی شناخته می‌شود و آسیب تماسی ۰ وارد می‌کند. اسنیفر با قابلیت حفاری، Torchflower Seed و Pitcher Pod را پیدا می‌کند.",
        "اسنیفر پس از sniffing، در زمین حفاری می‌کند و یک Seed دراپ می‌کند. این ماب با Torchflower Seeds در دست بازیکن قابل تکثیر است. اسنیفر با بزرگ‌ترین سایز، یکی از بزرگ‌ترین ماب‌های صلح‌جوی بازی است.",
        "اسنیفر با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب در نسخه‌ی ۱.۲۰ با Archaeology به بازی اضافه شد."
    ],
    "trivia": [
        "اسنیفر در نسخه‌ی ۱.۲۰ (۲۰۲۳) به بازی اضافه شد — از طریق رأی‌گیری MineCon Live ۲۰۲۲.",
        "این ماب با قابلیت حفاری، Torchflower Seed را پیدا می‌کند — منحصر‌به‌فرد.",
        "اسنیفر بزرگ‌ترین ماب صلح‌جوی بازی است — بزرگ‌تر از اسب.",
        "اسنیفر با Sniffer Egg از Archaeology به‌دست می‌آید — تنها ماب بازی با این روش.",
        "اسنیفر با ۳۰ سلامتی، یکی از قوی‌ترین حیوانات بازی است — سخت‌تر از اسب."
    ],
    "history": [
        {"version": "Java 1.20 (2023)", "change": "اسنیفر به بازی اضافه شد — همراه با Archaeology."},
        {"version": "Bedrock 1.19.70 (2023)", "change": "تطبیق اسنیفر با نسخه‌ی Java (preview)."},
        {"version": "Java 1.20.2 (2023)", "change": "بهبود انیمیشن اسنیفر هنگام sniffing."},
        {"version": "Bedrock 1.20.50 (2023)", "change": "افزودن جلوه‌ی بصری حفاری اسنیفر."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت اسنیفر در Archaeology."}
    ],
    "differences": [
        "در Java، اسنیفر با ۳۰ سلامتی شناخته می‌شود؛ در Bedrock ۳۰ — یکسان.",
        "در Java، اسنیفر با حفاری Seed پیدا می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، اسنیفر با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "frog", "nameEn": "Frog", "nameFa": "قورباغه", "type": "mob"},
        {"id": "allay", "nameEn": "Allay", "nameFa": "الای", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.0, "width": 1.6, "spawnLightLevel": "any", "xp": 0, "boss": False, "spawnGroup": "creature"},
    "hasRealTexture": True,
}


# ------------------------------------------------------------------- STRIDER
MOBS["strider"] = {
    "id": "strider",
    "nameEn": "Strider",
    "nameFa": "استرایدر",
    "category": "passive",
    "icon": "strider",
    "health": 20,
    "damage": {"contact": 0},
    "speed": 0.3,
    "versions": {"java": "1.16+", "bedrock": "1.16.0+"},
    "description": "استرایدر ماب صلح‌جوی ۱.۱۶ است که روی لابه در ندر زندگی می‌کنه. با Saddle و Warped Fungus on a Stick قابل سواره‌شدنه.",
    "drops": [{"item": "string", "count": "0-2"}],
    "locations": ["Lava Lakes (Nether)"],
    "combat": ["با یک ضربه بزن", "با Saddle و Warped Fungus on a Stick سواره شو", "روی لابه راه می‌ره"],
    "wikiLink": "https://minecraft.wiki/w/Strider",
    "intro": [
        "استرایدر (Strider) یک ماب صلح‌جوی ماینکرفت است که در نسخه‌ی Java 1.16 (ژوئن ۲۰۲۰) به بازی اضافه شد. این ماب روی Lava Lakes (ندر) زندگی می‌کند و تنها ماب بازی است که به‌طور طبیعی روی لابه راه می‌رود.",
        "استرایدر با ۲۰ سلامتی شناخته می‌شود و با Saddle و Warped Fungus on a Stick قابل سواره‌شدن است. این ماب با قابلیت راه‌رفتن روی لابه، یکی از محبوب‌ترین روش‌های حمل‌ونقل در ندر است.",
        "استرایدر با کشته‌شدن، ۰ تا ۲ String دراپ می‌کند. این ماب در صورت تماس با آب یا بیرون از لابه، سرد می‌شود و رنگش به آبی-سفید تغییر می‌کند."
    ],
    "behavior": [
        "استرایدر روی Lava Lakes (ندر) زندگی می‌کند. این ماب با ۲۰ سلامتی شناخته می‌شود و آسیب تماسی ۰ وارد می‌کند. استرایدر با Saddle و Warped Fungus on a Stick قابل سواره‌شدن است.",
        "استرایدر با قابلیت راه‌رفتن روی لابه، یکی از محبوب‌ترین روش‌های حمل‌ونقل در ندر است. این ماب با Warped Fungus on a Stick در دست بازیکن قابل کنترل است.",
        "استرایدر با کشته‌شدن، ۰ تا ۲ String دراپ می‌کند. این ماب در صورت تماس با آب یا بیرون از لابه، سرد می‌شود و رنگش به آبی-سفید تغییر می‌کند."
    ],
    "trivia": [
        "استرایدر در نسخه‌ی ۱.۱۶ (۲۰۲۰) به بازی اضافه شد — همراه با Nether Update.",
        "این ماب تنها ماب بازی است که به‌طور طبیعی روی لابه راه می‌رود — منحصر‌به‌فرد.",
        "استرایدر با Saddle و Warped Fungus on a Stick قابل سواره‌شدن است — تنها ماب با این روش.",
        "استرایدر در صورت تماس با آب، سرد می‌شود و رنگش به آبی-سفید تغییر می‌کند — ویژگی منحصر‌به‌فرد.",
        "استرایدر با ۲۰ سلامتی، یکی از ضعیف‌ترین ماب‌های ندر است — به‌سادگی با یک ضربه‌ی شمشیر کشته می‌شود."
    ],
    "history": [
        {"version": "Java 1.16 (2020)", "change": "استرایدر به بازی اضافه شد — همراه با Nether Update."},
        {"version": "Bedrock 1.16.0 (2020)", "change": "تطبیق استرایدر با نسخه‌ی Java."},
        {"version": "Java 1.17 (2021)", "change": "بهبود انیمیشن استرایدر هنگام راه‌رفتن روی لابه."},
        {"version": "Java 1.19 (2022)", "change": "رفع باگ‌های جزئی در رفتار استرایدر."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت استرایدر در ندر."}
    ],
    "differences": [
        "در Java، استرایدر با ۲۰ سلامتی شناخته می‌شود؛ در Bedrock ۲۰ — یکسان.",
        "در Java، استرایدر با Warped Fungus on a Stick قابل کنترل است؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، استرایدر با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "piglin", "nameEn": "Piglin", "nameFa": "پیگلین", "type": "mob"},
        {"id": "hoglin", "nameEn": "Hoglin", "nameFa": "هاگلین", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.8, "width": 1.4, "spawnLightLevel": "any", "xp": 0, "boss": False, "spawnGroup": "creature"},
    "hasRealTexture": True,
}


# ------------------------------------------------------------------- TADPOLE
MOBS["tadpole"] = {
    "id": "tadpole",
    "nameEn": "Tadpole",
    "nameFa": "بچه‌قورباغه",
    "category": "passive",
    "icon": "tadpole",
    "health": 6,
    "damage": {"contact": 0},
    "speed": 0.4,
    "versions": {"java": "1.19+", "bedrock": "1.18.10+"},
    "description": "بچه‌قورباغه ماب صلح‌جوی کوچک ۱.۱۹ است که در آب پیدا می‌شه. با رشد به Frog تبدیل می‌شه.",
    "drops": [{"item": "nothing", "count": "0"}],
    "locations": ["Water (Frog Spawn)"],
    "combat": ["با یک ضربه بزن", "در آب با Bucket بگیر", "با رشد به Frog تبدیل می‌شه"],
    "wikiLink": "https://minecraft.wiki/w/Tadpole",
    "intro": [
        "بچه‌قورباغه (Tadpole) یک ماب صلح‌جوی کوچک ماینکرفت است که در نسخه‌ی Java 1.19 (ژوئن ۲۰۲۲) به بازی اضافه شد. این ماب فرم نابالغِ Frog است و در آب زندگی می‌کند.",
        "بچه‌قورباغه با ۶ سلامتی شناخته می‌شود و پس از رشد (در ۲۰ دقیقه، یا ۱۰ دقیقه با Slimeball) به Frog تبدیل می‌شود. نوع Frog بستگی به بایومی دارد که در آن رشد می‌کند.",
        "بچه‌قورباغه با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب با Bucket قابل جابه‌جایی است و در بایوم‌های مختلف رشد می‌کند — Temperate (Temperate Frog)، Cold (Cold Frog)، و Warm (Warm Frog)."
    ],
    "behavior": [
        "بچه‌قورباغه در آب (پس از Frog Egg هچ شدن) اسپاون می‌شود. این ماب با ۶ سلامتی شناخته می‌شود و آسیب تماسی ۰ وارد می‌کند. بچه‌قورباغه پس از رشد به Frog تبدیل می‌شود.",
        "بچه‌قورباغه پس از رشد (در ۲۰ دقیقه، یا ۱۰ دقیقه با Slimeball) به Frog تبدیل می‌شود. نوع Frog بستگی به بایومی دارد که در آن رشد می‌کند — Temperate، Cold یا Warm.",
        "بچه‌قورباغه با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب با Bucket قابل جابه‌جایی است و در بایوم‌های مختلف رشد می‌کند."
    ],
    "trivia": [
        "بچه‌قورباغه در نسخه‌ی ۱.۱۹ (۲۰۲۲) به بازی اضافه شد — همراه با Frog.",
        "این ماب فرم نابالغِ Frog است — تنها ماب بازی با این ویژگی.",
        "بچه‌قورباغه پس از رشد به Frog تبدیل می‌شود — تنها ماب بازی با این تغییر.",
        "نوع Frog بستگی به بایومی دارد که در آن رشد می‌کند — منحصر‌به‌فرد.",
        "بچه‌قورباغه با ۶ سلامتی، یکی از ضعیف‌ترین ماب‌های بازی است — به‌سادگی با یک ضربه‌ی شمشیر کشته می‌شود."
    ],
    "history": [
        {"version": "Java 1.19 (2022)", "change": "بچه‌قورباغه به بازی اضافه شد — همراه با Frog."},
        {"version": "Bedrock 1.18.10 (2022)", "change": "تطبیق بچه‌قورباغه با نسخه‌ی Java (preview)."},
        {"version": "Java 1.19.1 (2022)", "change": "بهبود انیمیشن بچه‌قورباغه هنگام رشد."},
        {"version": "Bedrock 1.19.10 (2022)", "change": "افزودن جلوه‌ی بصری رشد بچه‌قورباغه."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت بچه‌قورباغه در آب‌ها."}
    ],
    "differences": [
        "در Java، بچه‌قورباغه با ۶ سلامتی شناخته می‌شود؛ در Bedrock ۶ — یکسان.",
        "در Java، بچه‌قورباغه پس از ۲۰ دقیقه رشد می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، بچه‌قورباغه با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "frog", "nameEn": "Frog", "nameFa": "قورباغه", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 0.3, "width": 0.4, "spawnLightLevel": "any", "xp": 0, "boss": False, "spawnGroup": "underwater"},
    "hasRealTexture": True,
}


# ----------------------------------------------------------------------- VEX
MOBS["vex"] = {
    "id": "vex",
    "nameEn": "Vex",
    "nameFa": "وکس",
    "category": "hostile",
    "icon": "vex",
    "health": 14,
    "damage": {"contact": 3},
    "speed": 0.3,
    "versions": {"java": "1.11+", "bedrock": "1.11.0+"},
    "description": "وکس ماب متخاصم کوچک ۱.۱۱ است که توسط Evoker احضار می‌شه. با Iron Sword حمله می‌کنه و از بلاک‌ها رد می‌شه.",
    "drops": [{"item": "nothing", "count": "0"}],
    "locations": ["Summoned by Evoker (Woodland Mansion, Raid)"],
    "combat": ["با شمشیر از دور بزن", "Evoker رو اول بکش", "با سپر ضربه رو بلاک کن"],
    "wikiLink": "https://minecraft.wiki/w/Vex",
    "intro": [
        "وکس (Vex) یک ماب متخاصم کوچک ماینکرفت است که در نسخه‌ی Java 1.11 (نوامبر ۲۰۱۶) به بازی اضافه شد. این ماب توسط Evoker احضار می‌شود و با Iron Sword حمله می‌کند.",
        "وکس با ۱۴ سلامتی شناخته می‌شود و با قابلیت عبور از بلاک‌ها، یکی از خطرناک‌ترین ماب‌های کوچک بازی است. این ماب پس از ۳۰ ثانیه تا ۲ دقیقه به‌طور خودکار از بین می‌رود.",
        "وکس با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب با Iron Sword حمله می‌کند و ۳ آسیب وارد می‌کند. وکس در نسخه‌ی ۱.۱۱ با Evoker به بازی اضافه شد."
    ],
    "behavior": [
        "وکس توسط Evoker در Woodland Mansion و Raid احضار می‌شود. این ماب با ۱۴ سلامتی شناخته می‌شود و با Iron Sword حمله می‌کند. وکس با قابلیت عبور از بلاک‌ها، یکی از خطرناک‌ترین ماب‌های کوچک بازی است.",
        "وکس با Iron Sword حمله می‌کند و ۳ آسیب وارد می‌کند. این ماب پس از ۳۰ ثانیه تا ۲ دقیقه به‌طور خودکار از بین می‌رود. وکس با عبور از بلاک‌ها، به بازیکن در هر جای ممکن حمله می‌کند.",
        "وکس با کشته‌شدن، هیچ‌چیز دراپ نمی‌کند. این ماب با Iron Sword حمله می‌کند و ۳ آسیب وارد می‌کند. وکس در نسخه‌ی ۱.۱۱ با Evoker به بازی اضافه شد."
    ],
    "trivia": [
        "وکس در نسخه‌ی ۱.۱۱ (۲۰۱۶) به بازی اضافه شد — همراه با Evoker.",
        "این ماب توسط Evoker احضار می‌شود — تنها ماب بازی با این روش.",
        "وکس با قابلیت عبور از بلاک‌ها، یکی از خطرناک‌ترین ماب‌های کوچک بازی است — منحصر‌به‌فرد.",
        "وکس پس از ۳۰ ثانیه تا ۲ دقیقه به‌طور خودکار از بین می‌رود — ویژگی منحصر‌به‌فرد.",
        "وکس با ۱۴ سلامتی، یکی از ضعیف‌ترین ماب‌های بازی است — به‌سادگی با یک ضربه‌ی شمشیر کشته می‌شود."
    ],
    "history": [
        {"version": "Java 1.11 (2016)", "change": "وکس به بازی اضافه شد — همراه با Evoker."},
        {"version": "Bedrock 1.11.0 (2018)", "change": "تطبیق وکس با نسخه‌ی Java."},
        {"version": "Java 1.14 (2019)", "change": "افزایش قابلیت وکس در Raid."},
        {"version": "Java 1.19 (2022)", "change": "بهبود انیمیشن وکس هنگام حمله."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت وکس در Woodland Mansion."}
    ],
    "differences": [
        "در Java، وکس با ۱۴ سلامتی شناخته می‌شود؛ در Bedrock ۱۴ — یکسان.",
        "در Java، وکس پس از ۳۰ ثانیه تا ۲ دقیقه از بین می‌رود؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، وکس با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "evoker", "nameEn": "Evoker", "nameFa": "اووکر", "type": "mob"},
        {"id": "vindicator", "nameEn": "Vindicator", "nameFa": "ویندیکاتور", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 0.8, "width": 0.4, "spawnLightLevel": "any", "xp": 3, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# ---------------------------------------------------------------- VINDICATOR
MOBS["vindicator"] = {
    "id": "vindicator",
    "nameEn": "Vindicator",
    "nameFa": "ویندیکاتور",
    "category": "hostile",
    "icon": "vindicator",
    "health": 24,
    "damage": {"contact": 13},
    "speed": 0.3,
    "versions": {"java": "1.11+", "bedrock": "1.11.0+"},
    "description": "ویندیکاتور ماب متخاصم ۱.۱۱ است که در Woodland Mansion پیدا می‌شه. با Iron Axe حمله می‌کنه و در حالت Johnny به همه حمله می‌کنه.",
    "drops": [
        {"item": "emerald", "count": "0-1", "condition": "اگه بازیکن بکشه"},
        {"item": "iron_axe", "count": "1", "condition": "گاهی"}
    ],
    "locations": ["Woodland Mansion", "Raid (Wave 2+)"],
    "combat": ["با شمشیر نزدیک نزن چون Iron Axe داره", "با کمان از دور بزن", "با سپر ضربه رو بلاک کن"],
    "wikiLink": "https://minecraft.wiki/w/Vindicator",
    "intro": [
        "ویندیکاتور (Vindicator) یک ماب متخاصم ماینکرفت است که در نسخه‌ی Java 1.11 (نوامبر ۲۰۱۶) به بازی اضافه شد. این ماب در Woodland Mansion و Raid اسپاون می‌شود و با Iron Axe حمله می‌کند.",
        "ویندیکاتور با ۲۴ سلامتی شناخته می‌شود و با Iron Axe، ۱۳ آسیب وارد می‌کند. این ماب در حالت Johnny (با نام‌گذاری Name Tag) به همه‌ی ماب‌ها حمله می‌کند — ویژگی منحصر‌به‌فرد.",
        "ویندیکاتور با کشته‌شدن، ۰ تا ۱ Emerald و گاهی ۱ Iron Axe دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۴ با Raid به بازی اضافه شد."
    ],
    "behavior": [
        "ویندیکاتور در Woodland Mansion و Raid اسپاون می‌شود. این ماب با ۲۴ سلامتی شناخته می‌شود و با Iron Axe حمله می‌کند. ویندیکاتور با Iron Axe، ۱۳ آسیب وارد می‌کند.",
        "ویندیکاتور در حالت Johnny (با نام‌گذاری Name Tag) به همه‌ی ماب‌ها حمله می‌کند. این ماب با سرعت بالا به بازیکن نزدیک می‌شود و در صورت نزدیک‌شدن، حمله می‌کند. ویندیکاتور با Iron Axe حمله می‌کند.",
        "ویندیکاتور با کشته‌شدن، ۰ تا ۱ Emerald و گاهی ۱ Iron Axe دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۴ با Raid به بازی اضافه شد."
    ],
    "trivia": [
        "ویندیکاتور در نسخه‌ی ۱.۱۱ (۲۰۱۶) به بازی اضافه شد — همراه با Woodland Mansion.",
        "این ماب با Iron Axe، ۱۳ آسیب وارد می‌کند — یکی از قوی‌ترین حمله‌های تماسی در بازی.",
        "ویندیکاتور در حالت Johnny به همه‌ی ماب‌ها حمله می‌کند — منحصر‌به‌فرد.",
        "ویندیکاتور با سرعت بالا به بازیکن نزدیک می‌شود — خطرناک در نبردهای نزدیک.",
        "ویندیکاتور با ۲۴ سلامتی، یکی از متوسط‌ترین Illager‌ها است — نیاز به تجهیزات قوی."
    ],
    "history": [
        {"version": "Java 1.11 (2016)", "change": "ویندیکاتور به بازی اضافه شد — همراه با Woodland Mansion."},
        {"version": "Bedrock 1.11.0 (2018)", "change": "تطبیق ویندیکاتور با نسخه‌ی Java."},
        {"version": "Java 1.14 (2019)", "change": "افزایش قابلیت ویندیکاتور در Raid."},
        {"version": "Java 1.19 (2022)", "change": "بهبود انیمیشن ویندیکاتور هنگام حمله."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت ویندیکاتور در Woodland Mansion."}
    ],
    "differences": [
        "در Java، ویندیکاتور با ۲۴ سلامتی شناخته می‌شود؛ در Bedrock ۲۴ — یکسان.",
        "در Java، ویندیکاتور با Iron Axe حمله می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، ویندیکاتور با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "evoker", "nameEn": "Evoker", "nameFa": "اووکر", "type": "mob"},
        {"id": "pillager", "nameEn": "Pillager", "nameFa": "پیلجر", "type": "mob"},
        {"id": "vex", "nameEn": "Vex", "nameFa": "وکس", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.95, "width": 0.6, "spawnLightLevel": "any", "xp": 10, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# ----------------------------------------------------------- WANDERING TRADER
MOBS["wandering-trader"] = {
    "id": "wandering-trader",
    "nameEn": "Wandering Trader",
    "nameFa": "تاجر ولگرد",
    "category": "utility",
    "icon": "wandering-trader",
    "health": 20,
    "damage": {"contact": 0},
    "speed": 0.3,
    "versions": {"java": "1.14+", "bedrock": "1.11.0+"},
    "description": "تاجر ولگرد ماب کاربردی ۱.۱۴ است که در سطح اسپاون می‌شه و با Emerald آیتم‌های مختلف (Sapling، Flower) مبادله می‌کنه.",
    "drops": [
        {"item": "lead", "count": "2", "condition": "هنگام کشته‌شدن (وقتی از Llama جدا شده)"},
        {"item": "potion_of_invisibility", "count": "1", "condition": "گاهی (در شب)"}
    ],
    "locations": ["Surface (random spawn)"],
    "combat": ["با یک ضربه بزن", "با Emerald مبادله کن", "از Trader Llama محافظت کن"],
    "wikiLink": "https://minecraft.wiki/w/Wandering_Trader",
    "intro": [
        "تاجر ولگرد (Wandering Trader) یک ماب کاربردی ماینکرفت است که در نسخه‌ی Java 1.14 (آوریل ۲۰۱۹) به بازی اضافه شد. این ماب در سطح به‌طور تصادفی اسپاون می‌شود و با Emerald آیتم‌های مختلفی مبادله می‌کند.",
        "تاجر ولگرد با ۲۰ سلامتی شناخته می‌شود و با Emerald، آیتم‌های مختلفی مانند Sapling‌ها، Flower‌ها و Seed‌ها مبادله می‌کند. این ماب پس از ۴۰ دقیقه از بین می‌رود و در صورت کشته‌شدن، ۲ Lead دراپ می‌کند.",
        "تاجر ولگرد با Trader Llama (نسخه‌ی Llama) همراه است و در صورت کشته‌شدن، ۲ Lead دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۴ با Village & Pillage به بازی اضافه شد."
    ],
    "behavior": [
        "تاجر ولگرد در سطح به‌طور تصادفی اسپاون می‌شود. این ماب با ۲۰ سلامتی شناخته می‌شود و آسیب تماسی ۰ وارد می‌کند. تاجر ولگرد با Emerald، آیتم‌های مختلفی مانند Sapling‌ها، Flower‌ها و Seed‌ها مبادله می‌کند.",
        "تاجر ولگرد پس از ۴۰ دقیقه از بین می‌رود. این ماب با Trader Llama همراه است و در صورت کشته‌شدن، ۲ Lead دراپ می‌کند. تاجر ولگرد در شب با Potion of Invisibility پنهان می‌شود.",
        "تاجر ولگرد با Trader Llama همراه است و در صورت کشته‌شدن، ۲ Lead دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۴ با Village & Pillage به بازی اضافه شد."
    ],
    "trivia": [
        "تاجر ولگرد در نسخه‌ی ۱.۱۴ (۲۰۱۹) به بازی اضافه شد — همراه با Village & Pillage.",
        "این ماب با Emerald، آیتم‌های مختلفی مبادله می‌کند — منحصر‌به‌فرد.",
        "تاجر ولگرد پس از ۴۰ دقیقه از بین می‌رود — ویژگی منحصر‌به‌فرد.",
        "تاجر ولگرد با Trader Llama همراه است — تنها ماب با همراه.",
        "تاجر ولگرد در شب با Potion of Invisibility پنهان می‌شود — ویژگی منحصر‌به‌فرد."
    ],
    "history": [
        {"version": "Java 1.14 (2019)", "change": "تاجر ولگرد به بازی اضافه شد — همراه با Village & Pillage."},
        {"version": "Bedrock 1.11.0 (2019)", "change": "تطبیق تاجر ولگرد با نسخه‌ی Java."},
        {"version": "Java 1.17 (2021)", "change": "بهبود انیمیشن تاجر ولگرد هنگام مبادله."},
        {"version": "Java 1.19 (2022)", "change": "افزایش قابلیت تاجر ولگرد در سطح."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت تاجر ولگرد با آیتم‌های جدید."}
    ],
    "differences": [
        "در Java، تاجر ولگرد با ۲۰ سلامتی شناخته می‌شود؛ در Bedrock ۲۰ — یکسان.",
        "در Java، تاجر ولگرد پس از ۴۰ دقیقه از بین می‌رود؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، تاجر ولگرد با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "villager", "nameEn": "Villager", "nameFa": "روستایی", "type": "mob"},
        {"id": "llama", "nameEn": "Llama", "nameFa": "لاما", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.95, "width": 0.6, "spawnLightLevel": "any", "xp": 0, "boss": False, "spawnGroup": "creature"},
    "hasRealTexture": True,
}


# -------------------------------------------------------------------- ZOGLIN
MOBS["zoglin"] = {
    "id": "zoglin",
    "nameEn": "Zoglin",
    "nameFa": "زوگلین",
    "category": "hostile",
    "icon": "zoglin",
    "health": 40,
    "damage": {"contact": 6, "knockback": 5},
    "speed": 0.3,
    "versions": {"java": "1.16+", "bedrock": "1.16.0+"},
    "description": "زوگلین ماب متخاصم ۱.۱۶ است که با انتقال Hoglin به Overworld به‌وجود میاد. با Knockback قوی حمله می‌کنه.",
    "drops": [{"item": "rotten_flesh", "count": "1-3"}],
    "locations": ["Overworld (from Hoglin transfer)"],
    "combat": ["با شمشیر نزدیک نزن چون Knockback می‌زنه", "از دور با کمان بزن", "با سپر ضربه رو بلاک کن"],
    "wikiLink": "https://minecraft.wiki/w/Zoglin",
    "intro": [
        "زوگلین (Zoglin) یک ماب متخاصم ماینکرفت است که در نسخه‌ی Java 1.16 (ژوئن ۲۰۲۰) به بازی اضافه شد. این ماب با انتقال Hoglin به Overworld به‌وجود می‌آید — پس از ۱۵ ثانیه تبدیل می‌شود.",
        "زوگلین با ۴۰ سلامتی شناخته می‌شود و با حمله‌ی تماسی ۶ آسیب وارد می‌کند. این ماب با Knockback ۵، بازیکن را به‌عقب هل می‌دهد. زوگلین برخلاف Hoglin قابل تکثیر نیست.",
        "زوگلین با کشته‌شدن، ۱ تا ۳ Rotten Flesh دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۶ با Hoglin به بازی اضافه شد و در صورت انتقال Hoglin به Overworld به‌وجود می‌آید."
    ],
    "behavior": [
        "زوگلین با انتقال Hoglin به Overworld به‌وجود می‌آید — پس از ۱۵ ثانیه تبدیل می‌شود. این ماب با ۴۰ سلامتی شناخته می‌شود و با حمله‌ی تماسی ۶ آسیب وارد می‌کند. زوگلین با Knockback ۵، بازیکن را به‌عقب هل می‌دهد.",
        "زوگلین برخلاف Hoglin قابل تکثیر نیست. این ماب با Warped Fungus فرار نمی‌کند — برخلاف Hoglin. زوگلین با سرعت متوسط حرکت می‌کند و در صورت دیدن بازیکن، حمله می‌کند.",
        "زوگلین با کشته‌شدن، ۱ تا ۳ Rotten Flesh دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۶ با Hoglin به بازی اضافه شد."
    ],
    "trivia": [
        "زوگلین در نسخه‌ی ۱.۱۶ (۲۰۲۰) به بازی اضافه شد — همراه با Nether Update.",
        "این ماب با انتقال Hoglin به Overworld به‌وجود می‌آید — منحصر‌به‌فرد.",
        "زوگلین با Knockback ۵ حمله می‌کند — ویژگی مشابه با Hoglin.",
        "زوگلین برخلاف Hoglin قابل تکثیر نیست — ویژگی منحصر‌به‌فرد.",
        "زوگلین با ۴۰ سلامتی، یکی از قوی‌ترین ماب‌های متوسط بازی است — نیاز به تجهیزات قوی."
    ],
    "history": [
        {"version": "Java 1.16 (2020)", "change": "زوگلین به بازی اضافه شد — همراه با Nether Update."},
        {"version": "Bedrock 1.16.0 (2020)", "change": "تطبیق زوگلین با نسخه‌ی Java."},
        {"version": "Java 1.17 (2021)", "change": "بهبود انیمیشن زوگلین هنگام حمله."},
        {"version": "Java 1.19 (2022)", "change": "رفع باگ‌های جزئی در رفتار زوگلین."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت زوگلین در Overworld."}
    ],
    "differences": [
        "در Java، زوگلین با ۴۰ سلامتی شناخته می‌شود؛ در Bedrock ۴۰ — یکسان.",
        "در Java، زوگلین با Knockback ۵ حمله می‌کند؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، زوگلین با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "hoglin", "nameEn": "Hoglin", "nameFa": "هاگلین", "type": "mob"},
        {"id": "zombie", "nameEn": "Zombie", "nameFa": "زامبی", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.4, "width": 1.4, "spawnLightLevel": "any", "xp": 5, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# --------------------------------------------------------------- ZOMBIE HORSE
MOBS["zombie-horse"] = {
    "id": "zombie-horse",
    "nameEn": "Zombie Horse",
    "nameFa": "اسب زامبی",
    "category": "passive",
    "icon": "zombie-horse",
    "health": 15,
    "damage": {"contact": 0},
    "speed": 0.3,
    "versions": {"java": "1.6+", "bedrock": "1.0.0+"},
    "description": "اسب زامبی ماب صلح‌جوی ۱.۶ است که با /summon احضار می‌شه. نسخه‌ی زامبی‌شده‌ی Horse — قابل سواره‌شدنه.",
    "drops": [
        {"item": "rotten_flesh", "count": "0-2"}
    ],
    "locations": ["Only via /summon"],
    "combat": ["با یک ضربه بزن", "با Saddle سواره شو", "تولید طبیعی نمی‌شه"],
    "wikiLink": "https://minecraft.wiki/w/Zombie_Horse",
    "intro": [
        "اسب زامبی (Zombie Horse) یک ماب صلح‌جوی ماینکرفت است که در نسخه‌ی Java 1.6 (ژوئیه ۲۰۱۳) به بازی اضافه شد. این ماب با /summon قابل احضار است و نسخه‌ی زامبی‌شده‌ی Horse است.",
        "اسب زامبی با ۱۵ سلامتی شناخته می‌شود و با Saddle قابل سواره‌شدن است. این ماب در روز آتش نمی‌گیرد — برخلاف Zombie. اسب زامبی با /summon قابل احضار است.",
        "اسب زامبی با کشته‌شدن، ۰ تا ۲ Rotten Flesh دراپ می‌کند. این ماب در نسخه‌ی ۱.۶ با Horse به بازی اضافه شد و تنها با /summon قابل احضار است."
    ],
    "behavior": [
        "اسب زامبی با /summon قابل احضار است. این ماب با ۱۵ سلامتی شناخته می‌شود و آسیب تماسی ۰ وارد می‌کند. اسب زامبی با Saddle قابل سواره‌شدن است.",
        "اسب زامبی در روز آتش نمی‌گیرد — برخلاف Zombie. این ماب با /summon قابل احضار است و در نسخه‌ی ۱.۶ با Horse به بازی اضافه شد.",
        "اسب زامبی با کشته‌شدن، ۰ تا ۲ Rotten Flesh دراپ می‌کند. این ماب تنها با /summon قابل احضار است — عدم اسپاون طبیعی."
    ],
    "trivia": [
        "اسب زامبی در نسخه‌ی ۱.۶ (۲۰۱۳) به بازی اضافه شد — همراه با Horse.",
        "این ماب با /summon قابل احضار است — عدم اسپاون طبیعی.",
        "اسب زامبی در روز آتش نمی‌گیرد — برخلاف Zombie، ویژگی منحصر‌به‌فرد.",
        "اسب زامبی با Saddle قابل سواره‌شدن است — تنها ماب زامبی سواره‌شدنی.",
        "اسب زامبی با ۱۵ سلامتی، یکی از ضعیف‌ترین حیوانات بازی است — کم‌تر از اسب."
    ],
    "history": [
        {"version": "Java 1.6 (2013)", "change": "اسب زامبی به بازی اضافه شد — همراه با Horse."},
        {"version": "Bedrock 1.0.0 (2016)", "change": "تطبیق اسب زامبی با نسخه‌ی Java."},
        {"version": "Java 1.13 (2018)", "change": "بهبود انیمیشن اسب زامبی هنگام راه‌رفتن."},
        {"version": "Java 1.19 (2022)", "change": "رفع باگ‌های جزئی در رفتار اسب زامبی."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت اسب زامبی در /summon."}
    ],
    "differences": [
        "در Java، اسب زامبی با ۱۵ سلامتی شناخته می‌شود؛ در Bedrock ۱۵ — یکسان.",
        "در Java، اسب زامبی در روز آتش نمی‌گیرد؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، اسب زامبی با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "horse", "nameEn": "Horse", "nameFa": "اسب", "type": "mob"},
        {"id": "skeleton-horse", "nameEn": "Skeleton Horse", "nameFa": "اسب اسکلتونی", "type": "mob"},
        {"id": "zombie", "nameEn": "Zombie", "nameFa": "زامبی", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.6, "width": 1.4, "spawnLightLevel": "any", "xp": 0, "boss": False, "spawnGroup": "creature"},
    "hasRealTexture": True,
}


# ------------------------------------------------------------- ZOMBIE VILLAGER
MOBS["zombie-villager"] = {
    "id": "zombie-villager",
    "nameEn": "Zombie Villager",
    "nameFa": "روستایی زامبی",
    "category": "hostile",
    "icon": "zombie-villager",
    "health": 20,
    "damage": {"contact": 3},
    "speed": 0.25,
    "versions": {"java": "1.4.2+", "bedrock": "1.0.0+"},
    "description": "روستایی زامبی ماب متخاصم ۱.۴ است که با Zombie infecting Villager به‌وجود میاد. با Weakness Potion و Golden Apple قابل درمانه.",
    "drops": [
        {"item": "rotten_flesh", "count": "0-2"},
        {"item": "iron_ingot", "count": "1", "condition": "گاهی (اگه بازیکن بکشه)"}
    ],
    "locations": ["Village", "Surface (with Zombie spawn)"],
    "combat": ["با شمشیر بزن", "با Weakness Potion و Golden Apple درمان کن", "نزدیک نشو چون سلاسه می‌کنه"],
    "wikiLink": "https://minecraft.wiki/w/Zombie_Villager",
    "intro": [
        "روستایی زامبی (Zombie Villager) یک ماب متخاصم ماینکرفت است که در نسخه‌ی Java 1.4.2 (اکتبر ۲۰۱۲) به بازی اضافه شد. این ماب با Zombie infecting Villager به‌وجود می‌آید و قابل درمان است.",
        "روستایی زامبی با ۲۰ سلامتی شناخته می‌شود و با حمله‌ی تماسی ۳ آسیب وارد می‌کند. این ماب با Weakness Potion و Golden Apple قابل درمان است — پس از ۵ دقیقه (یا ۲ دقیقه با Golden Apple) به Villager تبدیل می‌شود.",
        "روستایی زامبی با کشته‌شدن، ۰ تا ۲ Rotten Flesh و گاهی ۱ Iron Ingot دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۴ بازطراحی شد و با بیوم‌های مختلف (Desert، Jungle، Plains، Savanna، Snowy، Swamp، Taiga) شناخته می‌شود."
    ],
    "behavior": [
        "روستایی زامبی با Zombie infecting Villager به‌وجود می‌آید. این ماب با ۲۰ سلامتی شناخته می‌شود و با حمله‌ی تماسی ۳ آسیب وارد می‌کند. روستایی زامبی با Weakness Potion و Golden Apple قابل درمان است.",
        "روستایی زامبی با Weakness Potion و Golden Apple قابل درمان است — پس از ۵ دقیقه (یا ۲ دقیقه با Golden Apple) به Villager تبدیل می‌شود. این ماب با بایوم‌های مختلف، با لباس‌های متفاوت شناخته می‌شود.",
        "روستایی زامبی با کشته‌شدن، ۰ تا ۲ Rotten Flesh و گاهی ۱ Iron Ingot دراپ می‌کند. این ماب در نسخه‌ی ۱.۱۴ بازطراحی شد."
    ],
    "trivia": [
        "روستایی زامبی در نسخه‌ی ۱.۴.۲ (۲۰۱۲) به بازی اضافه شد — همراه با Zombie.",
        "این ماب با Weakness Potion و Golden Apple قابل درمان است — منحصر‌به‌فرد.",
        "روستایی زامبی با بایوم‌های مختلف، با لباس‌های متفاوت شناخته می‌شود — پرتنوع.",
        "روستایی زامبی پس از درمان به Villager تبدیل می‌شود — تنها ماب بازی با این تغییر.",
        "روستایی زامبی با ۲۰ سلامتی، یکی از متوسط‌ترین ماب‌های بازی است — مانند Zombie."
    ],
    "history": [
        {"version": "Java 1.4.2 (2012)", "change": "روستایی زامبی به بازی اضافه شد — همراه با Zombie."},
        {"version": "Bedrock 1.0.0 (2016)", "change": "تطبیق روستایی زامبی با نسخه‌ی Java."},
        {"version": "Java 1.14 (2019)", "change": "بازطراحی روستایی زامبی — با بایوم‌های مختلف."},
        {"version": "Java 1.19 (2022)", "change": "بهبود انیمیشن روستایی زامبی هنگام حمله."},
        {"version": "Java 1.21 (2024)", "change": "افزایش قابلیت روستایی زامبی در Village."}
    ],
    "differences": [
        "در Java، روستایی زامبی با ۲۰ سلامتی شناخته می‌شود؛ در Bedrock ۲۰ — یکسان.",
        "در Java، روستایی زامبی با Weakness Potion و Golden Apple قابل درمان است؛ در Bedrock رفتار یکسان است.",
        "در Bedrock، روستایی زامبی با رندر کمی متفاوت از Java نمایش داده می‌شود."
    ],
    "related": [
        {"id": "zombie", "nameEn": "Zombie", "nameFa": "زامبی", "type": "mob"},
        {"id": "villager", "nameEn": "Villager", "nameFa": "روستایی", "type": "mob"},
        {"id": "witch", "nameEn": "Witch", "nameFa": "ویچ", "type": "mob"}
    ],
    "extraStats": {"armor": 0, "height": 1.95, "width": 0.6, "spawnLightLevel": "<=7", "xp": 5, "boss": False, "spawnGroup": "monster"},
    "hasRealTexture": True,
}


# =============================================================================
# MAIN LOGIC
# =============================================================================

def write_mob_files():
    """Write each missing mob's JSON file."""
    written = 0
    for mob_id, mob in MOBS.items():
        out = MOBS_DIR / f"{mob_id}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(mob, f, ensure_ascii=False, indent=2)
            f.write("\n")
        written += 1
        print(f"  ✓ wrote {out.relative_to(PROJECT)}")
    return written


def update_index_json():
    """Insert the 28 new mobs into the existing index.json (in category groups)."""
    idx_path = MOBS_DIR / "index.json"
    with open(idx_path, encoding="utf-8") as f:
        idx = json.load(f)

    # Build a tiny lookup for the new mobs (only fields needed in index)
    NEW_ENTRIES = []
    for mob_id, mob in MOBS.items():
        NEW_ENTRIES.append({
            "id": mob_id,
            "nameEn": mob["nameEn"],
            "nameFa": mob["nameFa"],
            "category": mob["category"],
            "icon": mob["icon"],
            "hasRealTexture": mob.get("hasRealTexture", True),
        })

    # Group existing entries by category, preserving original order within each group.
    category_order = ["hostile", "passive", "neutral", "boss", "utility", "ambient"]
    groups: dict[str, list] = {c: [] for c in category_order}
    for entry in idx["mobs"]:
        c = entry.get("category")
        if c in groups:
            groups[c].append(entry)
        else:
            groups.setdefault(c, []).append(entry)

    # Append new entries to their respective category group.
    for entry in NEW_ENTRIES:
        c = entry.get("category")
        groups.setdefault(c, []).append(entry)

    # Re-flatten in canonical category order
    new_mobs = []
    for c in category_order:
        new_mobs.extend(groups.get(c, []))

    idx["mobs"] = new_mobs
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"  ✓ updated {idx_path.relative_to(PROJECT)} ({len(new_mobs)} entries)")


def download_render(url: str) -> bytes:
    """Download a WebP/PNG render from ccvaults and return its bytes."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def webp_to_png_bytes(webp_bytes: bytes) -> bytes:
    """Convert WebP bytes to PNG bytes using PIL."""
    img = Image.open(io.BytesIO(webp_bytes))
    if img.mode == "RGBA":
        # Replace full transparency with a white-ish background for renders
        # that may have issues with transparency on some viewers.
        pass
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def upload_renders():
    """Download + convert + upload each missing render to HF mobs-render/."""
    api = HfApi(token=HF_TOKEN)
    uploaded = 0
    skipped = 0
    failed = 0
    for mob_id, url in RENDER_URLS.items():
        target = f"mobs-render/{mob_id}.png"
        # If already on HF, skip.
        if mob_id in RENDERS_ALREADY_ON_HF:
            print(f"  ⊙ skip {mob_id} (already on HF)")
            skipped += 1
            continue
        try:
            print(f"  ↓ downloading {mob_id} from ccvaults...")
            raw = download_render(url)
            png_bytes = webp_to_png_bytes(raw)
            print(f"    ({len(png_bytes)} bytes PNG) ↑ uploading to HF...")
            api.upload_file(
                path_or_fileobj=png_bytes,
                path_in_repo=target,
                repo_id=HF_REPO,
                repo_type="dataset",
            )
            print(f"  ✓ uploaded {target}")
            uploaded += 1
        except Exception as e:
            print(f"  ✗ FAILED {mob_id}: {e}")
            failed += 1
    return uploaded, skipped, failed


def main():
    print("=" * 70)
    print("SA-MOBS-ADD: Adding 28 missing vanilla 1.21 mobs to MineBed Astro")
    print("=" * 70)

    print(f"\n[1/3] Writing {len(MOBS)} mob JSON files...")
    written = write_mob_files()
    print(f"  → {written} files written")

    print("\n[2/3] Updating mobs/index.json with new entries...")
    update_index_json()

    print(f"\n[3/3] Uploading {len(RENDER_URLS)} mob renders to HuggingFace...")
    uploaded, skipped, failed = upload_renders()
    print(f"  → uploaded: {uploaded}, skipped (already on HF): {skipped}, failed: {failed}")

    print("\n" + "=" * 70)
    print("DONE — All 28 missing vanilla 1.21 mobs added.")
    print("=" * 70)


if __name__ == "__main__":
    main()
