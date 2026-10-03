/**
 * MineBed Stats Worker — KV-based (NOT D1, so no row-read limit).
 *
 * How it works:
 *   POST /api/heartbeat  { user_uuid, page }
 *     → stores  hb:{uuid}        = { ts, page }            (TTL 5min)
 *     → stores  d:{date}:{uuid}  = 1                       (daily unique, TTL 31d)
 *     → stores  u:{uuid}         = 1                       (ever-seen, no TTL)
 *
 *   GET /api/stats
 *     → lists hb:* keys, counts those with ts < 60s = online now
 *     → counts d:{today}:* = today unique visitors
 *     → counts u:* = total unique visitors (all-time)
 *
 * Anti-inflation: each user_uuid = 1 unique per day. A browser can't
 * inflate by refreshing (same UUID, same day = 1 marker, not 2).
 *
 * Free tier: 100,000 KV reads/day + 1,000 writes/day — far more than
 * a small site needs (each visitor = ~3 writes, each stats fetch = ~3 list calls).
 *
 * Deploy (see worker/README.md):
 *   1. npm install -g wrangler
 *   2. wrangler login
 *   3. wrangler kv:namespace create MINEBED_HEARTBEAT
 *      → copy the id into wrangler.toml
 *   4. wrangler kv:namespace create MINEBED_HEARTBEAT --preview
 *      → copy the preview_id into wrangler.toml
 *   5. wrangler deploy
 */

const HEARTBEAT_TTL_SECONDS = 300; // 5 min — auto-expire stale heartbeats
const ONLINE_WINDOW_MS = 60_000; // 60s — "online" = heartbeat in last 60s

const K_HB = 'hb:'; // hb:{uuid} = { ts, page }
const K_DAILY = 'd:'; // d:{YYYY-MM-DD}:{uuid} = 1 (daily unique)
const K_UUID = 'u:'; // u:{uuid} = 1 (ever-seen)

function todayStr() {
  return new Date().toISOString().split('T')[0];
}

function normalizePath(p) {
  if (!p || typeof p !== 'string') return '/';
  return p.replace(/^\/website\//, '/') || '/';
}

function isValidUuid(v) {
  return typeof v === 'string' && v.length >= 16 && v.length <= 64 && /^[a-zA-Z0-9_-]+$/.test(v);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Content-Type': 'application/json',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // ── GET /api/stats ──────────────────────────────────────────
    if (url.pathname === '/api/stats' && request.method === 'GET') {
      try {
        const now = Date.now();

        // Online now: list heartbeat keys, check timestamps.
        const hbList = await env.MINEBED_HEARTBEAT.list({ prefix: K_HB, limit: 1000 });
        let online = 0;
        for (const key of hbList.keys) {
          const val = await env.MINEBED_HEARTBEAT.get(key.name);
          if (val) {
            try {
              const data = JSON.parse(val);
              if (now - data.ts < ONLINE_WINDOW_MS) online++;
            } catch {}
          }
        }

        // Today unique: count daily markers for today.
        const todayPrefix = K_DAILY + todayStr() + ':';
        const dailyList = await env.MINEBED_HEARTBEAT.list({ prefix: todayPrefix, limit: 1000 });
        const todayUnique = dailyList.keys.length;

        // Total unique: count ever-seen UUID markers.
        const uuidList = await env.MINEBED_HEARTBEAT.list({ prefix: K_UUID, limit: 1000 });
        const totalUnique = uuidList.keys.length;

        return new Response(
          JSON.stringify({
            online,
            today: todayUnique,
            total: totalUnique,
            totalUnique,
            todayUnique,
            source: 'kv',
            timestamp: now,
          }),
          { headers: corsHeaders }
        );
      } catch (e) {
        return new Response(
          JSON.stringify({ error: 'stats_error: ' + e.message, online: 0, today: 0, total: 0 }),
          { status: 500, headers: corsHeaders }
        );
      }
    }

    // ── POST /api/heartbeat ─────────────────────────────────────
    if (url.pathname === '/api/heartbeat' && request.method === 'POST') {
      try {
        let body;
        try {
          body = await request.json();
        } catch {
          return new Response(JSON.stringify({ ok: false, error: 'invalid_json' }), {
            status: 400,
            headers: corsHeaders,
          });
        }

        const userUuid = (body.user_uuid || '').trim();
        if (!isValidUuid(userUuid)) {
          return new Response(JSON.stringify({ ok: false, error: 'invalid_uuid' }), {
            status: 400,
            headers: corsHeaders,
          });
        }

        const page = normalizePath(body.page);
        const now = Date.now();
        const today = todayStr();

        // Write heartbeat (with TTL so stale entries auto-expire).
        await env.MINEBED_HEARTBEAT.put(
          K_HB + userUuid,
          JSON.stringify({ ts: now, page }),
          { expirationTtl: HEARTBEAT_TTL_SECONDS }
        );

        // Mark daily unique (idempotent).
        await env.MINEBED_HEARTBEAT.put(K_DAILY + today + ':' + userUuid, '1', {
          expirationTtl: 86400 * 31,
        });

        // Mark ever-seen UUID (no TTL).
        await env.MINEBED_HEARTBEAT.put(K_UUID + userUuid, '1');

        return new Response(JSON.stringify({ ok: true, ts: now }), { headers: corsHeaders });
      } catch (e) {
        return new Response(JSON.stringify({ ok: false, error: e.message }), {
          status: 500,
          headers: corsHeaders,
        });
      }
    }

    if (url.pathname === '/' || url.pathname === '/health') {
      return new Response(
        JSON.stringify({ ok: true, service: 'minebed-stats', backend: 'kv' }),
        { headers: corsHeaders }
      );
    }

    return new Response(JSON.stringify({ error: 'not_found' }), {
      status: 404,
      headers: corsHeaders,
    });
  },
};
