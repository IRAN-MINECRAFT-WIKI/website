// MineBed Stats Worker v2.1 — KV-based + page tracking + Tehran timezone
// ADDS: /api/pages endpoint + page-visit tracking + Asia/Tehran "today" boundary
// Paste this over the existing Worker code in the Cloudflare dashboard.
//
// REQUIRED: KV namespace bound as MINEBED_KV (already done per user)
// NOTE: "today" is computed in Asia/Tehran (UTC+3:30) so it matches the
// Iranian user's calendar day, not UTC.

const ONLINE_TTL = 60; // seconds — heartbeat auto-expires after 60s
const DAILY_TTL = 86400 * 31; // 31 days

// Compute today's date in Asia/Tehran timezone (returns YYYY-MM-DD).
// The Worker runs in UTC, but Iranian users expect "today" to match
// their calendar day (which starts at 00:00 Tehran = 20:30 UTC previous day).
function todayTehran() {
  // Tehran = UTC+3:30. Add 3.5h to UTC, then format as date.
  const now = new Date();
  const tehran = new Date(now.getTime() + (3.5 * 60 * 60 * 1000));
  return tehran.toISOString().split('T')[0];
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    if (!env.MINEBED_KV) {
      return Response.json(
        { error: 'KV not bound. Bind as MINEBED_KV in Worker Settings → Bindings.' },
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    try {
      // ── Health check ──────────────────────────────────────────────
      if (url.pathname === '/api/health') {
        return Response.json(
          { ok: true, time: new Date().toISOString(), backend: 'kv', version: 2 },
          { headers: corsHeaders }
        );
      }

      // ── Seeds submission ──────────────────────────────────────────
      if (url.pathname === '/api/seeds' && request.method === 'POST') {
        const body = await request.json();
        const ip = request.headers.get('cf-connecting-ip') || 'unknown';
        const today = todayTehran();
        const dayKey = `seeds|${today}|${ip}`;
        const countStr = await env.MINEBED_KV.get(dayKey);
        const count = parseInt(countStr || '0', 10);

        if (count >= 5) {
          return Response.json(
            { error: 'محدودیت روزانه: حداکثر ۵ سید در روز' },
            { status: 429, headers: corsHeaders }
          );
        }

        const seedId = `seed|${Date.now()}|${Math.random().toString(36).slice(2, 8)}`;
        await env.MINEBED_KV.put(
          seedId,
          JSON.stringify({
            seed_value: body.seed_value,
            version: body.version,
            platform: body.platform,
            features: body.features || [],
            coordinates: body.coordinates || {},
            user_uuid: body.user_uuid || '',
            ip_address: ip,
            created: new Date().toISOString(),
          }),
          { expirationTtl: DAILY_TTL }
        );
        await env.MINEBED_KV.put(dayKey, String(count + 1), { expirationTtl: DAILY_TTL });
        return Response.json({ ok: true }, { headers: corsHeaders });
      }

      // ── Stats — 3 KV reads (list operations) ─────────────────────
      if (url.pathname === '/api/stats') {
        const today = todayTehran();
        const hbList = await env.MINEBED_KV.list({ prefix: 'hb:', limit: 1000 });
        const online = hbList.keys.length;
        const dailyList = await env.MINEBED_KV.list({ prefix: `d:${today}:`, limit: 1000 });
        const todayCount = dailyList.keys.length;
        const uuidList = await env.MINEBED_KV.list({ prefix: 'u:', limit: 1000 });
        const total = uuidList.keys.length;
        return Response.json(
          { online, today: todayCount, total, source: 'kv' },
          { headers: corsHeaders }
        );
      }

      // ── Top pages (site-wide, real) — NEW in v2 ───────────────────
      // Returns the most-visited pages across ALL visitors, based on
      // unique-visitor-per-page-per-day markers (idempotent — a visitor
      // who refreshes a page 100 times counts as 1 for that page).
      //
      // Query param: ?range=today (default) or ?range=all
      if (url.pathname === '/api/pages') {
        const range = url.searchParams.get('range') || 'today';
        const today = todayTehran();
        const prefix = range === 'all' ? 'pv|' : `pv|${today}|`;
        const list = await env.MINEBED_KV.list({ prefix, limit: 1000 });

        // Each key: pv|{date}|{page}|{uuid}  (or pv|{page}|{uuid} — no, we use date)
        // Count unique (page, uuid) pairs per page.
        const pageCounts = {};
        for (const k of list.keys) {
          // Split by | — parts: ['pv', date, page, uuid]
          const parts = k.name.split('|');
          if (parts.length < 4) continue;
          const page = parts[2]; // page path (pages don't contain |)
          pageCounts[page] = (pageCounts[page] || 0) + 1;
        }

        const sorted = Object.entries(pageCounts)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 10)
          .map(([page, count]) => ({ page, count }));

        return Response.json(
          { pages: sorted, range, date: today, total: list.keys.length },
          { headers: corsHeaders }
        );
      }

      // ── Heartbeat — 4 KV writes (now includes page tracking) ─────
      if (url.pathname === '/api/heartbeat' && request.method === 'POST') {
        const body = await request.json();
        const userUuid = (body.user_uuid || '').trim();
        const page = (body.page || '/').replace(/^\/website\//, '/') || '/';
        const today = todayTehran();

        if (userUuid.length < 8) {
          return Response.json(
            { ok: false, error: 'invalid uuid' },
            { status: 400, headers: corsHeaders }
          );
        }

        // Heartbeat (auto-expires 60s)
        await env.MINEBED_KV.put(`hb:${userUuid}`, page, { expirationTtl: ONLINE_TTL });
        // Daily unique marker
        await env.MINEBED_KV.put(`d:${today}:${userUuid}`, '1', { expirationTtl: DAILY_TTL });
        // Ever-seen UUID
        await env.MINEBED_KV.put(`u:${userUuid}`, '1');
        // NEW: page-visit marker (unique per page per UUID per day)
        // Key format: pv|{date}|{page}|{uuid} — idempotent, so refreshing
        // a page 100 times = 1 count for that page.
        await env.MINEBED_KV.put(`pv|${today}|${page}|${userUuid}`, '1', {
          expirationTtl: DAILY_TTL,
        });

        return Response.json({ ok: true }, { headers: corsHeaders });
      }

      if (url.pathname === '/' || url.pathname === '/health') {
        return Response.json(
          { ok: true, service: 'minebed-stats', backend: 'kv', version: 2 },
          { headers: corsHeaders }
        );
      }

      return Response.json({ error: 'Not found' }, { status: 404, headers: corsHeaders });
    } catch (err) {
      return Response.json({ error: err.message }, { status: 500, headers: corsHeaders });
    }
  },
};
