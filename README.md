# 🎮 MineBed — ویکی فارسی ماینکرفت

وب‌سایت فارسی ماینکرفت با ویکی بلاک‌ها/ماب‌ها/آیتم‌ها، ساخت سید، کرافت، سرعت‌رانی و دانلود ماد.

**🔗 سایت زنده:** https://iran-minecraft-wiki.github.io/website/

> ⚠️ **وضعیت واقعی:** فقط **10/200 فاز = 5%** پروژه انجام شده.
> (نسخه‌های قبلی README عدد 53% را نشان می‌دادند که اشتباه بود — آن عدد از 10/19 آیتم نقشه‌ی راه بود، نه 10/200 فاز.)

---

## 📊 وضعیت صادقانه

### پیشرفت پروژه
| وضعیت | تعداد | درصد |
|---|---|---|
| ✅ انجام‌شده (کامل) | 8 | 4.0% |
| 🟡 نسبی (partial) | 2 | 1.0% |
| ❌ انجام‌نشده | 170 | 85.0% |
| ⛔ بلاک‌شده | 20 | 10.0% |
| **مجموع** | **200** | **100%** |

**پیشرفت واقعی: 10/200 = 5%**

### آمار سایت
| بخش | هدف (MC 1.21) | فعلی | درصد |
|---|---|---|---|
| بلاک‌ها | ~900 | 163 | 18% |
| ماب‌ها | ~83 | 52 | 63% |
| آیتم‌ها | ~1200 | ~410 | 34% |
| ساختارها | ~50 | 8 | 16% |
| نسخه‌ها | ~80 | 78 | 98% |
| سیدها تست‌شده | 60 | 20 | 33% |
| speedrun records | ~1500 | 1187 | ~79% |
| رسپی کرافت | ~500 | ~300 | ~60% |
| مقالات ویکی | ~30 | 10 | 33% |
| بلاگ پست‌ها | ~15 | 7 | 47% |
| آموزش‌ها | ~20 | 12 | 60% |

---

## ✅ کارهای انجام‌شده (10 فاز)

- **آمار سایت واقعی:** KV-backed Cloudflare Worker با ضد تقلب (هر UUID = ۱ در روز) — commit `09e8c7d`
- **نمودارها:** Chart.js با تم پیکسلی ماینکرفتی (۳۰ روز + ۲۴ ساعت) — commit `9e342f8`
- **تاریخ شمسی:** jalaali-js + منطقه‌ی زمانی تهران — commit `4f67ae1`
- **نقشه‌ی 2D سید:** Canvas + grid + compass (فاز ۸۴) — commit `900354c`
- **رندرهای سه‌بعدی ماب‌ها:** ۵۲/۵۲ از mcicons (ccvaults.com) — commit `41236f7`
- **رندرهای سه‌بعدی بلاک‌ها:** ۸۹/۱۱۳ از mcicons + 50 stubs → 163 total (partial 18%) — commit `4b2da8e`
- **اپارات embed:** iframe کانال + ویدیوهای جداگانه (فاز ۱۴۹/۱۵۰) — commit `01b71d9`
- **Drag & Drop کرافت:** HTML5 Drag API + touch support (فاز ۱۰۲) — commit `01b71d9`
- **FAQ:** ۲۱ سوال در ۷ دسته + JSON-LD (فاز ۷۳) — commit `01b71d9`
- **Worker v3:** KV-optimized (writes + lists زیر سقف free-tier) — commit `09e8c7d` (code only, deploy pending)

---

## 📁 ساختار پوشه‌ها

```
imc-website/                          ← repo root
├── README.md                         ← (این فایل) معرفی پروژه
├── PREVIEW_REPORT.md                 ← گزارش پروژه + پیشرفت
├── PHASES_STATUS.md                  ← جدول کامل ۲۰۰ فاز
├── REPORT.md                         ← خلاصه‌ی اجرایی
├── DEPLOY.md                         ← راهنمای دیپلوی
├── admin/                            ← ادمین پنل (FastAPI + static SPA)
│   ├── backend/                      ← Python: main, auth, config, crawler, agnes, mods, uploader
│   ├── ui/                           ← Static HTML/JS SPA (admin Control Center)
│   ├── start.sh / start.bat          ← runner scripts
│   └── requirements.txt
├── docs/                             ← مستندات فنی
│   ├── admin-panel.md
│   ├── crafting-3d.md
│   ├── seeds-system.md
│   └── stats.md
├── pb/                               ← PocketBase schema
├── pb_hooks/                         ← PocketBase hooks
├── scripts/                          ← utility scripts (fetch seeds, gen recipes)
├── worker/                           ← Cloudflare Worker (KV-based stats)
│   ├── src/index.js                  ← Worker v3 source
│   ├── README.md                     ← deploy guide
│   └── wrangler.toml
└── website/                          ← Astro website (main app)
    ├── README.md                     ← website-specific README
    ├── CHECKLIST.md                  ← فاز checklist (با اطلاعات بیش‌تر)
    ├── CHANGELOG.md                  ← تاریخچه‌ی نسخه‌ها
    ├── MCIcons-AUDIT.md              ← تحلیل پکیج mcicons
    ├── astro.config.mjs
    ├── package.json / bun.lock
    ├── tailwind.config.mjs / tsconfig.json
    ├── docs/                         ← docs/animations, crafting-3d, speedrun
    ├── pipeline/                     ← Python content pipeline (config, run, sync, ai_writer, speedrun_fetch)
    ├── public/                       ← static assets
    │   ├── textures/
    │   │   ├── blocks/               ← flat PNG textures
    │   │   ├── blocks-render/        ← 3D isometric webp renders (163 files)
    │   │   ├── items/                ← item PNG textures (~410 files)
    │   │   ├── mobs/                 ← mob face PNG + villager render
    │   │   ├── mobs-render/          ← 3D mob webp renders (60 files for 52 mobs)
    │   │   └── ui/                   ← GUI PNG textures
    │   ├── cubiomes/                 ← WASM seed finder
    │   ├── fonts/                    ← Rooyin (Persian) woff2
    │   ├── favicon.svg + webmanifest
    │   └── robots.txt
    └── src/
        ├── components/               ← 35+ Astro components (Header, Footer, Cube3D, CraftingHelper, StatsWidget, ...)
        ├── content/                  ← MDX content (wiki, blog, tutorials)
        ├── data/                      ← JSON data (blocks, mobs, items, mods, seeds, versions, speedrun, music, crafting-recipes)
        ├── layouts/BaseLayout.astro
        ├── lib/                      ← analytics.js, data.ts, seeddb.js, seo.ts, uuid.js
        ├── pages/                    ← Astro pages (index, wiki, blocks, mobs, mods, seeds, speedrun, crafting, faq, stats, about, blog, tutorials, search, tags, versions, ...)
        ├── styles/                   ← global.css + minecraft-bedrock-ui.css
        └── workers/                  ← seed-finder web worker
```

---

## 📎 لینک‌های مهم

### مستندات پروژه (repo root):
- [📋 PHASES_STATUS.md](./PHASES_STATUS.md) — جدول کامل ۲۰۰ فاز با وضعیت صادقانه
- [📊 PREVIEW_REPORT.md](./PREVIEW_REPORT.md) — گزارش پروژه + آمار سایت
- [📄 REPORT.md](./REPORT.md) — خلاصه‌ی اجرایی
- [🚀 DEPLOY.md](./DEPLOY.md) — راهنمای دیپلوی

### مستندات فنی (website/ subfolder):
- [📋 CHECKLIST.md](./website/CHECKLIST.md) — checklist فازها با اطلاعات بیشتر
- [🔍 MCIcons-AUDIT.md](./website/MCIcons-AUDIT.md) — تحلیل کامل پکیج mcicons (کدوم رسمی، کدوم ماد)
- [📜 CHANGELOG.md](./website/CHANGELOG.md) — تاریخچه‌ی نسخه‌های Astro
- [📖 website/README.md](./website/README.md) — README اختصاصی website
- [📚 docs/](./docs/) — مستندات فنی (stats, crafting-3d, admin-panel, seeds-system)

### سورس کد:
- [⚙️ Worker source](./worker/src/index.js) — کد Cloudflare Worker v3 (KV-based)
- [📖 Worker README](./worker/README.md) — راهنمای دیپلوی Worker
- [🐍 Admin backend](./admin/backend/main.py) — FastAPI admin panel

---

## 🚀 نصب و اجرا

### Astro website (main app):
```bash
# کلون کن
git clone https://github.com/IRAN-MINECRAFT-WIKI/website.git
cd website/website

# نصب deps
bun install

# اجرای dev
bun run dev          # → http://localhost:4321

# build برای production
bun run build

# preview build
bun run preview
```

### Admin panel (optional):
```bash
cd website/admin
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example ../.env  # fill in secrets
./start.sh               # → http://localhost:8000
```

### Cloudflare Worker deploy:
```bash
cd website/worker
npm install -g wrangler
wrangler login
wrangler deploy          # deploys to Cloudflare
```

---

## 🎨 تکنولوژی

- **Framework:** Astro 5 (static, GitHub Pages)
- **Styling:** Tailwind CSS 3 + Minecraft pixel theme
- **Font:** Press Start 2P (pixel) + Rooyin (Persian)
- **Charts:** Chart.js
- **Backend:** Cloudflare Worker (KV-based, anti-inflation)
- **Icons/Renders:** @klashdevelopment/mcicons (ccvaults.com CDN)
- **Date:** jalaali-js (Persian Shamsi)
- **Admin:** FastAPI + vanilla JS SPA
- **Seed finder:** cubiomes (WASM)
- **Search:** Pagefind
- **PWA:** @vite-pwa/astro

---

## ⚠️ نکات حیاتی

1. **هرگز از `modded_weapons` در mcicons استفاده نکن** — همه‌شون ماد هستن. برای سلاح از `items` استفاده کن (Diamond_Sword, Bow, etc.). [جزئیات در MCIcons-AUDIT.md](./website/MCIcons-AUDIT.md)
2. **Worker v3 رو دیپلوی کن** — کدش توی `worker/src/index.js`. KV limit محافظت‌شده (writes/lists زیر سقف).
3. **آمار واقعی بعد از midnight UTC کار می‌کنه** — KV daily limit ریست می‌شه.
4. **وضعیت واقعی 5% است**، نه 53%. فازهای انجام‌شده فقط 10 عدد هستن (8 کامل + 2 نسبی).

---

## 📜 License

- کد: GPL-2.0 (مطابق mcicons)
- محتوای ماینکرفت: Mojang Studios
- ترجمه‌ی فارسی: MineBed Team

---

## 👥 مشارکت

- [🐛 Issues](https://github.com/IRAN-MINECRAFT-WIKI/website/issues)
- [🔀 Pull Requests](https://github.com/IRAN-MINECRAFT-WIKI/website/pulls)
- [🌐 سایت زنده](https://iran-minecraft-wiki.github.io/website/)
