# MineBed Farsi

> مرجع فارسی دانلود افزونه، مپ، سید و آموزش ماینکرفت بدراک

## 📁 ساختار

```
minebed-github/
├── website/              ← وب‌سایت Astro (deploy روی GitHub Pages)
│   ├── src/
│   │   ├── components/   ← Cube3D، MusicPlayer، ParticleEffects، ...
│   │   ├── pages/         ← mods، seeds، versions، blog، wiki، ...
│   │   ├── data/          ← mods.json، seeds.json، versions.json
│   │   └── content/       ← blog/wiki/tutorials MDX
│   ├── public/
│   │   ├── textures/blocks/  ← تکسچرهای PNG Minecraft
│   │   └── fonts/            ← Rooyin
│   └── astro.config.mjs
│
├── admin/                ← اپ دسکتاپ (لوکال، فقط خودت)
│   ├── minebed-desktop.py
│   ├── backend/           ← FastAPI + crawler + AI + GitHub push
│   ├── ui/                ← HTML + CSS + JS
│   └── .env               ← کلیدها (gitignored!)
│
├── .github/workflows/
│   ├── deploy.yml         ← auto-build + deploy سایت
│   └── pipeline.yml       ← cron روزانه fetch ماد جدید
│
├── .env.example          ← template (safe to commit)
├── .gitignore            ← blocks .env و secrets
└── README.md
```

## 🚀 راه‌اندازی

### ۱. وب‌سایت (روی GitHub Pages)
1. این repo رو push کن به GitHub
2. Settings → Pages → Source: GitHub Actions
3. Workflow `deploy.yml` خودکار سایت رو build + deploy می‌کنه
4. سایت روی `https://iran-minecraft-wiki.github.io/website/` در دسترسه

### ۲. اپ ادمین (لوکال)
1. پوشه‌ی `admin/` رو دانلود کن
2. فایل `.env` رو با کلیدهای واقعی پر کن (از `.env.example` کپی کن)
3. `start.bat` رو اجرا کن
4. پنجره باز می‌شه → می‌تونی ماد اضافه کنی

### ۳. GitHub Secrets (برای اتوماسیون)
در Settings → Secrets:
- `AGNES_API_KEY` — کلید هوش مصنوعی
- `HF_TOKEN` — توکن HuggingFace

## 🔒 امنیت
- `.env` و `config.js` در `.gitignore` هستن — هرگز کامیت نشن
- کلیدها فقط لوکال یا در GitHub Secrets
