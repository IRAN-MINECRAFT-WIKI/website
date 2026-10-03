# 📄 REPORT — MineBed Project

**تاریخ:** 2026-10-03
**نسخه:** 1.0 (Honest Stats Edition)
** repo:** [IRAN-MINECRAFT-WIKI/website](https://github.com/IRAN-MINECRAFT-WIKI/website)

---

## 📝 Executive Summary

MineBed یک ویکی فارسی ماینکرفت (Astro 5 + Cloudflare Worker) است که هدفش ارائه‌ی محتوای کامل MC 1.21 شامل 900 بلاک، 83 ماب، 1200 آیتم، 50 ساختار، 80 نسخه، و سیستم سید/کرافت/سرعت‌رانی است. پروژه با 200 فاز برنامه‌ریزی شده، اما تا امروز فقط **10 فاز (5%)** واقعاً کامل شده — 8 فاز کامل و 2 فاز نسبی (تکسچر بلاک 163/900 و آیتم 410/1200). نسخه‌های قبلی مستندات عدد 53% را نشان می‌دادند که اشتباه بود (آمده از 10/19 آیتم نقشه‌ی راه Next.js، نه 10/200 فاز). این فایل اعداد واقعی را ثبت می‌کند.

---

## 📈 پیشرفت صادقانه

### پیشرفت فازها
| وضعیت | تعداد | درصد |
|---|---|---|
| ✅ انجام‌شده (کامل) | 8 | 4.0% |
| 🟡 نسبی (partial) | 2 | 1.0% |
| ❌ انجام‌نشده | 170 | 85.0% |
| ⛔ بلاک‌شده | 20 | 10.0% |
| **مجموع** | **200** | **100%** |

### 🎯 پیشرفت واقعی: **10/200 = 5%**

> ❌ عدد قبلی 53% **اشتباه بود** — از 10/19 آیتم نقشه‌ی راه پنل Next.js آمده بود، نه 10/200 فاز پروژه.

---

## 📊 آمار سایت (Honest)

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
| مادها | ~500 | ~50 | 10% |

---

## ✅ فازهای انجام‌شده (10 فاز)

| # | فاز | وضعیت | commit |
|---|---|---|---|
| 1 | نقشه‌ی 2D سید (فاز 84) | ✅ | `900354c` |
| 2 | رندر سه‌بعدی Villager + 52 ماب (فاز 22) | ✅ | `41236f7` |
| 3 | صفحه‌ی FAQ (فاز 73) | ✅ | `01b71d9` |
| 4 | Drag & Drop کرافت (فاز 102) | ✅ | `01b71d9` |
| 5 | اپارات embed (فاز 149/150) | ✅ | `01b71d9` |
| 6 | نمودار 30 روز + 24 ساعت (فاز 128-129) | ✅ | `9e342f8` |
| 7 | آمار واقعی آنلاین KV (فاز 125) | ✅ | `09e8c7d` |
| 8 | تاریخ شمسی (فاز 130) | ✅ | `4f67ae1` |
| 9 | تکسچر بلاک mcicons (فاز 21) | 🟡 partial | `4b2da8e` (163/900 = 18%) |
| 10 | تکسچر آیتم (فاز 24) | 🟡 partial | `01b71d9` (410/1200 = 34%) |

---

## ❌ فازهای باقی‌مونده (187 فاز — خلاصه)

### بحرانی (manual — کاربر باید بکند):
1. **Deploy Worker v3** — کد آماده در `worker/src/index.js`. بریز روی Cloudflare.
2. **Test 2-browser online** — Chrome + Firefox همزمان /stats/ باز کن.
3. **Setup Google OAuth** (برای فازهای 161-180).

### ایجنت می‌تونه بکند (6 فاز اصلی):
1. فاز 21 ادامه — دانلود 737 بلاک باقی‌مونده از mcicons
2. فاز 24 ادامه — دانلود 790 آیتم باقی‌مونده از mcicons
3. فاز 51 ادامه — ساخت data stub برای 737 بلاک باقی‌مونده
4. فاز 53 ادامه — نوشتن changelog برای 78 نسخه
5. فاز 73 بیشتر — اضافه کردن سوال‌های بیشتر به FAQ
6. فاز 155-156 — RSS feed + Aparat auto-update (cron)

### ⛔ بلاک‌شده (3 فاز):
1. **اکانت کاربر (فازهای 161-180)** — نیاز به Google OAuth + D1 database + Worker deploy

### باقی‌مانده (173 فاز):
- 20 فاز UI/UX polish (1-20)
- 8 فاز Textures (23, 25-30)
- 25 فاز Content/Wiki (31-50, 54-60)
- 40 فاز Seeds/Craft (61-72, 74-83, 85-99, 100-101, 103-110)
- 25 فاز Backend (111-124, 126-127, 131-140)
- 18 فاز Speedrun/Video (141-148, 151-160)
- 20 فاز Testing/Cleanup (181-200)

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

### لینک‌های خارجی:
- [🌐 سایت زنده](https://iran-minecraft-wiki.github.io/website/)
- [📦 mcicons package](https://www.npmjs.com/package/@klashdevelopment/mcicons)
- [🌐 ccvaults.com](https://ccvaults.com/) — منبع 3D renders
- [📖 Minecraft Wiki](https://minecraft.wiki/) — منبع داده‌ها

---

## 🚀 قدم‌های بعدی (Next Steps)

### فوری (این هفته):
1. کاربر: **deploy Worker v3** (5 دقیقه) — KV heartbeat آماده
2. کاربر: **test 2-browser online** (2 دقیقه) — باید online=2 بشه
3. ایجنت: **دانلود batch بعدی block textures** (فاز 21 ادامه) — 737 بلاک باقی‌مونده

### میان‌مدت (این ماه):
4. ایجنت: **دانلود batch بعدی item textures** (فاز 24 ادامه) — 790 آیتم باقی‌مونده
5. ایجنت: **ساخت data stubs** برای بلاک‌های باقی‌مونده (فاز 51) — 737 stub
6. ایجنت: **نوشتن version changelog** (فاز 65-68) — 78 نسخه

### بلندمدت (3 ماه):
7. کاربر: **setup Google OAuth** (برای فازهای 161-180)
8. ایجنت: **Lighthouse audit + fix** (فاز 181-192) — هدف >90 perf, >95 a11y/SEO
9. ایجنت: **integration tests + E2E** (فاز 193-200) — Playwright

---

## 📌 نتیجه‌گیری

- **پیشرفت واقعی:** 10/200 فاز = **5%** (اصلاح شد از 53% اشتباه)
- **91.5% کار باقی‌مونده** (187 فاز انجام‌نشده + 3 فاز بلاک‌شده)
- **3 کار manual بحرانی** لازم است کاربر بکند (deploy Worker، test 2-browser، setup OAuth)
- **6 کار اصلی** که ایجنت می‌تونه بکنه (دانلود بقیه‌ی textures، ساخت stubs، نوشتن محتوا)
- **mcicons package** آماده استفاده برای 807 بلاک + 1074 آیتم + 475 ساختار + 52 ماب (vanilla)
- **Worker v3** آماده deploy با KV limit protection (writes 3.5x under، lists 2.3x under)

---

**Generated by:** Sub-agent (general-purpose) — Task ID: SA-DOCS
**زمان:** 2026-10-03
