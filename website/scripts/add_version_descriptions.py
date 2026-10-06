#!/usr/bin/env python3
"""
Add `features` and `changelog` arrays to all 78 versions in src/data/versions.json.
Uses real Minecraft knowledge (version 1.14 = Village & Pillage, etc.).
Correct Persian translations: Nether = ندر, End = اند, Bedrock = بدراک, Redstone = رداستون.

Only adds fields if they are missing; existing `description` and `highlights`
are preserved.
"""
import json
from pathlib import Path

VERSIONS_FILE = Path(__file__).resolve().parent.parent / "src" / "data" / "versions.json"

# ---------------------------------------------------------------------------
# Per-version data.  Keyed by version id (e.g. "java-1-21", "bedrock-1-21-50").
# Each entry provides `features` (3-5) and `changelog` (3-5) in Persian.
# ---------------------------------------------------------------------------
VERSION_DATA = {
    # =====================================================================
    # JAVA EDITION
    # =====================================================================
    "java-26-3": {
        "features": [
            "Wilderness Camp — ساختار جدید کمپینگ با امکان اسکان کردن",
            "Quick Travel Rope — ابزار پرتاب‌ون برای سفر سریع بین کمپ‌ها",
            "Trail Marking با Banner — سیستم نشانه‌گذاری مسیرها",
            "Crystalline Caves — بیوم غاری جدید با کریستال‌های درخشان",
            "سیستم آب‌وهوای پویا با باران، برف و طوفان‌های فصلی"
        ],
        "changelog": [
            "افزودن بلوک Wilderness Camp و Quick Travel Rope",
            "افزودن بیوم Crystalline Caves در اعماق زمین",
            "افزودن سیستم Trail Marking با Banner",
            "بازطراحی سیستم آب‌وهوای پویا",
            "بازطراحی بیوم‌های وحشی با تنوع بیشتر"
        ]
    },
    "java-26-2": {
        "features": [
            "Cogwheel — بلوک منطقی جدید برای انتقال سیگنال رداستون",
            "Logic Gate Block — دروازه‌های AND/OR/XOR برای ساخت مدارهای پیچیده",
            "Redstone Dust بازطراحی‌شده با قابلیت تنظیم شدت سیگنال",
            "Scrap Block — قطعات خرد شده برای منطق ضعیف‌تر",
            "Comparator بازطراحی‌شده با حالت‌های جدید"
        ],
        "changelog": [
            "افزودن بلوک Cogwheel و Logic Gate Block",
            "بازطراحی Redstone Dust با شدت سیگنال متغیر",
            "افزودن Scrap Block برای منطق ضعیف‌تر",
            "بهبود Comparator با حالت‌های جدید",
            "رفع اشکال فراوان در سیستم رداستون"
        ]
    },
    "java-26-1": {
        "features": [
            "Bee Queen — ماب جدید رهبر زنبورها با قابلیت تولید عسل ویژه",
            "Mini Village — دهکده‌ی مینیاتوری با ویلجرهای کوچک",
            "Tiny Slime — اسلایم کوچک با رفتار دوستانه",
            "انیمیشن‌های جمع‌وجور برای تمام ماب‌ها",
            "سیستم Miniaturization برای تبدیل ابزارها به حالت کوچک"
        ],
        "changelog": [
            "افزودن ماب Bee Queen و Mini Village",
            "افزودن Tiny Slime با رفتار دوستانه",
            "افزودن انیمیشن‌های مینیاتوری برای ماب‌ها",
            "افزودن سیستم Miniaturization",
            "رفع اشکال فراوان و بهبود عملکرد"
        ]
    },
    "java-1-21": {
        "features": [
            "Trial Chambers — ساختارهای زیرزمینی با چالش‌های پویا و پاداش",
            "Breeze — ماب جدید با حملات بادی پرتاب‌کننده",
            "Mace — سلاح جدید با آسیب خنثی‌کننده و افزایش آسیب از ارتفاع",
            "Crafter — بلوک کرافت خودکار با رداستون",
            "Armadillo — ماب جدید با سپانه‌های محکم و Wolf Variants"
        ],
        "changelog": [
            "افزودن Trial Chambers و Trial Spawner",
            "افزودن ماب Breeze و Wind Charge",
            "افزودن سلاح Mace با انیمیشن smash",
            "افزودن بلوک Crafter برای کرافت خودکار",
            "افزودن Armadillo و Wolf Variants گوناگون"
        ]
    },
    "java-1-20": {
        "features": [
            "Cherry Blossom Biome — بیوم جدید با درختان شکوفه‌های صورتی",
            "Bamboo Wood Set — چوب بامبو کامل با پلانک، حصار و در",
            "سیستم Archaeology با Brush برای کاوش در خاک‌های باستانی",
            "Hanging Signs — تابلوهای آویزان با ظاهر متنوع",
            "Armor Trims — الگوهای تزئینی برای زره‌ها"
        ],
        "changelog": [
            "افزودن Cherry Blossom Biome و Bamboo Wood Set",
            "افزودن سیستم Archaeology با Brush و Suspicious Sand",
            "افزودن Hanging Signs و Bamboo Blocks",
            "افزودن Armor Trims با ۱۱ الگو",
            "افزودن Calibrated Sculk Sensor"
        ]
    },
    "java-1-19": {
        "features": [
            "Deep Dark Biome — بیوم ترسناک در اعماق زمین با Sculk",
            "Warden — قوی‌ترین ماب بازی با گوش حاد و نابینایی",
            "Mangrove Swamp — بیوم مردابی با درختان منگرو",
            "Allay — موجود کوچک که آیتم جمع می‌کند",
            "Frog و Tadpoles — قورباغه و بچه‌قورباغه با بیوم‌های متنوع"
        ],
        "changelog": [
            "افزودن Deep Dark Biome و Warden",
            "افزودن Mangrove Swamp با درختان منگرو",
            "افزودن موجود Allay برای جمع‌آوری آیتم",
            "افزودن Frog، Tadpoles و Froglight",
            "افزودن Echo Shards و Recovery Compass"
        ]
    },
    "java-1-18": {
        "features": [
            "World Generation جدید با ارتفاع ۳۸۴ بلوک (از -۶۴ تا ۳۲۰)",
            "Lush Caves — غارهای سرسبز با گیاهان و درختان",
            "Dripstone Caves — غارهای استالاکتیتی با Pointed Dripstone",
            "بیوم Meadow، Grove و Snowy Slopes",
            "عمق غارها به -۶۴ بلوک"
        ],
        "changelog": [
            "افزودن World Generation جدید با ارتفاع ۳۸۴ بلوک",
            "افزودن Lush Caves و Dripstone Caves",
            "افزودن بیوم Meadow، Grove و Snowy Slopes",
            "افزودن Amethyst Geodes و Large Ore Veins",
            "افزودن Copper Ore در سطح زمین"
        ]
    },
    "java-1-17": {
        "features": [
            "Copper Block — بلوک جدید که با گذشت زمان رنگش تغییر می‌کند",
            "Amethyst Geodes — ساختارهای کریستالی در اعماق زمین",
            "Lightning Rod — میله صاعقه‌گیر برای جذب صاعقه",
            "موجودات Axolotl و Goat با رفتارهای جدید",
            "Powder Snow — برف نرم که ماب‌ها را فرو می‌برد"
        ],
        "changelog": [
            "افزودن Copper Block و_cut Copper variants",
            "افزودن Amethyst Geodes و Budding Amethyst",
            "افزودن Lightning Rod و Spyglass",
            "افزودن Axolotl، Goat و Glow Squid",
            "افزودن Powder Snow و Deepslate Ore"
        ]
    },
    "java-1-16": {
        "features": [
            "بیوم‌های متنوع ندر: Crimson Forest، Warped Forest، Soulsand Valley",
            "Piglins — موجودات قابل تجارت و حملات",
            "Netherite — مادون قوی‌تر از Diamond",
            "Respawn Anchor — بستر تولد در ندر",
            "Bastion Remnants — ساختارهای جدید در ندر"
        ],
        "changelog": [
            "افزودن بیوم‌های ندر: Crimson Forest، Warped Forest، Soulsand Valley، Basalt Deltas",
            "افزودن Piglins، Hoglins و Striders",
            "افزودن Netherite و قاب upgrade",
            "افزودن Respawn Anchor و Crying Obsidian",
            "افزودن Bastion Remnants و Ruined Portals"
        ]
    },
    "java-1-15": {
        "features": [
            "Bee — زنبور جدید با رفتار群体ی",
            "Bee Hive و Bee Nest — کندو و لانه‌ی زنبورها",
            "Honey Bottle و Honey Block — آیتم‌های جدید از عسل",
            "Honey Block با خاصیت چسبندگی برای ماشین‌های رداستون",
            "رفع اشکال فراوان و بهبود عملکرد (Flattening)"
        ],
        "changelog": [
            "افزودن Bee و Bee Hive و Bee Nest",
            "افزودن Honey Bottle و Honey Block",
            "افزودن Honeycomb و Honeycomb Block",
            "بازطراحی سیستم دیتا (Flattening)",
            "رفع اشکال فراوان و بهبود عملکرد"
        ]
    },
    "java-1-14": {
        "features": [
            "بازطراحی کامل دهکده‌ها با ظاهر مختص هر بیوم",
            "Pillager و Pillager Outpost — دشمنان جدید",
            "Crossbow — سلاح جدید با مهمات متنوع",
            "Bamboo و Scaffolding برای ساخت سازه",
            "Village Features جدید با کارگران (Mason، Fletcher، و غیره)"
        ],
        "changelog": [
            "بازطراحی کامل دهکده‌ها با ۱۲ سبک بیومی",
            "افزودن Pillager و Pillager Outpost",
            "افزودن Crossbow و سه نوع پیکان (Rocket، Poison، Weakness)",
            "افزودن Bamboo و Scaffolding",
            "افزودن Village Features جدید با کارگران"
        ]
    },
    "java-1-13": {
        "features": [
            "اقیانوس‌های بازطراحی‌شده با Coral Reefs و Kelp Forest",
            "Dolphin و Turtle — موجودات دریایی جدید",
            "Drowned — زامبی زیرآبی با Trident",
            "Trident — سلاح جدید قابل پرتاب و شارژ",
            "Conduit — بلوک زیرآبی برای تنفس و آسیب"
        ],
        "changelog": [
            "بازطراحی اقیانوس‌ها با Coral و Kelp و Sea Grass",
            "افزودن Dolphin، Turtle و Drowned",
            "افزودن Trident با enchant های Riptide، Loyalty، Channeling، Impaling",
            "افزودن Conduit و Heart of the Sea",
            "افزودن Shipwrecks و Ocean Ruins و Buried Treasure"
        ]
    },
    "java-1-12": {
        "features": [
            "۱۶ رنگ Concrete و Concrete Powder",
            "Glazed Terracotta — ۱۶ نوع بلوک تزئینی با الگو",
            "Parrot — ماب رنگارنگی که روی شانه می‌نشیند",
            "Recipe Book — کتاب دستورالعمل در Crafting Table",
            "Bed شارژ شده با رنگ‌های جدید"
        ],
        "changelog": [
            "افزودن ۱۶ رنگ Concrete و Concrete Powder",
            "افزودن Glazed Terracotta با ۱۶ الگو",
            "افزودن Parrot به جنگل‌ها",
            "افزودن Recipe Book در Crafting Table",
            "بازطراحی Color System با کد ۱۶"
        ]
    },
    "java-1-11": {
        "features": [
            "Woodland Mansion — ساختار نادر در جنگل تاریک",
            "Llama — ماب جدید برای حمل بار در کاروان",
            "Shulker Box — جعبه با فضای ذخیره‌سازی",
            "Observer Block — بلوک رداستون برای تشخیص تغییرات",
            "Cartographer Villager — ویلجر جدید با نقشه‌ی ساختارها"
        ],
        "changelog": [
            "افزودن Woodland Mansion و Totem of Undying",
            "افزودن Llama و Caravan system",
            "افزودن Shulker Box با ۱۶ رنگ",
            "افزودن Observer Block",
            "افزودن Cartographer Villager و Woodland Explorer Map"
        ]
    },
    "java-1-10": {
        "features": [
            "Polar Bear — ماب جدید در مناطق یخی",
            "Stray — اسکلت یخی با اسلحه",
            "Structure Block — بلوک سازندگان برای کپی/جابجایی",
            "Igloo — ساختار یخی با زیرزمینه‌ی مخفی",
            "Magma Block — بلوک جدید در ندر"
        ],
        "changelog": [
            "افزودن Polar Bear به مناطق یخی",
            "افزودن Stray و Husk",
            "افزودن Structure Block برای Map Makers",
            "افزودن Igloo با Silverfish spawner",
            "افزودن Magma Block و Bone Block"
        ]
    },
    "java-1-9": {
        "features": [
            "سیستم Combat جدید با Cool Down برای حملات",
            "Shield — سپر برای دفاع در دست دوم",
            "Elytra — بال برای پرواز در اند",
            "End City — ساختار جدید در اند با Shulker",
            "بوابات اند جدید با اندر دراگن قابل احیا"
        ],
        "changelog": [
            "افزودن Cool Down و cooldown برای حملات",
            "افزودن Shield در دست دوم",
            "افزودن Elytra برای پرواز",
            "افزودن End City و Shulker",
            "افزودن سیستم Respawn Ender Dragon"
        ]
    },
    "java-1-8": {
        "features": [
            "Ocean Monument — ساختار جدید در اقیانوس",
            "Guardian و Elder Guardian — موجودات دریایی جدید",
            "Rabbit — ماب کوچک در بیوم‌های متنوع",
            "Slime Block — بلوک چسبناک با عملکرد رداستون",
            "Spectator Mode — حالت تماشا برای سازندگان"
        ],
        "changelog": [
            "افزودن Ocean Monument و Guardian و Elder Guardian",
            "افزودن Rabbit با ۶ نوع",
            "افزودن Slime Block برای ماشین‌های رداستون",
            "افزودن Spectator Mode",
            "افزودن Underwater Ruins و Desert Temple"
        ]
    },
    "java-1-7": {
        "features": [
            "بازطراحی World Generation با بیوم‌های فراوان",
            "بیوم جدید Savanna، Mesa، Extreme Hills و Deep Ocean",
            "سیستم Fishing بهبودیافته با Loot",
            "افزودن قابلیت‌های جدید Map Maker",
            "Achievement Commands برای ادمین‌ها"
        ],
        "changelog": [
            "بازطراحی World Generation با بیوم‌های جدید",
            "افزودن Savanna، Mesa، Extreme Hills",
            "بهبود سیستم Fishing با Loot Tables",
            "افزودن资源和 Achievement Commands",
            "افزودن Resource Pack System"
        ]
    },
    "java-1-6": {
        "features": [
            "Horse و Donkey — ماب‌های جدید برای سوار شدن",
            "سیستم زین و اسب‌سواری کامل",
            "Hay Block و Carpet — بلوک‌های جدید",
            "Resource Pack — سیستم پک‌های منابع",
            "Mule — قاطر برای حمل بار"
        ],
        "changelog": [
            "افزودن Horse، Donkey و Mule",
            "افزودن سیستم زین و Horse Armor",
            "افزودن Hay Block و Carpet",
            "افزودن Resource Pack System",
            "افزودن Name Tag و Lead"
        ]
    },
    "java-1-5": {
        "features": [
            "Redstone Comparator — بلوک منطقی پیشرفته",
            "Daylight Sensor — حسگر نور روز",
            "Block of Redstone — بلوک منبع سیگنال",
            "Hopper — قیف برای انتقال آیتم",
            "Nether Quartz و Comparator"
        ],
        "changelog": [
            "افزودن Redstone Comparator",
            "افزودن Daylight Sensor",
            "افزودن Block of Redstone",
            "افزودن Hopper و Dropper",
            "افزودن Nether Quartz و Quartz Block"
        ]
    },
    "java-1-4": {
        "features": [
            "Wither — باس جدید قابل احیا توسط بازیکن",
            "Anvil — بلوک تعمیر و تغییر نام ابزارها",
            "Flower Pot — گلدان برای تزیین",
            "Item Frame — قاب برای نمایش آیتم",
            "Wither Rose — گل جدید رشد پس از مرگ Wither"
        ],
        "changelog": [
            "افزودن ماب Wither و Nether Star",
            "افزودن Anvil برای تعمیر و تغییر نام",
            "افزودن Flower Pot و Item Frame",
            "افزودن Wither Rose و Cobweb قابل برداشت",
            "افزودن Vampire Bats و Witch"
        ]
    },
    "java-1-3": {
        "features": [
            "یکپارچه‌سازی Single-player و Multiplayer",
            "Trading با دهکده‌نشینان",
            "Emerald — منبع جدید برای تجارت",
            "Ender Chest — صندوقی مشترک بین ابعاد",
            "Adventure Settings برای نقشه‌های ماجراجویی"
        ],
        "changelog": [
            "یکپارچه‌سازی کد Single-player با Multiplayer",
            "افزودن سیستم Trading با Villager",
            "افزودن Emerald و Emerald Ore",
            "افزودن Ender Chest",
            "افزودن Adventure Mode و Command Block"
        ]
    },
    "java-1-2": {
        "features": [
            "Iron Golem — ماب محافظ دهکده",
            "Ocelot — گربه‌ی وحشی در جنگل",
            "Jungle Biome — بیوم گرم و مرطوب",
            "Redstone Lamp — لامپ با سیگنال رداستون",
            "ارتفاع بازی به ۲۵۶ بلوک افزایش یافت"
        ],
        "changelog": [
            "افزودن Iron Golem و Ocelot",
            "افزودن Jungle Biome با درختان بزرگ",
            "افزودن Redstone Lamp",
            "افزایش ارتفاع بازی به ۲۵۶ بلوک",
            "افزودن Chiseled Stone Brick و Wood Log variants"
        ]
    },
    "java-1-1": {
        "features": [
            "Spawn Egg — تخم احضار ماب‌ها در Creative",
            "Bow Enchant — افنت‌های Power و Flame",
            "Superflat World Type — نقشه‌ی تخت قابل تنظیم",
            "Large Biome — نقشه‌ی با بیوم‌های بزرگ",
            "پشتیبانی از زبان‌های اضافی"
        ],
        "changelog": [
            "افزودن Spawn Egg برای تمام ماب‌ها",
            "افزودن Bow Enchant: Power، Flame، Punch، Infinity",
            "افزودن Superflat World Type",
            "افزودن Large Biome World Type",
            "افزودن پشتیبانی از زبان‌های بیشتر"
        ]
    },
    "java-1-0": {
        "features": [
            "The End — بُعد جدید با Ender Dragon",
            "Brewing — سیستم دم‌کردن معجون‌ها",
            "Enchanting — سیستم افنت ابزارها",
            "Achievements — سیستم دستاوردها",
            "Nether Fortress — ساختار جدید در ندر"
        ],
        "changelog": [
            "افزودن The End و Ender Dragon",
            "افزودن Brewing Stand و Potions",
            "افزودن Enchanting Table و XP",
            "افزودن Achievement System",
            "افزودن Nether Fortress با Blazes"
        ]
    },
    "java-beta-1-8": {
        "features": [
            "Enderman — ماب بلندقامت با قابلیت جابجایی بلوک‌ها",
            "Creative Mode — حالت خلاقیت با آیتم‌های نامحدود",
            "سیستم Hunger — نوار غذا و خستگی",
            "Stronghold — ساختار زیرزمینی با End Portal",
            "End Portal Frame — قاب پرتال به اند"
        ],
        "changelog": [
            "افزودن Enderman",
            "افزودن Creative Mode با Inventory نامحدود",
            "افزودن سیستم Hunger و Regeneration",
            "افزودن Stronghold و End Portal",
            "افزودن Melon و vines و Mushroom Biome"
        ]
    },
    "java-beta-1-0": {
        "features": [
            "Server-side Inventory — همگام‌سازی آیتم با سرور",
            "Minecraft.net — پشتیبانی رسمی وب‌سایت",
            "Sneaking — قابلیت خم‌شدن",
            "Lava ریختن — فیزیک مایعات",
            "Statistics Tracking — ردیابی آمار بازی"
        ],
        "changelog": [
            "افزودن Server-side Inventory",
            "افزودن Minecraft.net authentication",
            "افزودن Sneaking و قابلیت خم‌شدن",
            "افزودن Lava ریختن قابل کنترل",
            "افزودن Statistics و Achievement framework"
        ]
    },
    "java-alpha": {
        "features": [
            "ندر — بُعد جدید با آتش و لاما",
            "Survival Multiplayer — بازی چندنفره Survival",
            "سیستم Biomes — بیوم‌های متنوع نقشه",
            "Snow Worlds — نقشه‌ی برفی",
            "Minecart و Boat — وسیله‌ی نقلیه"
        ],
        "changelog": [
            "افزودن ندر (Nether) با Ghasts و Zombie Pigmen",
            "افزودن Survival Multiplayer (SMP)",
            "افزودن سیستم Biomes",
            "افزودن Snow Worlds و Ice",
            "افزودن Minecart و Boat"
        ]
    },
    "java-infdev": {
        "features": [
            "نقشه‌ی بی‌نهایت — نقشه‌ی نامحدود به جای جزیره",
            "Caves و Lava — غارها و مواد مذاب",
            "Day/Night Cycle — چرخه‌ی روز و شب",
            "Stairs و Slabs — بلوک‌های پلکانی و نیمه",
            "Arrow و Bow — سیستم شلیک"
        ],
        "changelog": [
            "افزودن نقشه‌ی بی‌نهایت با World Generation",
            "افزودن Caves و Lava",
            "افزودن Day/Night Cycle",
            "افزودن Stairs و Slabs",
            "افزودن Bow و Arrow"
        ]
    },
    "java-indev": {
        "features": [
            "Crafting System — سیستم کرافت در بازی",
            "Inventory — کیف موجودی بازیکن",
            "TNT — ماده‌ی منفجره",
            "Day/Night Cycle — چرخه‌ی روز و شب",
            "Books و Bookshelves — کتاب و کتابخانه"
        ],
        "changelog": [
            "افزودن Crafting System با Recipe",
            "افزودن Inventory و Hotbar",
            "افزودن TNT و ماده‌ی منفجره",
            "افزودن Day/Night Cycle",
            "افزودن Books و Bookshelves"
        ]
    },
    "java-classic": {
        "features": [
            "نخستین نسخه‌ی عمومی ماینکرفت",
            "Creative-style gameplay با بلوک‌های نامحدود",
            "Multiplayer در نسخه‌ی 0.0.15a",
            "Survival Test بعدها اضافه شد",
            "Original 32 Block Types"
        ],
        "changelog": [
            "عرضه‌ی نخستین نسخه‌ی عمومی ماینکرفت",
            "افزودن Creative-style gameplay",
            "افزودن Multiplayer در نسخه‌ی 0.0.15a",
            "افزودن Survival Test",
            "افزودن 32 نوع بلوک ابتدایی"
        ]
    },

    # =====================================================================
    # BEDROCK EDITION
    # =====================================================================
    "bedrock-26-50": {
        "features": [
            "Wilderness Camp — کمپینگ جدید برای بازیکنان بدراک",
            "Quick Travel Rope — سفر سریع بین کمپ‌ها",
            "Trail Marking — سیستم نشانه‌گذاری مسیرها",
            "Crystalline Caves — غارهای کریستالی",
            "هماهنگی کامل با Java 26.3"
        ],
        "changelog": [
            "افزودن Wilderness Camp و Quick Travel Rope",
            "افزودن Crystalline Caves",
            "افزودن سیستم Trail Marking",
            "هماهنگی محتوا با Java 26.3",
            "رفع اشکال فراوان و بهبود عملکرد"
        ]
    },
    "bedrock-26-45": {
        "features": [
            "Cogwheel — بلوک منطقی بدراک",
            "Logic Gate Block — دروازه‌های منطقی",
            "Redstone Comparator بازطراحی‌شده",
            "Scrap Block برای منطق ضعیف‌تر",
            "هماهنگی با Java 26.2"
        ],
        "changelog": [
            "افزودن Cogwheel و Logic Gate Block",
            "بازطراحی Redstone Comparator",
            "افزودن Scrap Block",
            "هماهنگی محتوا با Java 26.2",
            "رفع اشکال و بهبود عملکرد"
        ]
    },
    "bedrock-1-21-80": {
        "features": [
            "Bundles — رسمی‌سازی باندل‌ها از حالت Experimental",
            "افزودن Armadillo به طور پیش‌فرض",
            "بهبود Wind Charge و Trial Chambers",
            "رفع اشکال فراوان",
            "بهبود عملکرد و ثبات"
        ],
        "changelog": [
            "رسمی‌سازی Bundles از Experimental",
            "افزودن Armadillo به طور پیش‌فرض",
            "بهبود Wind Charge و Trial Chambers",
            "رفع اشکال فراوان",
            "بهبود عملکرد و ثبات بازی"
        ]
    },
    "bedrock-1-21-70": {
        "features": [
            "Bundles (Experimental) — پیش‌نمایش باندل‌ها",
            "Wind Charge بهبودیافته",
            "Trial Chambers بهبودیافته",
            "رفع اشکال فراوان",
            "بهبود عملکرد"
        ],
        "changelog": [
            "افزودن Bundles به طور Experimental",
            "بهبود Wind Charge",
            "بهبود Trial Chambers",
            "رفع اشکال فراوان",
            "بهبود عملکرد"
        ]
    },
    "bedrock-1-21-60": {
        "features": [
            "درایور رداستون جدید",
            "Ticking Area بهبودیافته",
            "Wind Charge بهبودیافته",
            "رفع اشکال فراوان",
            "بهبود عملکرد"
        ],
        "changelog": [
            "افزودن درایور رداستون جدید",
            "بهبود Ticking Area",
            "بهبود Wind Charge",
            "رفع اشکال فراوان",
            "بهبود عملکرد بازی"
        ]
    },
    "bedrock-1-21-50": {
        "features": [
            "Trial Chambers — ساختارهای زیرزمینی با چالش پویا",
            "Armadillo — ماب جدید با سپانه",
            "Wind Charge — پرتابه‌ی بادی",
            "Breeze — ماب با حملات بادی",
            "Copper Bulb — لامپ مسی با رداستون"
        ],
        "changelog": [
            "افزودن Trial Chambers و Trial Spawner",
            "افزودن Armadillo و Wolf Variants",
            "افزودن Wind Charge و Breeze",
            "افزودن Copper Bulb و Crafter",
            "هماهنگی کامل با Java 1.21"
        ]
    },
    "bedrock-1-21-40": {
        "features": [
            "Trial Chambers (Experimental) — پیش‌نمایش ساختار جدید",
            "Armadillo (Experimental)",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI و کنترل‌ها"
        ],
        "changelog": [
            "افزودن Trial Chambers به طور Experimental",
            "افزودن Armadillo به طور Experimental",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI و کنترل‌ها"
        ]
    },
    "bedrock-1-21-30": {
        "features": [
            "هماهنگی با Java 1.21",
            "رفع اشکال فراوان",
            "بهبود Tomb و سینتک",
            "بهبود عملکرد",
            "بهبود UI و کنترل‌ها"
        ],
        "changelog": [
            "شروع هماهنگی با Java 1.21",
            "رفع اشکال فراوان",
            "بهبود Tomb و سینتک ماب",
            "بهبود عملکرد بازی",
            "بهبود UI و کنترل‌ها"
        ]
    },
    "bedrock-1-21-20": {
        "features": [
            "Wolf Variants (Experimental) — تنوع گرگ‌ها",
            "رفع اشکال فراوان",
            "بهبود Tomb",
            "بهبود عملکرد",
            "بهبود UI"
        ],
        "changelog": [
            "افزودن Wolf Variants به طور Experimental",
            "رفع اشکال فراوان",
            "بهبود Tomb",
            "بهبود عملکرد",
            "بهبود UI و کنترل‌ها"
        ]
    },
    "bedrock-1-21-0": {
        "features": [
            "Trial Chambers — ساختارهای زیرزمینی",
            "Armadillo — ماب جدید با سپانه",
            "Copper Bulb — لامپ مسی",
            "Wolf Variants — تنوع گرگ‌ها",
            "Crafter Block — بلوک کرافت خودکار"
        ],
        "changelog": [
            "افزودن Trial Chambers و Trial Spawner",
            "افزودن Armadillo و Wolf Variants",
            "افزودن Copper Bulb و Crafter",
            "افزودن Breeze و Wind Charge",
            "هماهنگی با Java 1.21"
        ]
    },
    "bedrock-1-20-80": {
        "features": [
            "بهبود Shield و سپر",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود Tomb"
        ],
        "changelog": [
            "رفع اشکال Shield",
            "رفع اشکال فراوان",
            "بهبود عملکرد بازی",
            "بهبود UI و کنترل‌ها",
            "بهبود Tomb"
        ]
    },
    "bedrock-1-20-70": {
        "features": [
            "Armadillo (Experimental) — ماب جدید با سپانه",
            "Wolf Variants — تنوع گرگ‌ها",
            "رفع اشکال فراوان",
            "بهبود Tomb",
            "بهبود عملکرد"
        ],
        "changelog": [
            "افزودن Armadillo به طور Experimental",
            "افزودن Wolf Variants",
            "رفع اشکال فراوان",
            "بهبود Tomb",
            "بهبود عملکرد بازی"
        ]
    },
    "bedrock-1-20-60": {
        "features": [
            "بهبود Ticking Area",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود Tomb"
        ],
        "changelog": [
            "بهبود Ticking Area",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود Tomb"
        ]
    },
    "bedrock-1-20-50": {
        "features": [
            "بهبود Shield",
            "رفع اشکال فراوان",
            "بهبود Tomb",
            "بهبود عملکرد",
            "بهبود UI"
        ],
        "changelog": [
            "بهبود Shield",
            "رفع اشکال فراوان",
            "بهبود Tomb",
            "بهبود عملکرد",
            "بهبود UI"
        ]
    },
    "bedrock-1-20-40": {
        "features": [
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود Tomb",
            "بهبود UI",
            "بهبود ثبات بازی"
        ],
        "changelog": [
            "رفع اشکال فراوان",
            "بهبود عملکرد بازی",
            "بهبود Tomb",
            "بهبود UI",
            "بهبود ثبات بازی"
        ]
    },
    "bedrock-1-20-30": {
        "features": [
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود Tomb",
            "بهبود ثبات"
        ],
        "changelog": [
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود Tomb",
            "بهبود ثبات بازی"
        ]
    },
    "bedrock-1-20-10": {
        "features": [
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود Tomb",
            "بهبود ثبات"
        ],
        "changelog": [
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود Tomb",
            "بهبود ثبات بازی"
        ]
    },
    "bedrock-1-20-0": {
        "features": [
            "Cherry Blossom Biome — بیوم شکوفه‌های صورتی",
            "Bamboo Set — چوب بامبو",
            "Archaeology با Brush — سیستم کاوش باستانی",
            "Hanging Signs — تابلوهای آویزان",
            "Armor Trims — الگوهای تزئینی زره"
        ],
        "changelog": [
            "افزودن Cherry Blossom Biome",
            "افزودن Bamboo Set",
            "افزودن Archaeology با Brush",
            "افزودن Hanging Signs",
            "افزودن Armor Trims"
        ]
    },
    "bedrock-1-19-80": {
        "features": [
            "Cherry Blossom (Experimental)",
            "Archaeology (Experimental)",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI"
        ],
        "changelog": [
            "افزودن Cherry Blossom به طور Experimental",
            "افزودن Archaeology به طور Experimental",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI"
        ]
    },
    "bedrock-1-19-70": {
        "features": [
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود Tomb",
            "بهبود ثبات بازی"
        ],
        "changelog": [
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود Tomb",
            "بهبود ثبات بازی"
        ]
    },
    "bedrock-1-19-60": {
        "features": [
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود Tomb",
            "بهبود ثبات بازی"
        ],
        "changelog": [
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود Tomb",
            "بهبود ثبات بازی"
        ]
    },
    "bedrock-1-19-50": {
        "features": [
            "Deep Dark — بیوم ترسناک در اعماق",
            "Warden — ماب قوی و نابینا",
            "Mangrove Swamp — بیوم مردابی",
            "Allay — موجود جمع‌آور آیتم",
            "Frog و Tadpoles — قورباغه و بچه‌قورباغه"
        ],
        "changelog": [
            "افزودن Deep Dark و Warden",
            "افزودن Mangrove Swamp",
            "افزودن Allay",
            "افزودن Frog و Tadpoles",
            "هماهنگی با Java 1.19"
        ]
    },
    "bedrock-1-18-30": {
        "features": [
            "World Generation جدید با ارتفاع ۳۸۴ بلوک",
            "Lush Caves — غارهای سرسبز",
            "Dripstone Caves — غارهای استالاکتیتی",
            "بیوم Meadow و Grove",
            "عمق غارها به -۶۴"
        ],
        "changelog": [
            "افزودن World Generation جدید",
            "افزودن Lush Caves و Dripstone Caves",
            "افزودن Meadow و Grove",
            "افزودن Amethyst Geodes",
            "افزودن Copper و Deepslate Ore"
        ]
    },
    "bedrock-1-17-40": {
        "features": [
            "Copper با رنگ‌پذیری زمان",
            "Amethyst Geodes",
            "Lightning Rod",
            "Axolotl و Goat",
            "Powder Snow"
        ],
        "changelog": [
            "افزودن Copper Block و cut variants",
            "افزودن Amethyst Geodes",
            "افزودن Lightning Rod و Spyglass",
            "افزودن Axolotl و Goat",
            "افزودن Powder Snow و Deepslate"
        ]
    },
    "bedrock-1-16-0": {
        "features": [
            "بیوم‌های متنوع ندر",
            "Piglins — موجودات قابل تجارت",
            "Netherite — مادون قوی‌تر از Diamond",
            "Respawn Anchor — بستر تولد در ندر",
            "Bastion Remnants"
        ],
        "changelog": [
            "افزودن بیوم‌های ندر (Crimson، Warped، Soulsand Valley، Basalt Deltas)",
            "افزودن Piglins، Hoglins و Striders",
            "افزودن Netherite و upgrade قاب",
            "افزودن Respawn Anchor و Crying Obsidian",
            "افزودن Bastion Remnants و Ruined Portals"
        ]
    },
    "bedrock-1-14-0": {
        "features": [
            "Bee — زنبور جدید",
            "Bee Hive و Bee Nest",
            "Honey Bottle و Honey Block",
            "رفع اشکال فراوان",
            "بهبود عملکرد"
        ],
        "changelog": [
            "افزودن Bee و Bee Hive",
            "افزودن Honey Bottle و Honey Block",
            "افزودن Honeycomb Block",
            "رفع اشکال فراوان",
            "بهبود عملکرد"
        ]
    },
    "bedrock-1-13-0": {
        "features": [
            "Foxes (Experimental) — روباه",
            "Light Block",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI"
        ],
        "changelog": [
            "افزودن Foxes به طور Experimental",
            "افزودن Light Block",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI"
        ]
    },
    "bedrock-1-12-0": {
        "features": [
            "Education Edition Features",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود کنترل‌ها"
        ],
        "changelog": [
            "افزودن Education Edition Features",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود کنترل‌ها"
        ]
    },
    "bedrock-1-11-0": {
        "features": [
            "بازطراحی دهکده‌ها با ۱۲ سبک بیومی",
            "Pillager و Pillager Outpost",
            "Crossbow — سلاح جدید",
            "Bamboo و Scaffolding",
            "Village Features با کارگران جدید"
        ],
        "changelog": [
            "بازطراحی دهکده‌ها",
            "افزودن Pillager و Pillager Outpost",
            "افزودن Crossbow و پیکان‌های متنوع",
            "افزودن Bamboo و Scaffolding",
            "افزودن Village Features با کارگران"
        ]
    },
    "bedrock-1-10-0": {
        "features": [
            "دهکده‌های جدید (Experimental)",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود ثبات"
        ],
        "changelog": [
            "افزودن دهکده‌های جدید به طور Experimental",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI",
            "بهبود ثبات"
        ]
    },
    "bedrock-1-9-0": {
        "features": [
            "Pillager (Experimental)",
            "Crossbow (Experimental)",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI"
        ],
        "changelog": [
            "افزودن Pillager به طور Experimental",
            "افزودن Crossbow به طور Experimental",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI"
        ]
    },
    "bedrock-1-8-0": {
        "features": [
            "Panda — ماب جدید در Bamboo Jungle",
            "گربه‌های جدید با تنوع",
            "Bamboo Jungle — بیوم جنگلی",
            "Structure Block",
            "رفع اشکال فراوان"
        ],
        "changelog": [
            "افزودن Panda و گربه‌های جدید",
            "افزودن Bamboo Jungle",
            "افزودن Structure Block",
            "افزودن Crossbow و Pillager",
            "رفع اشکال فراوان"
        ]
    },
    "bedrock-1-7-0": {
        "features": [
            "اقیانوس‌های بازطراحی‌شده",
            "Coral Reefs — صخره‌های مرجانی",
            "Kelp — جنگل‌های دریایی",
            "Dolphin و Turtle",
            "Drowned — زامبی زیرآبی"
        ],
        "changelog": [
            "بازطراحی اقیانوس‌ها",
            "افزودن Coral Reefs و Kelp",
            "افزودن Dolphin و Turtle",
            "افزودن Drowned و Trident",
            "افزودن Shipwrecks و Ocean Ruins"
        ]
    },
    "bedrock-1-6-0": {
        "features": [
            "Coral Reefs — صخره‌های مرجانی",
            "Drowned — زامبی زیرآبی",
            "Shipwrecks — کشتی‌های غرق‌شده",
            "Ocean Ruins — ویرانه‌های دریایی",
            "Conduit — بلوک زیرآبی"
        ],
        "changelog": [
            "افزودن Coral Reefs",
            "افزودن Drowned",
            "افزودن Shipwrecks و Ocean Ruins",
            "افزودن Conduit و Heart of the Sea",
            "افزودن Trident و Buried Treasure"
        ]
    },
    "bedrock-1-5-0": {
        "features": [
            "Coral — مرجان",
            "Kelp — جلبک دریایی",
            "Ocean Monument بهبودیافته",
            "Sea Turtle — لاک‌پشت دریایی",
            "رفع اشکال فراوان"
        ],
        "changelog": [
            "افزودن Coral و Coral Fans",
            "افزودن Kelp و Sea Grass",
            "بهبود Ocean Monument",
            "افزودن Sea Turtle",
            "رفع اشکال فراوان"
        ]
    },
    "bedrock-1-4-0": {
        "features": [
            "Coral (Experimental)",
            "Kelp (Experimental)",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI"
        ],
        "changelog": [
            "افزودن Coral به طور Experimental",
            "افزودن Kelp به طور Experimental",
            "رفع اشکال فراوان",
            "بهبود عملکرد",
            "بهبود UI"
        ]
    },
    "bedrock-1-2-0": {
        "features": [
            "Cross-platform Multiplayer بین Windows 10، Xbox، Mobile",
            "Recipe Book — کتاب دستورالعمل",
            "Host Options — تنظیمات میزبان",
            "Add-Ons — سیستم افزودنی‌ها",
            "New Mobs و Features"
        ],
        "changelog": [
            "افزودن Cross-platform Multiplayer",
            "افزودن Recipe Book",
            "افزودن Host Options",
            "افزودن Add-Ons System",
            "افزودن New Mobs و Features"
        ]
    },
    "bedrock-1-1-0": {
        "features": [
            "Woodland Mansion — ساختار نادر",
            "Llamas — ماب حمل بار",
            "Vindicator — ایلیجر تند",
            "Shulker Box (Creative)",
            "Off-hand Slot — اسلات دست فرعی"
        ],
        "changelog": [
            "افزودن Woodland Mansion",
            "افزودن Llamas و Caravan",
            "افزودن Vindicator و Evoker",
            "افزودن Shulker Box در Creative",
            "افزودن Off-hand Slot"
        ]
    },
    "bedrock-1-0-0": {
        "features": [
            "The End — بُعد جدید",
            "Ender Dragon — باس نهایی",
            "World Market — بازار آینده",
            "Boss Bar — نوار جان باس",
            "Big scarce dungeons"
        ],
        "changelog": [
            "افزودن The End و Ender Dragon",
            "افزودن World Market (بعداً Marketplace)",
            "افزودن Boss Bar",
            "افزودن Elytra و Shulker Shell",
            "افزودن End Cities و Chorus Plant"
        ]
    },
    "bedrock-0-16-0": {
        "features": [
            "Elder Guardian — باس جدید",
            "Wither — باس قابل احیا",
            "Slash Commands — فرامین نوار",
            "Add-Ons Preview",
            "Beacon — بلوک افکت‌بخش"
        ],
        "changelog": [
            "افزودن Elder Guardian و Ocean Monument",
            "افزودن Wither",
            "افزودن Slash Commands",
            "افزودن Add-Ons Preview",
            "افزودن Beacon و Hopper"
        ]
    },
    "bedrock-0-15-0": {
        "features": [
            "Horse و Donkey — ماب‌های سوار شونده",
            "Piston و Sticky Piston",
            "Realms — سرورهای اختصاصی",
            "Observer Block",
            "Mule — قاطر"
        ],
        "changelog": [
            "افزودن Horse، Donkey و Mule",
            "افزودن Piston و Sticky Piston",
            "افزودن Realms Multiplayer",
            "افزودن Observer Block",
            "افزودن Zombie Horse و Skeleton Horse"
        ]
    },
    "bedrock-0-14-0": {
        "features": [
            "Redstone Mechanics",
            "Minecart with Hopper",
            "Dropper و Dispenser",
            "Trapped Chest",
            "Item Frame"
        ],
        "changelog": [
            "افزودن Redstone Mechanics",
            "افزودن Minecart with Hopper",
            "افزودن Dropper و Dispenser",
            "افزودن Trapped Chest",
            "افزودن Item Frame"
        ]
    },
    "bedrock-0-13-0": {
        "features": [
            "Crafting در بازی (نه فقط در Crafting Table)",
            "Redstone Dust",
            "Pressure Plates",
            "Levers و Buttons",
            "Detector Rail"
        ],
        "changelog": [
            "افزودن Crafting در بازی با 2x2 grid",
            "افزودن Redstone Dust و Redstone Ore",
            "افزودن Pressure Plates",
            "افزودن Levers و Buttons",
            "افزودن Detector Rail و Activator Rail"
        ]
    },
    "bedrock-0-12-0": {
        "features": [
            "Nether — بُعد جدید با آتش",
            "Hunger System — نوار غذا",
            "Brewing — دم‌کردن معجون",
            "XP و Enchanting",
            "Ghasts و Blazes"
        ],
        "changelog": [
            "افزودن ندر با Ghasts و Zombie Pigmen",
            "افزودن Hunger System",
            "افزودن Brewing Stand و Potions",
            "افزودن XP و Enchanting Table",
            "افزودن Blazes و Magma Cube"
        ]
    },
    "bedrock-0-11-0": {
        "features": [
            "Skins System — پوسته‌های قابل تنظیم",
            "Fishing — سیستم ماهیگیری",
            "Cave Spider — عنکبوت غاری",
            "Zombie Pigman",
            "Boats — قایق"
        ],
        "changelog": [
            "افزودن Skins System با Custom Skins",
            "افزودن Fishing System",
            "افزودن Cave Spider",
            "افزودن Zombie Pigman",
            "افزودن Boats و Splash Potions"
        ]
    },
    "bedrock-0-10-0": {
        "features": [
            "Minecart — ماین‌کرت",
            "Glass Pane — شیشه‌ی نازک",
            "Render بهبودیافته",
            "Water Effects — افکت‌های آب",
            "Fire Brazing — افکت آتش"
        ],
        "changelog": [
            "افزودن Minecart و Rail",
            "افزودن Glass Pane",
            "بهبود Render و گرافیک",
            "افزودن Water Effects",
            "افزودن Fire Brazing"
        ]
    },
    "bedrock-0-9-0": {
        "features": [
            "نقشه‌ی بی‌نهایت — نقشه‌ی نامحدود",
            "Enderman",
            "Villager",
            "Minecart و Boat",
            "Caves"
        ],
        "changelog": [
            "افزودن نقشه‌ی بی‌نهایت",
            "افزودن Enderman",
            "افزودن Villager و Villager Zombie",
            "افزودن Minecart و Boat",
            "افزودن Caves و Lava"
        ]
    },
}


def main():
    data = json.loads(VERSIONS_FILE.read_text(encoding="utf-8"))

    updated = 0
    missing_keys = []

    for platform in ("java", "bedrock"):
        for version in data[platform]:
            vid = version["id"]
            if vid not in VERSION_DATA:
                missing_keys.append(vid)
                continue

            entry = VERSION_DATA[vid]
            if "features" not in version:
                version["features"] = entry["features"]
                updated += 1
            if "changelog" not in version:
                version["changelog"] = entry["changelog"]
                updated += 1

    if missing_keys:
        print("WARNING: Missing data for these version IDs:")
        for k in missing_keys:
            print(f"  - {k}")
    else:
        print("All version IDs have data ✓")

    # Save back to file
    VERSIONS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    total_versions = len(data["java"]) + len(data["bedrock"])
    print(f"Updated {updated} fields across {total_versions} versions.")
    print(f"File saved: {VERSIONS_FILE}")


if __name__ == "__main__":
    main()
