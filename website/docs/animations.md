# انیمیشن باز/بسته شدن کنترول سنتر

## معماری

انیمیشن با **Web Animations API** پیاده‌سازی شده (نه CSS transitions) برای کنترل دقیق روی توالی.

## توالی باز شدن

| مرحله | زمان | عنصر | حرکت |
|---|---|---|---|
| ۱ | ۰-۱۵۰ms | دکمه trigger | scale 1.0 → 1.15 → 1.08 + glow سبز |
| ۲ | ۱۵۰-۵۰۰ms | header | translateY(-100%) → translateY(0) + opacity 0→1 با spring easing |
| ۳ | ۵۰۰-۱۵۰۰ms | هر کارت | از position دکمه trigger → position نهایی، یکی‌یکی با delay 120ms |
| ۴ | هر کارت arrival | sparkle | ذره‌ی نور سبز ۸px → 20px → محو |

## توالی بسته شدن

معکوس باز شدن — کارت‌ها به ترتیب برعکس به دکمه trigger برمی‌گردن.

## easing

- ورود: `cubic-bezier(0.34, 1.56, 0.64, 1)` (spring-like)
- خروج: `cubic-bezier(0.4, 0, 0.2, 1)` (smooth ease-in)

## دسترس‌پذیری

`prefers-reduced-motion: reduce` → انیمیشن غیرفعال، overlay فوری نمایش داده می‌شه.

## فایل

`website/src/components/QuickAccess.astro` — بخش `<script is:inline>`
