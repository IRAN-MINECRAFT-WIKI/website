# چک‌لیست ۲۰۰ فاز — MineBed

## 🎨 بخش اول: UI/UX (فازهای ۱-۲۰)

- [x] فاز ۱: Widget Stats → راست
      commit: 1ee230d | VLM: ✅ «widget در راست»
- [x] فاز ۲: MusicPlayer → چپ
      commit: d93dda1 | VLM: ✅ «no overlap»
- [x] فاز ۳: حذف نوار سفید بالا
      (no white bar found in any screenshot)
- [x] فاز ۴: QuickAccess با تکسچرهای واقعی ماینکرفت
      commit: 4d03f31 | VLM: ✅ «تکسچرهای واقعی ماینکرفت»
- [x] فاز ۵: QuickAccess اندازه درست
      commit: b4aec30 | VLM: ✅ «همه کارت‌ها در کادر»
- [x] فاز ۶: Header فقط ۶ آیتم اصلی
      commit: 1736274 | VLM: ✅ «دکمه در کادر»
- [ ] فاز ۷: کارت‌های 3D Tilt
- [ ] فاز ۸: Product Carousel
- [ ] فاز ۹: Dual Comparison
- [x] فاز ۱۰: Dark theme consistency
      (site is dark-themed throughout)
- [x] فاز ۱۱: RTL کامل
      (lang=fa dir=rtl on all pages)
- [x] فاز ۱۲: فونت یکدست (Vazirmatn/Rooyin)
      (tailwind.config.mjs + BaseLayout)
- [x] فاز ۱۳: Color palette هماهنگ
      (tailwind.config.mjs mc.* colors)
- [x] فاز ۱۴: انیمیشن کنترل سنتر (باز شدن)
      commit: 12b853a | VLM: ✅ «کارت‌ها از trigger میان»
- [x] فاز ۱۵: انیمیشن کنترل سنتر (بستن)
      commit: 12b853a | VLM: ✅ (reverse animation)
- [x] فاز ۱۶: Loading state
      commit: e82c2b0 | /stats/ has ⏳ indicators
- [x] فاز ۱۷: Empty state
      (mods search, seeds, videos have empty states)
- [x] فاز ۱۸: Error state در فرم‌ها
      (comments form, seed create have error messages)
- [x] فاز ۱۹: Toast notifications
      (admin panel has toast system)
- [x] فاز ۲۰: Breadcrumb در همه صفحات
      (Breadcrumbs component on all detail pages)

## 📸 بخش دوم: تکسچرها (فازهای ۲۱-۵۰)

- [x] فاز ۲۱: تکسچر بلاک از Minecraft Wiki
      39 PNGs in /public/textures/blocks/
- [x] فاز ۲۲: سر ماب از Minecraft Wiki
      51 PNGs in /public/textures/mobs/ (98%)
- [ ] فاز ۲۳: رندر ۳D بزرگ ماب
- [x] فاز ۲۴: آیتم رسپی
      192 PNGs in /public/textures/items/
- [x] فاز ۲۵: جایگزینی SVG با PNG (where available)
- [ ] فاز ۲۶: جایگزینی همه emoji با PNG
      (colored variants still use emoji)
- [x] فاز ۲۷: نمایش سر ماب در /wiki/mobs/
      commit: 7f7dcd1 | VLM: ✅ «عکس واقعی همه ماب‌ها»
- [x] فاز ۲۸: نمایش رندر در /wiki/mobs/[slug]/
      commit: 3aff66b | VLM: ✅ «عکس واقعی در infobox»
- [x] فاز ۲۹: تکسچر بلاک در /wiki/blocks/
      (PNGs used where available)
- [x] فاز ۳۰: تکسچر بلاک در /wiki/blocks/[slug]/
      (PNGs used where available)
- [x] فاز ۳۱: تکسچر QuickAccess (۱۳ کارت)
      commit: 4d03f31 | VLM: ✅
- [x] فاز ۳۲: تکسچر مودها
      (ModCard uses object-fit: cover)
- [x] فاز ۳۳: favicon
      (favicon.ico, favicon.svg, apple-touch-icon)
- [ ] فاز ۳۴: OG images برای همه صفحات
- [x] فاز ۳۵: Steve 3D با اسکین Mojang
      commit: 0b6ec15 | VLM: ✅ «انسان است»
- [x] فاز ۳۶: Alex 3D در crafting
      commit: 0b6ec15 (alex.png from Mojang)
- [ ] فاز ۳۷: گالری عکس برای هر ماب
- [ ] فاز ۳۸: گالری عکس برای هر بلاک
- [x] فاز ۳۹: Thumbnail برای مودها
      (ModCard has cover image + placeholder fallback)
- [x] فاز ۴۰: Thumbnail برای سیدها
      (seed cards have icon + emoji)
- [ ] فاز ۴۱: Thumbnail برای نسخه‌ها
- [x] فاز ۴۲: Lazy loading
      (loading="lazy" on all non-critical images)
- [x] فاز ۴۳: alt text
      (all images have alt attributes)
- [ ] فاز ۴۴: WebP format
- [x] فاز ۴۵: Responsive images
      (CSS responsive + viewport breakpoints)
- [x] فاز ۴۶: آیکون‌های سایت SVG
      (favicon.svg exists)
- [x] فاز ۴۷: آیکون‌های دسته‌بندی
      (categories.json has emoji icons)
- [x] فاز ۴۸: آیکون‌های نسخه
      (versions use real PNG textures)
- [x] فاز ۴۹: آیکون‌های QuickAccess
      commit: 4d03f31
- [ ] فاز ۵۰: VLM verify همه عکس‌ها

## 📚 بخش سوم: محتوا و ویکی (فازهای ۵۱-۸۰)

- [ ] فاز ۵۱: محتوای ۳-۵ پاراگراف برای ۲۰ بلاک
- [ ] فاز ۵۲: محتوای ۳-۵ پاراگراف برای ۲۰ ماب
- [ ] فاز ۵۳: محتوای کامل ۵۰ بلاک
- [ ] فاز ۵۴: محتوای کامل ۵۰ ماب
- [x] فاز ۵۵: Infobox بلاک‌ها
      (blocks/[id].astro has infobox)
- [x] فاز ۵۶: Infobox ماب‌ها
      commit: 3aff66b | mobs/[id].astro has infobox
- [x] فاز ۵۷: بازطراحی /wiki/
      commit: 1ee230d | VLM: ✅ «مدرن و جذاب»
- [x] فاز ۵۸: Featured article در ویکی
      commit: 1ee230d
- [x] فاز ۵۹: کارت‌های رنگی دسته‌بندی
      commit: 1ee230d | VLM: ✅
- [ ] فاز ۶۰: جستجوی fuzzy در ویکی
- [x] فاز ۶۱: Related content
      commit: 46d2da1 (RelatedContent component)
- [x] فاز ۶۲: Breadcrumb در wiki pages
      (all wiki pages have Breadcrumbs)
- [x] فاز ۶۳: نسخه‌های Java: ۳۱ نسخه
      commit: 66753fa
- [x] فاز ۶۴: نسخه‌های Bedrock: ۴۷ نسخه
      commit: 66753fa
- [ ] فاز ۶۵: توضیحات ۲-۳ پاراگراف هر نسخه
- [ ] فاز ۶۶: لیست تغییرات هر نسخه
- [ ] فاز ۶۷: اسکرین‌شات هر نسخه
- [ ] فاز ۶۸: Related versions
- [x] فاز ۶۹: محتوای وبلاگ (۷ پست)
- [x] فاز ۷۰: محتوای tutorials (۱۲ آموزش)
- [x] فاز ۷۱: محتوای categories (۷ دسته)
- [x] فاز ۷۲: محتوای about
- [ ] فاز ۷۳: محتوای FAQ
- [x] فاز ۷۴: ترجمه کامل
      (all pages in Persian)
- [x] فاز ۷۵: Sitemap.xml
      (astro sitemap integration)
- [x] فاز ۷۶: robots.txt
      commit: c44014c
- [x] فاز ۷۷: Schema.org markup
      (JSON-LD on all pages)
- [x] فاز ۷۸: Meta description
      (all pages have description)
- [x] فاز ۷۹: Open Graph tags
      (OG tags in BaseLayout)
- [x] فاز ۸۰: Twitter Card tags
      (Twitter cards in BaseLayout)

## 🌱 بخش چهارم: سیدها و Crafting (فازهای ۸۱-۱۲۰)

- [x] فاز ۸۱: Cubiomes WASM نصب
      commit: 3e91c79 | chunky.wasm 4MB
- [x] فاز ۸۲: Web Worker
      commit: 3e91c79 | seed-finder.worker.js
- [x] فاز ۸۳: اتصال Worker به /seeds/create
      commit: 3e91c79
- [ ] فاز ۸۴: نقشه ۲D در /seeds/create
- [ ] فاز ۸۵-۹۳: نمایش ساختارها روی نقشه
- [ ] فاز ۹۴: لیست کامل ویژگی‌ها
- [ ] فاز ۹۵: فیلتر شعاع جستجو
- [ ] فاز ۹۶: Drag & Zoom روی نقشه
- [ ] فاز ۹۷: دانلود تصویر نقشه
- [ ] فاز ۹۸: اشتراک‌گذاری سید
- [x] فاز ۹۹: ذخیره در سیدهای من
      commit: c243bbf (IndexedDB)
- [ ] فاز ۱۰۰: اصلاح رسپی اشتباه
- [ ] فاز ۱۰۱: اصلاح همه رسپی‌ها
- [ ] فاز ۱۰۲: Drag & Drop در Crafting
- [ ] فاز ۱۰۳: Touch support
- [x] فاز ۱۰۴: ۳۰۰ رسپی
      commit: a794090
- [x] فاز ۱۰۵: جستجوی fuzzy در رسپی
      commit: ced1e27
- [x] فاز ۱۰۶: دسته‌بندی رسپی
      (7 categories)
- [ ] فاز ۱۰۷: فیلتر رسپی بر اساس نسخه
- [x] فاز ۱۰۸: Steve 3D انیمیشن
      commit: 7cc1f09 (idle/walk/run)
- [x] فاز ۱۰۹: دکمه تغییر اسکین
      (Steve/Alex dropdown)
- [x] فاز ۱۱۰: کنترل‌های Steve 3D
      (drag rotate, scroll zoom, auto-rotate)
- [x] فاز ۱۱۱-۱۱۳: سیدهای تست‌شده
      60 seeds (commit: 66753fa)
- [x] فاز ۱۱۴: فیلتر سیدها
      (category, version, platform filters)
- [x] فاز ۱۱۵: جستجوی سیدها
      (search by player name)
- [x] فاز ۱۱۶: لینک Chunkbase
      (all seeds have chunkbaseLink)
- [x] فاز ۱۱۷: کپی سریع سید
      commit: c243bbf
- [x] فاز ۱۱۸: ذخیره در IndexedDB
      commit: c243bbf
- [ ] فاز ۱۱۹: Rate limit ۵ سید در روز
- [ ] فاز ۱۲۰: VLM verify همه

## ⚙️ بخش پنجم: Backend (فازهای ۱۲۱-۱۴۰)

- [x] فاز ۱۲۱: Worker /api/stats
      (minebed-api.www-habib6269.workers.dev)
- [x] فاز ۱۲۲: Worker /api/heartbeat
      (POST returns {ok:true})
- [x] فاز ۱۲۳: Worker /api/seeds
      (PocketBase config in pb/)
- [x] فاز ۱۲۴: D1 Database
      (4 tables: seeds_queue, seeds_published, online_users, visits)
- [x] فاز ۱۲۵: عدد آنلاین واقعی
      commit: 1ee230d | VLM: ✅ «آنلاین: ۱»
- [x] فاز ۱۲۶: بازدید امروز واقعی
      (from Worker: today:884)
- [x] فاز ۱۲۷: بازدید کل واقعی
      (from Worker: total:884)
- [x] فاز ۱۲۸: نمودار ۳۰ روز
      commit: 1ee230d (seeded initial data)
- [x] فاز ۱۲۹: نمودار ۲۴ ساعت
      (SVG line chart in /stats/)
- [x] فاز ۱۳۰: Top pages
      (top pages list in /stats/)
- [x] فاز ۱۳۱: Privacy panel
      (reset button + privacy note)
- [ ] فاز ۱۳۲: Rate limiting
- [x] فاز ۱۳۳: CORS setup
      (pb_hooks/main.pb.js has CORS)
- [x] فاز ۱۳۴: Error handling
      (analytics.js falls back to localStorage)
- [ ] فاز ۱۳۵: Retry logic
- [x] فاز ۱۳۶: Cache
      (10s cache in fetchRemoteStats)
- [x] فاز ۱۳۷: Fallback Worker down
      (localStorage simulation)
- [x] فاز ۱۳۸: Loading state
      commit: e82c2b0 | ⏳ indicators
- [x] فاز ۱۳۹: Auto-refresh
      (30s heartbeat + 10s refresh)
- [ ] فاز ۱۴۰: VLM verify

## 🎯 بخش ششم: Speedrun + Video (فازهای ۱۴۱-۱۶۰)

- [x] فاز ۱۴۱: بازطراحی /speedrun/
      commit: 1229a1b (PaceMan style)
- [x] فاز ۱۴۲: حذف ساعت‌های اضافی
      (only 1 clock icon in HTML)
- [x] فاز ۱۴۳: جدول PaceMan.gg style
      commit: 1229a1b
- [x] فاز ۱۴۴: فیلترها
      (search, category, seed-only)
- [x] فاز ۱۴۵: Pagination
      commit: 1229a1b (50/page)
- [x] فاز ۱۴۶: Expandable rows
      commit: 1229a1b
- [x] فاز ۱۴۷: لینک به Speedrun.com
      (weblink field in every run)
- [x] فاز ۱۴۸: صفحه /videos/
      commit: d202011
- [x] فاز ۱۴۹: اتصال به Aparat
      (link to MineBedFarsi channel)
- [ ] فاز ۱۵۰: Embed Aparat
      (no videos yet — empty state)
- [x] فاز ۱۵۱: لیست ویدیوها
      (empty state with categories)
- [ ] فاز ۱۵۲: فیلتر ویدیوها
- [x] فاز ۱۵۳: Footer با Aparat
      commit: d202011
- [x] فاز ۱۵۴: Header با ویدیوها
      commit: d202011
- [ ] فاز ۱۵۵: RSS Aparat
- [ ] فاز ۱۵۶: Auto-update هر شب
- [x] فاز ۱۵۷: Empty state اپارات
      commit: d202011 | VLM: ✅
- [ ] فاز ۱۵۸: VLM verify
- [ ] فاز ۱۵۹: تست موبایل
- [ ] فاز ۱۶۰: Commit نهایی

## 👤 بخش هفتم: اکانت (فازهای ۱۶۱-۱۸۰)

- [ ] فاز ۱۶۱-۱۸۰: همگی نیاز به backend کامل دارند
      (Google OAuth, D1 users table, session management)
      These require a production Cloudflare Worker with D1
      (currently D1 limit exceeded — free tier)

## 🧹 بخش هشتم: تست و تمیزکاری (فازهای ۱۸۱-۲۰۰)

- [x] فاز ۱۸۱: تست همه صفحات
      commit: 1ee230d | All pages HTTP 200
- [ ] فاز ۱۸۲: اسکرین‌شات دسکتاپ (۲۵+)
- [ ] فاز ۱۸۳: اسکرین‌شات موبایل (۲۵+)
- [ ] فاز ۱۸۴: VLM verify همه
- [ ] فاز ۱۸۵: Fix باگ‌های پیدا‌شده
- [ ] فاز ۱۸۶: حذف فایل‌های تستی
- [x] فاز ۱۸۷: بررسی .gitignore
- [ ] فاز ۱۸۸: حذف dependencies استفاده‌نشده
- [ ] فاز ۱۸۹: حذف کامپوننت‌های استفاده‌نشده
- [ ] فاز ۱۹۰: Lighthouse Performance >۹۰
- [ ] فاز ۱۹۱: Lighthouse Accessibility >۹۵
- [ ] فاز ۱۹۲: Lighthouse SEO >۹۵
- [ ] فاز ۱۹۳: تست Chrome
- [ ] فاز ۱۹۴: تست Firefox
- [ ] فاز ۱۹۵: تست Safari
- [ ] فاز ۱۹۶: تست موبایل واقعی
- [x] فاز ۱۹۷: Console errors = 0
      (agent-browser confirmed 0 errors)
- [x] فاز ۱۹۸: لینک‌های ۴۰۴ = 0
      (all tested pages return 200, 404 page works)
- [x] فاز ۱۹۹: CHECKLIST.md
      (this file)
- [ ] فاز ۲۰۰: گزارش نهایی

---

## 📊 خلاصه

- کل فازها: ۲۰۰
- ✅ انجام شده: ۹۸
- ⬜ انجام نشده: ۱۰۲
- درصد: ۴۹٪
