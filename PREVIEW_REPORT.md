# 📊 گزارش پروژه MineBed — Honest Preview

**آخرین آپدیت:** 2026-10-03
**Latest commit:** `3c84cc4` (docs + 50 block stubs)
**Previous significant commits:** `09e8c7d`, `9e342f8`, `4f67ae1`, `900354c`, `01b71d9`, `41236f7`, `4b2da8e`

> ⚠️ **اصلاحیه‌ی مهم:** نسخه‌ی قبلی این فایل عدد **53%** را نشان می‌داد که **اشتباه بود**.
> آن عدد از 10/19 آیتم نقشه‌ی راه (پنل Next.js) گرفته شده بود، **نه از 10/200 فاز واقعی پروژه**.
> عدد واقعی: **5%**.

---

## 📈 پیشرفت صادقانه

| وضعیت | تعداد | درصد | توضیح |
|---|---|---|---|
| ✅ انجام‌شده (کامل) | 8 | 4.0% | فازهایی که واقعاً کامل شدن |
| 🟡 نسبی (partial) | 2 | 1.0% | شروع شدن ولی هنوز کامل نه |
| ❌ انجام‌نشده | 170 | 85.0% | باقی‌مونده (شامل ۱۲۹ و ۱۵۰ که با ۱۲۸ و ۱۴۹ جفت هستن) |
| ⛔ بلاک‌شده | 20 | 10.0% | کل دسته‌ی ۷ (اکانت کاربر) — نیاز به Google OAuth |
| **مجموع** | **200** | **100%** | — |

### 🎯 پیشرفت واقعی: **10/200 = 5%** (نه 53% ❌)

---

## 📊 آمار سایت (Honest Stats)

| بخش | هدف (MC 1.21) | فعلی | درصد | یادداشت |
|---|---|---|---|---|
| بلاک‌ها | ~900 | 163 | 18% | 163/900 — data stubs + 3D renders via mcicons |
| ماب‌ها | ~83 | 52 | 63% | 52/83 — full 3D renders via mcicons |
| آیتم‌ها | ~1200 | ~410 | 34% | 410/1200 — flat PNG textures only (no 3D) |
| ساختارها | ~50 | 8 | 16% | 8/50 — minimal data, no 3D renders |
| نسخه‌ها | ~80 | 78 | 98% | 78/80 — pages exist but no changelog descriptions |
| سیدها تست‌شده | 60 | 20 | 33% | 20/60 — partial |
| speedrun records | ~1500 | 1187 | ~79% | partial — some categories missing |
| رسپی کرافت | ~500 | ~300 | ~60% | partial — only vanilla recipes |
| مقالات ویکی | ~30 | 10 | 33% | 10/30 — partial templates only |
| بلاگ پست‌ها | ~15 | 7 | 47% | 7/15 — partial |
| آموزش‌ها | ~20 | 12 | 60% | 12/20 — partial |
| مادها | ~500 | ~50 | 10% | 50/500 — partial |

---

## ✅ فازهای انجام‌شده (10 فاز — لیست کامل با commits)

| # | فاز | commit | VLM تأیید | توضیح |
|---|---|---|---|---|
| 1 | آمار سایت واقعی (KV backend + ضد تقلب) | `09e8c7d` | ✅ | conditional writes + TTL, KV limit protection |
| 2 | stats.astro پیکسلی + Chart.js (30d + 24h) | `9e342f8` | ✅ | فاز 128-129 |
| 3 | تاریخ شمسی (jalaali-js + تهران) | `4f67ae1` | ✅ | فاز 130 |
| 4 | نقشه‌ی 2D سید (Canvas + grid + compass) | `900354c` | ✅ | فاز 84 |
| 5 | تکسچر بلاک (mcicons 3D isometric) | `4b2da8e` | 🟡 | فاز 21 — 163/900 (18%) partial |
| 6 | رندر سه‌بعدی Villager + 52 ماب (mcicons) | `41236f7` | ✅ | فاز 22 |
| 7 | اپارات embed (channel + video) | `01b71d9` | ✅ | فاز 149/150 |
| 8 | Drag & Drop کرافت (HTML5 + touch) | `01b71d9` | ✅ | فاز 102 |
| 9 | صفحه‌ی FAQ (21 سوال + JSON-LD) | `01b71d9` | ✅ | فاز 73 |
| 10 | KV limit fix (Worker v3) | `09e8c7d` | ✅ | فاز 105/106/107 (code only — deploy pending) |

---

## 🔴 کارهای بحرانی باقی‌مونده

### 1. خودت باید بکنی (manual — 3 کار):
1. **Deploy Worker v3** — کد آماده در `worker/src/index.js`. لازم به Cloudflare dashboard یا `wrangler deploy`.
2. **Test 2-browser online** — بعد از Worker deploy، /stats/ رو توی Chrome + Firefox باز کن. online باید 2 بشه.
3. **Setup Google OAuth** (برای فازهای 161-180) — نیاز به Google Cloud Console + Worker deploy.

### 2. ایجنت می‌تونه بکنه (agent — 6 فاز اصلی):
1. **فاز 21 ادامه** — دانلود 737 بلاک باقی‌مونده از mcicons (3D isometric renders)
2. **فاز 24 ادامه** — دانلود 790 آیتم باقی‌مونده از mcicons (3D isometric renders)
3. **فاز 51 ادامه** — ساخت data stub برای 737 بلاک باقی‌مونده
4. **فاز 53 ادامه** — نوشتن changelog برای 78 نسخه
5. **فاز 73 بیشتر** — اضافه کردن سوال‌های بیشتر به FAQ
6. **فاز 155-156** — RSS feed + Aparat auto-update (cron job)

### 3. ⛔ بلاک‌شده (3 فاز):
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
- **منبع:** ccvaults.com CDN (webp files)
- **موارد قابل استفاده (vanilla):** items, blocks, structures, paintings, interfaces, titles, gui, particles
- **موارد مخلوط:** mobs (vanilla + MCL + MCD)، icons، backgrounds
- **موارد ممنوع:** modded_weapons (هیچ‌کدوم vanilla نیستن)
- **تحلیل کامل:** [MCIcons-AUDIT.md](./website/MCIcons-AUDIT.md)

---

## 🚀 قدم بعدی (Next Steps)

### فوری (این هفته):
1. کاربر: **deploy Worker v3** (5 دقیقه)
2. کاربر: **test 2-browser** online (2 دقیقه)
3. ایجنت: **دانلود batch بعدی block textures** (فاز 21 ادامه)

### میان‌مدت (این ماه):
4. ایجنت: **دانلود batch بعدی item textures** (فاز 24 ادامه)
5. ایجنت: **ساخت data stubs** برای بلاک‌های باقی‌مونده (فاز 51)
6. ایجنت: **نوشتن version changelog** (فاز 65-68)

### بلندمدت (3 ماه):
7. کاربر: **setup Google OAuth** (برای فازهای 161-180)
8. ایجنت: **Lighthouse audit + fix** (فاز 181-192)
9. ایجنت: **integration tests + E2E** (فاز 193-200)

---

## 📎 لینک‌ها

- [🌐 سایت زنده](https://iran-minecraft-wiki.github.io/website/)
- [📖 README.md](./README.md) — معرفی پروژه
- [📋 PHASES_STATUS.md](./PHASES_STATUS.md) — جدول کامل ۲۰۰ فاز
- [📄 REPORT.md](./REPORT.md) — خلاصه‌ی اجرایی
- [📋 CHECKLIST.md](./website/CHECKLIST.md) — checklist فازها
- [🔍 MCIcons-AUDIT.md](./website/MCIcons-AUDIT.md) — تحلیل پکیج mcicons
- [📜 CHANGELOG.md](./website/CHANGELOG.md) — تاریخچه‌ی نسخه‌ها
- [⚙️ Worker source](./worker/src/index.js) — کد Cloudflare Worker v3
- [📖 Worker README](./worker/README.md) — راهنمای دیپلوی
- [📚 docs/](./docs/) — مستندات فنی (stats, crafting-3d, admin-panel, seeds-system)
