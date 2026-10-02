# Hidden Admin Panel — `/admin-minebed-control`

> ⚠️ **This document is for the project maintainers only.** Do NOT share the URL publicly; the only "security" protecting this page is that the URL is unguessable + the backend requires a real PocketBase admin token for any mutating action.

## Where it lives

| Environment | URL                                                                |
| ----------- | ----------------------------------------------------------------- |
| Local dev   | `http://localhost:4321/admin-minebed-control`                     |
| Production | `https://iran-minecraft-wiki.github.io/website/admin-minebed-control` |

The page is **not** linked from any nav, footer, or sitemap entry. The `<meta name="robots" content="noindex, nofollow">` tag (set via the `noindex: true` prop on the page's `BaseLayout` invocation) tells Google not to index it. `public/robots.txt` also has an explicit `Disallow: /admin-minebed-control` rule. The sitemap filter in `astro.config.mjs` (`exclude: ['/admin-minebed-control']`) strips it from `sitemap-index.xml`.

## How to access

1. Open the production URL above.
2. Paste your PocketBase admin JWT into the password box. The token comes from a one-shot POST to `/api/admins/auth-with-password` on the PocketBase server:

   ```bash
   curl -X POST https://minebed-pb.fly.dev/api/admins/auth-with-password \
     -H 'Content-Type: application/json' \
     -d '{"identity":"admin@minebed.local","password":"YOUR_PASSWORD"}'
   # → {"token":"eyJhbGciOiJIUzI1NiIs...","admin":{...}}
   ```

3. Click **ورود** (login). The token is stored in `sessionStorage` under the key `adminToken`.

## What's in the panel

### Dashboard tab

- 4 KPI cards: online users (refreshes every 30s), pending seeds, published seeds, total visits.
- Quick actions row: bulk approve (approves every `tested_by_admin=true` pending seed), refresh, jump to queue.
- Recent activity feed (last 8 events — visits + queue submissions, merged by timestamp).

### Queue tab

Table of seeds with the columns:

| Column    | Source field         | Notes                                           |
| --------- | -------------------- | ----------------------------------------------- |
| سید       | `seed_value`         | Displayed LTR in a monospace font.              |
| نسخه      | `version`            | e.g. `1.21`.                                    |
| پلتفرم    | `platform`           | `☕ Java` or `📱 Bedrock`.                       |
| ویژگی‌ها  | `features`           | JSON array → rendered as small chips.           |
| UUID کاربر | `user_uuid`         | Truncated to 8 chars + ellipsis. Full value in `title=` tooltip. |
| IP        | `ip_address`         | Last octet masked (e.g. `192.168.1.xxx`).       |
| تاریخ     | `created`            | Full Persian date+time.                          |
| وضعیت     | `status`             | Pill badge: ⏳ pending / ✅ approved / ❌ rejected. |
| اقدامات   | (n/a)                | 🧪 Test, ✅ Approve, ❌ Reject buttons.           |

Filters at the top: status, version, platform. Pagination is 20 per page.

### Stats tab

- 4 KPI cards (online, today, this week, unique IPs today).
- 24-hour visits bar chart (pure SVG, no Chart.js).
- Top 10 pages table.

## How it talks to the backend

Every API call is a `fetch()` to `${PB_URL}/api/collections/<name>/records`. The `PB_URL` constant is defined at the top of `admin-minebed-control.astro` — change it before deploying to point at the production PocketBase server. Every call carries the header `Authorization: Bearer <token>` where the token comes from `sessionStorage.adminToken`.

### Graceful degradation

If the PocketBase server is unreachable, the panel does NOT break — instead it shows a yellow banner ("Backend not available — showing simulated data") and populates every table/chart with simulated rows. This lets maintainers preview the UI before the backend is deployed, and serves as a fallback if the backend is briefly down (the page is still rendered, just with fake numbers).

Click the **🧪 ورود با داده‌ی شبیه‌سازی** button on the login screen to bypass the token check entirely and force the simulated mode.

## Security notes

1. **The login form is NOT real auth.** It just stores a token in `sessionStorage`. Anybody who can guess the URL can load the page. The real auth happens at the PocketBase layer — without a valid admin JWT, every mutating API call (`PATCH` to change a seed's status) returns 401. The login form exists purely to set the `Authorization` header on subsequent requests.

2. **Token storage is `sessionStorage`, not `localStorage`.** This is intentional: `sessionStorage` is per-tab and dies when the tab closes. A forgotten logged-in admin session doesn't outlive the day. The trade-off is that opening a new tab requires re-entering the token.

3. **No CSRF protection.** PocketBase's built-in CORS policy (enforced by `pb_hooks/main.pb.js`) only reflects the origin `https://iran-minecraft-wiki.github.io`. A malicious site embedding a `<form>` that POSTs to the admin API will be blocked by the browser because the response has no `Access-Control-Allow-Origin` header. This is sufficient for the threat model (anonymous script-kiddie CSRF). For higher-threat environments, add a CSRF token endpoint to PocketBase + verify it in the hooks.

4. **IP addresses are visible to admins.** The `ip_address` column shows the submitter's real IP. This is necessary for abuse mitigation (the rate-limit hook keys off IP). In the admin UI, the last octet is masked (`192.168.1.xxx`) — full IPs are only in the database. Don't export the seeds_queue table to a public place.

5. **The page is served over HTTPS in production** (GitHub Pages enforces TLS). The token in `sessionStorage` never travels over the wire in plaintext. The PB_URL constant points to a `https://` PocketBase server (Fly.io enforces TLS at the edge), so the API calls are also encrypted.

6. **Rotate the admin token** if you suspect it has been compromised. There is no UI for this — log into PocketBase directly, change the admin password, get a new token via the `/api/admins/auth-with-password` POST, and paste it into the panel.

## Setup checklist for a fresh deploy

- [ ] PocketBase server deployed (see `pb/README.md`).
- [ ] Schema imported from `pb/pb_schema.json` (4 collections).
- [ ] Hooks loaded from `pb_hooks/main.pb.js` (check the PocketBase log for `[hooks] loaded: main.pb.js`).
- [ ] Admin user created in PocketBase.
- [ ] `PB_URL` constant in `website/src/pages/admin-minebed-control.astro` updated to point at production (e.g. `https://minebed-pb.fly.dev`).
- [ ] `PB_URL` and `PB_ADMIN_TOKEN` secrets added to the GitHub repo (for the daily cron workflow — see `.github/workflows/publish-seeds.yml`).
- [ ] `robots.txt` has `Disallow: /admin-minebed-control`.
- [ ] `astro.config.mjs` sitemap filter excludes `/admin-minebed-control`.

## File paths

```
website/src/pages/admin-minebed-control.astro   ← the panel itself
pb/pb_schema.json                                ← backend schema (collections)
pb_hooks/main.pb.js                              ← backend hooks (CORS + rate-limit + auto-copy)
.github/workflows/publish-seeds.yml              ← daily cron that pulls approved seeds
scripts/fetch-approved-seeds.mjs                 ← Node fetcher used by the cron
website/public/robots.txt                        ← has Disallow: /admin-minebed-control
website/astro.config.mjs                         ← sitemap filter excludes admin URL
```

## Known limitations

1. **Bulk "approve all tested" action walks the cached queue page (20 rows).** A real bulk endpoint on PocketBase would let us approve all 200+ in one call. For now, an admin approving more than ~20 seeds needs to click "next page" between approve runs. Implementable as a future `POST /api/collections/seeds_queue/bulk-approve` endpoint with a single SQL `UPDATE` in a hook.

2. **The 24h visits chart aggregates client-side** from a 500-row sample, not from a server-side SQL aggregation. For a low-traffic site this is fine. For high traffic (>500 visits/day), the chart under-counts. A future enhancement: a custom PocketBase route `/api/visits/by-hour` that runs `SELECT strftime('%H', visited_at) AS h, COUNT(*) FROM visits WHERE visited_at >= ... GROUP BY h` server-side.

3. **No real-time online users count.** The "online" KPI polls `/api/collections/online_users/records?filter=last_seen>="5min ago"&perPage=1&count=1` every 30s. SSE/websockets would be lighter on the server. Out of scope for v1.

4. **The admin panel doesn't validate the token format** before storing it. A user pasting garbage into the password box will see a "Backend not available" banner (because every API call 401s). Add a `/api/admins/auth-refresh` call after login to validate the token before showing the dashboard — left as a v2 enhancement.
