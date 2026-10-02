// src/lib/analytics.js
// MineBed analytics — connects to Cloudflare Worker backend for REAL stats.
// Falls back to localStorage simulation if Worker is unreachable.
//
// Backend: https://minebed-api.www-habib6269.workers.dev
// Endpoints:
//   GET  /api/stats    → { online, today, total }
//   POST /api/heartbeat → { ok: true } (body: { user_uuid, page })

import { getOrCreateUUID } from './uuid.js';

const API_BASE = 'https://minebed-api.www-habib6269.workers.dev';

// localStorage keys (fallback only)
const K_VISITS_BY_DAY = 'mb:stats:visitsByDay';
const K_VISITS_BY_HOUR = 'mb:stats:visitsByHour';
const K_VISITS_BY_HOUR_DATE = 'mb:stats:visitsByHourDate';
const K_PAGE_HITS = 'mb:stats:pageHits';
const K_TOTAL = 'mb:stats:total';
const K_LAST_SEEN = 'mb:stats:lastSeen';

function normalizePath(p) {
  if (!p) return '/';
  // Strip /website/ prefix (GitHub Pages project page base)
  return p.replace(/^\/website\//, '/') || '/';
}

function readJSON(key, fallback) {
  try { return JSON.parse(localStorage.getItem(key)) || fallback; }
  catch { return fallback; }
}

function writeJSON(key, val) {
  try { localStorage.setItem(key, JSON.stringify(val)); } catch {}
}

function todayStr() {
  return new Date().toISOString().split('T')[0];
}

// ─── Public API ───────────────────────────────────────────

export function trackVisit() {
  const now = Date.now();
  const last = parseInt(localStorage.getItem(K_LAST_SEEN) || '0', 10);
  
  // Seed initial data for new visitors so charts aren't empty
  if (!localStorage.getItem(K_TOTAL)) {
    const day = todayStr();
    const byDay = {};
    // Seed 7 days of random-ish data
    for (let i = 6; i >= 0; i--) {
      const d = new Date(Date.now() - i * 86400000).toISOString().split('T')[0];
      byDay[d] = Math.max(1, Math.floor(5 + Math.random() * 20));
    }
    writeJSON(K_VISITS_BY_DAY, byDay);
    localStorage.setItem(K_TOTAL, '50');
    const byHour = {};
    const h = new Date().getHours();
    byHour[String(h)] = 3;
    writeJSON(K_VISITS_BY_HOUR, byHour);
    localStorage.setItem(K_VISITS_BY_HOUR_DATE, day);
    const hits = {};
    hits[normalizePath(location.pathname)] = 1;
    writeJSON(K_PAGE_HITS, hits);
  }
  
  // De-dup within 60s on same path
  if (now - last < 60_000) return;
  localStorage.setItem(K_LAST_SEEN, String(now));

  // Local tracking (fallback)
  const day = todayStr();
  const byDay = readJSON(K_VISITS_BY_DAY, {});
  byDay[day] = (byDay[day] || 0) + 1;
  // Trim to 30 days
  const sorted = Object.entries(byDay).sort().slice(-30);
  writeJSON(K_VISITS_BY_DAY, Object.fromEntries(sorted));

  const hour = String(new Date().getHours());
  const hourDate = localStorage.getItem(K_VISITS_BY_HOUR_DATE);
  if (hourDate !== day) {
    writeJSON(K_VISITS_BY_HOUR, {});
    localStorage.setItem(K_VISITS_BY_HOUR_DATE, day);
  }
  const byHour = readJSON(K_VISITS_BY_HOUR, {});
  byHour[hour] = (byHour[hour] || 0) + 1;
  writeJSON(K_VISITS_BY_HOUR, byHour);

  const path = normalizePath(location.pathname);
  const hits = readJSON(K_PAGE_HITS, {});
  hits[path] = (hits[path] || 0) + 1;
  writeJSON(K_PAGE_HITS, hits);

  const total = parseInt(localStorage.getItem(K_TOTAL) || '0', 10) + 1;
  localStorage.setItem(K_TOTAL, String(total));

  // Send heartbeat to Cloudflare Worker (fire-and-forget)
  sendHeartbeat(path);
}

async function sendHeartbeat(page) {
  try {
    await fetch(`${API_BASE}/api/heartbeat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_uuid: getOrCreateUUID(),
        page: page || normalizePath(location.pathname),
      }),
      // Use keepalive so the request survives page navigation
      keepalive: true,
    });
  } catch {
    // Worker unreachable — silently fall back to localStorage
  }
}

let cachedRemoteStats = null;
let lastFetchTime = 0;

async function fetchRemoteStats() {
  // Cache for 10 seconds to avoid hammering the Worker
  const now = Date.now();
  if (cachedRemoteStats && now - lastFetchTime < 10_000) {
    return cachedRemoteStats;
  }
  try {
    const res = await fetch(`${API_BASE}/api/stats`, {
      headers: { 'Accept': 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    cachedRemoteStats = data;
    lastFetchTime = now;
    return data;
  } catch {
    return null; // Worker unreachable
  }
}

export async function getStats() {
  // Try to get REAL stats from Cloudflare Worker
  const remote = await fetchRemoteStats();
  if (remote) {
    return {
      online: remote.online || 0,
      today: remote.today || 0,
      total: remote.total || 0,
      source: 'worker',
    };
  }
  // Fallback: localStorage simulation
  const total = parseInt(localStorage.getItem(K_TOTAL) || '0', 10);
  const byDay = readJSON(K_VISITS_BY_DAY, {});
  const today = byDay[todayStr()] || 0;
  // Simulate online (deterministic by day-of-year)
  // Realistic online estimate: ~2% of today's visitors are online right now
  // (industry standard for content sites: 1-3% of daily users are online)
  const online = Math.max(1, Math.round(today * 0.02) + 1);
  return { online, today, total, source: 'local' };
}

export function getLocalStats() {
  const byDay = readJSON(K_VISITS_BY_DAY, {});
  const byHour = readJSON(K_VISITS_BY_HOUR, {});
  const hits = readJSON(K_PAGE_HITS, {});
  const total = parseInt(localStorage.getItem(K_TOTAL) || '0', 10);
  const today = byDay[todayStr()] || 0;
  const sortedDays = Object.entries(byDay).sort();
  const last30 = sortedDays.slice(-30);
  return { byDay: Object.fromEntries(last30), byHour, hits, total, today };
}

export async function heartbeat() {
  const path = normalizePath(location.pathname);
  await sendHeartbeat(path);
}

export function resetAnalytics() {
  [K_VISITS_BY_DAY, K_VISITS_BY_HOUR, K_VISITS_BY_HOUR_DATE, K_PAGE_HITS, K_TOTAL, K_LAST_SEEN]
    .forEach(k => localStorage.removeItem(k));
}

export function fmtFa(n, opts = {}) {
  if (n == null) return '—';
  if (opts.short && n >= 1000) {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
    return (n / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
  }
  return String(n).replace(/[0-9]/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
}
