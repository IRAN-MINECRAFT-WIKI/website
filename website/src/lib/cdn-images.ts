/**
 * MineBed CDN image URLs — HuggingFace dataset (unlimited bandwidth).
 *
 * Repo: https://huggingface.co/datasets/Habib91700/minebed-assets
 * URL pattern: https://huggingface.co/datasets/Habib91700/minebed-assets/resolve/main/{dir}/{id}.png
 *
 * Also falls back to ccvaults.com (mcicons CDN) for items not yet on HF.
 */
import MCIcons from '@klashdevelopment/mcicons';

const HF_BASE = 'https://huggingface.co/datasets/Habib91700/minebed-assets/resolve/main';

const mc = MCIcons;

// Build ccvaults lookup (fallback) — same as before, $ → %24
function buildCdnLookup(category: Record<string, {high_url: string}>): Record<string, string> {
  const lookup: Record<string, string> = {};
  for (const [key, val] of Object.entries(category)) {
    const clean = key.replace(/\.webp$/, '').replace(/\.png$/, '');
    if (clean[0] === clean[0].toUpperCase() && clean[0] !== clean[0].toLowerCase()) {
      const kebab = clean.toLowerCase().replace(/_/g, '-');
      if (!lookup[kebab]) lookup[kebab] = val.high_url.replace(/\$/g, '%24');
    }
  }
  return lookup;
}

const ccvaultsBlocks = buildCdnLookup(mc.blocks);
const ccvaultsMobs = buildCdnLookup(mc.mobs);
const ccvaultsItems = buildCdnLookup(mc.items);

// HuggingFace URL helpers
export function blockImgUrl(id: string): string | null {
  // Try HuggingFace first (flat textures), then ccvaults (3D render), then null
  const kebab = id.replace(/^px-/, '').replace(/-face$/, '');
  return `${HF_BASE}/blocks/${kebab}.png`;
}

export function blockRenderUrl(id: string): string | null {
  const kebab = id.replace(/^px-/, '').replace(/-face$/, '');
  // Try HF render first, then ccvaults
  return `${HF_BASE}/blocks-render/${kebab}.png`;
}

export function mobImgUrl(id: string): string | null {
  const kebab = id.replace(/^px-/, '').replace(/-face$/, '');
  return `${HF_BASE}/mobs/${kebab}.png`;
}

export function mobRenderUrl(id: string): string | null {
  const kebab = id.replace(/^px-/, '').replace(/-face$/, '');
  return `${HF_BASE}/mobs-render/${kebab}.png`;
}

export function itemImgUrl(id: string): string | null {
  const kebab = id.replace(/^px-/, '').replace(/-face$/, '');
  return `${HF_BASE}/items/${kebab}.png`;
}

export function itemRenderUrl(id: string): string | null {
  const kebab = id.replace(/^px-/, '').replace(/-face$/, '');
  return `${HF_BASE}/items-render/${kebab}.png`;
}

export function uiImgUrl(id: string): string {
  return `${HF_BASE}/ui/${id}.png`;
}

// ccvaults fallback (for items not yet on HF)
export function ccvaultsBlock(id: string): string | null { return ccvaultsBlocks[id] || null; }
export function ccvaultsMob(id: string): string | null { return ccvaultsMobs[id] || null; }
export function ccvaultsItem(id: string): string | null { return ccvaultsItems[id] || null; }

export { HF_BASE };
