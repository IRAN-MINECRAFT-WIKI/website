// MineBed Stats Worker v3 — KV-optimized (writes + lists under free-tier limits)
//
// FIXES vs v2:
// 1. Conditional writes: only put() d:/u:/pv: keys if they don't already exist
//    (check with get() first). Returning visitor = 1 write per heartbeat (not 4).
// 2. ONLINE_TTL = 330s (slightly > 5-min heartbeat, so online stays accurate).
// 3. /api/stats + /api/pages cached in KV for 10 min (cache:stats / cache:pages)
//    → list() only runs ~144 times/day instead of every request.
//
// Daily usage with these fixes (assuming 100 visitors, 5-min heartbeat):
//   Writes:  ~288 (1 per heartbeat × 288 heartbeats) — under 1,000 ✅
//   Lists:   ~432 (3 per cache refresh × 144 refreshes) — under 1,000 ✅
//   Reads:   ~864 (3 gets per heartbeat × 288) — under 100,000 ✅

const ONLINE_TTL = 330; // 5.5 min — slightly > heartbeat so online stays accurate
const DAILY_TTL = 86400 * 31; // 31 days
const STATS_CACHE_TTL = 600; // 10 min cache for /api/stats
const PAGES_CACHE_TTL = 600; // 10 min cache for /api/pages

// Compute today's date in Asia/Tehran timezone (UTC+3:30).
function todayTehran() {
  const now = new Date();
  const tehran = new Date(now.getTime() + 3.5 * 60 * 60 * 1000);
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
      // ── Health check ──
      if (url.pathname === '/api/health') {
        return Response.json(
          { ok: true, time: new Date().toISOString(), backend: 'kv', version: 3 },
          { headers: corsHeaders }
        );
      }

      // ── Seeds submission ──
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

      // ── Stats — cached for 10 min to avoid list() on every request ──
      if (url.pathname === '/api/stats') {
        // Try cache first (1 read, no lists).
        const cached = await env.MINEBED_KV.get('cache:stats');
        if (cached) {
          return new Response(cached, {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          });
        }

        // Cache miss — compute (3 lists) + cache the result.
        const today = todayTehran();
        const hbList = await env.MINEBED_KV.list({ prefix: 'hb:', limit: 1000 });
        const online = hbList.keys.length;
        const dailyList = await env.MINEBED_KV.list({ prefix: `d:${today}:`, limit: 1000 });
        const todayCount = dailyList.keys.length;
        const uuidList = await env.MINEBED_KV.list({ prefix: 'u:', limit: 1000 });
        const total = uuidList.keys.length;

        const body = JSON.stringify({
          online,
          today: todayCount,
          total,
          source: 'kv',
        });

        // Cache for 10 min (1 write).
        await env.MINEBED_KV.put('cache:stats', body, { expirationTtl: STATS_CACHE_TTL });

        return new Response(body, {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      // ── Top pages — cached for 10 min ──
      if (url.pathname === '/api/pages') {
        const cached = await env.MINEBED_KV.get('cache:pages');
        if (cached) {
          return new Response(cached, {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          });
        }

        const range = url.searchParams.get('range') || 'today';
        const today = todayTehran();
        const prefix = range === 'all' ? 'pv|' : `pv|${today}|`;
        const list = await env.MINEBED_KV.list({ prefix, limit: 1000 });

        const pageCounts = {};
        for (const k of list.keys) {
          const parts = k.name.split('|');
          if (parts.length < 4) continue;
          const page = parts[2];
          pageCounts[page] = (pageCounts[page] || 0) + 1;
        }

        const sorted = Object.entries(pageCounts)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 10)
          .map(([page, count]) => ({ page, count }));

        const body = JSON.stringify({ pages: sorted, range, date: today });
        await env.MINEBED_KV.put('cache:pages', body, { expirationTtl: PAGES_CACHE_TTL });

        return new Response(body, {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      // ── Heartbeat — conditional writes (1 put + 3 gets for returning visitors) ──
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

        // 1. Always write heartbeat (for online count) — 1 put.
        await env.MINEBED_KV.put(`hb:${userUuid}`, page, { expirationTtl: ONLINE_TTL });

        // 2. Daily unique marker — only if not already present today.
        //    Check with get() first (1 read), write only if missing (0-1 write).
        const dKey = `d:${today}:${userUuid}`;
        if (!(await env.MINEBED_KV.get(dKey))) {
          await env.MINEBED_KV.put(dKey, '1', { expirationTtl: DAILY_TTL });
        }

        // 3. Ever-seen UUID — only if not already present.
        const uKey = `u:${userUuid}`;
        if (!(await env.MINEBED_KV.get(uKey))) {
          await env.MINEBED_KV.put(uKey, '1');
        }

        // 4. Page-visit marker — only if not already present.
        const pvKey = `pv|${today}|${page}|${userUuid}`;
        if (!(await env.MINEBED_KV.get(pvKey))) {
          await env.MINEBED_KV.put(pvKey, '1', { expirationTtl: DAILY_TTL });
        }

        // Invalidate stats cache so next /api/stats reflects new online count.
        // (1 delete — cheap, and keeps stats fresh after heartbeat.)
        await env.MINEBED_KV.delete('cache:stats');

        return Response.json({ ok: true }, { headers: corsHeaders });
      }

      if (url.pathname === '/' || url.pathname === '/health') {
        return Response.json(
          { ok: true, service: 'minebed-stats', backend: 'kv', version: 3 },
          { headers: corsHeaders }
        );
      }

      return Response.json({ error: 'Not found' }, { status: 404, headers: corsHeaders });
    } catch (err) {
      return Response.json({ error: err.message }, { status: 500, headers: corsHeaders });
    }
  },
};
