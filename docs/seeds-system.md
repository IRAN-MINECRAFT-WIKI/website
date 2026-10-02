# Seeds System — Architecture

The MineBed seeds system is a 4-layer pipeline:

1. **Front-end submission UI** — `/seeds/create` lets a user pick version + platform + features, generates a simulated seed + coords, saves it to IndexedDB locally, AND optionally submits it to PocketBase for review by the admin.
2. **PocketBase queue** — the `seeds_queue` collection holds every user-submitted seed pending admin review. Rate-limited 5/IP/day.
3. **Admin review** — the hidden `/admin-minebed-control` panel lets an admin test, approve, or reject each queued seed. Approving triggers a `pb_hooks` copy from `seeds_queue` to `seeds_published`.
4. **Static export** — a daily GitHub Action (`publish-seeds.yml`) pulls the `seeds_published` collection and writes it to `website/src/data/seeds-published.json`. The Astro site reads this JSON at build time and renders the public `/seeds` page.

## Data flow diagram

```
[User browser]
     │
     │ POST /api/collections/seeds_queue/records
     │     { seed_value, version, platform, features, coordinates, user_uuid }
     │     ← Authorization NOT required (anonymous create allowed by collection rule)
     │
     ▼
[PocketBase: seeds_queue]
     │
     │ pb_hooks/main.pb.js (onRecordBeforeCreateRequest):
     │   • Auto-set ip_address from request real IP (cannot be spoofed)
     │   • Default status='pending', tested_by_admin=false
     │   • IP rate-limit check: SELECT COUNT(*) FROM seeds_queue WHERE ip_address=? AND created >= today_00:00_utc
     │     → if count >= 5, throw BadRequestError
     │
     ▼
[PocketBase: seeds_queue]
     │
     │ Admin reviews via /admin-minebed-control → PATCH /api/collections/seeds_queue/records/{id}
     │     { status: 'approved' }     ← with Authorization: Bearer <admin_token>
     │
     ▼
[PocketBase: seeds_queue — after update]
     │
     │ pb_hooks/main.pb.js (onRecordAfterUpdateRequest):
     │   if newStatus === 'approved':
     │     SELECT id FROM seeds_published WHERE seed_value=? AND version=? AND platform=?
     │     → if exists: UPDATE seeds_published SET ... WHERE id=?
     │     → if not: INSERT INTO seeds_published (...) VALUES (...)
     │
     ▼
[PocketBase: seeds_published]
     │
     │ Daily cron at 03:00 IRST (23:30 UTC) → .github/workflows/publish-seeds.yml
     │   node scripts/fetch-approved-seeds.mjs
     │     (PB_URL, PB_ADMIN_TOKEN from GitHub secrets)
     │   GET /api/collections/seeds_published/records?perPage=500&sort=-published_at
     │   → maps rows → /home/z/work/imc-website/website/src/data/seeds-published.json
     │   → atomic write (tmp + rename)
     │   → git add + commit -m "chore: daily seed publish [skip ci]"
     │
     ▼
[website/src/data/seeds-published.json]
     │
     │ Astro build at deploy time (GitHub Actions deploy.yml)
     │   import seeds from './src/data/seeds-published.json'
     │   → renders /seeds/index.astro + /seeds/[slug].astro static HTML
     │
     ▼
[Public /seeds page on GitHub Pages]
```

## PocketBase schema

Four collections defined in [`pb/pb_schema.json`](../pb/pb_schema.json):

### `seeds_queue`

| Field             | Type   | Required | Notes                                                                     |
| ----------------- | ------ | -------- | ------------------------------------------------------------------------- |
| `seed_value`      | text   | ✅        | Max 64 chars. The numeric Minecraft seed string.                          |
| `version`         | text   | ✅        | e.g. `1.21`, `1.20.1`.                                                    |
| `platform`        | select | ✅        | One of `Java` / `Bedrock`.                                                |
| `features`        | json   | ❌        | Array of feature IDs (`village`, `stronghold`, etc.). Max 8KB.            |
| `coordinates`     | json   | ❌        | Array of `{ feature, x, y, z }` objects. Max 16KB.                        |
| `user_uuid`       | text   | ❌        | The browser UUID from `src/lib/uuid.js`. Lets us trace back to a session. |
| `ip_address`      | text   | ❌        | Set server-side by the hook (clients can't spoof).                       |
| `status`          | select | ✅        | `pending` / `approved` / `rejected`. Defaulted to `pending` if missing.   |
| `reject_reason`   | text   | ❌        | Required if `status=rejected` (admin-supplied).                          |
| `tested_by_admin` | bool   | ❌        | Defaults to `false`. Set to `true` when admin clicks 🧪 Test.              |
| `created`         | autodate | —      | Set on insert.                                                            |
| `updated`         | autodate | —      | Set on insert + every update.                                            |

Indexes: `status`, `ip_address`, `user_uuid`, `created`, `(version, platform)`.

### `seeds_published`

Same as `seeds_queue` **minus** `status`, plus:

| Field          | Type | Required | Notes                                     |
| -------------- | ---- | -------- | ----------------------------------------- |
| `published_at` | date | ✅        | Set by the hook at copy time.             |
| `published_by` | text | ✅        | The admin email that approved the seed.   |

Natural key: `(seed_value, version, platform)` — the hook uses this to upsert.

### `online_users`

Heartbeat table. The front-end `/admin-minebed-control` panel reads from here for the "online now" count.

| Field       | Type | Required | Notes                                         |
| ----------- | ---- | -------- | --------------------------------------------- |
| `user_uuid` | text | ✅        | Browser UUID.                                |
| `last_seen` | date | ✅        | Set to "now" on every heartbeat (every 30s). |
| `page`      | text | ❌        | The pathname the user is currently on.        |

Pruned nightly by the cron `prune-online-users` in `pb_hooks/main.pb.js` (anything older than 10 minutes is deleted).

### `visits`

Per-page visit log. Inserted by a fire-and-forget POST from BaseLayout's inline script on every Astro page load.

| Field        | Type | Required | Notes                              |
| ------------ | ---- | -------- | ---------------------------------- |
| `user_uuid`  | text | ✅        | Browser UUID.                     |
| `page`       | text | ✅        | Normalized pathname (max 256).    |
| `visited_at` | date | ✅        | Set server-side (clients can't lie). |
| `ip_address` | text | ❌        | Set server-side by hook.          |

## Cubiomes WASM — what's the long-term plan?

Today's `/seeds/create` page generates **simulated** seed values + coordinates. The features the user picks get random X/Y/Z values within plausible ranges. This is fine for the "feels like a real seed finder" UX, but the seeds aren't actually verified to contain the requested features.

The eventual plan: integrate [Cubiomes](https://github.com/Cubiest/cubiomes) compiled to WebAssembly. Cubiomes is a C library that implements Minecraft's world-generation algorithm in a way that can predict, for any given seed, where every biome / structure / village will appear — without ever loading the world in Java/Bedrock.

### Why WASM, not a backend?

1. **Privacy**: the seed never leaves the user's browser. A backend implementation would log every submitted seed in the wild, which is a privacy violation we're explicitly avoiding.
2. **Cost**: WASM runs in the user's browser tab; no compute cost on our servers.
3. **Latency**: WASM is ~10× faster than the same algorithm in JS for tight inner loops (PRNG state mutation).

### What it would replace

- The `randomSeedValue()` function in `seeds/create.astro` (currently a random 19-digit number).
- The `randomCoordsForFeature()` call (currently picks X/Y/Z at random in a -1500..1500 box).

### Implementation outline

1. **Build Cubiomes as WASM** — `cubiomes.c` is ~3000 LOC and depends only on libc. Emscripten + `emcc -O3 -s WASM=1 -s EXPORTED_FUNCTIONS=[...]` produces a ~600KB .wasm binary + ~30KB JS loader. Acceptable page weight for a tool page.
2. **Lazy-load only on /seeds/create** — never on the home page. The .wasm is fetched only when the user actually visits the seed finder.
3. **Pick features based on Cubiomes's biome/structure enum** — e.g. `Village`, `Stronghold`, `Ancient_City`, `Woodland_Mansion`, `Monument`, `Fortress`, `End_City`.
4. **Algorithm**:
   - User clicks "Generate" → loop until a random 64-bit seed produces all the requested features within a configurable radius (default 1024 blocks of origin).
   - For each feature, call Cubiomes's `locate_structure(seed, feature, X, Z)` to get the closest coords.
   - Return the seed + the coordinate list.
5. **Fallback**: if WASM isn't supported (very old browser) or Cubiomes fails to find a matching seed within N iterations (default 1000), fall back to the existing simulation. The UX stays identical; only the data quality changes.

### Page weight concern

Cubiomes WASM is ~600KB. With Brotli compression on the wire it's ~150KB. That's acceptable for a single-purpose page where the user explicitly chose to use a seed finder. It is NOT acceptable to ship on every page (hence the lazy-load restriction).

The current simulation approach is intentionally simple so we can ship the UX without the heavy dependency, then upgrade the data path later without touching the UI layer. The data shape (`{ code, version, platform, features[], coordinates[] }`) is identical between simulation and WASM modes, so the rendering code doesn't need to change.

## Privacy notes

1. **No account needed to submit a seed.** The browser UUID in `src/lib/uuid.js` is generated on first visit, persisted in `localStorage`, and sent with every submission. A user can clear it (`localStorage.removeItem('mb:uuid')`) to reset their identity.

2. **IP address is recorded** for rate-limiting + abuse mitigation, but:
   - It is set server-side by the hook (clients can't spoof or omit it).
   - The admin UI masks the last octet (`192.168.1.xxx`).
   - The full IP is only in the PocketBase database, not exposed in the public /seeds JSON.
   - We don't store IP in the published seeds export — the `seeds_published` collection has an `ip_address` field but the daily cron's mapper drops it before writing to `seeds-published.json`.

3. **No third-party analytics.** The front-end pageview POST to `/api/collections/visits/records` is fire-and-forget, with no cookies, no fingerprinting, no cross-origin requests. Compare to Google Analytics which sends ~12 cookies + 25 third-party requests on every page load.

4. **The published seeds JSON is committed to the public repo.** Anyone can read it. This is by design — the whole point of the pipeline is to take admin-curated seeds and publish them. The seed values, coordinates, features, version, and platform are all public data.

## File map

| File / Path                                            | Role                                                              |
| ------------------------------------------------------ | ----------------------------------------------------------------- |
| `pb/pb_schema.json`                                    | Schema export (4 collections).                                    |
| `pb_hooks/main.pb.js`                                  | CORS, IP rate-limit, auto-IP-set, approve→publish copy, cron.    |
| `pb/README.md`                                         | PocketBase setup + Fly.io deployment instructions.               |
| `.github/workflows/publish-seeds.yml`                  | Daily cron at 03:00 IRST.                                        |
| `scripts/fetch-approved-seeds.mjs`                     | Node fetcher used by the cron.                                   |
| `website/src/pages/admin-minebed-control.astro`        | Hidden admin panel for review + stats.                           |
| `website/src/pages/seeds/create.astro`                | Front-end submission UI.                                          |
| `website/src/pages/seeds/my.astro`                    | User's local IndexedDB collection.                               |
| `website/src/pages/seeds/index.astro`                 | Public /seeds listing (reads from `seeds-published.json`).       |
| `website/src/pages/seeds/[slug].astro`                 | Public per-seed detail page.                                     |
| `website/src/lib/seeddb.js`                            | IndexedDB wrapper for user-local saves.                          |
| `website/src/lib/uuid.js`                              | Browser UUID generator (localStorage-backed).                   |
| `website/src/data/seeds.json`                          | Hand-curated baseline seeds (always present even without PB).   |
| `website/src/data/seeds-published.json`                | Auto-generated by the daily cron (created on first run).         |
