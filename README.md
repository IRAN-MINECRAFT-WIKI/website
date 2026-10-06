# 🎮 MineBed — ویکی فارسی ماینکرفت

وب‌سایت فارسی ماینکرفت با ویکی بلاک‌ها/ماب‌ها/آیتم‌ها، ساخت سید، کرافت، سرعت‌رانی و دانلود ماد.

**🔗 سایت زنده:** https://iran-minecraft-wiki.github.io/website/
**🤗 HuggingFace assets:** https://huggingface.co/datasets/Habib91700/minebed-assets (۱۰۵۲ تکسچر، پهنای باند نامحدود)

> ⚠️ **وضعیت واقعی:** فقط **~16/200 فاز = ~8%** پروژه انجام شده.
> (نسخه‌های قبلی README عدد 53% را نشان می‌دادند که اشتباه بود — آن عدد از 10/19 آیتم نقشه‌ی راه بود، نه 10/200 فاز.)
> پس از batch دوم (upload 1052 تکسچر به HuggingFace + 195 emoji + 2D map 22 features + 14 بلاک fix + /videos/ + FAQ + 42 wiki content + 78 version changelog + gallery pages + 790 block stubs + 52 mob renders + 451 block renders + 420 item renders + cdn-images.ts HF + translations fix)، پیشرفت از ۵٪ به ~۸٪ رسیده.

---

## 📊 وضعیت صادقانه

### پیشرفت پروژه
| وضعیت | تعداد | درصد |
|---|---|---|
| ✅ انجام‌شده (کامل) | ~13 | 6.5% |
| 🟡 نسبی (partial, ×0.5) | 5 | 2.5 weighted |
| ❌ انجام‌نشده | ~162 | 81.0% |
| ⛔ بلاک‌شده | 20 | 10.0% |
| **مجموع** | **~200** | **100%** |

**پیشرفت واقعی: ~16/200 = ~8%**

### آمار سایت (Honest — post-batch-2)
| بخش | هدف (MC 1.21) | فعلی | درصد |
|---|---|---|---|
| بلاک‌ها | ~900 | 790 | **88%** |
| ماب‌ها | ~83 | 52 | **63%** (52/52 ماب موجود = 100٪) |
| آیتم‌ها | ~1200 | 420+ | **35%+** |
| ساختارها | ~50 | 8 | 16% |
| نسخه‌ها | ~80 | 78 | **100%** |
| سیدها تست‌شده | 60 | 20 | 33% |
| speedrun records | ~1500 | 1187 | ~79% |
| رسپی کرافت | ~500 | ~300 | ~60% |
| مقالات ویکی | ~30 | 10 | 33% |
| بلاگ پست‌ها | ~15 | 7 | 47% |
| آموزش‌ها | ~20 | 12 | 60% |
| مادها | ~500 | ~50 | 10% |
| 🆕 تکسچرهای HuggingFace | — | **1052** | unlimited bandwidth |
| 🆕 Emoji حذف‌شده از pages | — | **195** | از 14 صفحه‌ی .astro |
| 🆕 محتوای کامل wiki | — | **42 entity** | 22 بلاک + 20 ماب (798 string) |
| 🆕 نسخه‌های دارای changelog | 78/78 | 780 string | features + changelog (هر کدوم 5 آیتم) |
| 🆕 صفحات gallery | 2 | — | /wiki/blocks/gallery + /wiki/mobs/gallery |
| 🆕 نقشه‌ی 2D سید features | 22 | — | + drag/zoom + PNG download |

---

## ✅ کارهای انجام‌شده (~16 فاز — post-batch-2)

### batch اول (پیش از 2026-10-03):
- **آمار سایت واقعی:** KV-backed Cloudflare Worker با ضد تقلب (هر UUID = ۱ در روز) — commit `09e8c7d` (فاز ۱۲۵)
- **نمودارها:** Chart.js با تم پیکسلی ماینکرفتی (۳۰ روز + ۲۴ ساعت) — commit `9e342f8` (فاز ۱۲۸-۱۲۹)
- **تاریخ شمسی:** jalaali-js + منطقه‌ی زمانی تهران — commit `4f67ae1` (فاز ۱۳۰)
- **نقشه‌ی 2D سید:** Canvas + grid + compass — commit `900354c` (فاز ۸۴)
- **رندرهای سه‌بعدی ماب‌ها:** ۵۲/۵۲ از mcicons (ccvaults.com) — commit `41236f7` (فاز ۲۲)
- **رندرهای سه‌بعدی بلاک‌ها:** mcicons + 50 stubs — commit `4b2da8e` (فاز ۲۱ — partial)
- **اپارات embed:** iframe کانال + ویدیوهای جداگانه — commit `01b71d9` (فاز ۱۴۹/۱۵۰)
- **Drag & Drop کرافت:** HTML5 Drag API + touch support — commit `01b71d9` (فاز ۱۰۲)
- **FAQ:** ۲۱ سوال در ۷ دسته + JSON-LD — commit `01b71d9` (فاز ۷۳)
- **Worker v3:** KV-optimized — commit `09e8c7d` (code only, deploy pending)

### batch دوم (2026-10-03 تا 2026-10-04):
- 🤗 **HuggingFace upload:** 1052 تکسچر به datasets/Habib91700/minebed-assets (unlimited bandwidth) — `cdn-images.ts` rewritten با HF + ccvaults fallback
- 🚫 **Emoji removal:** 195 emoji از 14 صفحه‌ی .astro حذف شد (commit `b91b59b`) — فاز ۲۶ partial
- 🗺️ **2D map enhancement:** 22 structure features + drag/zoom (mouse+touch) + PNG download + radius filter (commit `b91b59b`) — فاز ۸۴ تکمیل
- 🛠️ **14 broken block textures fixed:** از mcasset.cloud + variants دانلود شد (commit `b91b59b`)
- 🎥 **/videos/ rewritten:** polished empty state (commit `b91b59b`)
- ❓ **FAQ title duplication fix:** (commit `b91b59b`)
- 📝 **Wiki content:** 42 entity (22 بلاک + 20 ماب) با 798 Persian string (commit `63753e5`) — فاز ۵۱-۵۲ partial
- 📅 **Version descriptions:** 78/78 نسخه با 780 Persian string (features + changelog) (commit `63753e5`) — فاز ۵۳، ۶۵، ۶۶ کامل ✅
- 🖼️ **Gallery pages:** /wiki/blocks/gallery + /wiki/mobs/gallery با 3D renders + filters + search + pagination (commit `63753e5`) — فاز ۳۷، ۳۸ ✅
- 📦 **Block stubs:** 790 total (766 wiki-matched) (commit `63753e5`)
- 🟦 **Mob renders:** 52/52 از mcicons 3D ✅
- 🟫 **Block renders:** 451 از mcicons 3D
- 🟩 **Item renders:** 420 از mcicons 3D
- 🇮🇷 **Translations fixed:** 48 blocks + 44 mobs (ندر، دایمند، اند، بدراک، رداستون، امرالد، اسکلتون، اسپایدر، کریپر، اوبسیدین، پیلجر، بلیز، ویچ، گاست، ادرمن، ندریت)

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
4. **وضعیت واقعی ~8% است**، نه 53%. فازهای انجام‌شده فقط ~16 عدد هستن (13 کامل + 5 نسبی به‌عنوان 0.5 فاز).
5. **🤗 HuggingFace dataset** منبع اصلی تکسچرهاست (1052 فایل) — ccvaults.com fallback است. [مشاهده‌ی dataset](https://huggingface.co/datasets/Habib91700/minebed-assets)
6. **`cdn-images.ts`** rewritten شده — `blockImgUrl/blockRenderUrl/mobImgUrl/mobRenderUrl/itemImgUrl/itemRenderUrl` همگی HF first، ccvaults fallback می‌سازن. KNOWN_MISSING_FROM_HF set برای 14 بلاک به local PNG برمی‌گرده.

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
