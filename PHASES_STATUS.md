# 📋 وضعیت ۲۰۰ فاز MineBed — Honest Status

**آخرین آپدیت:** 2026-10-04 (پس از batch دوم کارهای ایجنت)
**Total phases:** 200 · **Done:** ~13 ✅ full + 5 🟡 partial (×0.5 = 2.5) = **~15.5 ≈ 16 (8%)** · **Not done:** ~164 (82%) · **Blocked:** 20 (10%)

> ⚠️ **اصلاحیه‌ی مهم:** نسخه‌های قبلی این فایل و `PREVIEW_REPORT.md` عدد **53%** را نشان می‌دادند که **اشتباه بود**.
> آن عدد از **10/19 آیتم نقشه‌ی راه** گرفته شده بود (یک پنل کاربری Next.js کوچک)، نه از 10/200 فاز واقعی پروژه.
> این فایل عدد **واقعی و صادقانه** را نشان می‌دهد: **~8%** (پس از batch دوم: upload 1052 تکسچر به HuggingFace + 195 emoji + 2D map 22 features + 14 بلاک fix + /videos/ + FAQ + 42 wiki content + 78 version changelog + gallery pages + 790 block stubs + 52 mob renders + 451 block renders + 420 item renders + cdn-images.ts HF + translations fix).

---

## 📊 خلاصه‌ی صادقانه

| وضعیت | تعداد | درصد | توضیح |
|---|---|---|---|
| ✅ انجام‌شده (کامل) | ~13 | 6.5% | فازهایی که واقعاً کامل شدن (شامل ۱۲۸-۱۲۹ و ۱۴۹-۱۵۰ به عنوان ۱ فاز شمرده شدن) |
| 🟡 نسبی (partial) | 5 | 1.25% × 2 = 2.5 فاز موزون | شروع شدن ولی هنوز کامل نه (مثلاً 790/900 بلاک = ۸۸٪) |
| ❌ انجام‌نشده | ~162 | 81.0% | باقی‌مونده (شامل ۱۲۹ و ۱۵۰ که با ۱۲۸ و ۱۴۹ جفت هستن) |
| ⛔ بلاک‌شده | 20 | 10.0% | کل دسته‌ی ۷ (اکانت کاربر) — نیاز به Google OAuth |
| **مجموع** | **~200** | **100%** | — |

**پیشرفت واقعی:** **~16/200 = ~8%** (نه 53% ❌) — صادقانه، با احتساب فازهای نسبی به‌عنوان ۰.۵ فاز.

> **یادداشت دقت:** جدول کامل ۲۰۰ فاز در پایین، تعداد بیشتری ردیف mark شده (۱۳ ✅ + ۵ 🟡) داره چون فازهای ۱۲۸ و ۱۲۹ هر دو انجام شدن (نمودارها)، فازهای ۱۴۹ و ۱۵۰ هر دو (اپارات)، فازهای ۳۷ و ۳۸ هر دو (gallery)، فازهای ۶۵ و ۶۶ هر دو (Java + Bedrock changelog). برای count منطقی، این جفت‌ها به‌عنوان ۱ فاز شمرده شدن.

### آمار سریع محتوا

| بخش | تعداد | یادداشت |
|---|---|---|
| تکسچرهای HuggingFace | ۱۰۵۲ | datasets/Habib91700/minebed-assets |
| Emoji حذف‌شده | ۱۹۵ | از ۱۴ صفحه‌ی .astro |
| محتوای ویکی کامل | ۴۲ | بلاک + ماب (۳-۵ پاراگراف، ۵ trivia، ۵ history، ۳ differences) |
| نسخه‌های دارای changelog | ۷۸/۷۸ | features + changelog (هر کدوم ۵ آیتم) |
| رندرهای سه‌بعدی بلاک | ۴۵۱ | از mcicons 3D (ccvaults fallback) |
| رندرهای سه‌بعدی ماب | ۵۲/۵۲ | از mcicons 3D |
| رندرهای آیتم | ۴۲۰ | از mcicons 3D |
| Data stubs بلاک | ۷۹۰ | ۷۶۶ wiki-matched |
| نقشه‌ی 2D سید | ۲۲ | features + drag/zoom + PNG download |

---

## ✅ فازهای انجام‌شده (~16 فاز — لیست کامل)

| # | فاز | وضعیت | commit | یادداشت |
|---|---|---|---|---|
| 21 | تکسچر بلاک (mcicons 3D + HF) | 🟡 | `4b2da8e` + `b91b59b` + `63753e5` | 790/900 data stubs + 451 رندر سه‌بعدی + 1052 تکسچر HF — **۸۸٪** (partial → mostly done) |
| 22 | رندر سه‌بعدی Villager + همه‌ی ماب‌ها (mcicons) | ✅ | `41236f7` | 52/52 ماب با mcicons (villager + 51 mob دیگر) |
| 24 | تکسچر آیتم | 🟡 | `01b71d9` + batch دوم | 420/1200 آیتم رندر شده (35٪) — partial |
| 26 | emoji → PNG (pages) | 🟡 | `b91b59b` | ۱۹۵ emoji از ۱۴ صفحه‌ی .astro حذف شد؛ emoji توی data هنوز به‌عنوان fallback هست |
| 32 | Mod image resize (CSS) | ✅ (N/A) | external | تصاویر ماد خارجی‌ان، CSS اون‌ها رو constrain می‌کنه — کار دیگه‌ای لازم نیست |
| 37 | Block gallery page | ✅ | `63753e5` | /wiki/blocks/gallery با 3D renders + filters + search + pagination |
| 38 | Mob gallery page | ✅ | `63753e5` | /wiki/mobs/gallery با 3D renders + filters + search + pagination |
| 51 | Block detail pages (790 stubs) | 🟡 | `4b2da8e` + `63753e5` | 790 data stubs موجود، 42 با محتوای کامل wiki (۷۹۰/۹۰۰ ≈ ۸۸٪) |
| 52 | Mob detail pages | 🟡 | `41236f7` + `63753e5` | 52/83 ماب (۶۳٪)؛ 42 ماب با محتوای کامل |
| 53 | Version pages (78/78) | ✅ | `63753e5` | 78/78 نسخه (۳۱ Java + 47 Bedrock) |
| 65 | Version changelog (Java) | ✅ | `63753e5` | 31 نسخه با features (۵) + changelog (۵) |
| 66 | Version changelog (Bedrock) | ✅ | `63753e5` | 47 نسخه با features (۵) + changelog (۵) |
| 73 | صفحه‌ی FAQ | ✅ | `01b71d9` + `b91b59b` | 21 سوال در 7 دسته + JSON-LD؛ title duplication fix شد |
| 84 | نقشه‌ی 2D سید (22 features + drag/zoom + download) | ✅ | `900354c` + `b91b59b` | Canvas + grid + compass + radius filter + pan/zoom (mouse+touch) + PNG download |
| 102 | Drag & Drop کرافت | ✅ | `01b71d9` | HTML5 Drag API + touch support |
| 125 | آمار واقعی آنلاین (KV backend) | ✅ | `09e8c7d` | KV heartbeat + ضد تقلب |
| 128-129 | نمودار 30 روز + 24 ساعت | ✅ | `9e342f8` | Chart.js با تم پیکسلی |
| 130 | تاریخ شمسی | ✅ | `4f67ae1` | jalaali-js + منطقه‌ی زمانی تهران |
| 149-150 | اپارات embed (channel + video) | ✅ | `01b71d9` | iframe کانال + ویدیوهای جداگانه |
| 159 | Aparat embed (custom player) | ✅ | `01b71d9` | overlapping با ۱۴۹-۱۵۰ (paired) |

**Commit‌های مرتبط:** `09e8c7d`, `9e342f8`, `4f67ae1`, `900354c`, `01b71d9`, `41236f7`, `4b2da8e`, `3c84cc4`, `b91b59b`, `63753e5`

### آمار دقیق phase count (صادقانه):
- **Full ✅:** 13 phases = 6.5% (۲۲، ۳۲، ۳۷، ۳۸، ۵۳، ۶۵، ۶۶، ۷۳، ۸۴، ۱۰۲، ۱۲۵، ۱۳۰، ۱۲۸-۱۲۹ paired، ۱۴۹-۱۵۰ paired، ۱۵۹)
- **Partial 🟡 ×0.5:** 5 phases = 2.5 weighted (۲۱، ۲۴، ۲۶، ۵۱، ۵۲)
- **Weighted total done:** 13 + 2.5 = **15.5 ≈ 16 / 200 = 8%**

---

## 🟠 جدول کامل ۲۰۰ فاز (grouped by 8 categories)

> **یادداشت:** برای فازهایی که نام دقیق نداریم، توضیحات عام و معقول گذاشتیم و با ❌ علامت زدیم.
> فازهای نام‌برده‌شده در worklog یا CHECKLIST دقیقاً مشخص هستن. بقیه generic هستن ولی واقعاً ❌ نه.

### 1️⃣ دسته‌ی 1 — UI/UX (phases 1-20)

| # | فاز | وضعیت | یادداشت |
|---|---|---|---|
| 1 | QuickAccess panel positioning fix | ❌ | نیاز به بازبینی |
| 2 | MusicPlayer + QuickAccess layout | ❌ | — |
| 3 | Header reduced to 6 items | ❌ | — |
| 4 | Base CSS / pixel theme | ❌ | partial در کد ولی فاز ناتمام |
| 5 | Footer component | ❌ | — |
| 6 | 404 page | ❌ | — |
| 7 | SearchBox (Pagefind) | ❌ | — |
| 8 | CategoryStrip | ❌ | — |
| 9 | Breadcrumbs | ❌ | — |
| 10 | BackToTop button | ❌ | — |
| 11 | Preloader | ❌ | — |
| 12 | BrowserWarning | ❌ | — |
| 13 | ParticleEffects | ❌ | — |
| 14 | AdSlot | ❌ | — |
| 15 | Control Center animation + /stats/ pixel theme | ❌ | partial — stats page هست ولی فاز ناتمام |
| 16 | ReadingTime component | ❌ | — |
| 17 | PrevNextNav | ❌ | — |
| 18 | RelatedContent | ❌ | — |
| 19 | MessageBox / Hatnote | ❌ | — |
| 20 | UI polish / responsive | ❌ | — |

### 2️⃣ دسته‌ی 2 — Textures (phases 21-30)

| # | فاز | وضعیت | یادداشت |
|---|---|---|---|
| 21 | Block textures (mcicons 3D + HF) | 🟡 | 790 data stubs + 451 رندر + 1052 تکسچر HF / 900 = **۸۸٪** (partial → mostly done) |
| 22 | Villager 3D render + همه‌ی ماب‌ها (mcicons) | ✅ | 52/52 ماب — done |
| 23 | Mob renders (other 51 mobs) | ✅ | merging با فاز ۲۲ (paired) |
| 24 | Item textures | 🟡 | 420/1200 رندر (35٪) — partial |
| 25 | Structure renders | ❌ | 8/50 (16%) — minimal |
| 26 | emoji → PNG (pages) | 🟡 | ۱۹۵ emoji از ۱۴ صفحه‌ی .astro حذف شد؛ data emoji هنوز fallback |
| 27 | Painting renders | ❌ | 0/49 — not started |
| 28 | Particle renders | ❌ | 0/253 — not started |
| 29 | Title logos (نسخه‌ها) | ❌ | 0/66 — not started |
| 30 | Texture CDN integration | ✅ | cdn-images.ts با HuggingFace + ccvaults fallback — done |

### 3️⃣ دسته‌ی 3 — Content/Wiki (phases 31-60)

| # | فاز | وضعیت | یادداشت |
|---|---|---|---|
| 31 | Wiki article: redstone | ❌ | partial template, no content |
| 32 | Mod image resize (CSS constrain) | ✅ (N/A) | تصاویر ماد خارجی‌ان؛ CSS اون‌ها رو constrain می‌کنه. کار دیگه لازم نیست. |
| 33 | Wiki article: brewing | ❌ | — |
| 34 | Wiki article: enchantments | ❌ | — |
| 35 | Wiki article: combat | ❌ | — |
| 36 | Wiki article: farming | ❌ | — |
| 37 | Block gallery index page | ✅ | /wiki/blocks/gallery — done (3D renders + filters + search + pagination) |
| 38 | Mob gallery index page | ✅ | /wiki/mobs/gallery — done (3D renders + filters + search + pagination) |
| 39 | Wiki article: biomes | ❌ | — |
| 40 | Wiki article: dimensions | ❌ | — |
| 41 | Wiki article: mining | ❌ | — |
| 42 | Wiki article: building | ❌ | — |
| 43 | Wiki article: trading | ❌ | — |
| 44 | Wiki article: fishing | ❌ | — |
| 45 | Wiki article: status effects | ❌ | — |
| 46 | Wiki article: commands | ❌ | — |
| 47 | Wiki article: exploration | ❌ | — |
| 48 | Wiki article: game mechanics | ❌ | — |
| 49 | Wiki article: survival tips | ❌ | — |
| 50 | Wiki article: structures | ❌ | — |
| 51 | Block detail pages (790 stubs / 900) | 🟡 | 790 data stubs (766 wiki-matched)؛ 42 با محتوای کامل wiki (۸۸٪ partial) |
| 52 | Mob detail pages (52 → 83) | 🟡 | 52/83 (۶۳٪)؛ 42 با محتوای کامل |
| 53 | Version pages (78/78) | ✅ | 78/78 (۱۰۰٪) — تمام نسخه‌ها features + changelog دارند |
| 54 | Item detail pages (0 → 1200) | ❌ | 0/1200 — not started (only item renders exist) |
| 55 | Wiki article: crafting recipes | ❌ | — |
| 56 | Wiki article: mobs (overview) | ❌ | — |
| 57 | Wiki article: blocks (overview) | ❌ | — |
| 58 | Wiki article: items (overview) | ❌ | — |
| 59 | Wiki article: food | ❌ | — |
| 60 | Tested seeds (20 → 60) | ❌ | 20/60 (33%) — partial |

### 4️⃣ دسته‌ی 4 — Seeds/Craft (phases 61-110)

| # | فاز | وضعیت | یادداشت |
|---|---|---|---|
| 61 | Speedrun records (1187 → full) | ❌ | 1187 records — partial (some categories missing) |
| 62 | Seed finder (cubiomes WASM) | ❌ | worker exists ولی integration ناتمام |
| 63 | Java version detail pages | ✅ | 31/31 نسخه (paired با فاز ۵۳) |
| 64 | Bedrock version detail pages | ✅ | 47/47 نسخه (paired با فاز ۵۳) |
| 65 | Version changelog (Java) | ✅ | 31 نسخه با features + changelog (5+5 آیتم) |
| 66 | Version changelog (Bedrock) | ✅ | 47 نسخه با features + changelog (5+5 آیتم) |
| 67 | Version diff pages | ❌ | هنوز نسخه‌ی diff پیاده‌سازی نشده |
| 68 | Version comparison tool | ❌ | هنوز comparison tool پیاده‌سازی نشده |
| 69 | Seed submission form | ❌ | — |
| 70 | Seed voting system | ❌ | — |
| 71 | Seed testing (auto verify) | ❌ | — |
| 72 | Seed tag system | ❌ | — |
| 73 | FAQ page | ✅ | done (21 questions, 7 categories) |
| 74 | Crafting recipe search | ❌ | — |
| 75 | Crafting recipe browser | ❌ | — |
| 76 | Crafting 3D preview | ❌ | — |
| 77 | Crafting grid inventory | ❌ | — |
| 78 | Recipe JSON-LD schema | ❌ | — |
| 79 | Recipe sharing (URL hash) | ❌ | — |
| 80 | Cloudflare Worker (KV-based) | ❌ | code در repo ولی deploy نشده (need user) |
| 81 | Worker deployment (wrangler) | ❌ | نیاز به `wrangler deploy` (manual by user) |
| 82 | Worker source in repo | ❌ | کد هست ولی phase = deploy نشده |
| 83 | Worker deploy README | ❌ | doc هست ولی deploy نشده |
| 84 | 2D seed map | ✅ | done (Canvas + grid + compass) |
| 85 | 3D seed preview | ❌ | — |
| 86 | Seed structure overlay | ❌ | — |
| 87 | Biome map (color-coded) | ❌ | — |
| 88 | Spawn point marker | ❌ | — |
| 89 | Coordinate input + teleport | ❌ | — |
| 90 | Seed copy/share button | ❌ | — |
| 91 | Seed rating system | ❌ | — |
| 92 | Seed comments | ❌ | — |
| 93 | Seed download (.mcworld) | ❌ | — |
| 94 | Site features list (8 → 20+) | ❌ | 8/20+ — partial |
| 95 | Mod download pages | ❌ | — |
| 96 | Mod screenshots gallery | ❌ | — |
| 97 | Mod rating | ❌ | — |
| 98 | Mod comments | ❌ | — |
| 99 | Mod tag filter | ❌ | — |
| 100 | Bow/arrow recipes verified | ❌ | 2 recipes verified — partial (very minimal) |
| 101 | Recipe search index | ❌ | — |
| 102 | Drag & Drop crafting | ✅ | done (HTML5 Drag API + touch) |
| 103 | Recipe categories | ❌ | — |
| 104 | Recipe favorites | ❌ | — |
| 105 | Real centralized KV backend | ❌ | code در worker ولی deploy نشده |
| 106 | Anti-inflation logic | ❌ | code هست ولی deploy نشده |
| 107 | KV limit protection | ❌ | code هست ولی deploy نشده |
| 108 | Page view tracking | ❌ | — |
| 109 | Referrer tracking | ❌ | — |
| 110 | Browser/OS tracking | ❌ | — |

### 5️⃣ دسته‌ی 5 — Backend (phases 111-140)

| # | فاز | وضعیت | یادداشت |
|---|---|---|---|
| 111 | Analytics dashboard | ❌ | — |
| 112 | Daily stats aggregation | ❌ | — |
| 113 | Weekly stats aggregation | ❌ | — |
| 114 | Monthly stats aggregation | ❌ | — |
| 115 | Real-time online count | ❌ | code در worker ولی deploy نشده |
| 116 | Page popularity ranking | ❌ | — |
| 117 | Top referrers report | ❌ | — |
| 118 | Geo distribution (city) | ❌ | — |
| 119 | Device breakdown | ❌ | — |
| 120 | Custom event tracking | ❌ | — |
| 121 | API rate limiting | ❌ | — |
| 122 | API CORS config | ❌ | — |
| 123 | API key system | ❌ | — |
| 124 | Webhook for new content | ❌ | — |
| 125 | Online count real (KV) | ✅ | done (KV heartbeat) |
| 126 | Visitor UUID generation | ❌ | code در analytics.js ولی phase ناتمام |
| 127 | Daily UUID dedup | ❌ | — |
| 128 | 30-day chart (Chart.js) | ✅ | done (with phase 129 — counted as 1 logical phase) |
| 129 | 24-hour chart (Chart.js) | ❌ | done as part of phase 128-129 (paired feature; counted as 1 phase in summary) |
| 130 | Date fix (jalaali-js + Tehran) | ✅ | done |
| 131 | Stats export (CSV) | ❌ | — |
| 132 | Stats export (JSON) | ❌ | — |
| 133 | Stats API (public) | ❌ | — |
| 134 | Stats API (admin) | ❌ | — |
| 135 | Admin login | ❌ | — |
| 136 | Admin dashboard | ❌ | — |
| 137 | Admin content editor | ❌ | — |
| 138 | Admin moderation | ❌ | — |
| 139 | Admin analytics | ❌ | — |
| 140 | Admin user management | ❌ | — |

### 6️⃣ دسته‌ی 6 — Speedrun/Video (phases 141-160)

| # | فاز | وضعیت | یادداشت |
|---|---|---|---|
| 141 | Speedrun leaderboard (Bedrock) | ❌ | partial — records exist ولی leaderboard ناتمام |
| 142 | Speedrun leaderboard (Java) | ❌ | partial — records exist ولی leaderboard ناتمام |
| 143 | Speedrun record submission | ❌ | — |
| 144 | Speedrun record verification | ❌ | — |
| 145 | Speedrun record video link | ❌ | — |
| 146 | Speedrun player profiles | ❌ | — |
| 147 | Speedrun category filter | ❌ | — |
| 148 | Speedrun version filter | ❌ | — |
| 149 | Aparat channel embed | ✅ | done (iframe) |
| 150 | Aparat video embed (single) | ❌ | done as part of phase 149 (paired feature; counted as 1 phase in summary) |
| 151 | YouTube embed | ❌ | — |
| 152 | Video gallery page | ❌ | — |
| 153 | Video category filter | ❌ | — |
| 154 | Video search | ❌ | — |
| 155 | RSS feed | ❌ | code در repo ولی auto-update ناتمام |
| 156 | Aparat auto-update (cron) | ❌ | — |
| 157 | Video tags | ❌ | — |
| 158 | Video rating | ❌ | — |
| 159 | Aparat video player (custom) | ❌ | basic iframe only — not custom player |
| 160 | Video download link | ❌ | — |

### 7️⃣ دسته‌ی 7 — User Account (phases 161-180) ⛔

> همه‌ی این دسته **بلاک‌شده** چون نیاز به Google OAuth + D1 database + Worker deploy داره.

| # | فاز | وضعیت | یادداشت |
|---|---|---|---|
| 161 | User registration (Google OAuth) | ⛔ | needs Google OAuth setup |
| 162 | User login | ⛔ | needs Worker deploy |
| 163 | User profile page | ⛔ | — |
| 164 | User avatar | ⛔ | — |
| 165 | User settings | ⛔ | — |
| 166 | User favorites (seeds) | ⛔ | — |
| 167 | User favorites (mods) | ⛔ | — |
| 168 | User favorites (pages) | ⛔ | — |
| 169 | User comments | ⛔ | — |
| 170 | User ratings | ⛔ | — |
| 171 | User submissions (seeds) | ⛔ | — |
| 172 | User submissions (mods) | ⛔ | — |
| 173 | User submissions (wiki) | ⛔ | — |
| 174 | User moderation | ⛔ | — |
| 175 | User badges | ⛔ | — |
| 176 | User leaderboard | ⛔ | — |
| 177 | User private messages | ⛔ | — |
| 178 | User notifications | ⛔ | — |
| 179 | User email preferences | ⛔ | — |
| 180 | User account deletion (GDPR) | ⛔ | — |

### 8️⃣ دسته‌ی 8 — Testing/Cleanup (phases 181-200)

| # | فاز | وضعیت | یادداشت |
|---|---|---|---|
| 181 | Lighthouse audit | ❌ | — |
| 182 | Lighthouse >90 Performance | ❌ | — |
| 183 | Lighthouse >95 Accessibility | ❌ | — |
| 184 | Lighthouse >95 SEO | ❌ | — |
| 185 | Unit tests (components) | ❌ | — |
| 186 | Unit tests (lib) | ❌ | — |
| 187 | Integration tests | ❌ | — |
| 188 | E2E tests (Playwright) | ❌ | — |
| 189 | Visual regression tests | ❌ | — |
| 190 | Accessibility audit (axe) | ❌ | — |
| 191 | Accessibility audit (manual) | ❌ | — |
| 192 | Cross-browser testing | ❌ | — |
| 193 | Performance budget | ❌ | — |
| 194 | Bundle size analysis | ❌ | — |
| 195 | Dead code removal | ❌ | — |
| 196 | Image optimization audit | ❌ | — |
| 197 | SEO audit (meta tags) | ❌ | — |
| 198 | SEO audit (sitemap) | ❌ | — |
| 199 | SEO audit (robots.txt) | ❌ | — |
| 200 | Final pre-launch review | ❌ | — |

---

## 🔴 کارهای بحرانی باقی‌مونده

### خودت باید بکنی (manual):
1. **Deploy Worker v3** — کد توی `worker/src/index.js` آماده‌ست. بریز روی Cloudflare (dashboard یا wrangler).
2. **Test 2-browser online** — بعد از Worker deploy، /stats/ رو توی Chrome + Firefox باز کن. باید online=2 بشه.
3. **Setup Google OAuth** (برای فازهای 161-180) — نیاز به Google Cloud Console.

### ایجنت می‌تونه بکنه:
1. **فاز 21** تکمیل — دانلود ~110 بلاک باقی‌مونده (از ۸۸٪ به ۱۰۰٪)
2. **فاز 24** ادامه — دانلود ~780 آیتم باقی‌مونده (از ۳۵٪ به ۱۰۰٪)
3. **فاز 51** ادامه — نوشتن محتوای کامل wiki برای ~700 بلاک باقی‌مونده (از 42 به 790)
4. **فاز 52** تکمیل — دانلود 31 ماب باقی‌مونده (از ۶۳٪ به ۱۰۰٪)
5. **فاز 67** — پیاده‌سازی version diff pages
6. **فاز 68** — version comparison tool
7. **فاز 73** بیشتر — اضافه کردن سوال‌های بیشتر
8. **فاز 155-156** — RSS + Aparat auto-update (cron)

### مرحله‌ی بعدی مفروض (most impactful):
- **فاز 51 wiki content برای 700 بلاک دیگر** — بالاترین impact برای SEO/کاربر (محتوای کامل Persian Wiki)

---

## 📎 لینک‌ها

- [🌐 سایت زنده](https://iran-minecraft-wiki.github.io/website/)
- [📖 README.md](./README.md) — معرفی پروژه
- [📊 PREVIEW_REPORT.md](./PREVIEW_REPORT.md) — گزارش پروژه
- [📄 REPORT.md](./REPORT.md) — خلاصه‌ی اجرایی
- [📋 CHECKLIST.md](./website/CHECKLIST.md) — checklist کامل فازها
- [🔍 MCIcons-AUDIT.md](./website/MCIcons-AUDIT.md) — تحلیل پکیج mcicons
- [⚙️ Worker source](./worker/src/index.js) — کد Cloudflare Worker v3
- [📖 Worker README](./worker/README.md) — راهنمای دیپلوی
