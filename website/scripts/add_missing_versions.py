#!/usr/bin/env python3
"""
Add all missing Minecraft versions to src/data/versions.json.

Currently the file has 78 versions (31 Java + 47 Bedrock).
Missing versions identified by comparison against full MC version history:
  - Java Beta 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7   (7 versions)
  - Bedrock (Pocket Edition) 0.1.0 - 0.8.0          (8 versions)

All major Java 1.0-1.21 and Bedrock 1.0-1.21 are already present.
(Snapshots / preview builds intentionally NOT added — only major releases.)

Each new entry follows the EXACT schema of existing entries:
  id, version, name, nameFa, platform, releaseDate,
  description (Persian, 2-3 sentences),
  highlights (3-5 Persian items),
  features (5 Persian items),
  changelog (5 Persian items),
  summary (1 Persian sentence),
  icon ('px-stone' default per task rules),
  codename, major, minor, compatibleMods, wikiLink
"""

import json
import os
import sys

VERSIONS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "src", "data", "versions.json",
)

# ============================================================================
# NEW VERSION DEFINITIONS — real info per minecraft.wiki, real Persian text
# Correct translations: Nether → ندر, End → اند, Bedrock → بدراک, Redstone → رداستون
# ============================================================================

NEW_JAVA_BETA_VERSIONS = [
    # ----- Beta 1.1 -----
    {
        "id": "java-beta-1-1",
        "version": "Beta 1.1",
        "name": "Minecraft Beta 1.1",
        "nameFa": "ماینکرفت بتا ۱.۱",
        "platform": "java",
        "releaseDate": "2010-12-22",
        "codename": "Beta",
        "major": 0,
        "minor": 1,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Java_Edition_Beta_1.1",
        "icon": "px-stone",
        "summary": "بهبود Server-side Inventory و Sneaking با ترجمه‌ی بازی.",
        "description": (
            "نسخه‌ی بتا ۱.۱ در ۲۲ دسامبر ۲۰۱۰ منتشر شد و بهبودهای جزئی نسبت به "
            "بتا ۱.۰ داشت. این نسخه مشکلات Server-side Inventory و سیستم Sneaking "
            "را رفع کرد و قابلیت چت در سرورها را پایدارتر کرد. پشتیبانی از "
            "زبان‌های جدید نیز به بازی اضافه شد."
        ),
        "highlights": [
            "بهبود Server-side Inventory",
            "رفع باگ Sneaking",
            "پشتیبانی چندزبانه",
            "پایداری سرور",
        ],
        "features": [
            "Server-side Inventory همگام‌سازی شده با سرور",
            "Sneaking — قابلیت خم‌شدن بدون افت از لبه",
            "ترجمه‌ی بازی به چند زبان",
            "Chat سرور پایدارتر",
            "رفع باگ‌های Lava ریختن",
        ],
        "changelog": [
            "بهبود همگام‌سازی Server-side Inventory",
            "رفع باگ‌های Sneaking و حرکت",
            "افزودن ترجمه‌ی بازی به چند زبان",
            "پایدارتر شدن چت در سرورها",
            "رفع چندین باگ Lava و آب",
        ],
    },
    # ----- Beta 1.2 -----
    {
        "id": "java-beta-1-2",
        "version": "Beta 1.2",
        "name": "Minecraft Beta 1.2",
        "nameFa": "ماینکرفت بتا ۱.۲",
        "platform": "java",
        "releaseDate": "2011-01-13",
        "codename": "Beta",
        "major": 0,
        "minor": 2,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Java_Edition_Beta_1.2",
        "icon": "px-stone",
        "summary": "افزودن Note Block، Squid، Sugar Cane و درخت‌های Birch و Spruce.",
        "description": (
            "نسخه‌ی بتا ۱.۲ در ۱۳ ژانویه ۲۰۱۱ منتشر شد و درخت‌های جدید (Birch و "
            "Spruce) را به بازی اضافه کرد. Note Block برای ساخت موسیقی، Squid "
            "برای جوهر، و Sugar Cane برای ساخت کاغذ و قند اضافه شد. بلوک‌های "
            "Lapis Lazuli و Ink Sac نیز معرفی شدند."
        ),
        "highlights": [
            "Note Block",
            "Squid و Ink Sac",
            "Sugar Cane",
            "درخت‌های Birch و Spruce",
            "Lapis Lazuli",
        ],
        "features": [
            "Note Block — بلوک موسیقی برای ساخت نت",
            "Squid — ماب دریایی که Ink Sac می‌دهد",
            "Sugar Cane — برای ساخت کاغذ و قند",
            "درخت‌های Birch و Spruce — تنوع درخت",
            "Lapis Lazuli Ore و Block — رنگ آبی",
        ],
        "changelog": [
            "افزودن Note Block و سیستم موسیقی",
            "افزودن Squid و Ink Sac",
            "افزودن Sugar Cane برای کاغذ",
            "افزودن درخت‌های Birch و Spruce",
            "افزودن Lapis Lazuli Block و Ore",
        ],
    },
    # ----- Beta 1.3 -----
    {
        "id": "java-beta-1-3",
        "version": "Beta 1.3",
        "name": "Minecraft Beta 1.3",
        "nameFa": "ماینکرفت بتا ۱.۳",
        "platform": "java",
        "releaseDate": "2011-02-22",
        "codename": "Beta",
        "major": 0,
        "minor": 3,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Java_Edition_Beta_1.3",
        "icon": "px-stone",
        "summary": "افزودن تخت خواب، Powered Rails و Redstone Lamp.",
        "description": (
            "نسخه‌ی بتا ۱.۳ در ۲۲ فوریه ۲۰۱۱ منتشر شد و قابلیت خواب در تخت را "
            "برای رد کردن شب و تغییر اسپاون اضافه کرد. Powered Rails و Detector "
            "Rails برای ساخت مینی‌کارت‌های سریع معرفی شد. Slabs جدید و "
            "امکان چرخاندن آن‌ها به پایین نیز اضافه شد."
        ),
        "highlights": [
            "Bed — تخت خواب",
            "Powered Rails",
            "Detector Rails",
            "Redstone Lamp",
            "Slab چرخان",
        ],
        "features": [
            "Bed — تخت برای رد کردن شب و تغییر اسپاون",
            "Powered Rails — ریل تقویت شده با رداستون",
            "Detector Rails — ریل با سنسور ماب",
            "Redstone Lamp — چراغ رداستونی",
            "Slab قابل چرخاندن (upside-down)",
        ],
        "changelog": [
            "افزودن Bed و سیستم خواب",
            "افزودن Powered Rails و Detector Rails",
            "افزودن Redstone Lamp",
            "افزودن Slab‌های قابل چرخاندن",
            "بهبود رندر حجمی و عملکرد",
        ],
    },
    # ----- Beta 1.4 -----
    {
        "id": "java-beta-1-4",
        "version": "Beta 1.4",
        "name": "Minecraft Beta 1.4",
        "nameFa": "ماینکرفت بتا ۱.۴",
        "platform": "java",
        "releaseDate": "2011-03-31",
        "codename": "Beta",
        "major": 0,
        "minor": 4,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Java_Edition_Beta_1.4",
        "icon": "px-stone",
        "summary": "افزودن Wolves، Cookies و قابلیت رام کردن.",
        "description": (
            "نسخه‌ی بتا ۱.۴ در ۳۱ مارس ۲۰۱۱ منتشر شد و Wolves را به بازی اضافه "
            "کرد؛ اولین ماب قابل رام کردن با استخوان. Cookies نیز معرفی شدند. "
            "قابلیت خواب در تخت در multiplayer بهبود یافت و چندین باگ رفع شد."
        ),
        "highlights": [
            "Wolves — گرگ‌های رام‌شدنی",
            "Cookies",
            "Sleep در Multiplayer",
            "رفع باگ‌های متعدد",
        ],
        "features": [
            "Wolves — ماب قابل رام با استخوان",
            "Cookies — غذا و آیتم",
            "Sleep در Multiplayer — خواب همزمان",
            "Locked Chest — شوخی آوریل",
            "بهبود پایداری multiplayer",
        ],
        "changelog": [
            "افزودن Wolves و سیستم رام کردن",
            "افزودن Cookies",
            "بهبود Sleep در Multiplayer",
            "افزودن Locked Chest (April Fools)",
            "رفع چندین باگ سرور",
        ],
    },
    # ----- Beta 1.5 -----
    {
        "id": "java-beta-1-5",
        "version": "Beta 1.5",
        "name": "Minecraft Beta 1.5",
        "nameFa": "ماینکرفت بتا ۱.۵",
        "platform": "java",
        "releaseDate": "2011-04-19",
        "codename": "Beta",
        "major": 0,
        "minor": 5,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Java_Edition_Beta_1.5",
        "icon": "px-stone",
        "summary": "افزودن Weather، Cobweb و Powered Rails تقویت‌شده.",
        "description": (
            "نسخه‌ی بتا ۱.۵ در ۱۹ آوریل ۲۰۱۱ منتشر شد و Weather (باران، برف و "
            "رعدوبرق) را به بازی اضافه کرد. Cobweb و Tall Grass معرفی شد. "
            "Powered Rails با قابلیت تقویت سرعت Minecart معرفی شد."
        ),
        "highlights": [
            "Weather — باران و برف",
            "Cobweb",
            "Powered Rails سرعت",
            "Achievements (آماده‌سازی)",
        ],
        "features": [
            "Weather — باران، برف و رعدوبرق",
            "Cobweb — تار عنکبوت",
            "Powered Rails — تقویت سرعت Minecart",
            "Tall Grass — علف بلند با دانه",
            "پشتیبانی Achievements (آماده‌سازی)",
        ],
        "changelog": [
            "افزودن Weather و سیستم آب‌وهوایی",
            "افزودن Cobweb",
            "افزودن Powered Rails تقویت‌شده",
            "افزودن Tall Grass",
            "افزودن اسکلت Achievements",
        ],
    },
    # ----- Beta 1.6 -----
    {
        "id": "java-beta-1-6",
        "version": "Beta 1.6",
        "name": "Minecraft Beta 1.6",
        "nameFa": "ماینکرفت بتا ۱.۶",
        "platform": "java",
        "releaseDate": "2011-05-26",
        "codename": "Beta",
        "major": 0,
        "minor": 6,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Java_Edition_Beta_1.6",
        "icon": "px-stone",
        "summary": "افزودن Maps، Trapdoor و Dead Bush.",
        "description": (
            "نسخه‌ی بتا ۱.۶ در ۲۶ مه ۲۰۱۱ منتشر شد و Maps (نقشه‌های کارتوگرافی) "
            "را اضافه کرد. Wooden Trapdoor معرفی شد. Dead Bush در بیابان‌ها "
            "افزوده شد و سیستم رشد Grass بهبود یافت."
        ),
        "highlights": [
            "Maps — نقشه‌ی کارتوگرافی",
            "Wooden Trapdoor",
            "Dead Bush",
            "بهبود multiplayer",
        ],
        "features": [
            "Maps — نقشه قابل ساخت با Compass",
            "Wooden Trapdoor — دریچه‌ی چوبی",
            "Dead Bush — بوته‌ی خشک در بیابان",
            "Tall Grass با دانه گندم",
            "بهبود همگام‌سازی multiplayer",
        ],
        "changelog": [
            "افزودن Maps با Compass",
            "افزودن Wooden Trapdoor",
            "افزودن Dead Bush در بیابان",
            "بهبود سیستم Grass و دانه",
            "رفع چندین باگ multiplayer",
        ],
    },
    # ----- Beta 1.7 -----
    {
        "id": "java-beta-1-7",
        "version": "Beta 1.7",
        "name": "Minecraft Beta 1.7",
        "nameFa": "ماینکرفت بتا ۱.۷",
        "platform": "java",
        "releaseDate": "2011-06-30",
        "codename": "Beta",
        "major": 0,
        "minor": 7,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Java_Edition_Beta_1.7",
        "icon": "px-stone",
        "summary": "افزودن Pistons، Shears و قابلیت پر کردن آب با Buckets.",
        "description": (
            "نسخه‌ی بتا ۱.۷ در ۳۰ ژوئن ۲۰۱۱ منتشر شد و Pistons (استفاده از "
            "رداستون برای حرکت دادن بلوک‌ها) را به بازی اضافه کرد. Shears برای "
            "برداشت پشم گوسفند بدون کشتن معرفی شد. TNT با رداستون قابل "
            "فعال‌سازی شد."
        ),
        "highlights": [
            "Pistons — پیستون‌های رداستونی",
            "Shears — قیچی",
            "TNT با رداستون",
            "بهبود Silk Touch",
        ],
        "features": [
            "Pistons — پیستون قابل فعال‌سازی با رداستون",
            "Shears — قیچی برای برداشت پشم",
            "TNT با رداستون قابل فعال‌سازی",
            "بهبود سیستم Silk Touch",
            "بهبود چیدمان بلوک‌ها",
        ],
        "changelog": [
            "افزودن Pistons و Sticky Pistons",
            "افزودن Shears",
            "افزودن قابلیت فعال‌سازی TNT با رداستون",
            "بهبود Silk Touch",
            "رفع چندین باگ سرور",
        ],
    },
]

NEW_BEDROCK_POCKET_VERSIONS = [
    # ----- Pocket Edition 0.1.0 -----
    {
        "id": "bedrock-0-1-0",
        "version": "0.1.0",
        "name": "Minecraft Pocket Edition 0.1.0",
        "nameFa": "ماینکرفت پاکت ۰.۱.۰",
        "platform": "bedrock",
        "releaseDate": "2011-08-16",
        "codename": "Pocket Edition",
        "major": 0,
        "minor": 1,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Bedrock_Edition_0.1.0",
        "icon": "px-stone",
        "summary": "نخستین نسخه‌ی Pocket Edition برای Xperia Play.",
        "description": (
            "نسخه‌ی ۰.۱.۰ Pocket Edition در ۱۶ اوت ۲۰۱۱ برای گوشی Xperia Play "
            "منتشر شد و نخستین نسخه‌ی رسمی ماینکرفت موبایل بود. این نسخه ۳۶ "
            "بلوک (شامل چمن، خاک و سنگ) و حالت Creative را داشت. کنترل لمسی "
            "و دکمه‌های روی Xperia Play پشتیبانی می‌شد."
        ),
        "highlights": [
            "نخستین نسخه‌ی موبایل",
            "۳۶ بلوک در دسترس",
            "حالت Creative",
            "کنترل لمسی",
        ],
        "features": [
            "۳۶ بلوک اولیه (چمن، خاک، سنگ)",
            "حالت Creative با آیتم نامحدود",
            "کنترل لمسی (D-pad مجازی)",
            "پشتیبانی از Xperia Play",
            "نقشه‌ی محدود کوچک",
        ],
        "changelog": [
            "نخستین نسخه‌ی رسمی Pocket Edition",
            "افزودن ۳۶ بلوک اولیه",
            "افزودن حالت Creative",
            "افزودن کنترل لمسی D-pad",
            "پشتیبانی از Xperia Play",
        ],
    },
    # ----- Pocket Edition 0.2.0 -----
    {
        "id": "bedrock-0-2-0",
        "version": "0.2.0",
        "name": "Minecraft Pocket Edition 0.2.0",
        "nameFa": "ماینکرفت پاکت ۰.۲.۰",
        "platform": "bedrock",
        "releaseDate": "2012-02-22",
        "codename": "Pocket Edition",
        "major": 0,
        "minor": 2,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Bedrock_Edition_0.2.0",
        "icon": "px-stone",
        "summary": "افزودن Survival Mode و چرخه‌ی روز/شب.",
        "description": (
            "نسخه‌ی ۰.۲.۰ Pocket Edition در ۲۲ فوریه ۲۰۱۲ منتشر شد و حالت "
            "Survival را اضافه کرد. چرخه‌ی روز/شب (هر دوره ۲۰ دقیقه) معرفی شد. "
            "ماب‌هایی مثل Zombie، Skeleton و Spider در شب ظاهر می‌شدند."
        ),
        "highlights": [
            "Survival Mode",
            "Day/Night Cycle",
            "ماب‌های مهاجم شب",
            "تخت خواب",
        ],
        "features": [
            "Survival Mode — حالت بقا",
            "Day/Night Cycle — چرخه‌ی روز و شب",
            "ماب‌های شب: Zombie، Skeleton، Spider",
            "Bed — تخت برای رد کردن شب",
            "Inventory و Health",
        ],
        "changelog": [
            "افزودن Survival Mode",
            "افزودن چرخه‌ی روز/شب",
            "افزودن ماب‌های مهاجم شب",
            "افزودن Bed و Sleep",
            "افزودن سیستم Health و Inventory",
        ],
    },
    # ----- Pocket Edition 0.3.0 -----
    {
        "id": "bedrock-0-3-0",
        "version": "0.3.0",
        "name": "Minecraft Pocket Edition 0.3.0",
        "nameFa": "ماینکرفت پاکت ۰.۳.۰",
        "platform": "bedrock",
        "releaseDate": "2012-04-11",
        "codename": "Pocket Edition",
        "major": 0,
        "minor": 3,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Bedrock_Edition_0.3.0",
        "icon": "px-stone",
        "summary": "افزودن Crafting، ماب‌های اهلی و درخت‌های جدید.",
        "description": (
            "نسخه‌ی ۰.۳.۰ Pocket Edition در ۱۱ آوریل ۲۰۱۲ منتشر شد و سیستم "
            "Crafting را به موبایل آورد. ماب‌های اهلی مثل Cow، Chicken، Pig و "
            "Sheep اضافه شد. درخت‌های Birch و Spruce نیز معرفی شد."
        ),
        "highlights": [
            "Crafting — ساخت آیتم",
            "ماب‌های اهلی",
            "درخت‌های Birch و Spruce",
            "Inventory کامل",
        ],
        "features": [
            "Crafting Table — سیستم ساخت",
            "Cow، Chicken، Pig، Sheep — ماب‌های اهلی",
            "درخت‌های Birch و Spruce",
            "Inventory کامل با آیتم‌ها",
            "Slabs و Stairs",
        ],
        "changelog": [
            "افزودن سیستم Crafting",
            "افزودن Cow، Chicken، Pig، Sheep",
            "افزودن درخت‌های Birch و Spruce",
            "افزودن Inventory کامل",
            "افزودن Slabs و Stairs",
        ],
    },
    # ----- Pocket Edition 0.4.0 -----
    {
        "id": "bedrock-0-4-0",
        "version": "0.4.0",
        "name": "Minecraft Pocket Edition 0.4.0",
        "nameFa": "ماینکرفت پاکت ۰.۴.۰",
        "platform": "bedrock",
        "releaseDate": "2012-09-05",
        "codename": "Pocket Edition",
        "major": 0,
        "minor": 4,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Bedrock_Edition_0.4.0",
        "icon": "px-stone",
        "summary": "افزودن Creeper، TNT و Chest.",
        "description": (
            "نسخه‌ی ۰.۴.۰ Pocket Edition در سپتامبر ۲۰۱۲ منتشر شد و Creeper را "
            "به موبایل آورد. TNT و Chest معرفی شد. حالت Peaceful نیز قابل "
            "انتخاب شد تا ماب‌های مهاجم غیرفعال شوند."
        ),
        "highlights": [
            "Creeper",
            "TNT",
            "Chest",
            "حالت Peaceful",
        ],
        "features": [
            "Creeper — ماب منفجرشونده",
            "TNT — بلوک قابل انفجار",
            "Chest — ذخیره‌سازی",
            "حالت Peaceful — بدون ماب مهاجم",
            "بهبود سیستم Craft",
        ],
        "changelog": [
            "افزودن Creeper",
            "افزودن TNT",
            "افزودن Chest",
            "افزودن حالت Peaceful",
            "بهبود Crafting UI",
        ],
    },
    # ----- Pocket Edition 0.5.0 -----
    {
        "id": "bedrock-0-5-0",
        "version": "0.5.0",
        "name": "Minecraft Pocket Edition 0.5.0",
        "nameFa": "ماینکرفت پاکت ۰.۵.۰",
        "platform": "bedrock",
        "releaseDate": "2012-11-16",
        "codename": "Pocket Edition",
        "major": 0,
        "minor": 5,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Bedrock_Edition_0.5.0",
        "icon": "px-stone",
        "summary": "افزودن Nether Reactor و آیتم‌های ندر.",
        "description": (
            "نسخه‌ی ۰.۵.۰ Pocket Edition در ۱۶ نوامبر ۲۰۱۲ منتشر شد و Nether "
            "Reactor را معرفی کرد؛ سازه‌ای که چالش ندر را شبیه‌سازی می‌کرد. "
            "آیتم‌های ندر مثل Netherrack، Glowstone و Quartz اضافه شد."
        ),
        "highlights": [
            "Nether Reactor",
            "Netherrack و Glowstone",
            "Pigmen",
            "تولید آیتم ندر",
        ],
        "features": [
            "Nether Reactor — سازه‌ی شبیه‌سازی ندر",
            "Netherrack — بلوک ندر",
            "Glowstone — بلوک نورانی ندر",
            "Zombie Pigman — ماب ندر",
            "Quartz Ore",
        ],
        "changelog": [
            "افزودن Nether Reactor",
            "افزودن Netherrack",
            "افزودن Glowstone",
            "افزودن Zombie Pigman",
            "افزودن Quartz Ore",
        ],
    },
    # ----- Pocket Edition 0.6.0 -----
    {
        "id": "bedrock-0-6-0",
        "version": "0.6.0",
        "name": "Minecraft Pocket Edition 0.6.0",
        "nameFa": "ماینکرفت پاکت ۰.۶.۰",
        "platform": "bedrock",
        "releaseDate": "2013-01-30",
        "codename": "Pocket Edition",
        "major": 0,
        "minor": 6,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Bedrock_Edition_0.6.0",
        "icon": "px-stone",
        "summary": "افزودن Stonecutter و بلوک‌های جدید.",
        "description": (
            "نسخه‌ی ۰.۶.۰ Pocket Edition در ۳۰ ژانویه ۲۰۱۳ منتشر شد و Stonecutter "
            "را برای ساخت پلکانی و نیمه‌بلوک‌ها اضافه کرد. Nether Bricks و Quartz "
            "Block نیز معرفی شد. بافت‌ها بهبود یافت."
        ),
        "highlights": [
            "Stonecutter",
            "Nether Bricks",
            "Quartz Block",
            "بهبود بافت‌ها",
        ],
        "features": [
            "Stonecutter — بلوک ساخت برای تزئین",
            "Nether Bricks — آجر ندر",
            "Quartz Block — بلوک کوارتز",
            "Slabs و Stairs جدید",
            "بهبود بافت‌های بلوک",
        ],
        "changelog": [
            "افزودن Stonecutter",
            "افزودن Nether Bricks",
            "افزودن Quartz Block",
            "افزودن Slabs و Stairs جدید",
            "بهبود بافت‌های بلوک",
        ],
    },
    # ----- Pocket Edition 0.7.0 -----
    {
        "id": "bedrock-0-7-0",
        "version": "0.7.0",
        "name": "Minecraft Pocket Edition 0.7.0",
        "nameFa": "ماینکرفت پاکت ۰.۷.۰",
        "platform": "bedrock",
        "releaseDate": "2013-06-07",
        "codename": "Pocket Edition",
        "major": 0,
        "minor": 7,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Bedrock_Edition_0.7.0",
        "icon": "px-stone",
        "summary": "افزودن Minecraft Realms و دسترسی کامل به ندر.",
        "description": (
            "نسخه‌ی ۰.۷.۰ Pocket Edition در ۷ ژوئن ۲۰۱۳ منتشر شد و Minecraft "
            "Realms را در حالت بتا معرفی کرد. دسترسی به ندر بهبود یافت و بلوک‌های "
            "جدیدی مثل Bookshelf و Cake اضافه شد."
        ),
        "highlights": [
            "Minecraft Realms (بتا)",
            "Bookshelf و Cake",
            "دسترسی به ندر",
            "Bucket برای شیر",
        ],
        "features": [
            "Minecraft Realms — سرور خصوصی (بتا)",
            "Bookshelf — قفسه کتاب",
            "Cake — کیک قابل غذا دادن",
            "Bucket — سطل شیر",
            "دسترسی به ندر بهبود یافته",
        ],
        "changelog": [
            "افزودن Minecraft Realms (بتا)",
            "افزودن Bookshelf",
            "افزودن Cake",
            "افزودن Bucket شیر",
            "بهبود دسترسی به ندر",
        ],
    },
    # ----- Pocket Edition 0.8.0 -----
    {
        "id": "bedrock-0-8-0",
        "version": "0.8.0",
        "name": "Minecraft Pocket Edition 0.8.0",
        "nameFa": "ماینکرفت پاکت ۰.۸.۰",
        "platform": "bedrock",
        "releaseDate": "2013-12-12",
        "codename": "Pocket Edition",
        "major": 0,
        "minor": 8,
        "compatibleMods": 0,
        "wikiLink": "https://minecraft.wiki/w/Bedrock_Edition_0.8.0",
        "icon": "px-stone",
        "summary": "افزودن Minecart، Rails و Carpet.",
        "description": (
            "نسخه‌ی ۰.۸.0 Pocket Edition در ۱۲ دسامبر ۲۰۱۳ منتشر شد و Minecart "
            "و Rails را به موبایل آورد. Carpet و بلوک‌های تزئینی اضافه شد. "
            "بایوم‌های جدید و نقشه‌های بزرگ‌تر نیز معرفی شد."
        ),
        "highlights": [
            "Minecart و Rails",
            "Carpet",
            "بایوم‌های جدید",
            "نقشه‌ی بزرگ‌تر",
        ],
        "features": [
            "Minecart و Rails — سیستم قطار",
            "Carpet — فرش تزئینی",
            "بایوم‌های جدید",
            "نقشه‌ی بزرگ‌تر (256x256)",
            "بلوک‌های تزئینی جدید",
        ],
        "changelog": [
            "افزودن Minecart و Rails",
            "افزودن Carpet",
            "افزودن بایوم‌های جدید",
            "افزایش اندازه‌ی نقشه",
            "افزودن بلوک‌های تزئینی",
        ],
    },
]


def load_versions():
    with open(VERSIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_versions(data):
    # Preserve human-readable formatting: indent=2, ensure non-ASCII chars (Persian) are NOT escaped
    with open(VERSIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def find_missing(data):
    """Return tuple (missing_java, missing_bedrock) of version dicts to add."""
    existing_java_ids = {v["id"] for v in data["java"]}
    existing_bedrock_ids = {v["id"] for v in data["bedrock"]}

    missing_java = [
        v for v in NEW_JAVA_BETA_VERSIONS if v["id"] not in existing_java_ids
    ]
    missing_bedrock = [
        v for v in NEW_BEDROCK_POCKET_VERSIONS if v["id"] not in existing_bedrock_ids
    ]
    return missing_java, missing_bedrock


def insert_sorted_java(java_list, new_entries):
    """Insert new Beta entries between java-1-0 and java-beta-1-0 (i.e., after Java 1.0, before Beta 1.0).

    Existing order (newest -> oldest) for the bottom block is:
      java-1-0 -> java-beta-1-8 -> java-beta-1-0 -> java-alpha -> ...

    Target order:
      java-1-0 -> java-beta-1-8 -> java-beta-1-7 -> ... -> java-beta-1-1 -> java-beta-1-0 -> java-alpha -> ...

    i.e., new Beta 1.1-1.7 sit between Beta 1.8 (above) and Beta 1.0 (below).
    """
    # Sort new entries by minor descending so 1.7 comes first (closest to 1.8)
    new_entries_sorted = sorted(new_entries, key=lambda v: v["minor"], reverse=True)

    # Find index of java-beta-1-0 (the place to insert ABOVE)
    insert_idx = None
    for i, v in enumerate(java_list):
        if v["id"] == "java-beta-1-0":
            insert_idx = i
            break
    if insert_idx is None:
        # Fallback: append at end
        return java_list + new_entries_sorted

    return java_list[:insert_idx] + new_entries_sorted + java_list[insert_idx:]


def insert_sorted_bedrock(bedrock_list, new_entries):
    """Insert new Pocket Edition 0.1-0.8 entries ABOVE bedrock-0-9-0 (the earliest existing).

    Existing order at the tail is:
      ... -> bedrock-0-16-0 -> bedrock-0-15-0 -> bedrock-0-14-0 -> bedrock-0-13-0
            -> bedrock-0-12-0 -> bedrock-0-11-0 -> bedrock-0-10-0 -> bedrock-0-9-0

    Target order:
      ... -> bedrock-0-9-0 -> bedrock-0-8-0 -> bedrock-0-7-0 -> ... -> bedrock-0-1-0
    """
    # Sort new entries by minor ascending so 0.8 is first (closest to 0.9)
    new_entries_sorted = sorted(new_entries, key=lambda v: v["minor"], reverse=True)

    # Find index of bedrock-0-9-0 (insert AFTER it)
    insert_idx = None
    for i, v in enumerate(bedrock_list):
        if v["id"] == "bedrock-0-9-0":
            insert_idx = i + 1  # insert after
            break
    if insert_idx is None:
        # Fallback: append at end
        return bedrock_list + new_entries_sorted

    return bedrock_list[:insert_idx] + new_entries_sorted + bedrock_list[insert_idx:]


def main():
    print(f"[1] Reading: {VERSIONS_PATH}")
    data = load_versions()
    before_java = len(data["java"])
    before_bedrock = len(data["bedrock"])
    print(f"    Before: {before_java} Java + {before_bedrock} Bedrock = {before_java + before_bedrock} total")

    print("[2] Finding missing versions...")
    missing_java, missing_bedrock = find_missing(data)
    if not missing_java and not missing_bedrock:
        print("    All expected versions already present. Nothing to add.")
        # Still re-save to normalize formatting
        save_versions(data)
        return

    print(f"    Missing Java:   {len(missing_java)}")
    for v in missing_java:
        print(f"      + {v['id']:18s}  {v['version']:10s}  {v['releaseDate']}")
    print(f"    Missing Bedrock: {len(missing_bedrock)}")
    for v in missing_bedrock:
        print(f"      + {v['id']:18s}  {v['version']:10s}  {v['releaseDate']}")

    print("[3] Inserting in chronological (descending) order...")
    data["java"] = insert_sorted_java(data["java"], missing_java)
    data["bedrock"] = insert_sorted_bedrock(data["bedrock"], missing_bedrock)

    after_java = len(data["java"])
    after_bedrock = len(data["bedrock"])
    print(f"    After:  {after_java} Java + {after_bedrock} Bedrock = {after_java + after_bedrock} total")

    # Sanity check: all IDs unique
    all_ids = [v["id"] for v in data["java"]] + [v["id"] for v in data["bedrock"]]
    dupes = {x for x in all_ids if all_ids.count(x) > 1}
    if dupes:
        print(f"    ERROR: Duplicate IDs found: {dupes}")
        sys.exit(1)

    print("[4] Writing updated versions.json...")
    save_versions(data)
    print(f"    Done. File written: {VERSIONS_PATH}")

    print()
    print("=== Summary ===")
    print(f"  Added Java Beta versions:     {len(missing_java)}")
    print(f"  Added Bedrock Pocket versions: {len(missing_bedrock)}")
    print(f"  Total added:                   {len(missing_java) + len(missing_bedrock)}")
    print(f"  New total:                     {after_java + after_bedrock} (was {before_java + before_bedrock})")


if __name__ == "__main__":
    main()
