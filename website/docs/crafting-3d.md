# میز کار سه‌بعدی با Steve (Crafting 3D)

## معماری

صفحه‌ی `/crafting/` شامل:
1. **میز کار ۳×۳** — Grid قابل تعامل با کشیدن آیتم
2. **لیست رسپی‌ها** — ۳۳+ رسپی قابل جستجو
3. **Steve سه‌بعدی** — رندر شده با Three.js + skinview3d

## Steve Viewer

### کتابخانه‌ها
- `three` (Three.js) — موتور ۳D
- `skinview3d` — رندر رسمی Minecraft skin

### تکسچر
- فایل: `public/textures/steve.png` (۶۴×۶۴)
- منبع: Crafatar API (`https://crafatar.com/skins/8667ba71b85a4004af54457a9734eed7`)
- این UUID رسمی Steve در Mojang است

### اندازه‌های واقعی
- ۱ بلوک = ۱۶ پیکسل
- قد کل Steve = ۳۲ پیکسل = ۱.۸ بلوک
- skinview3d به‌طور خودکار از این نسبت استفاده می‌کنه

### انیمیشن‌ها
- `IdleAnimation` — ایستاده با تنفس ملایم
- `WalkingAnimation` — راه رفتن
- `RunningAnimation` — دویدن

### کنترل‌ها
- Drag: چرخش Steve
- Scroll: زوم
- دکمه‌های انیمیشن: idle / walk / run
- دکمه چرخش خودکار: toggle
- دکمه بازنشانی دید: reset camera
- Skin dropdown: Steve / Alex

### عملکرد
- Three.js فقط در صفحه‌ی /crafting/ لود می‌شه (not global)
- Canvas GPU-accelerated
- `prefers-reduced-motion`: auto-rotate غیرفعال

## حذف /3d/

صفحه‌ی `/3d/` که قبلاً با CSS 3D ساخته شده بود، حذف شد. همه‌ی قابلیت‌های ۳D حالا در `/crafting/` ادغام شدن با کیفیت بهتر (Three.js به‌جای CSS 3D).

- Header nav: `/3d/` حذف شد، `/crafting/` به «کرافت + ۳D» تغییر نام داد
- QuickAccess: همین تغییر
- Sitemap: /3d/ دیگر ساخته نمی‌شه

## فایل‌ها
- `src/components/SteveViewer.astro` — کامپوننت Steve 3D
- `src/pages/crafting.astro` — صفحه‌ی اصلی (شامل SteveViewer)
- `public/textures/steve.png` — تکسچر Steve
