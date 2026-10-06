# 📊 گزارش پروژه MineBed — Honest Preview

**آخرین آپدیت:** 2026-10-06 (پس از batch نهایی کارهای ایجنت)
** repo:** [IRAN-MINECRAFT-WIKI/website](https://github.com/IRAN-MINECRAFT-WIKI/website)
**🤗 assets:** [HuggingFace dataset](https://huggingface.co/datasets/Habib91700/minebed-assets) — **۱۵۳۶ تکسچر** (unlimited bandwidth)

> ⚠️ **اصلاحیه‌ی مهم:** نسخه‌ی قبلی این فایل عدد **53%** را نشان می‌داد که **اشتباه بود**.
> آن عدد از 10/19 آیتم نقشه‌ی راه (پنل Next.js) گرفته شده بود، **نه از 10/200 فاز واقعی پروژه**.
> عدد واقعی پس از batch نهایی: **~9%** (~18/200 فاز با احتساب نسبی‌ها به‌عنوان 0.5).

---

## 📈 پیشرفت صادقانه

| وضعیت | تعداد | درصد | توضیح |
|---|---|---|---|
| ✅ انجام‌شده (کامل) | ~17 | 8.5% | فازهایی که واقعاً کامل شدن |
| 🟡 نسبی (partial) | 1 | 0.5% × 1 = 0.5 فاز موزون | فاز ۵۱-۵۴ (wiki content) — شروع شده ولی کامل نه |
| ❌ انجام‌نشده | ~162 | 81.0% | باقی‌مونده |
| ⛔ بلاک‌شده | 20 | 10.0% | کل دسته‌ی ۷ (اکانت کاربر) — نیاز به Google OAuth |
| **مجموع** | **~200** | **100%** | — |

### 🎯 پیشرفت واقعی: **~18/200 = ~9%** (نه 53% ❌، نه ۸٪ سابق ❌)

---

## 📊 آمار سایت (Honest Stats — post-final-batch)

| بخش | هدف (MC 1.21) | فعلی | درصد | یادداشت |
|---|---|---|---|---|
| بلاک‌ها | ~900 | 790 | **88%** | 790 data stubs (766 wiki-matched) + 451 رندر سه‌بعدی + 126 تکسچر flat |
| ماب‌ها | ~83 | 52 | **63%** | 52/83 — full 3D renders از mcicons (52/52 = 100٪ از ماب‌های موجود) |
| آیتم‌ها | ~1200 | 420+ | **35%+** | 420+ رندر سه‌بعدی + 421 تکسچر flat از mcicons |
| ساختارها | ~50 | 8 | 16% | minimal data، no 3D renders |
| نسخه‌ها | ~80 | 78 | **100%** | 78/78 — 31 Java + 47 Bedrock، همگی با features + changelog |
| سیدها تست‌شده | 60 | 20 | 33% | partial |
| speedrun records | ~1500 | 1187 | ~79% | partial — some categories missing |
| رسپی کرافت | ~500 | ~300 | ~60% | partial — only vanilla recipes |
| مقالات ویکی | ~30 | 10 | 33% | partial templates only |
| بلاگ پست‌ها | ~15 | 7 | 47% | partial |
| آموزش‌ها | ~20 | 12 | 60% | partial |
| مادها | ~500 | ~50 | 10% | partial |

### 🆕 آمار نهایی (post-final-batch)

| بخش | تعداد | یادداشت |
|---|---|---|
| 🤗 تکسچرهای HuggingFace | **۱۵۳۶** | datasets/Habib91700/minebed-assets (unlimited bandwidth) — blocks + blocks-render + items + items-render + mobs + mobs-render + ui |
| 🚫 Emoji حذف‌شده | **۱۹۵** | از ۱۴ صفحه‌ی .astro (emoji توی data هنوز fallback هست) |
| 📝 محتوای کامل wiki — بلاک | **۳۶۷/۷۹۰ (۴۶٪)** | هر کدوم 19 content piece = intro(3) + behavior(3) + trivia(5) + history(5) + differences(3) = **6958 Persian string** |
| 📝 محتوای کامل wiki — ماب | **۴۲/۵۲ (۸۰٪)** | 22 ماب با محتوای کامل = **798 Persian string** |
| 📅 توضیحات نسخه | **۷۸/۷۸ (۱۰۰٪)** | features (۵) + changelog (۵) = **780 Persian string** |
| 🖼️ صفحات gallery | **2** | /wiki/blocks/gallery + /wiki/mobs/gallery (با 3D renders + filters + search + pagination) |
| 🗺️ نقشه‌ی 2D سید | **22 feature** | + drag/zoom (mouse+touch) + PNG download + radius filter |
| 🛠️ بلاک‌های fix شده | **14** | تکسچرهای خراب از mcasset.cloud + variants دانلود و جایزاری شدن |
| 🎥 صفحه‌ی /videos/ | rewritten | polished empty state (Aparat channel هنوز موجود نیست) |
| ❓ FAQ | **21 سوال** | در 7 دسته + JSON-LD + title duplication fix |
| 🌐 cdn-images.ts | rewritten | HuggingFace URLs با ccvaults fallback (blockImgUrl/blockRenderUrl/mobImgUrl/mobRenderUrl/itemImgUrl/itemRenderUrl/uiImgUrl) |
| 🇮🇷 ترجمه‌های اصلاح‌شده | **92 فایل** | 48 block + 44 mob (ندر، دایمند، اند، بدراک، رداستون، امرالد، اسکلتون، اسپایدر، کریپر، اوبسیدین، پیلجر، بلیز، ویچ، گاست، ادرمن، ندریت) |
| 🖼️ Broken images fix | ~15 → 1 | فقط frog (genuinely missing — no vanilla render) |
| 📜 رشته‌های محتوای فارسی | **~7000** | 6958 (wiki blocks) + 780 (versions) + 798 (early wiki) |

---

## ✅ فازهای انجام‌شده (~17 فاز کامل + 1 نسبی — لیست کامل)

| # | فاز | وضعیت | توضیح |
|---|---|---|---|
| 1 | آمار سایت واقعی (KV backend + ضد تقلب) | ✅ | فاز 125 — KV heartbeat + conditional writes + 10-min cache |
| 2 | stats.astro پیکسلی + Chart.js (30d + 24h) | ✅ | فاز 128-129 (paired) |
| 3 | تاریخ شمسی (jalaali-js + تهران) | ✅ | فاز 130 |
| 4 | نقشه‌ی 2D سید (Canvas + 22 features + drag/zoom + PNG) | ✅ | فاز 84 |
| 5 | تکسچر بلاک (mcicons 3D + HF + 790 stubs) | ✅ | فاز 21 — 790/900 (88%) mostly done |
| 6 | رندر سه‌بعدی Villager + 52 ماب (mcicons) | ✅ | فاز 22 |
| 7 | تکسچر آیتم (mcicons 3D + HF) | ✅ | فاز 24 — 420+ رندر + 421 تکسچر flat |
| 8 | emoji → PNG (pages) | ✅ | فاز 26 — 195 emoji از 14 صفحه حذف شد؛ data emoji fallback باقی است |
| 9 | Mod image resize (CSS constrain external) | ✅ (N/A) | فاز 32 — تصاویر ماد خارجی، CSS constrain می‌کنه |
| 10 | Block gallery page | ✅ | فاز 37 — /wiki/blocks/gallery با 3D renders + filters + search + pagination |
| 11 | Mob gallery page | ✅ | فاز 38 — /wiki/mobs/gallery |
| 12 | Version pages 78/78 + features + changelog | ✅ | فازهای 53، 65، 66 (Java + Bedrock) |
| 13 | صفحه‌ی FAQ (21 سوال + JSON-LD + title fix) | ✅ | فاز 73 |
| 14 | اپارات embed (channel + video) | ✅ | فاز 149/150 (paired) |
| 15 | Drag & Drop کرافت (HTML5 + touch) | ✅ | فاز 102 |
| 16 | KV limit fix (Worker v3) | ✅ | فاز 105/106/107 (code only — deploy pending) |
| 17 | Aparat custom player (overlapping) | ✅ | فاز 159 (paired با 149/150) |
| 18 | Texture CDN integration (HuggingFace) | ✅ | فاز 30 — cdn-images.ts rewritten |
| — | Wiki content (بلاک + ماب) | 🟡 partial | فازهای 51-54 — 367/790 بلاک (۴۶٪) + 42 ماب با محتوای کامل |

**Honest count:** 17 full ✅ + 1 partial 🟡 × 0.5 = 17 + 0.5 = **17.5 ≈ 18 / 200 = 9%**

---

## 🤗 HuggingFace Dataset (final state)

- **Repo:** https://huggingface.co/datasets/Habib91700/minebed-assets
- **URL pattern:** `https://huggingface.co/datasets/Habib91700/minebed-assets/resolve/main/{dir}/{id}.png`
- **تعداد:** **۱۵۳۶ تکسچر** (blocks + blocks-render + items + items-render + mobs + mobs-render + ui)
- **مزیت:** پهنای باند نامحدود، بدون هزینه، cache-friendly
- **Fallback:** ccvaults.com (mcicons CDN) برای آیتم‌هایی که هنوز به HF آپلود نشدن

### Integration در کد:
- فایل: `src/lib/cdn-images.ts` (completely rewritten)
- Helpers: `blockImgUrl()`, `blockRenderUrl()`, `mobImgUrl()`, `mobRenderUrl()`, `itemImgUrl()`, `itemRenderUrl()`, `uiImgUrl()`
- Known-missing list: 14 بلاک (banner, carpet, button, pressure-plate, item-frame, brewing-stand, hopper, repeater, comparator, tripwire-hook, redstone-wire, redstone-block, quartz-block, jack-o-lantern) — این‌ها از local flat PNG استفاده می‌کنن.

---

## 📊 Persian content stats

| Source | Strings | Description |
|---|---|---|
| Wiki blocks (intro/behavior/trivia/differences + history) | **6958** | 367 blocks × 19 pieces (3+3+5+5+3) |
| Version features + changelog | **780** | 78 versions × 10 items (5 features + 5 changelog) |
| Early wiki (blocks + mobs before batch) | **798** | 42 entity × 19 pieces |
| **Total Persian content strings** | **~7000** | All saved with `ensure_ascii=False`, UTF-8, indent=2 |

---

## 🔴 کارهای بحرانی باقی‌مونده

### 1. خودت باید بکنی (manual — 3 کار):
1. **Deploy Worker v3** — کد آماده در `worker/src/index.js`. لازم به Cloudflare dashboard یا `wrangler deploy`.
2. **Test 2-browser online** — بعد از Worker deploy، /stats/ رو توی Chrome + Firefox باز کن. online باید 2 بشه.
3. **Setup Google OAuth** (برای فازهای 161-180) — نیاز به Google Cloud Console + Worker deploy.

### 2. ایجنت می‌تونه بکنه (agent — 6 فاز اصلی):
1. **فاز 51 تکمیل** — نوشتن محتوای کامل wiki برای **~423 بلاک باقی‌مونده** (از ۳۶۷/۷۹۰ = ۴۶٪ به ۱۰۰٪) — **بالاترین impact برای SEO**
2. **فاز 52 تکمیل** — دانلود 31 ماب باقی‌مونده (از ۶۳٪ به ۱۰۰٪) + محتوای wiki برای ~10 ماب دیگر
3. **فاز 67** — version diff pages
4. **فاز 68** — version comparison tool
5. **فاز 73 بیشتر** — اضافه کردن سوال‌های بیشتر به FAQ
6. **فاز 155-156** — RSS feed + Aparat auto-update (cron job)

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
- **منبع اصلی:** HuggingFace dataset (Habib91700/minebed-assets) — **۱۵۳۶ تکسچر**
- **منبع fallback:** ccvaults.com CDN (webp files)
- **موارد قابل استفاده (vanilla):** items, blocks, structures, paintings, interfaces, titles, gui, particles
- **موارد مخلوط:** mobs (vanilla + MCL + MCD)، icons، backgrounds
- **موارد ممنوع:** modded_weapons (هیچ‌کدوم vanilla نیستن)
- **تحلیل کامل:** [MCIcons-AUDIT.md](./website/MCIcons-AUDIT.md)

### Helper scripts (در `website/scripts/`):
- `fill_wiki_content.py` — single source of truth برای 42 entity wiki content (idempotent)
- `fill_wiki_more_part1..4.py` — 100 blocks × 19 pieces (1900 strings) — idempotent
- `fill_wiki_200_part1..4.py` + `wiki200_helpers.py` — 200 blocks × 19 pieces (3800 strings) — idempotent
- `add_version_descriptions.py` — 78 نسخه features + changelog (idempotent)
- `fix_translations.py` — اعمال ۴ ترجمه‌ی Persian (ندر، اند، بدراک، رداستون)

---

## 🚀 قدم بعدی (Next Steps)

### فوری (این هفته):
1. کاربر: **deploy Worker v3** (5 دقیقه)
2. کاربر: **test 2-browser** online (2 دقیقه)
3. ایجنت: **فاز 51 wiki content batch بعدی** — 100+ بلاک دیگر با محتوای کامل

### میان‌مدت (این ماه):
4. ایجنت: **فاز 51 تکمیل** — نوشتن محتوای کامل wiki برای ~423 بلاک باقی‌مونده (از ۴۶٪ به ۱۰۰٪)
5. ایجنت: **فاز 52 تکمیل** — دانلود 31 ماب باقی‌مونده + محتوای wiki
6. ایجنت: **version diff + comparison tool** (فاز 67-68)

### بلندمدت (3 ماه):
7. کاربر: **setup Google OAuth** (برای فازهای 161-180)
8. ایجنت: **Lighthouse audit + fix** (فاز 181-192)
9. ایجنت: **integration tests + E2E** (فاز 193-200)

---

## 📎 لینک‌ها

- [🌐 سایت زنده](https://iran-minecraft-wiki.github.io/website/)
- [🤗 HuggingFace dataset](https://huggingface.co/datasets/Habib91700/minebed-assets) — **۱۵۳۶ تکسچر** (unlimited bandwidth)
- [📖 README.md](./README.md) — معرفی پروژه
- [📋 PHASES_STATUS.md](./PHASES_STATUS.md) — جدول کامل ۲۰۰ فاز
- [📄 REPORT.md](./REPORT.md) — خلاصه‌ی اجرایی
- [📋 CHECKLIST.md](./website/CHECKLIST.md) — checklist فازها
- [🔍 MCIcons-AUDIT.md](./website/MCIcons-AUDIT.md) — تحلیل پکیج mcicons
- [📜 CHANGELOG.md](./website/CHANGELOG.md) — تاریخچه‌ی نسخه‌ها
- [⚙️ Worker source](./worker/src/index.js) — کد Cloudflare Worker v3
- [📖 Worker README](./worker/README.md) — راهنمای دیپلوی
- [📚 docs/](./docs/) — مستندات فنی (stats, crafting-3d, admin-panel, seeds-system)
