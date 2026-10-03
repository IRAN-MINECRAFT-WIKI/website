# 📊 گزارش پروژه MineBed

**آخرین آپدیت:** 2026-10-03 (commit `4b2da8e`)

---

## 📈 پیشرفت کلی

| وضعیت | تعداد | درصد |
|---|---|---|
| ✅ انجام شده | ۱۰ | ۵۳٪ |
| 🔴 خودت باید بکنی | ۲ | — |
| 🟠 ایجنت می‌تونه بکنه | ۶ | — |
| ⛔ بلاک شده | ۱ | — |
| **مجموع** | **۱۹** | — |

---

## 🎯 فازهای انجام‌شده

| # | فاز | commit | VLM تأیید |
|---|---|---|---|
| ۱ | آمار سایت از KV (واقعی + متمرکز + ضد تقلب) | `09e8c7d` | ✅ |
| ۲ | stats.astro پیکسلی + Chart.js | `9e342f8` | ✅ |
| ۳ | تاریخ شمسی (jalaali-js + وقت تهران) | `4f67ae1` | ✅ |
| ۴ | نقشه‌ی ۲D سید (فاز ۸۴) | `900354c` | ✅ |
| ۵ | تکسچر ۷۳ بلاک — ۱۱۲/۱۱۳ (۹۹٪) | `01b71d9` | ✅ |
| ۶ | villager mob PNG (mcicons 3D render) | `41236f7` | ✅ |
| ۷ | اپارات embed (فاز ۱۴۹/۱۵۰) | `01b71d9` | ✅ |
| ۸ | Drag & Drop در کرافت (فاز ۱۰۲) | `01b71d9` | ✅ |
| ۹ | صفحه‌ی FAQ (فاز ۷۳) | `01b71d9` | ✅ |
| ۱۰ | رندرهای سه‌بعدی بلاک (۸۹/۱۳۳) + ۸۷ باگ fix | `4b2da8e` | ✅ |

---

## 🔴 کارهای بحرانی باقی‌مونده

### خودت باید بکنی (۲ فاز):

1. **دیپلوی Worker v3** — کد توی `worker/src/index.js` (KV limit fix شده)
2. **تست آنلاین با ۲ مرورگر** — Chrome + Firefox همزمان، باید online=2 بشه

### ایجنت می‌تونه بکنه (۶ فاز):

1. تکسچر ۴۳ آیتم باقی‌مونده (فاز ۲۴ ادامه)
2. محتوای ۳-۵ پاراگراف ویکی (فاز ۵۱-۵۴، ۴۰ آیتم)
3. گالری بلاک + ماب (فاز ۳۷-۳۸)
4. توضیحات نسخه‌ها (فاز ۶۵-۶۸، ۷۸ نسخه)
5. emoji → PNG (فاز ۲۶)
6. resize عکس مودها به ۱۲۸×۱۲۸ (فاز ۳۲)

### ⛔ بلاک شده (۱ فاز):

1. اکانت کاربر (فاز ۱۶۱-۱۸۰) — نیاز به Google OAuth + Worker deploy

---

## 📊 آمار سایت

| بخش | واقعی MC 1.21 | فعلی | درصد |
|---|---|---|---|
| بلاک‌ها | ~۹۰۰ | ۱۱۳ | ۱۲٪ |
| ماب‌ها | ~۸۳ | ۵۲ | ۶۳٪ |
| آیتم‌ها | ~۱۲۰۰ | ~۴۱۰ | ۳۴٪ |
| ساختارها | ~۵۰ | ۸ | ۱۶٪ |
| نسخه‌ها | ~۸۰ | ۷۸ | ۹۸٪ |
| سیدها تست‌شده | — | ۲۰ | — |
| speedrun records | — | ۱۱۸۷ | — |
| رسپی کرافت | — | ۳۰۰ | — |

---

## 📎 لینک‌ها

- [سایت زنده](https://iran-minecraft-wiki.github.io/website/)
- [README](https://github.com/IRAN-MINECRAFT-WIKI/website/blob/main/README.md)
- [CHECKLIST.md](https://github.com/IRAN-MINECRAFT-WIKI/website/blob/main/website/CHECKLIST.md)
- [MCIcons-AUDIT.md](https://github.com/IRAN-MINECRAFT-WIKI/website/blob/main/website/MCIcons-AUDIT.md)
- [PHASES_STATUS.md](https://github.com/IRAN-MINECRAFT-WIKI/website/blob/main/PHASES_STATUS.md)
- [Worker source](https://github.com/IRAN-MINECRAFT-WIKI/website/blob/main/worker/src/index.js)

---

## 🚀 قدم بعدی

1. استخراج لیست کامل بلاک‌ها (~۹۰۰) از Minecraft Wiki
2. تولید data stubs برای بلاک‌های mcicons که داده‌ نداریم
3. آیتم‌ها: دانلود رندرهای سه‌بعدی از mcicons (۱۰۷۴ آیتم)
4. emoji → PNG با gui/interfaces
