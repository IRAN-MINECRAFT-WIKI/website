# 📄 REPORT — MineBed Project

**تاریخ:** 2026-10-04 (post-batch-2)
**نسخه:** 2.0 (Honest Stats Edition — post-batch-2)
** repo:** [IRAN-MINECRAFT-WIKI/website](https://github.com/IRAN-MINECRAFT-WIKI/website)
**🤗 assets:** [HuggingFace dataset](https://huggingface.co/datasets/Habib91700/minebed-assets) (1052 تکسچر، unlimited bandwidth)

---

## 📝 Executive Summary

MineBed یک ویکی فارسی ماینکرفت (Astro 5 + Cloudflare Worker) است که هدفش ارائه‌ی محتوای کامل MC 1.21 شامل 900 بلاک، 83 ماب، 1200 آیتم، 50 ساختار، 80 نسخه، و سیستم سید/کرافت/سرعت‌رانی است. پروژه با 200 فاز برنامه‌ریزی شده، و تا امروز پس از دو batch کارِ ایجنت، فقط **~16 فاز (~8%)** واقعاً کامل شده — 13 فاز کامل و 5 فاز نسبی (تکسچر بلاک 790/900 = 88٪، تکسچر آیتم 420/1200 = 35٪، emoji 195 از 14 صفحه، wiki content 42 entity از ~742، mob detail 52/83 = 63٪).

نسخه‌های قبلی مستندات عدد 53% را نشان می‌دادند که اشتباه بود (آمده از 10/19 آیتم نقشه‌ی راه Next.js، نه 10/200 فاز). پس از اصلاحِ batch اول، عدد واقعی 5٪ بود. پس از batch دوم (که شامل upload 1052 تکسچر به HuggingFace، حذف 195 emoji، expand نقشه‌ی 2D به 22 feature با drag/zoom/PNG download، fix 14 بلاک خراب، rewrite /videos/، fix FAQ title، نوشتن 42 entity wiki content با 798 Persian string، افزودن 780 string برای 78 نسخه با features + changelog، ساخت 2 gallery page با 3D renders/filters/search/pagination، 790 block data stubs، 52/52 mob renders از mcicons 3D، 451 block renders، 420 item renders، rewrite cdn-images.ts با HuggingFace + ccvaults fallback، و fix 48 block + 44 mob translation) عدد واقعی به **~8%** رسیده.

این فایل اعداد واقعی post-batch-2 را ثبت می‌کند.

---

## 📈 پیشرفت صادقانه (post-batch-2)

### پیشرفت فازها
| وضعیت | تعداد | درصد |
|---|---|---|
| ✅ انجام‌شده (کامل) | ~13 | 6.5% |
| 🟡 نسبی (partial, ×0.5) | 5 | 2.5 weighted |
| ❌ انجام‌نشده | ~162 | 81.0% |
| ⛔ بلاک‌شده | 20 | 10.0% |
| **مجموع** | **~200** | **100%** |

### 🎯 پیشرفت واقعی: **~16/200 = ~8%** (نه 53% ❌، نه 5٪ سابق ❌)

> ❌ عدد قبلی 53% **اشتباه بود** — از 10/19 آیتم نقشه‌ی راه پنل Next.js آمده بود، نه 10/200 فاز پروژه.
> ✅ پس از batch دوم، عدد واقعی از ۵٪ (10/200) به ~۸٪ (~16/200) رسیده.

---

## 📊 آمار سایت (Honest — post-batch-2)

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

### 🆕 آمار batch دوم (صادقانه)
| بخش | تعداد | توضیح |
|---|---|---|
| 🤗 تکسچرهای HuggingFace | 1052 | datasets/Habib91700/minebed-assets (unlimited bandwidth) |
| 🚫 Emoji حذف‌شده از pages | 195 | از 14 صفحه‌ی .astro (data emoji هنوز fallback) |
| 📝 محتوای کامل wiki | 42 entity | 22 بلاک + 20 ماب، 798 Persian string |
| 📅 توضیحات نسخه | 78/78 | features + changelog = 780 Persian string |
| 🖼️ صفحات gallery | 2 | /wiki/blocks/gallery + /wiki/mobs/gallery |
| 🗺️ نقشه‌ی 2D سید | 22 feature | + drag/zoom + PNG download + radius filter |
| 🛠️ بلاک‌های fix شده | 14 | از mcasset.cloud + variants |
| 🟫 رندر سه‌بعدی بلاک | 451 | از mcicons 3D |
| 🟦 رندر سه‌بعدی ماب | 52/52 | از mcicons 3D (100٪ ماب‌های موجود) |
| 🟩 رندر سه‌بعدی آیتم | 420 | از mcicons 3D |
| 📦 Block data stubs | 790 | 766 wiki-matched |
| 🇮🇷 ترجمه‌های اصلاح‌شده | 48 block + 44 mob | ندر، دایمند، اند، بدراک، رداستون، امرالد، اسکلتون، اسپایدر، کریپر، اوبسیدین، پیلجر، بلیز، ویچ، گاست، ادرمن، ندریت |

---

## ✅ فازهای انجام‌شده (~16 فاز — post-batch-2)

| # | فاز | وضعیت | commit |
|---|---|---|---|
| 1 | نقشه‌ی 2D سید (فاز 84) | ✅ | `900354c` + `b91b59b` |
| 2 | رندر سه‌بعدی Villager + 52 ماب (فاز 22) | ✅ | `41236f7` |
| 3 | صفحه‌ی FAQ (فاز 73) | ✅ | `01b71d9` + `b91b59b` |
| 4 | Drag & Drop کرافت (فاز 102) | ✅ | `01b71d9` |
| 5 | اپارات embed (فاز 149/150) | ✅ | `01b71d9` |
| 6 | نمودار 30 روز + 24 ساعت (فاز 128-129) | ✅ | `9e342f8` |
| 7 | آمار واقعی آنلاین KV (فاز 125) | ✅ | `09e8c7d` |
| 8 | تاریخ شمسی (فاز 130) | ✅ | `4f67ae1` |
| 9 | Mod image resize CSS (فاز 32 — N/A external) | ✅ (N/A) | external |
| 10 | Block gallery page (فاز 37) | ✅ | `63753e5` |
| 11 | Mob gallery page (فاز 38) | ✅ | `63753e5` |
| 12 | Version pages + features + changelog 78/78 (فازهای 53، 65، 66) | ✅ | `63753e5` |
| 13 | Aparat embed custom (فاز 159 — paired با 149/150) | ✅ | `01b71d9` |
| 14 | تکسچر بلاک mcicons + HF (فاز 21) | 🟡 partial | `4b2da8e` + `b91b59b` + `63753e5` (790/900 = 88٪) |
| 15 | تکسچر آیتم mcicons (فاز 24) | 🟡 partial | `01b71d9` (420/1200 = 35٪) |
| 16 | emoji → PNG (فاز 26) | 🟡 partial | `b91b59b` (195 از 14 page، data fallback) |
| 17 | Block detail pages 790 stubs (فاز 51) | 🟡 partial | `4b2da8e` + `63753e5` (42 با محتوای کامل) |
| 18 | Mob detail pages (فاز 52) | 🟡 partial | `41236f7` + `63753e5` (52/83 = 63٪) |
| — | Texture CDN integration (فاز 30) | ✅ | `cdn-images.ts` rewritten |

**Honest count:** 13 full ✅ + 5 partial 🟡 × 0.5 = 13 + 2.5 = **15.5 ≈ 16 / 200 = 8%**

---

## ❌ فازهای باقی‌مونده (~184 فاز — خلاصه)

### بحرانی (manual — کاربر باید بکند):
1. **Deploy Worker v3** — کد آماده در `worker/src/index.js`. بریز روی Cloudflare.
2. **Test 2-browser online** — Chrome + Firefox همزمان /stats/ باز کن.
3. **Setup Google OAuth** (برای فازهای 161-180).

### ایجنت می‌تونه بکند (8 فاز اصلی):
1. فاز 21 تکمیل — دانلود ~110 بلاک باقی‌مونده (از ۸۸٪ به ۱۰۰٪)
2. فاز 24 ادامه — دانلود ~780 آیتم باقی‌مونده (از ۳۵٪ به ۱۰۰٪)
3. **فاز 51 ادامه — نوشتن محتوای کامل wiki برای ~700 بلاک باقی‌مونده** (از 42 به 790) — بالاترین impact برای SEO
4. فاز 52 تکمیل — دانلود 31 ماب باقی‌مونده (از ۶۳٪ به ۱۰۰٪)
5. فاز 67 — version diff pages
6. فاز 68 — version comparison tool
7. فاز 73 بیشتر — اضافه کردن سوال‌های بیشتر به FAQ
8. فاز 155-156 — RSS feed + Aparat auto-update (cron)

### ⛔ بلاک‌شده (20 فاز):
1. **اکانت کاربر (فازهای 161-180)** — نیاز به Google OAuth + D1 database + Worker deploy

### باقی‌مانده (~164 فاز):
- 20 فاز UI/UX polish (1-20)
- 7 فاز Textures (23, 25, 27-29)
- 20 فاز Content/Wiki (31, 33-36, 39-50, 54-60)
- 36 فاز Seeds/Craft (61-62, 67-72, 74-83, 85-99, 100-101, 103-110)
- 25 فاز Backend (111-124, 126-127, 131-140)
- 18 فاز Speedrun/Video (141-148, 151-160)
- 20 فاز Testing/Cleanup (181-200)

---

## 🤗 HuggingFace Dataset (جدید در batch دوم)

- **Repo:** https://huggingface.co/datasets/Habib91700/minebed-assets
- **URL pattern:** `https://huggingface.co/datasets/Habib91700/minebed-assets/resolve/main/{dir}/{id}.png`
- **تعداد:** 1052 تکسچر (blocks + blocks-render + items + items-render + mobs + mobs-render + ui)
- **مزیت:** پهنای باند نامحدود، بدون هزینه، cache-friendly
- **Integration در کد:** `src/lib/cdn-images.ts` (rewritten)
  - Helpers: `blockImgUrl()`, `blockRenderUrl()`, `mobImgUrl()`, `mobRenderUrl()`, `itemImgUrl()`, `itemRenderUrl()`, `uiImgUrl()`
  - Fallback: ccvaults.com (mcicons CDN)
  - Known-missing list: 14 بلاک (banner, carpet, button, pressure-plate, item-frame, brewing-stand, hopper, repeater, comparator, tripwire-hook, redstone-wire, redstone-block, quartz-block, jack-o-lantern) — از local flat PNG استفاده می‌کنن

---

## 📎 لینک‌ها به همه‌ی فایل‌ها

### مستندات (repo root):
- [📖 README.md](./README.md) — معرفی پروژه
- [📊 PREVIEW_REPORT.md](./PREVIEW_REPORT.md) — گزارش کامل + آمار
- [📋 PHASES_STATUS.md](./PHASES_STATUS.md) — جدول ۲۰۰ فاز
- [📄 REPORT.md](./REPORT.md) — این فایل (خلاصه‌ی اجرایی)
- [🚀 DEPLOY.md](./DEPLOY.md) — راهنمای دیپلوی

### مستندات فنی (website/ subfolder):
- [📋 CHECKLIST.md](./website/CHECKLIST.md) — checklist فازها
- [🔍 MCIcons-AUDIT.md](./website/MCIcons-AUDIT.md) — تحلیل پکیج mcicons
- [📜 CHANGELOG.md](./website/CHANGELOG.md) — تاریخچه‌ی نسخه‌ها
- [📖 website/README.md](./website/README.md) — README اختصاصی website

### مستندات فنی (docs/):
- [docs/stats.md](./docs/stats.md) — آمار سیستم
- [docs/crafting-3d.md](./docs/crafting-3d.md) — کرافت سه‌بعدی
- [docs/admin-panel.md](./docs/admin-panel.md) — پنل ادمین
- [docs/seeds-system.md](./docs/seeds-system.md) — سیستم سید

### سورس کد:
- [⚙️ Worker source](./worker/src/index.js) — Cloudflare Worker v3
- [📖 Worker README](./worker/README.md) — راهنمای دیپلوی
- [🐍 Admin backend](./admin/backend/main.py) — FastAPI admin
- [🖼️ cdn-images.ts](./website/src/lib/cdn-images.ts) — HuggingFace + ccvaults URL helpers

### لینک‌های خارجی:
- [🌐 سایت زنده](https://iran-minecraft-wiki.github.io/website/)
- [🤗 HuggingFace dataset](https://huggingface.co/datasets/Habib91700/minebed-assets) — 1052 تکسچر
- [📦 mcicons package](https://www.npmjs.com/package/@klashdevelopment/mcicons)
- [🌐 ccvaults.com](https://ccvaults.com/) — fallback منبع 3D renders
- [📖 Minecraft Wiki](https://minecraft.wiki/) — منبع داده‌ها

---

## 🚀 قدم‌های بعدی (Next Steps)

### فوری (این هفته):
1. کاربر: **deploy Worker v3** (5 دقیقه) — KV heartbeat آماده
2. کاربر: **test 2-browser online** (2 دقیقه) — باید online=2 بشه
3. ایجنت: **فاز 51 wiki content batch بعدی** — 50 بلاک دیگر با محتوای کامل (highest SEO impact)

### میان‌مدت (این ماه):
4. ایجنت: **دانلود batch بعدی block textures** (فاز 21 تکمیل) — ~110 بلاک باقی‌مونده
5. ایجنت: **دانلود batch بعدی item textures** (فاز 24 ادامه) — ~780 آیتم باقی‌مونده
6. ایجنت: **version diff + comparison tool** (فاز 67-68)

### بلندمدت (3 ماه):
7. کاربر: **setup Google OAuth** (برای فازهای 161-180)
8. ایجنت: **Lighthouse audit + fix** (فاز 181-192) — هدف >90 perf, >95 a11y/SEO
9. ایجنت: **integration tests + E2E** (فاز 193-200) — Playwright

---

## 📌 نتیجه‌گیری

- **پیشرفت واقعی:** ~16/200 فاز = **~8%** (پس از batch دوم؛ از ۵٪ batch اول افزایش یافته)
- **~82% کار باقی‌مونده** (~164 فاز انجام‌نشده + 20 فاز بلاک‌شده)
- **3 کار manual بحرانی** لازم است کاربر بکند (deploy Worker، test 2-browser، setup OAuth)
- **8 کار اصلی** که ایجنت می‌تونه بکنه (تکمیل textures، نوشتن محتوای wiki برای 700 بلاک دیگر، version diff/comparison، RSS cron)
- **mcicons package** آماده استفاده برای 807 بلاک + 1074 آیتم + 475 ساختار + 52 ماب (vanilla)
- **🤗 HuggingFace dataset** با 1052 تکسچر آماده (unlimited bandwidth، ccvaults fallback)
- **Worker v3** آماده deploy با KV limit protection (writes 3.5x under، lists 2.3x under)
- **۷۹۰ block data stubs** آماده (766 wiki-matched)، فقط 42 با محتوای کامل wiki — biggest gap در پروژه
- **۷۸/۷۸ نسخه** با features + changelog کامل ✅
- **2 gallery page** برای blocks + mobs با 3D renders + filters + search + pagination ✅

---

**Generated by:** Sub-agent (general-purpose) — Task ID: SA-DOCS-UPDATE
**زمان:** 2026-10-04
