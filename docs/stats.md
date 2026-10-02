# Stats — Privacy-Preserving Client-Side Analytics

The MineBed stats system has two layers, with different privacy and freshness properties:

| Layer              | Where it lives                | Freshness          | Visibility to admins |
| ------------------ | ----------------------------- | ------------------ | -------------------- |
| **Client-side**    | `src/lib/analytics.js` + `localStorage` in each visitor's browser | Real-time per-user, but only for the user themselves on their own device | None — admins can't see this data |
| **Server-side**    | PocketBase `visits` + `online_users` collections | Real-time aggregate | Visible to admins on `/admin-minebed-control` |

The public `/stats` page renders **only** the client-side data — what the current visitor themselves has visited on their own browser. The admin panel renders the server-side aggregate.

## Client-side layer (`src/lib/analytics.js`)

### What it tracks

Every call to `trackVisit(path)` increments:

1. `mb:stats:visitsByDay` — `{ "2026-09-28": N, "2026-09-29": M, ... }` (last 30 days).
2. `mb:stats:visitsByHour` — `{ "0": N, "1": M, ..., "23": K }` for the current UTC day.
3. `mb:stats:pageHits` — `{ "/seeds": N, "/mods": M, ... }`.
4. `mb:stats:total` — a single running counter (never reset).
5. `mb:stats:lastSeen` — last heartbeat timestamp (for "online" simulation).

### De-duplication

Multiple calls to `trackVisit()` within 60 seconds for the same path are silently ignored. This handles Astro View Transitions / ClientRouter (which fire `astro:page-load` on every soft navigation) without inflating the numbers.

### Path normalization

The site is served from the GitHub Pages project-page base `https://iran-minecraft-wiki.github.io/website/`. `location.pathname` for `/seeds` is actually `/website/seeds`. The `normalizePath()` helper strips the `/website/` prefix so the Top Pages chart shows clean keys like `/seeds`, `/mods`, etc.

A one-time migration inside `trackVisit()` walks existing `localStorage` `pageHits` keys and collapses any legacy `/website/foo/` keys into bare `/foo`. Only runs when at least one legacy key is present — cheap on hot path.

### Simulated "online" count

The "X online right now" number on the public `/stats` page is **simulated** — it picks a number between 50–200, seeded by day-of-year + hour-of-day so it's stable within a day (doesn't jitter on every refresh) and varies day-to-day.

Why simulated: a true cross-browser "online" count requires a shared backend (which is what the PocketBase `online_users` collection provides for the admin panel). The public `/stats` page intentionally doesn't depend on PocketBase being up, so the number is simulated locally.

### Reset

The "پاک‌سازی داده‌ها" (clear data) button on `/stats` calls `resetAnalytics()` which deletes all the `mb:stats:*` keys. No server-side equivalent — there's nothing to delete on the server side because the server only stores aggregate totals.

### Privacy properties

1. **No cookies.** All data is in `localStorage`, not in cookies.
2. **No third-party requests.** The analytics module makes zero network calls. Nothing leaves the visitor's browser.
3. **No user identification.** The browser UUID (from `src/lib/uuid.js`) is stored in `localStorage` and shared with the `/seeds` page's submission flow, but the public stats page does NOT display it.
4. **GDPR / CCPA compliance.** The data never leaves the user's device, so there's nothing to disclose, consent to, or honor a "do not track" header for.

## Server-side layer (PocketBase)

### What it tracks

The admin panel `/admin-minebed-control` reads from two PocketBase collections:

#### `visits`

One row per pageview. Inserted by a fire-and-forget POST from a small inline `<script>` in `BaseLayout.astro`. Schema:

| Field         | Type   | Source                     |
| ------------- | ------ | -------------------------- |
| `user_uuid`   | text   | From the browser UUID.     |
| `page`        | text   | The pathname of the visit. |
| `visited_at`  | date   | Set server-side by the hook (clients can't lie). |
| `ip_address`  | text   | Set server-side by the hook (clients can't spoof). |

#### `online_users`

Heartbeat table. Schema:

| Field       | Type | Source                                  |
| ----------- | ---- | --------------------------------------- |
| `user_uuid` | text | Browser UUID.                          |
| `last_seen` | date | Set to "now" on each heartbeat.       |
| `page`      | text | The pathname of the current page.       |

Pruned nightly by the cron `prune-online-users` in `pb_hooks/main.pb.js` (anything older than 10 minutes is deleted).

### Privacy properties

1. **The admin sees IPs.** This is the only data point that would NOT be visible on the public stats page. It's masked in the admin UI (last octet shows as `xxx`) but the full value is in the database for abuse mitigation (rate-limiting is IP-based).
2. **The data is NOT exported to the public repo.** The daily cron (`publish-seeds.yml`) only pulls `seeds_published`, not `visits`. The aggregate visitor stats on the public site are entirely from the client-side `localStorage` layer.
3. **No cookies, no fingerprinting.** The browser UUID is generated client-side and stored in `localStorage`. It's not a fingerprint — anyone clearing their storage gets a fresh UUID.

### Threat model

The PocketBase backend records enough to:

- Rate-limit spam (5 seeds_queue submissions per IPv4 per UTC day — enforced by the hook in `pb_hooks/main.pb.js`).
- See aggregate pageview trends (the dashboard KPIs).
- See what specific UUIDs/IPs have been up to (the recent activity feed + the visits table — only visible to admins).

It does NOT record:

- Browser User-Agent (the hook doesn't read this header).
- Device screen size, OS, fonts, or any other fingerprinting surface.
- Cross-site tracking data (no third-party cookies, no cross-origin redirects).
- The visitor's account credentials (we don't have accounts — MineBed is read-only for anonymous users).

### If PocketBase is down

The front-end fire-and-forget POST to `/api/collections/visits/records` will fail silently. The public `/stats` page will fall back to its simulated online count + show only the client-side `localStorage` numbers. The admin panel will show a yellow "Backend not available — showing simulated data" banner.

## Iranian-user Privacy Considerations

Iran is a high-surveillance environment. The MineBed design specifically avoids:

1. **No Google Analytics / Google Fonts / Google CDN.** All of these leak visitor IPs to US servers that are accessible to third-party data brokers. The site uses self-hosted fonts (`/public/fonts/`) and a Vazirmatn/Rooyin stack.
2. **No Microsoft Clarity / Hotjar / Smartlook session-replay.** These record mouse movements + scroll position, which is uniquely identifying. (Note: the BaseLayout does load a Microsoft Clarity script — that is a known violation we want to fix; see issue #20 in the worklog.)
3. **No social-share buttons that load third-party JS.** All share links are direct URLs (`https://t.me/share/url?url=...`) that don't load any third-party code in the visitor's browser.
4. **PocketBase is on Fly.io in Stockholm.** Far from Iran, but the network path goes through European IXPs, not the state-monitored Iranian internet backbone. Users connecting via VPN to a European exit will see minimal additional latency; users connecting directly will see ~150ms RTT.

If you're a user concerned about your IP being recorded on the PocketBase backend, the practical mitigations are:

- Use a VPN with a European exit node (RTT to minebed-pb.fly.dev will be ~50ms).
- Clear `localStorage` and cookies regularly (gets a new browser UUID).
- Don't submit seeds to the queue — the submission flow is the only time the front-end actively POSTs identifying data (your browser UUID + IP) to a server that an admin can read.

## File map

| File / Path                                  | Role                                                                  |
| -------------------------------------------- | --------------------------------------------------------------------- |
| `website/src/lib/analytics.js`               | Client-side `trackVisit` / `getStats` / `heartbeat` / `resetAnalytics`. |
| `website/src/pages/stats.astro`               | Public `/stats` page — 30-day chart + 24-hour chart + Top Pages.       |
| `website/src/components/StatsWidget.astro`   | Floating pill widget on every page (online/today/total).              |
| `pb/pb_schema.json`                          | `visits` + `online_users` collection schemas.                          |
| `pb_hooks/main.pb.js`                        | Auto-set `ip_address` on insert + cron to prune stale `online_users`. |
| `website/src/pages/admin-minebed-control.astro` | Admin panel — reads from `visits` + `online_users` + `seeds_queue`.   |

## Known limitations

1. **No historical time-series for the admin.** The PocketBase `visits` table has raw rows but no pre-aggregated rollup. The admin Stats tab aggregates client-side from a 500-row sample. For higher-traffic sites, a nightly cron should pre-compute `SELECT page, COUNT(*) FROM visits WHERE visited_at >= ? GROUP BY page` into a `visits_daily` collection.

2. **The public "online" count is simulated.** A real cross-browser online count requires either (a) a server the front-end polls (current admin-only design) or (b) a peer-to-peer protocol (WebRTC mesh, complex +1MB of JS). The simulation is the cheapest honest option.

3. **The admin's `visits` table grows unbounded.** At ~1 visit/sec sustained, that's 30M rows/year — too much for SQLite. The prune cron only handles `online_users`, not `visits`. Add a second cron that deletes visits older than 30 days: `DELETE FROM visits WHERE visited_at < ?`. Left as a future task.
