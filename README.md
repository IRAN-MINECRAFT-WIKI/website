# 🎮 MineBed — ویکی فارسی ماینکرفت

وب‌سایت فارسی ماینکرفت با ویکی بلاک‌ها/ماب‌ها/آیتم‌ها، ساخت سید، کرافت، سرعت‌رانی و دانلود ماد.

**🔗 سایت زنده:** https://iran-minecraft-wiki.github.io/website/

---

## 📊 وضعیت فعلی

| بخش | واقعی MC 1.21 | فعلی | درصد |
|---|---|---|---|
| بلاک‌ها | ~۹۰۰ | ۱۱۳ | ۱۲٪ |
| ماب‌ها | ~۸۳ | ۵۲ | ۶۳٪ |
| آیتم‌ها | ~۱۲۰۰ | ~۴۱۰ | ۳۴٪ |
| ساختارها | ~۵۰ | ۸ | ۱۶٪ |

---

## ✅ کارهای انجام‌شده

- **آمار سایت واقعی:** KV-backed Cloudflare Worker با ضد تقلب (هر UUID = ۱ در روز)
- **نمودارها:** Chart.js با تم پیکسلی ماینکرفتی (۳۰ روز + ۲۴ ساعت)
- **تاریخ شمسی:** jalaali-js + منطقه‌ی زمانی تهران
- **نقشه‌ی ۲D سید:** Canvas + grid + compass (فاز ۸۴)
- **رندرهای سه‌بعدی ماب‌ها:** ۵۲/۵۲ از mcicons (ccvaults.com)
- **رندرهای سه‌بعدی بلاک‌ها:** ۸۹/۱۱۳ از mcicons
- **اپارات embed:** iframe کانال + ویدیوهای جداگانه
- **Drag & Drop کرافت:** HTML5 Drag API + touch support
- **FAQ:** ۲۱ سوال در ۷ دسته + JSON-LD
- **Worker v3:** KV-optimized (writes + lists زیر سقف free-tier)

---

## 📎 لینک‌های مهم

- [🔍 MCIcons-AUDIT.md](./MCIcons-AUDIT.md) — تحلیل کامل پکیج mcicons (کدوم رسمی، کدوم ماد)
- [📋 CHECKLIST.md](./website/CHECKLIST.md) — وضعیت ۲۰۰ فاز
- [📊 PREVIEW_REPORT.md](./PREVIEW_REPORT.md) — گزارش پروژه + پیشرفت
- [📋 PHASES_STATUS.md](./PHASES_STATUS.md) — جدول کامل فازها
- [⚙️ Worker source](./worker/src/index.js) — کد Cloudflare Worker v3
- [📖 Worker README](./worker/README.md) — راهنمای دیپلوی

---

## 🚀 نصب و اجرا

```bash
# کلون کن
git clone https://github.com/IRAN-MINECRAFT-WIKI/website.git
cd website/website

# نصب deps
bun install

# اجرای dev
bun run dev

# build
bun run build
```

### کلاینت آمار (پریویو پنل)

```bash
# Next.js preview (نقشه‌ی راه + آمار)
cd /home/z/my-project
bun run dev
# → http://localhost:3000
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

---

## ⚠️ نکات

1. **هرگز از `modded_weapons` در mcicons استفاده نکن** — همه‌شون ماد هستن. برای سلاح از `items` استفاده کن.
2. **Worker v3 رو دیپلوی کن** — کدش توی `worker/src/index.js`. KV limit محافظت‌شده (writes/lists زیر سقف).
3. **آمار واقعی بعد از midnight UTC کار می‌کنه** — KV daily limit ریست می‌شه.

---

## 📜 License

- کد: GPL-2.0 (مطابق mcicons)
- محتوای ماینکرفت: Mojang Studios
- ترجمه‌ی فارسی: MineBed Team
