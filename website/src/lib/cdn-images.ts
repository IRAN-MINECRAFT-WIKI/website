/**
 * lib/cdn-images.ts — CDN URL lookups for Minecraft block/mob/item renders.
 *
 * Why: GitHub Pages has strict bandwidth limits (~100 GB/month soft cap).
 * Storing ~1000 PNG/WEBP render files in git would burn that cap fast.
 * Instead, we resolve the ccvaults.com CDN URLs at build time via the
 * `@klashdevelopment/mcicons` package and emit absolute CDN URLs in the
 * rendered HTML. The local *-render/ directories remain git-ignored but
 * available for dev/testing fallback.
 *
 * Usage (Astro frontmatter):
 *   import { blockImgUrl, mobImgUrl, itemImgUrl } from '@/lib/cdn-images';
 *   const cdn = blockImgUrl('diamond-block'); // or null
 *
 * The lookup keys are kebab-case IDs (e.g. "diamond-block", "creeper",
 * "diamond-sword") — matching the convention used in /src/data/blocks/*.json
 * and crafting-recipes.json. The mcicons package exposes Title_Case keys
 * (e.g. "Diamond_Block", "Creeper", "Diamond_Sword"); we normalize them
 * to kebab at build time.
 */
import MCIcons from '@klashdevelopment/mcicons';

// The mcicons package exports a default object with `.blocks`, `.mobs`,
// `.items` categories. Each entry has shape `{ low_url, high_url, path }`.
const mc = MCIcons as {
  blocks: Record<string, { high_url?: string }>;
  mobs: Record<string, { high_url?: string }>;
  items: Record<string, { high_url?: string }>;
};

/** Convert a Title_Case or snake_case name to kebab-case. */
const toKebab = (s: string): string => s.toLowerCase().replace(/_/g, '-');

/**
 * Build a kebab-case → CDN URL lookup map for one mcicons category.
 * Strips trailing `.webp`/`.png` from the package's key names (some keys
 * in `mc.mobs` end with `.webp`, e.g. `"Allay.webp"`). First occurrence
 * wins (Title_Case keys tend to come first in insertion order).
 *
 * URL fix: mcicons emits mob URLs with a literal `$` in the path
 * (e.g. `https://ccvaults.com/assets/15.$%20Mobs/.../Creeper.webp`).
 * The ccvaults.com server 302-redirects that to `/` (returns HTML, not
 * the image). URL-encoding `$` as `%24` makes the server return the real
 * image bytes with Content-Type: image/webp. We apply this fix here so
 * every consumer of the lookup gets a working URL.
 */
function buildLookup(
  category: Record<string, { high_url?: string }>,
  toKebabFn: (name: string) => string
): Record<string, string> {
  const lookup: Record<string, string> = {};
  for (const [key, val] of Object.entries(category || {})) {
    if (!val || !val.high_url) continue;
    const clean = key.replace(/\.webp$/, '').replace(/\.png$/, '');
    const kebab = toKebabFn(clean);
    if (!lookup[kebab]) {
      // Encode bare `$` → `%24` (ccvaults.com needs this for mob URLs).
      lookup[kebab] = val.high_url.replace(/\$/g, '%24');
    }
  }
  return lookup;
}

export const blockCdnUrls: Record<string, string> = buildLookup(mc.blocks, toKebab);
export const mobCdnUrls: Record<string, string> = buildLookup(mc.mobs, toKebab);
export const itemCdnUrls: Record<string, string> = buildLookup(mc.items, toKebab);

/** Resolve a kebab-case block ID (e.g. "diamond-block") to a ccvaults.com CDN URL, or null. */
export function blockImgUrl(id: string): string | null {
  if (!id) return null;
  return blockCdnUrls[id] || null;
}

/** Resolve a kebab-case mob ID (e.g. "iron-golem") to a ccvaults.com CDN URL, or null. */
export function mobImgUrl(id: string): string | null {
  if (!id) return null;
  return mobCdnUrls[id] || null;
}

/** Resolve a kebab-case item ID (e.g. "diamond-sword") to a ccvaults.com CDN URL, or null. */
export function itemImgUrl(id: string): string | null {
  if (!id) return null;
  return itemCdnUrls[id] || null;
}
