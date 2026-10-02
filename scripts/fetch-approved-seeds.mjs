#!/usr/bin/env node
// scripts/fetch-approved-seeds.mjs
//
// Pulls approved seeds from PocketBase and writes them as a static
// JSON file that the Astro site imports at build time.
//
// Why a static JSON (and not a fetch at page-load):
//   • Page weight — the published seeds page must stay light; an
//     in-browser fetch to PocketBase adds ~200ms on cold cache and
//     ties the page to the backend's uptime.
//   • SEO — Google's crawler doesn't run JS long enough to wait for
//     a fetch; the data has to be in the HTML at SSG time.
//   • Privacy — no third-party domain in the browser's network log
//     of /seeds visitors.
//
// Error handling:
//   This script NEVER deletes the existing output file on failure.
//   If the fetch dies mid-way, the existing JSON is preserved so the
//   site keeps serving the last-known-good list. The script exits 0
//   on fetch failure (so the GitHub Action step still "succeeds" and
//   the "commit if changed" step no-ops gracefully) — non-zero exit
//   would only happen on truly unrecoverable errors (no env vars
//   configured, output dir missing).
//
// Usage:
//   node scripts/fetch-approved-seeds.mjs
//
// Env vars:
//   PB_URL            — e.g. https://minebed-pb.fly.dev   (REQUIRED)
//   PB_ADMIN_TOKEN    — admin JWT from /api/admins/auth-with-password  (REQUIRED)
//   OUTPUT_PATH       — defaults to website/src/data/seeds-published.json
//   PB_PAGE_SIZE      — defaults to 500 (PocketBase max)
//   PB_TIMEOUT_MS     — defaults to 15000

import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PB_URL = (process.env.PB_URL || '').replace(/\/+$/, '');
const PB_ADMIN_TOKEN = process.env.PB_ADMIN_TOKEN || '';
const OUTPUT_PATH = process.env.OUTPUT_PATH || path.join(__dirname, '..', 'website', 'src', 'data', 'seeds-published.json');
const PAGE_SIZE = parseInt(process.env.PB_PAGE_SIZE || '500', 10);
const TIMEOUT_MS = parseInt(process.env.PB_TIMEOUT_MS || '15000', 10);

// ============================================================
// Helpers
// ============================================================

function log(msg) {
  const ts = new Date().toISOString();
  console.log(`[fetch-approved-seeds ${ts}] ${msg}`);
}

function warn(msg) {
  const ts = new Date().toISOString();
  console.warn(`[fetch-approved-seeds ${ts}] WARN: ${msg}`);
}

function errOut(msg) {
  const ts = new Date().toISOString();
  console.error(`[fetch-approved-seeds ${ts}] ERROR: ${msg}`);
}

/**
 * Fetch with timeout. Returns the parsed JSON body, or throws on
 * non-2xx response. Aborts the request after TIMEOUT_MS so a hung
 * PocketBase server doesn't block the GitHub Action forever.
 */
async function fetchJSON(url, headers = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      headers,
      signal: controller.signal,
    });
    if (!res.ok) {
      const body = await res.text().catch(() => '');
      throw new Error(`HTTP ${res.status} ${res.statusText} — ${body.slice(0, 500)}`);
    }
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Paginate through PocketBase records from a collection.
 *
 * PocketBase list endpoint returns:
 *   { "page": N, "perPage": M, "totalItems": T, "totalPages": P, "items": [...] }
 *
 * We auto-page until we've seen every row, sleeping 100ms between
 * requests to be polite to the server (the daily Action run has no
 * deadline pressure).
 *
 * Returns the full items[] array concatenated in API order (oldest
 * first by `created`). The caller sorts by published_at afterwards.
 */
async function listAll(collection, filter = '') {
  const all = [];
  let page = 1;
  let totalPages = 1;
  const headers = {
    'Accept': 'application/json',
  };
  if (PB_ADMIN_TOKEN) {
    headers['Authorization'] = `Bearer ${PB_ADMIN_TOKEN}`;
  }
  do {
    const params = new URLSearchParams({
      page: String(page),
      perPage: String(PAGE_SIZE),
      sort: '-published_at,-created',
    });
    if (filter) params.set('filter', filter);
    const url = `${PB_URL}/api/collections/${collection}/records?${params.toString()}`;
    log(`GET ${url}`);
    const body = await fetchJSON(url, headers);
    if (!Array.isArray(body.items)) {
      throw new Error(`Unexpected response shape — no items[] array. Got: ${JSON.stringify(body).slice(0, 300)}`);
    }
    all.push(...body.items);
    totalPages = body.totalPages || 1;
    log(`  page ${body.page}/${totalPages} — got ${body.items.length} items (total ${body.totalItems})`);
    page++;
    if (page <= totalPages) {
      await new Promise((r) => setTimeout(r, 100));
    }
  } while (page <= totalPages);
  return all;
}

/**
 * Map a PocketBase seeds_published row → the shape the Astro site
 * expects in src/data/seeds.json. Keeps the field names consistent
 * so the existing /seeds page components don't need to learn two
 * data sources.
 */
function mapToSiteSchema(row) {
  // features + coordinates are JSON strings on the wire (PocketBase
  // json fields come back as parsed objects when fetched via the
  // REST API). We pass them through unchanged.
  let features = row.features;
  if (typeof features === 'string') {
    try { features = JSON.parse(features); } catch { features = []; }
  }
  let coordinates = row.coordinates;
  if (typeof coordinates === 'string') {
    try { coordinates = JSON.parse(coordinates); } catch { coordinates = []; }
  }

  // The site uses a slug field as the URL key — derive from seed_value
  // + platform + version so duplicates are impossible (each natural
  // key only appears once in seeds_published thanks to the upsert
  // hook).
  const slug = [
    String(row.seed_value || 'seed').replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 18),
    String(row.platform || 'p').toLowerCase(),
    String(row.version || 'v').replace(/\./g, '-'),
  ].join('-').toLowerCase();

  return {
    id: slug,
    code: row.seed_value,
    version: row.version,
    platform: (row.platform || 'Bedrock').toLowerCase(),
    features: features || [],
    coordinates: coordinates || [],
    user_uuid: row.user_uuid || '',
    tested_by_admin: row.tested_by_admin || false,
    published_at: row.published_at || row.created || new Date().toISOString(),
    published_by: row.published_by || 'admin',
    // Synthetic fields the existing site schema expects — kept empty
    // so the /seeds page components don't break:
    nameFa: row.seed_value ? `سید ${row.seed_value.slice(0, 12)}` : 'سید نامشخص',
    tagline: buildTagline(features || [], row.platform, row.version),
    icon: '🌱',
    category: deriveCategory(features || []),
    biome: null,
    rating: 0,
    featured: false,
    isNew: true,
  };
}

function buildTagline(features, platform, version) {
  const feats = Array.isArray(features) ? features : [];
  const names = feats.map((f) => {
    if (typeof f === 'string') return f;
    return f?.label || f?.feature || f?.id || '';
  }).filter(Boolean);
  const head = names.slice(0, 3).join('، ');
  const extra = names.length > 3 ? ` و ${names.length - 3} مورد دیگر` : '';
  const tail = ` — MC ${version} ${platform}`;
  return (head || 'سید منتشر شده') + extra + tail;
}

function deriveCategory(features) {
  const feats = Array.isArray(features) ? features : [];
  const ids = feats.map((f) => (typeof f === 'string' ? f : f?.id || f?.feature || ''))
    .filter(Boolean);
  if (ids.some((id) => /stronghold|end-city|nether-fortress/i.test(id))) return 'structures';
  if (ids.some((id) => /village|ancient-city/i.test(id))) return 'spawn';
  return 'resources';
}

/**
 * Atomic write — never overwrite the existing file with partial data
 * if anything below this point throws. We write to a tmp path then
 * rename, so a SIGKILL mid-write leaves the old file intact.
 */
async function atomicWriteJSON(targetPath, data) {
  const dir = path.dirname(targetPath);
  await fs.mkdir(dir, { recursive: true });
  const tmp = `${targetPath}.tmp.${process.pid}`;
  await fs.writeFile(tmp, JSON.stringify(data, null, 2) + '\n', 'utf8');
  await fs.rename(tmp, targetPath);
}

/**
 * Preserve the existing file by reading its contents and returning
 * them so the caller can decide whether to fall back to them.
 */
async function readExisting(path_) {
  try {
    const raw = await fs.readFile(path_, 'utf8');
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

// ============================================================
// Main
// ============================================================

async function main() {
  log(`OUTPUT_PATH = ${OUTPUT_PATH}`);
  log(`PB_URL     = ${PB_URL || '(empty)'}`);
  log(`token set? = ${PB_ADMIN_TOKEN ? 'yes' : 'no'}`);

  if (!PB_URL) {
    errOut('PB_URL env var is not set. Nothing to fetch — bailing.');
    process.exit(1);
  }
  if (!PB_ADMIN_TOKEN) {
    warn('PB_ADMIN_TOKEN is empty — will attempt anonymous fetch (likely to fail on admin-only collection).');
  }

  // 1. Try seeds_published (the canonical source).
  let seeds = [];
  let source = '';
  try {
    const rows = await listAll('seeds_published');
    source = 'seeds_published';
    seeds = rows.map(mapToSiteSchema);
    log(`Fetched ${seeds.length} rows from seeds_published.`);
  } catch (e) {
    warn(`Could not fetch from seeds_published: ${e.message}`);
    warn('Falling back to seeds_queue with filter: status="approved" (rows approved but not yet copied).');
    try {
      const rows = await listAll('seeds_queue', 'status="approved"');
      source = 'seeds_queue[approved]';
      seeds = rows.map((r) => {
        // seeds_queue doesn't have published_at/published_by — synthesize them.
        r.published_at = r.updated || r.created || new Date().toISOString();
        r.published_by = 'admin';
        return mapToSiteSchema(r);
      });
      log(`Fetched ${seeds.length} rows from seeds_queue (approved).`);
    } catch (e2) {
      errOut(`Both sources failed. seeds_published: ${e.message} | seeds_queue fallback: ${e2.message}`);
      const existing = await readExisting(OUTPUT_PATH);
      if (existing) {
        log(`Preserving existing output (${Array.isArray(existing) ? existing.length : Object.keys(existing).length} entries) — no write.`);
        process.exit(0);
      }
      errOut('No existing output file to preserve. Writing an empty array so the site still builds.');
      await atomicWriteJSON(OUTPUT_PATH, { items: [], fetched_at: new Date().toISOString(), source: 'error' });
      process.exit(0);
    }
  }

  // 2. Sort newest-first by published_at (string comparison works on ISO datetimes).
  seeds.sort((a, b) => String(b.published_at).localeCompare(String(a.published_at)));

  // 3. Wrap in a metadata envelope so the consuming code knows when
  //    the data was last refreshed and where it came from.
  const output = {
    items: seeds,
    fetched_at: new Date().toISOString(),
    source,
    count: seeds.length,
  };

  // 4. Compare with the existing file (so we can skip the commit if
  //    nothing changed). We compare by `code+version+platform` keys
  //    only — published_at will tick on every re-fetch, but that's
  //    metadata, not a real change.
  const existing = await readExisting(OUTPUT_PATH);
  if (existing) {
    const oldKeys = new Set((existing.items || []).map((s) => `${s.code}|${s.version}|${s.platform}`));
    const newKeys = new Set(seeds.map((s) => `${s.code}|${s.version}|${s.platform}`));
    const same = oldKeys.size === newKeys.size && [...newKeys].every((k) => oldKeys.has(k));
    if (same && existing.count === seeds.length) {
      log('No seed set changes since last run — keeping existing file as-is (published_at metadata will refresh on next real change).');
      // Still update fetched_at so a curious admin can see when the
      // last successful fetch ran. This WILL produce a git diff but
      // only on the timestamp line — acceptable noise.
      await atomicWriteJSON(OUTPUT_PATH, output);
      log('Wrote updated fetched_at timestamp.');
      process.exit(0);
    }
  }

  // 5. Atomic write.
  await atomicWriteJSON(OUTPUT_PATH, output);
  log(`Wrote ${seeds.length} seeds to ${OUTPUT_PATH}.`);
  process.exit(0);
}

main().catch((e) => {
  errOut(`Uncaught: ${e?.stack || e?.message || e}`);
  process.exit(1);
});
