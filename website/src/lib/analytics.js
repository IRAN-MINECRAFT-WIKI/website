// src/lib/analytics.js
// Client-side analytics for MineBed — no backend, no third-party JS.
//
// What this tracks (all stored in the browser's own localStorage):
//   • Per-day visit counts (last 30 days) — for the 30-day bar chart.
//   • Per-hour visit counts for today — for the 24-hour line chart.
//   • Top pages — a small hardcoded list of "interesting" pages with
//     locally-tracked hit counts per page.
//   • Total visits all-time — a single running counter.
//   • Online users — simulated (random between 50-200) since we have
//     no shared backend. The simulation seeds off the day-of-year so
//     the number is stable within a single day (doesn't jitter every
//     refresh), but changes day-to-day.
//
// Privacy:
//   • NO cross-origin requests, NO cookies sent.
//   • All data lives in this browser only. A user visiting from a
//     different browser/device is a fresh counter.
//   • Reset by clearing site data — there's a "reset analytics" button
//     on /stats.

import { getOrCreateUUID } from './uuid.js';

const K_VISITS_BY_DAY = 'mb:stats:visitsByDay'; // JSON: { "2026-09-28": N }
const K_VISITS_BY_HOUR = 'mb:stats:visitsByHour'; // JSON: { "14": N } — only for today
const K_VISITS_BY_HOUR_DATE = 'mb:stats:visitsByHourDate'; // string date for which the hour map is valid
const K_PAGE_HITS = 'mb:stats:pageHits'; // JSON: { "/seeds": N, "/mods": N }
const K_TOTAL = 'mb:stats:total'; // string number
const K_LAST_SEEN = 'mb:stats:lastSeen'; // ms timestamp — for "online" simulation

// Hardcoded "top pages" list — taken from the sitemap.
// Used so the Top Pages chart always has a meaningful baseline even
// before the user has visited every page.
const SEED_PAGES = [
  { path: '/', label: 'خانه' },
  { path: '/mods', label: 'افزونه‌ها' },
  { path: '/seeds', label: 'سیدها' },
  { path: '/versions', label: 'نسخه‌ها' },
  { path: '/categories', label: 'دسته‌ها' },
  { path: '/blog', label: 'وبلاگ' },
  { path: '/wiki', label: 'ویکی' },
  { path: '/tutorials', label: 'آموزش‌ها' },
  { path: '/speedrun', label: 'سرعت‌رانی' },
  { path: '/crafting', label: 'کرافتینگ' },
];

const MAX_DAYS = 30;
const MAX_PAGES = 12;

// ============================================================
// Helpers
// ============================================================

function safeGet(key, fallback) {
  try {
    const v = localStorage.getItem(key);
    return v === null ? fallback : JSON.parse(v);
  } catch {
    return fallback;
  }
}

function safeSet(key, val) {
  try {
    localStorage.setItem(key, JSON.stringify(val));
  } catch {}
}

function ymd(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

// ============================================================
// trackVisit — call on every page load
// ============================================================

/**
 * Tracks a visit on the current page. Updates day/hour/total/page counters.
 * Safe to call multiple times per page (subsequent calls within the same
 * minute are de-duplicated to avoid inflating numbers on View Transitions
 * or rapid in-page navigation).
 *
 * @param {string} [pagePath] — current pathname (defaults to location.pathname).
 *   The Astro site is served from the project-page base `/website/`, so
 *   `/website/seeds/create` is normalized to `/seeds/create` so it matches
 *   the SEED_PAGES list and looks clean in the Top Pages chart.
 */
export function trackVisit(pagePath) {
  if (typeof localStorage === 'undefined') return;

  const now = new Date();
  let path = pagePath || (typeof location !== 'undefined' ? location.pathname : '/');
  path = normalizePath(path);

  // De-duplicate: ignore if same path was tracked in the last 60s
  const lastPath = safeGet('mb:stats:lastPath', '');
  const lastTs = safeGet('mb:stats:lastPathTs', 0);
  if (lastPath === path && now.getTime() - lastTs < 60_000) {
    // Still update heartbeat so "online" badge reflects activity
    safeSet(K_LAST_SEEN, now.getTime());
    return;
  }
  safeSet('mb:stats:lastPath', path);
  safeSet('mb:stats:lastPathTs', now.getTime());

  // 1. Today's counter
  const byDay = safeGet(K_VISITS_BY_DAY, {});
  const todayKey = ymd(now);
  byDay[todayKey] = (byDay[todayKey] || 0) + 1;
  // Trim anything older than 30 days
  trimOldDays(byDay, now);
  safeSet(K_VISITS_BY_DAY, byDay);

  // 2. Today's hour bucket
  const hourDateKey = ymd(now);
  const storedHourDate = safeGet(K_VISITS_BY_HOUR_DATE, '');
  let byHour = safeGet(K_VISITS_BY_HOUR, {});
  if (storedHourDate !== hourDateKey) {
    // Reset hour buckets for a new day
    byHour = {};
    safeSet(K_VISITS_BY_HOUR_DATE, hourDateKey);
  }
  const h = String(now.getHours());
  byHour[h] = (byHour[h] || 0) + 1;
  safeSet(K_VISITS_BY_HOUR, byHour);

  // 3. Page hits
  const pageHits = safeGet(K_PAGE_HITS, {});
  pageHits[path] = (pageHits[path] || 0) + 1;
  safeSet(K_PAGE_HITS, pageHits);

  // 4. Total
  const total = parseInt(safeGet(K_TOTAL, '0'), 10);
  safeSet(K_TOTAL, String(total + 1));

  // 5. Heartbeat
  safeSet(K_LAST_SEEN, now.getTime());

  // Ensure UUID is created
  getOrCreateUUID();
}

function trimOldDays(byDay, now) {
  const cutoff = new Date(now);
  cutoff.setDate(cutoff.getDate() - MAX_DAYS);
  for (const key of Object.keys(byDay)) {
    // key is "YYYY-MM-DD"
    const [y, m, d] = key.split('-').map(Number);
    const dt = new Date(y, m - 1, d);
    if (dt < cutoff) delete byDay[key];
  }
}

/**
 * Normalize a page path so the GitHub Pages project-page base URL
 * (e.g. `/website/`) is stripped. Trailing slash is also removed so
 * `/seeds` and `/seeds/` collapse to the same key.
 */
function normalizePath(p) {
  // Hardcoded for the iran-minecraft-wiki.github.io/website/ project
  // page. Stripping the BASE_URL keeps paths short in the Top Pages
  // chart and matches the SEED_PAGES list.
  let s = String(p || '/');
  if (s.startsWith('/website/')) s = s.slice('/website'.length);
  if (s.length > 1 && s.endsWith('/')) s = s.slice(0, -1);
  if (s.length === 0) s = '/';
  return s;
}

// ============================================================
// getStats — read everything back for the /stats page
// ============================================================

export function getStats() {
  if (typeof localStorage === 'undefined') {
    return simulatedStats();
  }

  const now = new Date();
  const byDay = safeGet(K_VISITS_BY_DAY, {});
  const byHour = safeGet(K_VISITS_BY_HOUR, {});
  const pageHits = safeGet(K_PAGE_HITS, {});
  const total = parseInt(safeGet(K_TOTAL, '0'), 10);
  const lastSeen = safeGet(K_LAST_SEEN, 0);

  // Build 30-day series (oldest→newest)
  const last30 = [];
  for (let i = MAX_DAYS - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    const key = ymd(d);
    last30.push({
      date: key,
      label: `${d.getDate()}/${d.getMonth() + 1}`,
      count: byDay[key] || 0,
    });
  }

  // Build 24-hour series (00→23)
  const last24 = [];
  for (let h = 0; h < 24; h++) {
    const k = String(h);
    last24.push({
      hour: h,
      label: `${String(h).padStart(2, '0')}:00`,
      count: byHour[k] || 0,
    });
  }

  // Today's total
  const todayKey = ymd(now);
  const today = byDay[todayKey] || 0;

  // Top pages — merge SEED_PAGES (so chart always has rows) + actual hits
  const top = SEED_PAGES.map((p) => ({
    path: p.path,
    label: p.label,
    hits: pageHits[p.path] || 0,
  }));
  // Add any other paths the user has visited that aren't in the seed list
  for (const p of Object.keys(pageHits)) {
    if (!SEED_PAGES.find((s) => s.path === p)) {
      top.push({ path: p, label: p, hits: pageHits[p] });
    }
  }
  top.sort((a, b) => b.hits - a.hits);
  const topPages = top.slice(0, MAX_PAGES);

  return {
    total,
    today,
    online: simulateOnline(),
    last30,
    last24,
    topPages,
    lastSeen,
    uuid: getOrCreateUUID(),
  };
}

/**
 * Simulated stats (used on first visit / before any localStorage data
 * is collected, so the charts aren't all empty).
 */
function simulatedStats() {
  return {
    total: 234000,
    today: 3456,
    online: simulateOnline(),
    last30: [],
    last24: [],
    topPages: SEED_PAGES.map((p) => ({ path: p.path, label: p.label, hits: 0 })),
    lastSeen: 0,
    uuid: 'simulated',
  };
}

/**
 * Simulate online users — random between 50-200, stable within a day
 * (deterministic by day-of-year seed).
 */
function simulateOnline() {
  const now = new Date();
  const dayOfYear = Math.floor(
    (now - new Date(now.getFullYear(), 0, 0)) / 86_400_000
  );
  // Seed the day's number
  const dayBase = 60 + (dayOfYear % 80); // 60..139
  // Add a small intra-day variance (refreshes change the number a little
  // but the day-average stays stable)
  const hour = now.getHours();
  // Busier during evening hours (16-22) — peak shape
  const peakBoost = Math.round(40 * Math.sin(((hour - 4) / 24) * Math.PI));
  const noise = (Math.random() * 20 - 10) | 0;
  let n = dayBase + peakBoost + noise;
  if (n < 50) n = 50 + (Math.random() * 10) | 0;
  if (n > 200) n = 200 - (Math.random() * 10) | 0;
  return n;
}

/**
 * Heartbeat — call every N seconds so we can simulate "online" status.
 * Updates the lastSeen timestamp.
 */
export function heartbeat() {
  if (typeof localStorage === 'undefined') return;
  safeSet(K_LAST_SEEN, Date.now());
}

/**
 * Reset all analytics data (Privacy panel button).
 */
export function resetAnalytics() {
  if (typeof localStorage === 'undefined') return;
  [
    K_VISITS_BY_DAY,
    K_VISITS_BY_HOUR,
    K_VISITS_BY_HOUR_DATE,
    K_PAGE_HITS,
    K_TOTAL,
    K_LAST_SEEN,
    'mb:stats:lastPath',
    'mb:stats:lastPathTs',
  ].forEach((k) => {
    try {
      localStorage.removeItem(k);
    } catch {}
  });
}

/**
 * Format a number as Persian digits with thousands separator.
 * e.g. 3456 → "۳٬۴۵۶", 234000 → "۲۳۴K" (when called with short=true)
 */
export function fmtFa(n, opts = {}) {
  if (typeof n !== 'number' || isNaN(n)) n = 0;
  if (opts.short && n >= 1000) {
    if (n >= 1_000_000) {
      const v = (n / 1_000_000).toFixed(1).replace(/\.0$/, '');
      return toFa(v) + 'M';
    }
    const v = Math.round(n / 1000);
    return toFa(String(v)) + 'K';
  }
  // Full number with Persian digits + Arabic thousands separator
  const withSep = Math.round(n).toLocaleString('en-US');
  return toFa(withSep);
}

function toFa(s) {
  const fa = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  return String(s).replace(/[0-9]/g, (d) => fa[+d]).replace(/,/g, '٬');
}
