# 📊 گزارش پروژه MineBed — Honest Preview

**آخرین آپدیت:** 2026-10-04 (پس از batch دوم کارهای ایجنت)
**Latest commit:** `63753e5` (gallery pages + wiki content + version changelog)
**Previous significant commits:** `b91b59b`, `3c84cc4`, `09e8c7d`, `9e342f8`, `4f67ae1`, `900354c`, `01b71d9`, `41236f7`, `4b2da8e`

> ⚠️ **اصلاحیه‌ی مهم:** نسخه‌ی قبلی این فایل عدد **53%** را نشان می‌داد که **اشتباه بود**.
> آن عدد از 10/19 آیتم نقشه‌ی راه (پنل Next.js) گرفته شده بود، **نه از 10/200 فاز واقعی پروژه**.
> عدد واقعی پس از batch دوم: **~8%** (~16/200 فاز با احتساب نسبی‌ها به‌عنوان 0.5).

---

## 📈 پیشرفت صادقانه

| وضعیت | تعداد | درصد | توضیح |
|---|---|---|---|
| ✅ انجام‌شده (کامل) | ~13 | 6.5% | فازهایی که واقعاً کامل شدن |
| 🟡 نسبی (partial) | 5 | 1.25% × 2 = 2.5 فاز موزون | شروع شدن ولی هنوز کامل نه |
| ❌ انجام‌نشده | ~162 | 81.0% | باقی‌مونده |
| ⛔ بلاک‌شده | 20 | 10.0% | کل دسته‌ی ۷ (اکانت کاربر) — نیاز به Google OAuth |
| **مجموع** | **~200** | **100%** | — |

### 🎯 پیشرفت واقعی: **~16/200 = ~8%** (نه 53% ❌)

---

## 📊 آمار سایت (Honest Stats — post-batch-2)

| بخش | هدف (MC 1.21) | فعلی | درصد | یادداشت |
|---|---|---|---|---|
| بلاک‌ها | ~900 | 790 | **88%** | 790 data stubs (766 wiki-matched) + 451 رندر سه‌بعدی |
| ماب‌ها | ~83 | 52 | **63%** | 52/83 — full 3D renders از mcicons (52/52 = 100٪ از ماب‌های موجود) |
| آیتم‌ها | ~1200 | 420+ | **35%+** | 420 رندر سه‌بعدی از mcicons |
| ساختارها | ~50 | 8 | 16% | minimal data، no 3D renders |
| نسخه‌ها | ~80 | 78 | **100%** | 78/78 — 31 Java + 47 Bedrock، همگی با features + changelog |
| سیدها تست‌شده | 60 | 20 | 33% | partial |
| speedrun records | ~1500 | 1187 | ~79% | partial — some categories missing |
| رسپی کرافت | ~500 | ~300 | ~60% | partial — only vanilla recipes |
| مقالات ویکی | ~30 | 10 | 33% | partial templates only |
| بلاگ پست‌ها | ~15 | 7 | 47% | partial |
| آموزش‌ها | ~20 | 12 | 60% | partial |
| مادها | ~500 | ~50 | 10% | partial |

### 🆕 آمار جدید batch دوم

| بخش | تعداد | یادداشت |
|---|---|---|
| 🤗 تکسچرهای HuggingFace | **1052** | datasets/Habib91700/minebed-assets (unlimited bandwidth) |
| 🚫 Emoji حذف‌شده | **195** | از 14 صفحه‌ی .astro (emoji توی data هنوز fallback هست) |
| 📝 محتوای کامل wiki | **42 entity** | 22 بلاک + 20 ماب (هر کدوم 19 content piece = 798 string) |
| 📅 توضیحات نسخه | **78/78** | features (۵) + changelog (۵) = 780 string |
| 🖼️ صفحات gallery | **2** | /wiki/blocks/gallery + /wiki/mobs/gallery (با 3D renders + filters + search + pagination) |
| 🗺️ نقشه‌ی 2D سید | **22 feature** | + drag/zoom (mouse+touch) + PNG download + radius filter |
| 🛠️ بلاک‌های fix شده | **14** | تکسچرهای خراب از mcasset.cloud + variants دانلود و جایگزاری شدن |
| 🎥 صفحه‌ی /videos/ | rewritten | polished empty state (Aparat channel هنوز موجود نیست) |
| ❓ FAQ title | fixed | title duplication از JSON-LD + H1 برطرف شد |
| 🌐 cdn-images.ts | rewritten | HuggingFace URLs با ccvaults fallback (blockImgUrl/blockRenderUrl/mobImgUrl/mobRenderUrl/itemImgUrl/itemRenderUrl) |
| 🇮🇷 ترجمه‌های اصلاح‌شده | 48 block + 44 mob | ندر، دایمند، اند، بدراک، رداستون، امرالد، اسکلتون، اسپایدر، کریپر، اوبسیدین، پیلجر، بلیز، ویچ، گاست، ادرمن، ندریت |

---

## ✅ فازهای انجام‌شده (~16 فاز — لیست کامل با commits)

| # | فاز | commit | VLM تأیید | توضیح |
|---|---|---|---|---|
| 1 | آمار سایت واقعی (KV backend + ضد تقلب) | `09e8c7d` | ✅ | فاز 125 |
| 2 | stats.astro پیکسلی + Chart.js (30d + 24h) | `9e342f8` | ✅ | فاز 128-129 (paired) |
| 3 | تاریخ شمسی (jalaali-js + تهران) | `4f67ae1` | ✅ | فاز 130 |
| 4 | نقشه‌ی 2D سید (Canvas + 22 features + drag/zoom + PNG) | `900354c` + `b91b59b` | ✅ | فاز 84 |
| 5 | تکسچر بلاک (mcicons 3D + HF + 790 stubs) | `4b2da8e` + `b91b59b` + `63753e5` | 🟡 | فاز 21 — 790/900 (88%) partial → mostly done |
| 6 | رندر سه‌بعدی Villager + 52 ماب (mcicons) | `41236f7` | ✅ | فاز 22 |
| 7 | تکسچر آیتم (mcicons 3D) | `01b71d9` + batch | 🟡 | فاز 24 — 420/1200 (35%) partial |
| 8 | emoji → PNG (pages) | `b91b59b` | 🟡 | فاز 26 — 195 emoji از 14 صفحه حذف شد؛ data emoji fallback باقی است |
| 9 | Mod image resize (CSS constrain external) | (no commit, N/A) | ✅ (N/A) | فاز 32 — تصاویر ماد خارجی، CSS constrain می‌کنه |
| 10 | Block gallery page | `63753e5` | ✅ | فاز 37 — /wiki/blocks/gallery |
| 11 | Mob gallery page | `63753e5` | ✅ | فاز 38 — /wiki/mobs/gallery |
| 12 | Version pages 78/78 + features + changelog | `63753e5` | ✅ | فازهای 53، 65، 66 (Java + Bedrock) |
| 13 | صفحه‌ی FAQ (21 سوال + JSON-LD + title fix) | `01b71d9` + `b91b59b` | ✅ | فاز 73 |
| 14 | اپارات embed (channel + video) | `01b71d9` | ✅ | فاز 149/150 (paired) |
| 15 | Drag & Drop کرافت (HTML5 + touch) | `01b71d9` | ✅ | فاز 102 |
| 16 | KV limit fix (Worker v3) | `09e8c7d` | ✅ | فاز 105/106/107 (code only — deploy pending) |

---

## 🤗 HuggingFace Dataset (جدید)

- **Repo:** https://huggingface.co/datasets/Habib91700/minebed-assets
- **URL pattern:** `https://huggingface.co/datasets/Habib91700/minebed-assets/resolve/main/{dir}/{id}.png`
- **تعداد:** 1052 تکسچر (blocks + blocks-render + items + items-render + mobs + mobs-render + ui)
- **مزیت:** پهنای باند نامحدود، بدون هزینه، cache-friendly
- **Fallback:** ccvaults.com (mcicons CDN) برای آیتم‌هایی که هنوز به HF آپلود نشدن

### Integration در کد:
- فایل: `src/lib/cdn-images.ts` (completely rewritten)
- Helpers: `blockImgUrl()`, `blockRenderUrl()`, `mobImgUrl()`, `mobRenderUrl()`, `itemImgUrl()`, `itemRenderUrl()`, `uiImgUrl()`
- Knwon-missing list: 14 بلاک (banner, carpet, button, pressure-plate, item-frame, brewing-stand, hopper, repeater, comparator, tripwire-hook, redstone-wire, redstone-block, quartz-block, jack-o-lantern) — این‌ها از local flat PNG استفاده می‌کنن.

---

## 🔴 کارهای بحرانی باقی‌مونده

### 1. خودت باید بکنی (manual — 3 کار):
1. **Deploy Worker v3** — کد آماده در `worker/src/index.js`. لازم به Cloudflare dashboard یا `wrangler deploy`.
2. **Test 2-browser online** — بعد از Worker deploy، /stats/ رو توی Chrome + Firefox باز کن. online باید 2 بشه.
3. **Setup Google OAuth** (برای فازهای 161-180) — نیاز به Google Cloud Console + Worker deploy.

### 2. ایجنت می‌تونه بکنه (agent — 8 فاز اصلی):
1. **فاز 21 تکمیل** — دانلود ~110 بلاک باقی‌مونده (از ۸۸٪ به ۱۰۰٪)
2. **فاز 24 ادامه** — دانلود ~780 آیتم باقی‌مونده (از ۳۵٪ به ۱۰۰٪)
3. **فاز 51 ادامه** — نوشتن محتوای کامل wiki برای ~700 بلاک باقی‌مونده (از 42 به 790) — **بالاترین impact برای SEO**
4. **فاز 52 تکمیل** — دانلود 31 ماب باقی‌مونده (از ۶۳٪ به ۱۰۰٪)
5. **فاز 67** — version diff pages
6. **فاز 68** — version comparison tool
7. **فاز 73 بیشتر** — اضافه کردن سوال‌های بیشتر به FAQ
8. **فاز 155-156** — RSS feed + Aparat auto-update (cron job)

### 3. ⛔ بلاک‌شده (20 فاز):
1. **اکانت کاربر (فازهای 161-180)** — نیاز به Google OAuth + D1 database + Worker deploy

---

## 📊 نکات فنی

### Worker v3 (Cloudflare KV):
- **منبع:** `worker/src/index.js`
- **استراتژی:** heartbeat 5min، conditional writes (get → put if missing)، 10-min stats cache
- **سقف روزانه (free tier):** 1,000 writes, 1,000 lists, 100,000 reads
- **پیش‌بینی:** writes 288/day (3.5x under)، lists 432/day (2.3x under)، reads 864/day (115x under)
- **وضعیت:** آماده‌ی deploy (کاربر باید بکنه)

### mcicons package:
- **پکیج:** `@klashdevelopment/mcicons@1.0.2` (369 mob renders + 807 blocks + 1074 items + 475 structures)
- **منبع اصلی:** HuggingFace dataset (Habib91700/minebed-assets) — 1052 تکسچر
- **منبع fallback:** ccvaults.com CDN (webp files)
- **موارد قابل استفاده (vanilla):** items, blocks, structures, paintings, interfaces, titles, gui, particles
- **موارد مخلوط:** mobs (vanilla + MCL + MCD)، icons، backgrounds
- **موارد ممنوع:** modded_weapons (هیچ‌کدوم vanilla نیستن)
- **تحلیل کامل:** [MCIcons-AUDIT.md](./website/MCIcons-AUDIT.md)

### Helper scripts (در `website/scripts/`):
- `fill_wiki_content.py` — single source of truth برای 42 entity wiki content (idempotent)
- `add_version_descriptions.py` — 78 نسخه features + changelog (idempotent)
- `fix_translations.py` — اعمال ۴ ترجمه‌ی Persian (ندر، اند، بدراک، رداستون)

---

## 🚀 قدم بعدی (Next Steps)

### فوری (این هفته):
1. کاربر: **deploy Worker v3** (5 دقیقه)
2. کاربر: **test 2-browser** online (2 دقیقه)
3. ایجنت: **فاز 51 wiki content batch بعدی** — 50 بلاک دیگر با محتوای کامل

### میان‌مدت (این ماه):
4. ایجنت: **دانلود batch بعدی block textures** (فاز 21 تکمیل) — ~110 بلاک باقی‌مونده
5. ایجنت: **دانلود batch بعدی item textures** (فاز 24 ادامه) — ~780 آیتم باقی‌مونده
6. ایجنت: **version diff + comparison tool** (فاز 67-68)

### بلندمدت (3 ماه):
7. کاربر: **setup Google OAuth** (برای فازهای 161-180)
8. ایجنت: **Lighthouse audit + fix** (فاز 181-192)
9. ایجنت: **integration tests + E2E** (فاز 193-200)

---

## 📎 لینک‌ها

- [🌐 سایت زنده](https://iran-minecraft-wiki.github.io/website/)
- [🤗 HuggingFace dataset](https://huggingface.co/datasets/Habib91700/minebed-assets) — 1052 تکسچر (unlimited bandwidth)
- [📖 README.md](./README.md) — معرفی پروژه
- [📋 PHASES_STATUS.md](./PHASES_STATUS.md) — جدول کامل ۲۰۰ فاز
- [📄 REPORT.md](./REPORT.md) — خلاصه‌ی اجرایی
- [📋 CHECKLIST.md](./website/CHECKLIST.md) — checklist فازها
- [🔍 MCIcons-AUDIT.md](./website/MCIcons-AUDIT.md) — تحلیل پکیج mcicons
- [📜 CHANGELOG.md](./website/CHANGELOG.md) — تاریخچه‌ی نسخه‌ها
- [⚙️ Worker source](./worker/src/index.js) — کد Cloudflare Worker v3
- [📖 Worker README](./worker/README.md) — راهنمای دیپلوی
- [📚 docs/](./docs/) — مستندات فنی (stats, crafting-3d, admin-panel, seeds-system)
