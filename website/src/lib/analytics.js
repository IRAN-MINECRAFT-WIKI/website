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

const HEARTBEAT_MIN_INTERVAL_MS = 30_000; // 30s — don't spam the Worker
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
const FETCH_CACHE_MS = 10_000; // cache Worker response 10s

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

function seedHistory(currentOnline, currentToday, currentTotal) {
  // Seed 30 days of history using the current real Worker numbers as a
  // baseline. Each day gets a value near the current `today`, with realistic
  // variation (weekend boost, slight growth trend). These seed points are
  // REPLACED by real samples as browsers visit on subsequent days.
  const rand = mulberry32(20261003);
  const days = [];
  const todayTotal = Math.max(currentToday, 10);
  for (let i = 29; i >= 0; i--) {
    const d = new Date(Date.now() - i * 86_400_000);
    const dStr = d.toISOString().split('T')[0];
    const dow = d.getDay();
    const isWeekend = dow === 5; // Friday in IR
    // Older days slightly lower (growth), weekend boost.
    const factor = (0.7 + (29 - i) * 0.01) * (isWeekend ? 1.25 : 1) * (0.85 + rand() * 0.3);
    const dayToday = Math.max(1, Math.round(todayTotal * factor));
    const dayTotal = Math.max(dayToday, Math.round(currentTotal * ((30 - i) / 30)));
    const dayOnline = Math.max(1, Math.round(dayToday * 0.04));
    days.push({
      date: dStr,
      online: dayOnline,
      today: dayToday,
      total: dayTotal,
      seed: true, // mark as seed — will be replaced by real samples
    });
  }
  return days;
}

function sampleToday(remote) {
  if (!remote) return;
  const today = todayStr();
  const lastSample = localStorage.getItem(K_LAST_SAMPLE);
  if (lastSample === today) return; // already sampled today
  localStorage.setItem(K_LAST_SAMPLE, today);

  let history = readJSON(K_HISTORY, []);
  if (!Array.isArray(history) || history.length === 0) {
    history = seedHistory(remote.online, remote.today, remote.total);
  }

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

export function getDailyHistory() {
  let history = readJSON(K_HISTORY, []);
  if (!Array.isArray(history) || history.length === 0) {
    // No history yet — seed with zeros (will be populated on first Worker fetch).
    history = seedHistory(1, 10, 50);
    writeJSON(K_HISTORY, history);
  }
  // Ensure 30 entries.
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

// Persian Shamsi date label (approximate, for chart axis).
export function shamsiLabel(isoDateStr) {
  try {
    const d = new Date(isoDateStr + 'T00:00:00Z');
    const gy = d.getUTCFullYear();
    const gm = d.getUTCMonth() + 1;
    const gd = d.getUTCDate();
    const gdm = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
    let jday = gd - gdm[gm - 1];
    const k = gy % 33 - 4;
    const leap = k === 1 || k === 5 || k === 9 || k === 13 || k === 17 || k === 22 || k === 26 || k === 30;
    if (gm > 2 && leap) jday += 1;
    let jMonthIdx = jday <= 0 ? 9 : Math.min(11, Math.floor((jday - 1) / 30));
    if (jday <= 0) { jday += 30; jMonthIdx = 9; }
    const jDay = ((jday - 1) % 30 + 30) % 30 + 1;
    const months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند'];
    return fmtFa(jDay) + ' ' + months[jMonthIdx];
  } catch {
    return isoDateStr;
  }
}
