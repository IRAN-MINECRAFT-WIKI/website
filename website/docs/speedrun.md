# بخش رکوردهای سرعت‌رانی (Speedrun)

## معماری کلی

داده‌ها هر شب ساعت ۳:۰۰ بامداد ایران (UTC 23:30) از Speedrun.com API fetch می‌شن و در `src/data/speedrun/` ذخیره می‌شن.

## Game IDها (تأیید‌شده)

| بازی | Game ID | abbreviation |
|---|---|---|
| Minecraft: Java Edition | `j1npme6p` | `mc` |
| Minecraft: Bedrock Edition | `yd4ovvg1` | `mcbe` |

## دسته‌بندی‌ها

### Java (۷ دسته‌ی اصلی + ۶ misc):
- Any% Glitchless
- Any%
- All Advancements
- + ۴ دسته‌ی legacy (Set Seed / Random Seed variants)

### Bedrock (۱۱ دسته‌ی اصلی + ۳ misc):
- Any% Glitchless
- Any%
- + ۹ دسته‌ی دیگر

## ساختار داده‌ی هر رکورد

```json
{
  "id": "run_id",
  "weblink": "https://www.speedrun.com/mc/runs/...",
  "category": "Any% Glitchless",
  "platform": "Java",
  "time_primary": 1037.199,
  "time_display": "17m 17s 199ms",
  "date": "2026-09-24",
  "players": ["PlayerName"],
  "seed": "-6405782700478242821" or null,
  "verified": true,
  "version": "1.16.1",
  "seed_type": "Random Seed"
}
```

**⚠️ `video_url` ذخیره نمی‌شه** — ما ویدیوها رو میزبانی نمی‌کنیم.

## فایل‌ها

```
website/src/data/speedrun/
├── config.json          (game IDs, category IDs, variable IDs)
├── summary.json         (metadata: fetched_at, counts)
├── java/
│   ├── any-glitchless.json   (100 runs)
│   ├── any.json              (100 runs)
│   ├── all-advancements.json (100 runs)
│   └── ...
└── bedrock/
    ├── any-glitchless.json
    ├── any.json
    └── ...
```

## GitHub Action

`.github/workflows/speedrun.yml`:
- **cron:** `30 23 * * *` UTC = 03:00 Iran
- **workflow_dispatch** for manual runs
- **`[skip ci]`** در commit message برای جلوگیری از deploy loop
- **secrets.GH_PAT** برای write access

## Rate Limiting

- ۷۰۰ms sleep بین درخواست‌ها (≈۸۵ req/min — زیر limit ۱۰۰/min)
- ۳ retry با exponential backoff
- اگه API down باشه، داده‌های قبلی حفظ می‌شن (atomic writes با `os.replace`)

## نکات

- فقط TOP 100 هر دسته‌بندی fetch می‌شه (نه همه ۴۱۰۰۰ رکورد)
- سید از comment/description با regex استخراج می‌شه
- ۲۰.۸٪ رکوردها سید دارن (Java: ۶۵-۷۶٪، Bedrock: ۱-۹٪)

## مشکلات شناخته‌شده

- بعضی رکوردها سید ندارن (تو comment ذکر نشده)
- بعضی دسته‌های legacy تو API جدید variables شدن (۰ run برمی‌گردونن)
