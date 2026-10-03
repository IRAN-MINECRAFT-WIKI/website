# MCIcons Audit — تحلیل کامل

**تاریخ:** 2026-10-03
**منبع:** [@klashdevelopment/mcicons](https://www.npmjs.com/package/@klashdevelopment/mcicons) v1.0.2
**سایت اصلی:** https://ccvaults.com/
**روش دسترسی:** npm package → JS module → {low_url, high_url} on ccvaults.com CDN

## 📊 خلاصه‌ی ۱۲ دسته

| # | دسته | تعداد | رسمی vanilla؟ | نتیجه |
|---|---|---|---|---|
| ۱ | **Items** | ۱۰۷۴ | ✅ بله | قابل استفاده |
| ۲ | **Mobs** | ۳۵۹ | ⚠️ مخلوط | فقط vanillaها |
| ۳ | **Structures** | ۴۷۵ | ✅ بله | قابل استفاده |
| ۴ | **Blocks** | ۸۰۷ | ✅ بله | قابل استفاده |
| ۵ | **Paintings** | ۴۹ | ✅ بله | قابل استفاده |
| ۶ | **modded_weapons** | ۹۵ | ❌ **هیچ‌کدام!** | **استفاده نکن** |
| ۷ | **icons** | ۱۳۵ | ⚠️ MC Dungeons | فقط اگه MCD OK |
| ۸ | **interfaces** | ۳۴۴ | ✅ بله | قابل استفاده |
| ۹ | **titles** | ۶۶ | ✅ بله (version logos) | قابل استفاده |
| ۱۰ | **backgrounds** | ۴۱ | ⚠️ MC Dungeons | فقط اگه MCD OK |
| ۱۱ | **gui** | ۴۷ | ✅ بله | قابل استفاده |
| ۱۲ | **particles** | ۲۵۳ | ✅ بله | قابل استفاده |

## ✅ دسته‌های قابل استفاده (vanilla Minecraft)

### ۱. Items (۱۰۷۴) — ⭐⭐⭐⭐⭐
- **نوع:** رندر سه‌بعدی آیتم‌ها (ایزومتریک)
- **کیفیت:** عالی — پیکسلی، شفاف، رسمی
- **نمونه‌ها:** Diamond_Sword, Bow, Acacia_Boat, Activator_Rail, Allay_Spawn_Egg
- **نکته:** بعضی آیتم‌ها دو بار هستن (Title_Case + lowercase) — فقط یکی استفاده کن
- **VLM تأیید:** «official vanilla Minecraft items, classic 16x16 pixel art»

### ۲. Blocks (۸۰۷) — ⭐⭐⭐⭐⭐
- **نوع:** رندر سه‌بعدی ایزومتریک بلاک‌ها
- **کیفیت:** عالی — رسمی vanilla
- **نمونه‌ها:** Beacon, Diamond_Ore, Acacia_Log, Acacia_Door, Crafting_Table
- **VLM تأیید:** «official vanilla Minecraft texture, isometric 3D style»

### ۳. Structures (۴۷۵) — ⭐⭐⭐⭐⭐
- **نوع:** رندر سه‌بعدی ساختارهای دنیا
- **نمونه‌ها:** Amethyst_Geode, Woodland_Mansion, Ocean_Monument
- **کاربرد:** نقشه‌ی ۲D سید، صفحه‌ی ساختارها

### ۴. Paintings (۴۹) — ⭐⭐⭐⭐⭐
- **نوع:** نقاشی‌های داخل بازی (آویزان‌کردنی)
- **نمونه‌ها:** Alban, Aztec, Burning_Skull, Wither, Bust
- **کاربرد:** گالری نقاشی‌ها، صفحه‌ی دکوراسیون

### ۵. Interfaces (۳۴۴) — ⭐⭐⭐⭐⭐
- **نوع:** المان‌های GUI رسمی
- **نمونه‌ها:** Gamemode_Switcher, Hanging_Sign_Acacia, Hammer_Anvil
- **VLM تأیید:** «official vanilla Minecraft GUI elements»

### ۶. gui (۴۷) — ⭐⭐⭐⭐⭐
- **نوع:** پنل‌های GUI (مثل اینونتوری، میز کرافت)
- **نمونه‌ها:** crafting_table, anvil, beacon, brewing_stand, villager (trading GUI)
- **کاربرد:** پس‌زمینه‌ی پنل‌ها، اینونتوری کرافت

### ۷. Particles (۲۵۳) — ⭐⭐⭐⭐⭐
- **نوع:** افکت‌های ذره‌ای
- **نمونه‌ها:** angry, big_smoke, trial_spawner, vibration
- **کاربرد:** افکت‌های انیمیشن

### ۸. Titles (۶۶) — ⭐⭐⭐⭐
- **نوع:** لوگو/عنوان نسخه‌های ماینکرفت
- **نمونه‌ها:** Bedrock_Edition, Caves_&_Cliffs, Wild_Update, Village_&_Pillage
- **کاربرد:** صفحه‌ی نسخه‌ها، header

## ⚠️ دسته‌های مخلوط (مراقب باش)

### ۹. Mobs (۳۵۹) — ⭐⭐⭐⭐
- **نوع:** رندر سه‌بعدی کامل ماب‌ها (سر + بدن)
- **ریشه:** MC vanilla + MC Legends (MCL) + MC Dungeons (MCD)
- **نکته:** بعضی ماب‌ها از MC Legends یا Dungeons هستن (مثل Fearless_Frog, Badger) — این‌ها رسمی موجانگ هستن ولی vanilla نیستن
- **کاربرد:** فقط vanillaها رو برای ویکی vanilla استفاده کن
- **تشخیص:** اگه اسم ماب توی minecraft.wiki/w/{name} باشه → vanilla. اگه نباشه → MCL/MCD.
- **VLM تأیید:** Villager = «proper in-game 3D render, official Minecraft asset style»

### ۱۰. icons (۱۳۵) — ⭐⭐⭐
- **نوع:** آیکون‌های UI
- **ریشه:** بیشتر از MC Dungeons
- **نمونه‌ها:** Accelerate, Acrobat, Altruistic, Bag_Of_Souls, Void_Shot
- **نکته:** این‌ها آیکون‌های enchantment/glyph از MCD هستن — برای vanilla مناسب نیستن

### ۱۱. backgrounds (۴۱) — ⭐⭐⭐
- **نوع:** پس‌زمینه‌های صحنه
- **ریشه:** همشون از MC Dungeons
- **نمونه‌ها:** Ancient_Hunt, Basalt_Deltas, Creeper_Woods, Treetop_Tangle
- **نکته:** برای vanilla استفاده نکن — مگه صفحه‌ی MC Dungeons بسازی

## ❌ دسته‌های غیرقابل استفاده

### ۱۲. modded_weapons (۹۵) — ❌ **ممنوع**
- **نوع:** سلاح‌های ماد (نه رسمی)
- **نمونه‌ها:** Ares_Sword, Zeus_Bolt, Backstabber, Bat_Crossbow, Beacon_Staff, Void_Bow
- **ریشه:** از مادهای مختلف (احتمالاً Terraria-like یا fan-made)
- **VLM تأیید:** «modded / custom content, not vanilla Minecraft»
- **دلیل:** اسم دسته خودش میگه "modded" — این‌ها سلاح‌های ماد هستن، نه رسمی
- **اقدام:** **هرگز استفاده نکن** — برای صفحه‌ی سلاح‌ها از `items` استفاده کن (Diamond_Sword, Bow, etc.)

## 📋 نقشه‌ی جایگزینی (بخش‌به‌بخش)

| بخش سایت | از کدوم دسته | تعداد | وضعیت |
|---|---|---|---|
| ویکی ماب‌ها | Mobs (vanilla) | ۵۲ | ✅ انجام شد |
| ویکی بلاک‌ها | Blocks | ۱۱۳ | 🔴 هنوز |
| ویکی آیتم‌ها | Items | ~۳۷۷ | 🔴 هنوز |
| صفحه‌ی کرافت | gui (crafting_table, anvil) | ۱ | 🔴 هنوز |
| اینونتوری کرافت | interfaces (inventory) | ~۵ | 🔴 هنوز |
| QuickAccess | gui + interfaces | ~۱۳ | 🔴 هنوز |
| نقشه‌ی ۲D سید | structures | ~۲۰ | 🔴 هنوز |
| گالری نقاشی | paintings | ۴۹ | 🔴 هنوز |
| صفحه‌ی نسخه‌ها | titles | ۶۶ | 🔴 هنوز |
| آیکون‌های دکمه | Items (tool items) | ~۲۰ | 🔴 هنوز |
| افکت‌های انیمیشن | particles | ۲۵۳ | 🔴 هنوز |
| **سلاح‌ها** | **Items (نه modded_weapons!)** | ~۲۰ | 🔴 هنوز |

## ⚠️ نکات حیاتی

1. **هرگز از `modded_weapons` استفاده نکن** — همه‌شون از ماد هستن
2. **برای سلاح‌ها** از `items` استفاده کن: `Diamond_Sword`, `Bow`, `Iron_Sword`, `Crossbow`, `Trident`, etc.
3. **ماب‌های MCL/MCD** (مثل Fearless_Frog, Badger) رسمی موجانگ هستن ولی vanilla نیستن — برای ویکی vanilla استفاده نکن
4. **Items تکراری دارند** — بعضی آیتم‌ها هم با Title_Case و هم lowercase هستن. فقط یکی استفاده کن.
5. **کیفیت high_url** بهتر از low_url است (high = اصلی، low = thumbnail)

## ✅ کارهای انجام‌شده

- [x] کل mcicons package اسکن شد
- [x] ۱۲ دسته بررسی شد
- [x] VLM تأیید: modded_weapons = ماد، items/blocks/gui = vanilla
- [x] ۵۲ ماب با Mobs (vanilla) جایگزین شد
- [x] villager با رندر سه‌بعدی fix شد
- [x] ۱۴ باگ آیکون ماب fix شد (همه px-cow-face بودن)

## 🔴 کارهای باقی‌مونده

- [ ] ۱۱۳ بلاک با Blocks جایگزین (الان از minecraft.wiki تکسچر دارن، به رندر ۳D تغییر بده)
- [ ] ~۳۷۷ آیتم با Items جایگزین
- [ ] QuickAccess با gui + interfaces
- [ ] اینونتوری کرافت با interfaces
- [ ] نقشه‌ی ۲D سید با structures
- [ ] گالری نقاشی با paintings
- [ ] صفحه‌ی نسخه‌ها با titles
- [ ] emoji‌ها حذف + با Items جایگزین
