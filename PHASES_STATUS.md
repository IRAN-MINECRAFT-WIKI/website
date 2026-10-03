# 📋 وضعیت ۲۰۰ فاز MineBed

**آخرین آپدیت:** 2026-10-03

---

## خلاصه

| وضعیت | تعداد |
|---|---|
| ✅ انجام شده | ۱۰ |
| 🔴 خودت باید بکنی | ۲ |
| 🟠 ایجنت می‌تونه بکنه | ۶ |
| ⛔ بلاک شده | ۱ |
| ❌ انجام نشده | ۱۸۱ |
| **مجموع** | **۲۰۰** |

---

## ✅ فازهای انجام‌شده

| # | فاز | وضعیت | commit |
|---|---|---|---|
| ۱ | آمار سایت از KV (واقعی + ضد تقلب) | ✅ | `09e8c7d` |
| ۲ | stats.astro پیکسلی + Chart.js | ✅ | `9e342f8` |
| ۳ | تاریخ شمسی (jalaali-js + تهران) | ✅ | `4f67ae1` |
| ۴ | نقشه‌ی ۲D سید (فاز ۸۴) | ✅ | `900354c` |
| ۵ | تکسچر بلاک ۱۱۲/۱۱۳ (۹۹٪) | ✅ | `01b71d9` |
| ۶ | villager mcicons 3D render | ✅ | `41236f7` |
| ۷ | اپارات embed (فاز ۱۴۹) | ✅ | `01b71d9` |
| ۸ | Drag & Drop کرافت (فاز ۱۰۲) | ✅ | `01b71d9` |
| ۹ | FAQ صفحه (فاز ۷۳) | ✅ | `01b71d9` |
| ۱۰ | رندر سه‌بعدی بلاک (۸۹/۱۳۳) + ۸۷ باگ fix | ✅ | `4b2da8e` |

---

## 🔴 فازهای بحرانی — خودت باید بکنی

| # | فاز | چرا | اقدام |
|---|---|---|---|
| ۵ | دیپلوی Worker v3 | نیاز به Cloudflare dashboard | کد توی `worker/src/index.js` رو جایگزین کن |
| ۶ | تست آنلاین ۲ مرورگر | بعد از Worker deploy | Chrome + Firefox همزمان باز کن |

---

## 🟠 فازهای باقی‌مونده — ایجنت می‌تونه بکنه

| # | فاز | توضیح |
|---|---|---|
| ۱۶ | تکسچر ۴۳ آیتم باقی‌مونده | از mcicons items |
| ۲۶ | emoji → PNG | با gui/interfaces |
| ۳۲ | resize عکس مودها به ۱۲۸×۱۲۸ | با sharp/ImageMagick |
| ۳۷-۳۸ | گالری بلاک + ماب | صفحه‌ی گرید تصویری |
| ۵۱-۵۴ | محتوای ۳-۵ پاراگراف ویکی | ۴۰ آیتم |
| ۶۵-۶۸ | توضیحات نسخه‌ها | ۷۸ نسخه |

---

## ⛔ فازهای بلاک‌شده

| # | فاز | چرا |
|---|---|---|
| ۱۶۱-۱۸۰ | اکانت کاربر | نیاز به Google OAuth + Worker |

---

## ❌ فازهای انجام‌نشده (نمونه)

| # | فاز | اولویت |
|---|---|---|
| ۱۵۵-۱۵۶ | RSS + Aparat auto-update | متوسط |
| ۱۹۰-۱۹۲ | Lighthouse audit (>۹۰/>۹۵) | متوسط |
| ۱۹۳-۲۰۰ | تست‌های integration/E2E | کم |

---

## 📎 لینک‌ها

- [سایت زنده](https://iran-minecraft-wiki.github.io/website/)
- [README](https://github.com/IRAN-MINECRAFT-WIKI/website/blob/main/README.md)
- [CHECKLIST.md](https://github.com/IRAN-MINECRAFT-WIKI/website/blob/main/website/CHECKLIST.md)
- [PREVIEW_REPORT.md](https://github.com/IRAN-MINECRAFT-WIKI/website/blob/main/PREVIEW_REPORT.md)
- [MCIcons-AUDIT.md](https://github.com/IRAN-MINECRAFT-WIKI/website/blob/main/website/MCIcons-AUDIT.md)
