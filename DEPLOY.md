# 🚀 راهنمای نصب و آنلاین کردن

## ۱. نصب وب‌سایت روی GitHub Pages

```bash
# ۱. repo جدید بساز یا از قبل داریم
git init
git add .
git commit -m "MineBed — website + admin"

# ۲. به GitHub پوش کن
git remote add origin https://github.com/IRAN-MINECRAFT-WIKI/website.git
git push -u origin main
```

### تنظیم GitHub Pages:
1. به Settings → Pages برو
2. Source: **GitHub Actions**
3. Workflow `deploy.yml` خودکار سایت رو build + deploy می‌کنه
4. ۲-۳ دقیقه بعد سایت روی این URL در دسترسه:
   `https://iran-minecraft-wiki.github.io/website/`

## ۲. نصب GitHub Secrets

در Settings → Secrets and variables → Actions:
- `AGNES_API_KEY` → کلید AI
- `HF_TOKEN` → توکن HuggingFace
- `GITHUB_TOKEN` → خودکار (نیازی به اضافه‌کردن نیست)

## ۳. اپ ادمین (لوکال)

1. پوشه‌ی `admin/` رو دانلود کن
2. فایل `.env` رو با کلیدهای واقعی پر کن
3. `start.bat` رو اجرا کن

## ۴. اتوماسیون روزانه

Workflow `pipeline.yml` هر روز ساعت ۰۵:۳۰ IRST:
- ۵ ماد جدید از MCPEDL fetch می‌کنه
- با AI توضیحات فارسی تولید می‌کنه
- در `mods.json` ذخیره می‌کنه
- به GitHub پوش می‌کنه
- سایت خودکار rebuild می‌شه

## 🔒 امنیت
- `.env` در `.gitignore` — هرگز کامیت نشه
- کلیدها فقط در GitHub Secrets یا لوکال
- هیچ کلیدی توی کد نیست
