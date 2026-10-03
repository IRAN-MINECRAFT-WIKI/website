# MineBed Stats Worker (KV-based)

این Worker آمار بازدید سایت را با **Cloudflare KV** ذخیره می‌کند (نه D1).
سقف رایگان KV: ۱۰۰٬۰۰۰ خواندن + ۱٬۰۰۰ نوشتن در روز — برای سایت شما ۳۴ برابر بیشتر از نیاز.

## چرا KV نه D1؟

D1 (SQLite ابری Cloudflare) سقف رایگان خواندن ردیف روزانه‌اش پر شد
(`D1_ERROR: ... daily row read limit`). KV این محدودیت را ندارد.

## نحوه‌ی کار

```
[مرورگر] --POST /api/heartbeat--> [Worker] --writes--> [KV]
            { user_uuid, page }
                                   keys:
                                   hb:{uuid}    = {ts, page}   (TTL 5min)
                                   d:{date}:{uuid} = 1          (TTL 31d)
                                   u:{uuid}    = 1              (بدون TTL)

[مرورگر] --GET /api/stats--> [Worker] --reads--> [KV]
                             online  = count hb:* where ts < 60s
                             today   = count d:{today}:*
                             total   = count u:*
```

**ضد تقلب:** هر `user_uuid` فقط ۱ بار در روز شمرده می‌شود (کلید `d:{date}:{uuid}` idempotent است). رفرش‌کردن آمار را بالا نمی‌برد.

## نصب (۵ دقیقه)

### ۱. نصب Wrangler
```bash
npm install -g wrangler
wrangler login  # با حساب Cloudflare خود لاگین کنید
```

### ۲. ساخت KV namespace
```bash
cd worker
wrangler kv:namespace create MINEBED_HEARTBEAT
# خروجی: { "id": "abc123..." }
wrangler kv:namespace create MINEBED_HEARTBEAT --preview
# خروجی: { "id": "def456..." }
```

### ۳. تنظیم wrangler.toml
دو ID بالا را در `wrangler.toml` جای‌گزین کنید:
```toml
[[kv_namespaces]]
binding = "MINEBED_HEARTBEAT"
id = "abc123..."        # ← اینجا
preview_id = "def456..." # ← و اینجا
```

همچنین `account_id` خود را از داشبورد Cloudflare بردار و جای‌گزین کنید.

### ۴. دیپلوی
```bash
wrangler deploy
# خروجی: https://minebed-api.www-habib6269.workers.dev
```

### ۵. تست
```bash
# ثبت heartbeat
curl -X POST https://minebed-api.www-habib6269.workers.dev/api/heartbeat \
  -H "Content-Type: application/json" \
  -d '{"user_uuid":"test-uuid-abc-1234567890","page":"/"}'

# خواندن آمار
curl https://minebed-api.www-habib6269.workers.dev/api/stats
# {"online":1,"today":1,"total":1,...}
```

## مهاجرت از Worker قبلی

Worker قبلی از D1 استفاده می‌کرد. برای مهاجرت:
1. این Worker جدید را deploy کنید (مراحل بالا)
2. کد کلاینت (`website/src/lib/analytics.js`) تغییری نیاز ندارد — همان `/api/stats` و `/api/heartbeat` را صدا می‌زند
3. آدرس `API_BASE` در `analytics.js` اگر عوض شد، آپدیت کنید

## ساختار فایل‌ها

```
worker/
├── src/
│   └── index.js      # کد Worker
├── wrangler.toml     # تنظیمات (KV namespace IDs)
├── package.json
└── README.md         # این فایل
```

## سقف رایگان (Free Tier)

| منبع | سقف روزانه | مصرف تخمینی سایت شما |
|---|---|---|
| KV reads | ۱۰۰٬۰۰۰ | ~۵۰۰ (هر بازدید) |
| KV writes | ۱٬۰۰۰ | ~۳۰۰ (هر بازدید ۳ نوشتن) |
| KV storage | ۱ GB | < ۱ MB |
| Worker requests | ۱۰۰٬۰۰۰ | ~۱٬۰۰۰ |

**نتیجه:** برای سایت شما کاملاً رایگان و کافی.
