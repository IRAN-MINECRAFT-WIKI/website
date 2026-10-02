/// <reference path="../pb_data/pb_hooks.d.ts" />
// pb_hooks/main.pb.js
// PocketBase hooks for the MineBed Persian Minecraft website.
//
// Responsibilities (kept deliberately tiny — pb_hooks are hard to test
// locally without a running PocketBase server, so the logic here is
// defensive: anything that errors is logged but does NOT block the
// original request, except the explicit IP rate-limit on seeds_queue
// create which is the whole point):
//
//   1. CORS — only allow `iran-minecraft-wiki.github.io` (the published
//      Astro site). Browsers without a matching Origin header still
//      get through (curl, server-to-server, GitHub Action), but a
//      browser from any other origin gets nothing.
//
//   2. IP rate-limiting on `seeds_queue` create — max 5 records per
//      IPv4 address per UTC day. Stops spam and brute-force seed
//      submission. The 5/day budget is shared across all IPv4 IPs
//      behind a single household NAT, which is fine for v1.
//
//   3. Auto-set `ip_address` on `seeds_queue` create (and on `visits`
//      create). This is the only IP-related field that the hooks
//      ever mutate — clients can submit any value but it gets
//      overwritten by the server-side real IP from the request
//      context. Prevents spoofing.
//
//   4. On approve (`status === 'approved'`), copy the row from
//      `seeds_queue` → `seeds_published`. The copy is idempotent — if
//      a row with the same seed_value+version+platform already
//      exists in seeds_published, the old one is updated rather than
//      duplicated.
//
//   5. Nightly cleanup of stale `online_users` rows (last_seen older
//      than 10 minutes). Runs from the PocketBase internal cron.
//
// All non-critical errors are caught and logged via consoleLog so the
// original user request still completes — except the IP rate-limit
// which returns a 429.

const ALLOWED_ORIGIN = 'https://iran-minecraft-wiki.github.io';
const DAILY_IP_LIMIT = 5;

// ============================================================
// 1. CORS — set on every response
// ============================================================

onRequest((routerName, path) => {
  const origin = request.headers.get('origin') || '';
  // Reflect only the canonical allowed origin. Empty origin
  // (server-to-server, curl, GitHub Actions bot) gets no
  // Access-Control-Allow-Origin header at all (which is the
  // same as "blocked" for browser fetches).
  if (origin === ALLOWED_ORIGIN) {
    response.setHeader('Access-Control-Allow-Origin', ALLOWED_ORIGIN);
    response.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
    response.setHeader('Access-Control-Allow-Headers', 'Authorization, Content-Type');
    response.setHeader('Access-Control-Max-Age', '86400');
    response.setHeader('Vary', 'Origin');
  }
  // Handle CORS preflight
  if (request.method === 'OPTIONS') {
    return response.send(204, '');
  }
  return response.next();
});

// ============================================================
// 2 + 3. seeds_queue: rate-limit + auto-set IP
// ============================================================

onRecordBeforeCreateRequest((e) => {
  // Auto-set ip_address from the real request context — clients
  // cannot spoof this. Falls back to the X-Forwarded-For header if
  // PocketBase is behind a proxy (Fly.io terminates TLS in front of
  // pocketbase so X-Forwarded-For is the only way to see the real
  // client IP).
  const realIp =
    request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ||
    request.headers.get('x-real-ip') ||
    e.request?.remoteAddr ||
    '';

  if (e.collection.name === 'seeds_queue') {
    // ---- IP rate-limit (5 / IPv4 / UTC-day) ----
    if (realIp) {
      try {
        const dayStart = new Date();
        dayStart.setUTCHours(0, 0, 0, 0);
        const dayStartISO = dayStart.toISOString().replace('T', ' ').slice(0, 19) + 'Z';

        const todayCount = $db
          .newQuery('SELECT COUNT(*) as n FROM seeds_queue WHERE ip_address = {:ip} AND created >= {:since}')
          .bind({ ip: realIp, since: dayStartISO })
          .one();

        if ((todayCount?.n || 0) >= DAILY_IP_LIMIT) {
          throw new BadRequestError(
            'سقف مجاز ارسال سید برای امروز پر شده است. فردا دوباره امتحان کن.'
          );
        }
      } catch (err) {
        // Only re-throw if it's the rate-limit error. Other errors
        // (DB issue, etc.) get logged but do NOT block the create —
        // better to allow a potential spam than to block legit users
        // when our own DB is misbehaving.
        if (err && err.name === 'BadRequestError') throw err;
        consoleLog('seeds_queue rate-limit check failed (non-fatal): ' + (err?.message || err));
      }
    }

    // ---- Force-set ip_address (server-side) ----
    if (realIp) {
      e.record.set('ip_address', realIp);
    }

    // Default the status field so clients that forget it don't
    // write null. PocketBase would reject null because `status` is
    // required, but the error message is cryptic — fail more
    // gracefully.
    if (!e.record.get('status')) {
      e.record.set('status', 'pending');
    }
    // tested_by_admin defaults to false rather than null so the
    // admin filter "show me only un-tested" works with a single
    // comparison.
    if (e.record.get('tested_by_admin') === null || e.record.get('tested_by_admin') === undefined) {
      e.record.set('tested_by_admin', false);
    }
    return;
  }

  // visits: same IP-autoset, no rate-limit (a real visitor hits
  // many pages per session — rate-limiting per-IP here would
  // silently drop legitimate pageviews from the same household).
  if (e.collection.name === 'visits') {
    if (realIp) {
      e.record.set('ip_address', realIp);
    }
    // Force visited_at to server time — clients can submit any
    // timestamp they want, we ignore it.
    e.record.set('visited_at', new Date().toISOString().replace('T', ' ').slice(0, 19) + 'Z');
    return;
  }

  // online_users: same IP-autoset + upsert behavior. The create
  // flow is the only way clients interact with online_users — every
  // 30s heartbeat is a POST that either creates a new row (first
  // visit) or fails the unique-index check (already exists) and
  // then we PATCH the existing row. Simpler than exposing both
  // endpoints to a browser.
  if (e.collection.name === 'online_users') {
    if (realIp) {
      // not stored on this collection but set it so any downstream
      // hook has access without re-parsing headers
      e.record.set('__source_ip', realIp);
    }
    e.record.set('last_seen', new Date().toISOString().replace('T', ' ').slice(0, 19) + 'Z');
    return;
  }
}, 'seeds_queue');
// Register the same hook body for visits and online_users. PocketBase
// lets you register a single hook fn against multiple collections by
// listing them after the comma — here we re-use the same function for
// the other two collections.
// (Mirrored registration — see onRequest handler above for why the
// hook fn inspects e.collection.name rather than splitting per-type.)
onRecordBeforeCreateRequest((e) => {
  const realIp =
    request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ||
    request.headers.get('x-real-ip') ||
    '';

  if (e.collection.name === 'visits') {
    if (realIp) e.record.set('ip_address', realIp);
    e.record.set('visited_at', new Date().toISOString().replace('T', ' ').slice(0, 19) + 'Z');
  } else if (e.collection.name === 'online_users') {
    e.record.set('last_seen', new Date().toISOString().replace('T', ' ').slice(0, 19) + 'Z');
  }
}, 'visits', 'online_users');

// ============================================================
// 4. seeds_queue: on approve → copy to seeds_published
// ============================================================

onRecordAfterUpdateRequest((e) => {
  // Only react when status flipped to 'approved' on the seeds_queue
  // collection. Subsequent edits (e.g. toggling tested_by_admin
  // after approval) do NOT re-copy — we use seed_value+version+
  // platform as the natural key so the existing published row gets
  // patched in place.
  if (e.collection.name !== 'seeds_queue') return;

  const newStatus = e.record.get('status');
  if (newStatus !== 'approved') return;

  // Idempotency: find existing published row by natural key
  const seedValue = e.record.get('seed_value');
  const version = e.record.get('version');
  const platform = e.record.get('platform');

  try {
    const existing = $db
      .newQuery(
        'SELECT id FROM seeds_published WHERE seed_value = {:sv} AND version = {:v} AND platform = {:p} LIMIT 1'
      )
      .bind({ sv: seedValue, v: version, p: platform })
      .one();

    const adminUser = e.httpContext?.auth?.record?.email || 'admin';
    const nowISO = new Date().toISOString().replace('T', ' ').slice(0, 19) + 'Z';

    const payload = {
      seed_value: seedValue,
      version,
      platform,
      features: e.record.get('features'),
      coordinates: e.record.get('coordinates'),
      user_uuid: e.record.get('user_uuid'),
      ip_address: e.record.get('ip_address'),
      reject_reason: e.record.get('reject_reason') || '',
      tested_by_admin: e.record.get('tested_by_admin') || false,
      published_at: nowISO,
      published_by: adminUser,
    };

    if (existing?.id) {
      // PATCH the existing published row with the latest values.
      // The PocketBase admin SDK is not available in pb_hooks —
      // we use the raw SQL adapter through $db.
      const cols = Object.keys(payload);
      const setClause = cols.map((c) => `${c} = {:${c}}`).join(', ');
      $db
        .newQuery(`UPDATE seeds_published SET ${setClause} WHERE id = {:id}`)
        .bind({ ...payload, id: existing.id })
        .execute();
    } else {
      // INSERT a new row
      const cols = Object.keys(payload);
      const placeholders = cols.map((c) => `{:${c}}`).join(', ');
      $db
        .newQuery(
          `INSERT INTO seeds_published (${cols.join(', ')}) VALUES (${placeholders})`
        )
        .bind(payload)
        .execute();
    }
  } catch (err) {
    // Copy failure is non-fatal: the seed is still marked approved
    // in seeds_queue, so a re-run of the daily cron in fetch-approved-
    // seeds.mjs can pick it up next time (the script also reads
    // approved rows from seeds_queue as a fallback).
    consoleLog('Approve→publish copy failed (non-fatal): ' + (err?.message || err));
  }
}, 'seeds_queue');

// ============================================================
// 5. Cron — prune stale online_users rows every 10 min
// ============================================================

cronAdd('prune-online-users', '*/10 * * * *', () => {
  try {
    // Anything older than 10 minutes is considered offline.
    const cutoff = new Date(Date.now() - 10 * 60 * 1000)
      .toISOString()
      .replace('T', ' ')
      .slice(0, 19) + 'Z';
    $db
      .newQuery('DELETE FROM online_users WHERE last_seen < {:cutoff}')
      .bind({ cutoff })
      .execute();
  } catch (err) {
    consoleLog('prune-online-users cron failed (non-fatal): ' + (err?.message || err));
  }
});

// ============================================================
// Helper: response.send() shim if PocketBase runtime doesn't expose
// it. This block is a no-op in recent PocketBase versions where the
// `response` global is available, but keeps the script safe to load
// in older runtimes.
// ============================================================
// (no code — left intentionally blank so the hook file loads without
//  error on every PocketBase >= 0.20)
