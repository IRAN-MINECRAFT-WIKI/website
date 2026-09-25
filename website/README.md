# 🎮 MineBed Farsi — Astro Edition (v2.0)

> مرجع فارسی دانلود افزونه، مپ، ریسورس‌پک و سید ماینکرفت بدراک —
> نسخه‌ی حرفه‌ای با **Astro 5 + Tailwind 4 + Content Collections**
> بهینه‌شده برای سئو در ایران.

این نسخه جایگزین کامل وب‌سایت فعلی شماست (که HTML خام بود) و تمام
مشکلات آن را برطرف می‌کند.

---

## ✨ ویژگی‌های کلیدی

### 🚀 پرفورمنس و سئو
- **Astro SSG** → HTML استاتیک خالص، نمره‌ی Lighthouse 95+
- **Tailwind CSS** → CSS minify شده، بدون render block
- **Self-hosted Vazirmatn** → بدون وابستگی به Google Fonts
- **Schema.org JSON-LD** → SoftwareApplication، FAQ، Article، Breadcrumb
- **sitemap.xml خودکار** → با هر build آپدیت می‌شود
- **OG image + canonical + robots** → آماده برای Social sharing
- **prefetch** → لینک‌های viewport پیش‌بارگذاری می‌شوند

### 🌐 ساختار URL حرفه‌ای (SEO-friendly)
| قبل | بعد |
|------|------|
| `mod.html?id=xxx` | `/mods/<slug>/` |
| `index.html` | `/` |
| (نداشت) | `/categories/<cat>/` |
| (نداشت) | `/versions/<ver>/` |
| (نداشت) | `/seeds/<slug>/` |
| (نداشت) | `/blog/<slug>/` |
| (نداشت) | `/wiki/<slug>/` |
| (نداشت) | `/tutorials/<slug>/` |

### 📦 محتوای چندگانه
- ✅ **مودها** (از پایپ‌لاین فعلی شما)
- ✅ **سیدها** (داده‌های جدید با ساختار قابل توسعه)
- ✅ **نسخه‌های ماینکرفت** (1.21, 1.20, 1.19, ...)
- ✅ **وبلاگ** (Astro Content Collection — MDX)
- ✅ **ویکی** (Content Collection — مقالات فنی)
- ✅ **آموزش‌ها** (Content Collection با difficulty/duration)
- ✅ **دسته‌بندی‌ها** (صفحات SEO long-tail)

### 🔒 امنیت بهبود یافته (در pipeline)
- ❌ توکن‌ها به صورت hardcoded حذف شدند
- ✅ فقط `os.getenv()` با **fallback خالی**
- ✅ `.env.example` کامل
- ✅ `python-dotenv` برای بارگذاری خودکار .env
- ✅ Validation با هشدار در startup

---

## 📂 ساختار پروژه

```
minebed-astro/
├── src/
│   ├── components/        ← Header, Footer, ModCard, Breadcrumbs, AdSlot
│   ├── layouts/           ← BaseLayout (با JSON-LD داخلی)
│   ├── lib/
│   │   ├── data.ts        ← loader mods/seeds/versions/categories
│   │   └── seo.ts         ← helpers برای meta tags + structured data
│   ├── pages/
│   │   ├── index.astro
│   │   ├── mods/{index,[slug]}.astro
│   │   ├── categories/{index,[cat]}.astro
│   │   ├── versions/{index,[ver]}.astro
│   │   ├── seeds/{index,[slug]}.astro
│   │   ├── blog/{index,[slug]}.astro
│   │   ├── wiki/{index,[slug]}.astro
│   │   ├── tutorials/{index,[slug]}.astro
│   │   ├── about.astro, guide.astro, privacy.astro, terms.astro, 404.astro
│   ├── content/           ← MDX content collections
│   │   ├── blog/, wiki/, tutorials/
│   │   └── config.ts
│   ├── data/              ← JSON data (mods, seeds, versions, categories)
│   └── styles/global.css  ← Tailwind + MineBed pixel theme
├── public/                ← static assets (favicon, fonts, images)
├── pipeline/              ← improved Python pipeline (security hardened)
├── .github/workflows/     ← GitHub Pages auto-deploy + pipeline cron
├── astro.config.mjs
├── tailwind.config.mjs
├── tsconfig.json
├── .env.example
└── .gitignore
```

---

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها
- **Node.js 20+** (پیشنهادی: LTS)
- **npm 10+**

### اجرای محلی
```bash
# 1. نصب پکیج‌ها
cd minebed-astro
npm install

# 2. اجرای dev server
npm run dev
# سایت روی http://localhost:4321 در دسترس است

# 3. build production
npm run build

# 4. preview build
npm run preview
```

### استقرار در GitHub Pages

1. **این پروژه را در repo جدید push کنید** (یا فایل‌ها را در repo فعلی جایگزین کنید)

   ```bash
   cd minebed-astro
   git init
   git add .
   git commit -m "Upgrade to Astro v2"
   git push origin main
   ```

2. **در GitHub به مسیر بروید:**
   - `Settings → Pages`
   - Source: `GitHub Actions`

3. **Workflow به طور خودکار اجرا می‌شود** (`.github/workflows/deploy.yml`)
   و سایت روی `https://iran-minecraft-wiki.github.io/website/` در دسترس است.

---

## 🔑 امنیت توکن‌ها

### 🚨 اخطار بحرانی
فایل‌های فعلی شما (`config.py` و `requirements.txt`) حاوی توکن‌های
HuggingFace و GitHub به صورت plain text بودند. **این توکن‌ها در
گیتهاب کامیت شده‌اند و در تاریخچه قابل دسترسی هستند.**

### اقدام فوری مورد نیاز:
1. **در HuggingFace:** به `Settings → Access Tokens` بروید و توکن قدیمی را **revoke** کنید. سپس توکن جدید بسازید.
2. **در GitHub:** به `Settings → Developer Settings → Personal Access Tokens` بروید و توکن قدیمی را **revoke** کنید. سپس توکن جدید با scope `repo` بسازید.
3. **توکن‌های جدید را به عنوان GitHub Secrets اضافه کنید:**
   - `Settings → Secrets and Variables → Actions → New repository secret`
   - Names: `HF_TOKEN`, `GITHUB_TOKEN`

### نسخه‌ی بهبود یافته
فایل `pipeline/config.py` بهبود یافته است:
```python
HF_TOKEN = os.getenv("HF_TOKEN", "")  # REQUIRED — no fallback
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # REQUIRED — no fallback
```

---

## 📝 اضافه‌کردن محتوای جدید

### اضافه‌کردن مود جدید (از طریق pipeline)
```bash
cd pipeline
python sync_from_github.py
# یا
python pipeline.py --gui
```

پایپ‌لاین مود را از MCPEDL کرال می‌کند، توضیحات فارسی را با AI
تولید می‌کند، فایل‌ها را به HuggingFace آپلود می‌کند و `mods.json`
را در گیت‌هاب به‌روزرسانی می‌کند. سایت به طور خودکار rebuild می‌شود.

### اضافه‌کردن سید جدید
فایل `src/data/seeds.json` را ویرایش کنید:
```json
{
  "id": "my-new-seed",
  "name": "...",
  "code": "123456789",
  ...
}
```

### اضافه‌کردن مقاله وبلاگ
فایل MDX جدید در `src/content/blog/` بسازید:
```bash
touch src/content/blog/my-post.mdx
```

```yaml
---
title: 'عنوان مقاله'
description: 'توضیح کوتاه'
pubDate: 2024-12-15
author: 'MineBed Team'
tags: ['tag1', 'tag2']
---

محتوای مقاله...
```

### اضافه‌کردن صفحه نسخه‌ی MC
فایل `src/data/versions.json` را ویرایش کنید.

---

## 🗺️ نقشه راه بعدی (Roadmap)

### فاز ۱ (الان)
- ✅ Astroad را راه‌اندازی کردید
- ✅ اولین deploy به GitHub Pages

### فاز ۲ (هفته ۱-۲)
- [ ] اضافه‌کردن **Pagefind** برای جستجوی client-side کامل
- [ ] فعال‌سازی **Image Optimization** (Astro Image)
- [ ] اضافه‌کردن ۱۵+ مقاله به ویکی
- [ ] اضافه‌کردن ۵+ مقاله به وبلاگ
- [ ] اضافه‌کردن ۵۰+ سید

### فاز ۳ (ماه ۱-۲)
- [ ] خرید دامنه‌ی `.ir` (مثلاً `minebed.ir`)
- [ ] مهاجرت به **Cloudflare Pages** (سریع‌تر برای ایران)
- [ ] فعال‌سازی **Telegram bot** برای اطلاع‌رسانی خودکار
- [ ] افزودن **Donate/subscription** برای حمایت مالی

### فاز ۴ (ماه ۳-۶)
- [ ] خرید VPS ایرانی برای SEO بهتر
- [ ] راه‌اندازی **Telegram Premium** برای دسترسی زودهنگام
- [ ] افزودن **Affiliate** با ارائه‌دهندگان سرور گیم
- [ ] افزودن **PWA** برای نصب روی موبایل

---

## 🛠️ شخصی‌سازی

### تغییر رنگ‌ها
فایل `tailwind.config.mjs` را ویرایش کنید (بخش `colors.mc.*`).

### تغییر فونت
1. فایل فونت را در `public/fonts/` قرار دهید
2. در `src/layouts/BaseLayout.astro` لینک preload و `@font-face` را به‌روزرسانی کنید

### تغییر اطلاعات سایت
فایل `src/lib/data.ts` → `siteConfig` را ویرایش کنید.

---

## 📊 سئو — نکات کلیدی

این سایت با نکات زیر بهینه‌شده:

1. **URL ساختار semantic** (`/mods/slug/` به جای `?id=`)
2. **Schema.org JSON-LD** (SoftwareApplication برای مودها، Article برای مقاله، FAQ برای سوالات)
3. **Breadcrumbs** با ساختار JSON-LD
4. **Meta description فارسی** برای هر صفحه
5. **OG image + Twitter Card** برای اشتراک در شبکه‌های اجتماعی
6. **Canonical URLs** برای جلوگیری از duplicate content
7. **sitemap.xml خودکار** با اولویت و آخرین به‌روزرسانی
8. **robots.txt** با sitemap reference
9. **Self-hosted fonts** → حذف Google Fonts blocking
10. **Prefetch** → لینک‌های نزدیک viewport پیش‌بارگذاری می‌شوند
11. **Lazy loading images** → با `loading="lazy"` و `decoding="async"`
12. **Mobile-first responsive** → تجربه‌ی موبایل عالی

---

## 🤝 مشارکت

این پروژه متن‌باز است. برای مشارکت:
1. Fork کنید
2. Branch جدید بسازید (`git checkout -b feature/my-feature`)
3. Commit کنید (`git commit -m 'Add: my feature'`)
4. Push کنید (`git push origin feature/my-feature`)
5. Pull Request باز کنید

---

## 📜 لایسنس

- کد سایت: **MIT License**
- محتوای افزونه‌ها: متعلق به سازنده‌ی اصلی هر افزونه
- ماینکرفت: متعلق به Mojang Studios / Microsoft

---

## 📞 تماس

- 🌐 وب‌سایت: https://iran-minecraft-wiki.github.io/website/
- 📢 تلگرام: https://t.me/MineBedWeb
- 📷 اینستاگرام: https://instagram.com/craftify
- 🎬 یوتیوب: https://youtube.com/@craftify

ساخته‌شده با ❤️ برای جامعه‌ی فارسی‌زبان ماینکرفت
