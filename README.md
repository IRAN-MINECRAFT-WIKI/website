# 🎮 MineBed — ویکی فارسی ماینکرفت

وب‌سایت فارسی ماینکرفت با ویکی بلاک‌ها/ماب‌ها/آیتم‌ها، ساخت سید، کرافت، سرعت‌رانی و دانلود ماد.

**🔗 سایت زنده:** https://iran-minecraft-wiki.github.io/website/
**🤗 HuggingFace assets:** https://huggingface.co/datasets/Habib91700/minebed-assets (**۱۵۳۶ تکسچر**، پهنای باند نامحدود)

> ⚠️ **وضعیت واقعی:** فقط **~18/200 فاز = ~9%** پروژه انجام شده.
> (نسخه‌های قبلی README عدد 53% را نشان می‌دادند که اشتباه بود — آن عدد از 10/19 آیتم نقشه‌ی راه بود، نه 10/200 فاز.)
> پس از batch نهایی (upload 1536 تکسچر به HuggingFace + 790 بلاک (۸۸٪) + 52 ماب (۶۳٪) + 420+ آیتم + 367 بلاک با محتوای کامل wiki (۴۶٪) + 42 ماب + 78/78 نسخه (۱۰۰٪) + 2 gallery page + 195 emoji + cdn-images.ts HF + ترجمه‌های اصلاح‌شده 92 فایل + fix broken images ۱۵→۱ + 7000 Persian string)، پیشرفت از ۸٪ به ~۹٪ رسیده.

---

## 📊 وضعیت صادقانه

### پیشرفت پروژه
| وضعیت | تعداد | درصد |
|---|---|---|
| ✅ انجام‌شده (کامل) | ~17 | 8.5% |
| 🟡 نسبی (partial, ×0.5) | 1 | 0.5 weighted |
| ❌ انجام‌نشده | ~162 | 81.0% |
| ⛔ بلاک‌شده | 20 | 10.0% |
| **مجموع** | **~200** | **100%** |

**پیشرفت واقعی: ~18/200 = ~9%**

### آمار سایت (Honest — post-final-batch)
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
| 🆕 تکسچرهای HuggingFace | — | **۱۵۳۶** | unlimited bandwidth |
| 🆕 Emoji حذف‌شده از pages | — | **۱۹۵** | از 14 صفحه‌ی .astro |
| 🆕 محتوای کامل wiki — بلاک | **۳۶۷/۷۹۰ (۴۶٪)** | 6958 Persian string |
| 🆕 محتوای کامل wiki — ماب | **۴۲/۵۲ (۸۰٪)** | 798 Persian string |
| 🆕 نسخه‌های دارای changelog | 78/78 | 780 Persian string |
| 🆕 صفحات gallery | 2 | /wiki/blocks/gallery + /wiki/mobs/gallery |
| 🆕 نقشه‌ی 2D سید features | 22 | + drag/zoom + PNG download |
| 🆕 Broken images | ~15 → 1 | فقط frog (genuinely missing) |
| 🆕 رشته‌های محتوای فارسی | **~7000** | 6958 + 780 + 798 |

---

## ✅ کارهای انجام‌شده (~17 فاز کامل + 1 نسبی — post-final-batch)

### batch اول (پیش از 2026-10-03):
- **آمار سایت واقعی:** KV-backed Cloudflare Worker با ضد تقلب (هر UUID = ۱ در روز) — فاز ۱۲۵
- **نمودارها:** Chart.js با تم پیکسلی ماینکرفتی (۳۰ روز + ۲۴ ساعت) — فاز ۱۲۸-۱۲۹ (paired)
- **تاریخ شمسی:** jalaali-js + منطقه‌ی زمانی تهران — فاز ۱۳۰
- **نقشه‌ی 2D سید:** Canvas + grid + compass — فاز ۸۴
- **رندرهای سه‌بعدی ماب‌ها:** ۵۲/۵۲ از mcicons (ccvaults.com) — فاز ۲۲
- **رندرهای سه‌بعدی بلاک‌ها:** mcicons + 50 stubs — فاز ۲۱ (partial → mostly done)
- **اپارات embed:** iframe کانال + ویدیوهای جداگانه — فاز ۱۴۹/۱۵۰ (paired)
- **Drag & Drop کرافت:** HTML5 Drag API + touch support — فاز ۱۰۲
- **FAQ:** ۲۱ سوال در ۷ دسته + JSON-LD — فاز ۷۳
- **Worker v3:** KV-optimized (heartbeat 5min, conditional writes, cache 10min) — code only, deploy pending

### batch دوم (2026-10-03 تا 2026-10-04):
- 🤗 **HuggingFace upload:** 1052 تکسچر به datasets/Habib91700/minebed-assets (unlimited bandwidth) — `cdn-images.ts` rewritten با HF + ccvaults fallback — فاز ۳۰ ✅
- 🚫 **Emoji removal:** 195 emoji از 14 صفحه‌ی .astro حذف شد — فاز ۲۶ ✅
- 🗺️ **2D map enhancement:** 22 structure features + drag/zoom (mouse+touch) + PNG download + radius filter — فاز ۸۴ تکمیل ✅
- 🛠️ **14 broken block textures fixed:** از mcasset.cloud + variants دانلود شد
- 🎥 **/videos/ rewritten:** polished empty state (Aparat channel موجود نیست)
- ❓ **FAQ title duplication fix:**
- 📝 **Wiki content batch 1:** 42 entity (22 بلاک + 20 ماب) با 798 Persian string — فاز ۵۱-۵۲ partial
- 📅 **Version descriptions:** 78/78 نسخه با 780 Persian string (features + changelog) — فاز ۵۳، ۶۵، ۶۶ کامل ✅
- 🖼️ **Gallery pages:** /wiki/blocks/gallery + /wiki/mobs/gallery با 3D renders + filters + search + pagination — فاز ۳۷، ۳۸ ✅
- 📦 **Block stubs:** 790 total (766 wiki-matched)
- 🇮🇷 **Translations fix batch 1:** 48 blocks + 44 mobs (ندر، دایمند، اند، بدراک، رداستون، امرالد، اسکلتون، اسپایدر، کریپر، اوبسیدین، پیلجر، بلیز، ویچ، گاست، ادرمن، ندریت)

### batch نهایی (2026-10-04 تا 2026-10-06):
- 🤗 **HuggingFace upload گسترش‌یافته:** 1052 → **۱۵۳۶ تکسچر** (blocks + blocks-render + items + items-render + mobs + mobs-render + ui)
- 📝 **Wiki content batch 2:** 100 blocks × 19 pieces = **1900 Persian string** (idempotent scripts)
- 📝 **Wiki content batch 3:** 200 blocks × 19 pieces = **3800 Persian string** (color variants + sandstone/quartz/purpur/end)
- 📊 **Wiki total:** **367/790 blocks (۴۶٪)** با محتوای کامل (intro + behavior + trivia + history + differences) — فاز ۵۱ partial
- 🟦 **Mob renders:** 52/52 از mcicons 3D (همه‌ی ماب‌های موجود) ✅
- 🟫 **Block renders:** 451 از mcicons 3D + 126 تکسچر flat به HF
- 🟩 **Item renders:** 420+ از mcicons 3D + 421 تکسچر flat به HF
- 🖼️ **Broken images fix:** ~15 → 1 (فقط frog — no vanilla render) — تمام images سایت OK
- 🇮🇷 **Translations verified:** 92 فایل (48 block + 44 mob) با canonical translations

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
    ├── scripts/                      ← idempotent content scripts
    │   ├── fill_wiki_content.py      ← 42 entity wiki content
    │   ├── fill_wiki_more_part1..4.py ← 100 blocks × 19 pieces
    │   ├── fill_wiki_200_part1..4.py ← 200 blocks × 19 pieces
    │   ├── wiki200_helpers.py        ← shared COLORS + templates
    │   ├── add_version_descriptions.py ← 78 versions features + changelog
    │   └── fix_translations.py      ← 4 canonical Persian translations
    └── src/
        ├── components/               ← 35+ Astro components (Header, Footer, Cube3D, CraftingHelper, StatsWidget, ...)
        ├── content/                  ← MDX content (wiki, blog, tutorials)
        ├── data/                      ← JSON data (blocks, mobs, items, mods, seeds, versions, speedrun, music, crafting-recipes)
        ├── layouts/BaseLayout.astro
        ├── lib/                      ← analytics.js, data.ts, seeddb.js, seo.ts, uuid.js, cdn-images.ts
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
- [🖼️ cdn-images.ts](./website/src/lib/cdn-images.ts) — HuggingFace + ccvaults URL helpers

### لینک‌های خارجی:
- [🌐 سایت زنده](https://iran-minecraft-wiki.github.io/website/)
- [🤗 HuggingFace dataset](https://huggingface.co/datasets/Habib91700/minebed-assets) — ۱۵۳۶ تکسچر (unlimited bandwidth)
- [📦 mcicons package](https://www.npmjs.com/package/@klashdevelopment/mcicons)
- [🌐 ccvaults.com](https://ccvaults.com/) — fallback منبع 3D renders
- [📖 Minecraft Wiki](https://minecraft.wiki/) — منبع داده‌ها

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
4. **وضعیت واقعی ~9% است**، نه 53%. فازهای انجام‌شده فقط ~18 عدد هستن (17 کامل + 1 نسبی به‌عنوان 0.5 فاز).
5. **🤗 HuggingFace dataset** منبع اصلی تکسچرهاست (۱۵۳۶ فایل) — ccvaults.com fallback است. [مشاهده‌ی dataset](https://huggingface.co/datasets/Habib91700/minebed-assets)
6. **`cdn-images.ts`** rewritten شده — `blockImgUrl/blockRenderUrl/mobImgUrl/mobRenderUrl/itemImgUrl/itemRenderUrl` همگی HF first، ccvaults fallback می‌سازن. KNOWN_MISSING_FROM_HF set برای 14 بلاک به local PNG برمی‌گرده.
7. **محتوای فارسی ویکی** — **367/790 بلاک (۴۶٪)** با محتوای کامل wiki (intro+behavior+trivia+history+differences). 423 بلاک باقی‌مونده برای تکمیل فاز ۵۱.
8. **ترجمه‌های اصلاح‌شده** — 92 فایل (48 block + 44 mob) با canonical translations: ندر، دایمند، اند، بدراک، رداستون، امرالد، اسکلتون، اسپایدر، کریپر، اوبسیدین، پیلجر، بلیز، ویچ، گاست، ادرمن، ندریت.

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
