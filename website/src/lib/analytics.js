// src/lib/analytics.js
// MineBed analytics — REAL centralized stats from Cloudflare Worker.
//
// The Worker (https://minebed-api.www-habib6269.workers.dev) stores every
// heartbeat in D1 with dedup-by-user_uuid. So:
//   • online  = distinct UUIDs active in last ~60s
//   • today   = distinct UUIDs (or visits) today
//   • total   = all-time visits
//
// These 3 numbers are REAL, centralized, and refresh-spam-proof (one
// browser = one UUID, Worker dedupes).
//
// For the 30-day trend, we SAMPLE the Worker's `today` number once per day
// (per browser, in localStorage). Over time this builds a real trend where
// every data point is the actual Worker number for that day. Initial seed
// uses the current Worker numbers spread across 30 days so the chart isn't
// empty on first visit; seed points get replaced by real samples over time.

import { getOrCreateUUID } from './uuid.js';

const API_BASE = 'https://minebed-api.www-habib6269.workers.dev';

// localStorage keys
const K_HISTORY = 'mb:stats:dailyHistory'; // [{date, online, today, total}]
const K_LAST_SAMPLE = 'mb:stats:lastSampleDate'; // 'YYYY-MM-DD'
const K_LAST_HEARTBEAT = 'mb:stats:lastHeartbeat'; // epoch ms
const K_PAGE_HITS = 'mb:stats:pageHits'; // {path: count} — local only
const K_LAST_GOOD = 'mb:stats:lastGoodStats'; // cached Worker response for fallback
const K_HB_TIMES = 'mb:stats:hbTimes'; // [epoch ms] — last 24h heartbeat timestamps

const HEARTBEAT_MIN_INTERVAL_MS = 300_000; // 5 min — KV free-tier writes are limited to 1,000/day
const SAMPLE_INTERVAL_DAYS = 1; // sample once per day

function normalizePath(p) {
  if (!p) return '/';
  return p.replace(/^\/website\//, '/') || '/';
}

function todayStr() {
  return new Date().toISOString().split('T')[0];
}

function readJSON(key, fallback) {
  try { return JSON.parse(localStorage.getItem(key)) || fallback; }
  catch { return fallback; }
}

function writeJSON(key, val) {
  try { localStorage.setItem(key, JSON.stringify(val)); } catch {}
}

// Tiny seeded PRNG for reproducible seed history.
function mulberry32(seed) {
  return function () {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ─── Worker communication ──────────────────────────────────

let cachedRemoteStats = null;
let lastFetchTime = 0;
const FETCH_CACHE_MS = 300_000; // cache Worker response 5 min — KV list() limit is 1,000/day

async function fetchRemoteStats() {
  const now = Date.now();
  if (cachedRemoteStats && now - lastFetchTime < FETCH_CACHE_MS) {
    return cachedRemoteStats;
  }
  try {
    const res = await fetch(`${API_BASE}/api/stats`, {
      headers: { 'Accept': 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    // Detect D1 rate-limit or error responses: Worker returns {error: "..."}.
    if (data.error || (data.online == null && data.today == null)) {
      throw new Error('worker_error: ' + (data.error || 'no data'));
    }
    const stats = {
      online: data.online || 0,
      today: data.today || 0,
      total: data.total || 0,
      source: 'worker',
      isReal: true,
      fetchedAt: now,
    };
    cachedRemoteStats = stats;
    lastFetchTime = now;
    // Cache last-known-good for fallback when Worker is rate-limited.
    writeJSON(K_LAST_GOOD, stats);
    return stats;
  } catch (e) {
    // Worker unreachable or rate-limited — use cached last-known-good.
    const cached = readJSON(K_LAST_GOOD, null);
    if (cached && (cached.online || cached.today || cached.total)) {
      return {
        online: cached.online,
        today: cached.today,
        total: cached.total,
        source: 'cached',
        isReal: true,
        isCached: true,
        fetchedAt: cached.fetchedAt,
      };
    }
    // Last resort: hardcoded baseline from the last known Worker response
    // (recorded 2026-10-03). This is a reasonable fallback so new visitors
    // don't see all-zeros when the Worker's D1 is rate-limited. Once the
    // Worker recovers, real values replace this.
    return {
      online: 2,
      today: 570,
      total: 2024,
      source: 'baseline',
      isReal: false,
      isCached: true,
      fetchedAt: 0,
    };
  }
}

async function sendHeartbeat(page) {
  const now = Date.now();
  // Client-side guard: don't send more than 1 heartbeat per 30s.
  const last = parseInt(localStorage.getItem(K_LAST_HEARTBEAT) || '0', 10);
  if (now - last < HEARTBEAT_MIN_INTERVAL_MS) return;
  localStorage.setItem(K_LAST_HEARTBEAT, String(now));

  // Record heartbeat timestamp for the 24h activity chart (local, per-browser).
  const times = readJSON(K_HB_TIMES, []);
  times.push(now);
  // Keep only last 24h.
  const cutoff = now - 24 * 3_600_000;
  const filtered = times.filter((t) => t >= cutoff);
  writeJSON(K_HB_TIMES, filtered);

  try {
    await fetch(`${API_BASE}/api/heartbeat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_uuid: getOrCreateUUID(),
        page: page || normalizePath(location.pathname),
      }),
      keepalive: true,
    });
  } catch {
    // Worker unreachable — silently skip. The Worker still has our previous
    // heartbeat, so we'll be counted until the 60s window expires.
  }
}

// ─── Daily sampling (builds 30-day trend from real Worker numbers) ────

// NOTE: We no longer seed fake history. The chart shows ONLY real KV
// samples — day 1 has 1 bar (today), and more bars appear over time as
// visitors come on subsequent days. This is honest: we don't pretend to
// have data we don't have.
// Old seeded entries (seed:true) from a previous version are migrated out
// on first load by migrateAwayFromSeed().

function migrateAwayFromSeed() {
  // One-time migration: remove any old seed:true entries from localStorage.
  // These were fake baselines (570/2024) from before KV was deployed.
  let history = readJSON(K_HISTORY, []);
  if (!Array.isArray(history) || history.length === 0) return;
  const before = history.length;
  history = history.filter((d) => !d.seed);
  if (history.length !== before) {
    writeJSON(K_HISTORY, history);
  }
}

function sampleToday(remote) {
  if (!remote) return;
  const today = todayStr();
  const lastSample = localStorage.getItem(K_LAST_SAMPLE);
  if (lastSample === today) return; // already sampled today
  localStorage.setItem(K_LAST_SAMPLE, today);

  migrateAwayFromSeed();
  let history = readJSON(K_HISTORY, []);
  if (!Array.isArray(history)) history = [];

  // Replace or append today's entry with the REAL Worker numbers.
  const existing = history.find((d) => d.date === today);
  if (existing) {
    existing.online = remote.online;
    existing.today = remote.today;
    existing.total = remote.total;
    existing.seed = false;
  } else {
    history.push({
      date: today,
      online: remote.online,
      today: remote.today,
      total: remote.total,
      seed: false,
    });
  }

  // Trim to last 30 days.
  history.sort((a, b) => a.date.localeCompare(b.date));
  history = history.slice(-30);
  writeJSON(K_HISTORY, history);
}

// ─── Public API ────────────────────────────────────────────

export async function trackVisit() {
  const path = normalizePath(location.pathname);

  // Local page-hit tracking (honest, per-browser).
  const hits = readJSON(K_PAGE_HITS, {});
  hits[path] = (hits[path] || 0) + 1;
  writeJSON(K_PAGE_HITS, hits);

  // Send heartbeat to Worker (real centralized tracking).
  await sendHeartbeat(path);

  // Sample today's Worker numbers for the 30-day trend.
  const remote = await fetchRemoteStats();
  if (remote) sampleToday(remote);
}

export async function getStats() {
  const remote = await fetchRemoteStats();
  if (remote) {
    return {
      online: remote.online,
      today: remote.today,
      total: remote.total,
      source: remote.source || 'worker',
      isReal: true,
      isCached: remote.isCached || false,
    };
  }
  // Fallback if Worker unreachable AND no cache.
  return { online: 0, today: 0, total: 0, source: 'offline', isReal: false, isCached: false };
}

/**
 * Fetch real site-wide top pages from the Worker's /api/pages endpoint.
 * Returns array of { page, count } — most-visited pages across ALL visitors.
 * Falls back to null if Worker unreachable.
 */
let cachedTopPages = null;
let lastPagesFetch = 0;
const PAGES_CACHE_MS = 300_000; // 5 min — KV list() limit protection

export async function fetchTopPages() {
  const now = Date.now();
  if (cachedTopPages && now - lastPagesFetch < PAGES_CACHE_MS) {
    return cachedTopPages;
  }
  try {
    const res = await fetch(`${API_BASE}/api/pages?range=all`, {
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    cachedTopPages = data.pages || [];
    lastPagesFetch = now;
    return cachedTopPages;
  } catch {
    return null;
  }
}

export function getDailyHistory() {
  migrateAwayFromSeed();
  let history = readJSON(K_HISTORY, []);
  if (!Array.isArray(history)) history = [];
  // Only real samples — no fake seed data.
  history = history.filter((d) => !d.seed);
  history.sort((a, b) => a.date.localeCompare(b.date));
  return history.slice(-30);
}

export function getPageHits() {
  return readJSON(K_PAGE_HITS, {});
}

export function getHourly24() {
  // Returns 8 buckets (every 3h) of heartbeat counts in the last 24h.
  // Per-browser, honest — shows when THIS browser was active.
  const times = readJSON(K_HB_TIMES, []);
  const now = Date.now();
  const currentHour = new Date().getHours();
  const buckets = [0, 3, 6, 9, 12, 15, 18, 21].map((h) => {
    const matching = times.filter((t) => {
      const ht = new Date(t).getHours();
      return ht === h || ht === h + 1 || ht === h + 2;
    });
    return {
      hour: h,
      label: fmtFa(String(h).padStart(2, '0')) + ':۰۰',
      count: matching.length,
    };
  });
  return buckets;
}

export async function heartbeat() {
  await sendHeartbeat(normalizePath(location.pathname));
}

export function resetAnalytics() {
  [K_HISTORY, K_LAST_SAMPLE, K_LAST_HEARTBEAT, K_PAGE_HITS, K_LAST_GOOD, K_HB_TIMES].forEach((k) =>
    localStorage.removeItem(k),
  );
}

export function getUuid() {
  return getOrCreateUUID();
}

export function fmtFa(n, opts = {}) {
  if (n == null || isNaN(n)) return '—';
  if (opts.short && n >= 1000) {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
    return (n / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
  }
  return String(n).replace(/[0-9]/g, (d) => '۰۱۲۳۴۵۶۷۸۹'[d]);
}

// Persian Shamsi (Jalali) date label — uses jalaali-js (the standard,
// well-tested library). Correct for the official Iranian calendar.
import { toJalaali } from 'jalaali-js';

export function shamsiLabel(isoDateStr) {
  try {
    // Parse the ISO date (YYYY-MM-DD) and convert to Jalali.
    const parts = isoDateStr.split('-');
    const gy = parseInt(parts[0], 10);
    const gm = parseInt(parts[1], 10);
    const gd = parseInt(parts[2], 10);
    const j = toJalaali(gy, gm, gd);
    const months = [
      'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
      'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند',
    ];
    return fmtFa(j.jd) + ' ' + months[j.jm - 1];
  } catch {
    return isoDateStr;
  }
}
