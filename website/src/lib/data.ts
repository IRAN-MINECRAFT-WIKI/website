/**
 * lib/data.ts — Central data loader for MineBed Astro site
 *
 * Loads mods, seeds, versions, categories and exposes helpers
 * used across all pages. Data is statically imported so Astro can
 * tree-shake at build time (no runtime fetching).
 */
import modsRaw from '@/data/mods.json';
import seedsRaw from '@/data/seeds.json';
import versionsRaw from '@/data/versions.json';
import seedsTestedRaw from '@/data/seeds-tested.json';
import categoriesRaw from '@/data/categories.json';
import musicRaw from '@/data/music.json';

export type Mod = {
  id: string;
  name: string;
  nameFa: string;
  keywords?: string;
  category: string;
  catName?: string;
  tagline: string;
  desc: string;
  icon?: string;
  version?: string;
  size?: string;
  downloads?: string;
  downloadUrl: string;
  cover?: string;
  gallery?: string[];
  featured?: boolean;
  isNew?: boolean;
  author?: string;
  updated?: string;
};

export type Seed = {
  id: string;
  name: string;
  nameFa: string;
  code: string;
  version: string;
  category: string;
  catName?: string;
  icon?: string;
  tagline: string;
  description: string;
  biome?: string;
  structures?: string[];
  screenshots?: string[];
  author?: string;
  downloads?: number;
  rating?: number;
  isNew?: boolean;
  featured?: boolean;
  updated?: string;
};

export type MCVersion = {
  id: string;
  version?: string;
  name: string;
  nameFa: string;
  releaseDate: string;
  codename: string;
  major: number;
  minor: number;
  icon: string;
  summary: string;
  description: string;
  highlights: string[];
  compatibleMods: number;
  platform?: 'java' | 'bedrock';
  isLatest?: boolean;
  featured?: boolean;
  wikiLink?: string;
};

export type TestedSeedCoordinate = {
  name: string;
  x: number | string;
  y?: number | string;
  z?: number | string;
};

export type TestedSeed = {
  id: string;
  seed: string;
  version: string;
  platform: 'java' | 'bedrock';
  category: 'survival' | 'speedrun' | 'beautiful' | 'rare' | 'island' | 'challenge';
  name: string;
  description: string;
  coordinates?: TestedSeedCoordinate[];
  features?: string[];
  rating: number;
  source?: string;
  chunkbaseLink?: string;
};

export type Category = {
  id: string;
  name: string;
  nameEn: string;
  icon: string;
  color: string;
  description: string;
};

export type MusicTrack = {
  title: string;
  src: string;
};

export const mods: Mod[] = (modsRaw as { mods: Mod[] }).mods;
export const seeds: Seed[] = (seedsRaw as { seeds: Seed[] }).seeds;
export const testedSeeds: TestedSeed[] = (seedsTestedRaw as { seeds?: TestedSeed[] }).seeds ?? [];

// Versions are stored in two arrays (java + bedrock). The flat `versions`
// export keeps backwards-compatibility with existing pages that iterate
// over a single list — newest-first by release date.
type VersionsFile = { java: MCVersion[]; bedrock: MCVersion[] };
const parsedVersions = versionsRaw as unknown as VersionsFile;

export const javaVersions: MCVersion[] = parsedVersions.java ?? [];
export const bedrockVersions: MCVersion[] = parsedVersions.bedrock ?? [];

export const versions: MCVersion[] = [...javaVersions, ...bedrockVersions].sort((a, b) => {
  if (a.releaseDate < b.releaseDate) return 1;
  if (a.releaseDate > b.releaseDate) return -1;
  return 0;
});

export const categories: Category[] = (categoriesRaw as { categories: Category[] }).categories;
export const musicTracks: MusicTrack[] = (musicRaw as { tracks?: MusicTrack[] }).tracks ?? [];

// === Helpers ===

export function getModBySlug(slug: string): Mod | undefined {
  return mods.find((m) => m.id === slug);
}

export function getModsByCategory(catId: string): Mod[] {
  return mods.filter((m) => m.category === catId);
}

export function getModsByVersion(verId: string): Mod[] {
  // New versions have a `version` field (e.g. "1.21", "1.21.50", "26.3").
  // To match mods, we strip to the first two numeric parts (e.g. "1.21.50"
  // → "1.21") so Bedrock minor releases match the major Java release.
  const v = getVersionById(verId);
  let prefix = '';
  if (v && v.version) {
    const m = v.version.match(/^(\d+\.\d+)/);
    prefix = m ? m[1] : v.version;
  } else {
    // Backwards-compat fallback: legacy IDs like "1-21"
    prefix = verId.replace('-', '.');
  }
  return mods.filter((m) => (m.version || '').startsWith(prefix));
}

export function getFeaturedMods(): Mod[] {
  return mods.filter((m) => m.featured);
}

export function getNewMods(): Mod[] {
  return mods.filter((m) => m.isNew);
}

export function getCategoryById(id: string): Category | undefined {
  return categories.find((c) => c.id === id);
}

export function getSeedBySlug(slug: string): Seed | undefined {
  return seeds.find((s) => s.id === slug);
}

export function getVersionById(id: string): MCVersion | undefined {
  return versions.find((v) => v.id === id);
}

export function getLatestVersion(): MCVersion | undefined {
  return versions.find((v) => v.isLatest) || versions[0];
}

// Returns the latest version for a specific platform
export function getLatestVersionByPlatform(platform: 'java' | 'bedrock'): MCVersion | undefined {
  return (
    versions.find((v) => v.platform === platform && v.isLatest) ||
    versions.find((v) => v.platform === platform)
  );
}

export function getTestedSeedsByPlatform(platform: 'java' | 'bedrock'): TestedSeed[] {
  return testedSeeds.filter((s) => s.platform === platform);
}

export function getTestedSeedsByCategory(category: string): TestedSeed[] {
  return testedSeeds.filter((s) => s.category === category);
}

export function getTestedSeedsByVersion(version: string): TestedSeed[] {
  return testedSeeds.filter((s) => s.version === version);
}

export function getTestedSeedById(id: string): TestedSeed | undefined {
  return testedSeeds.find((s) => s.id === id);
}

export function searchTestedSeeds(query: string): TestedSeed[] {
  const q = query.trim().toLowerCase();
  if (!q) return testedSeeds;
  return testedSeeds.filter((s) =>
    [s.seed, s.name, s.description, s.version, ...(s.features || [])]
      .join(' ')
      .toLowerCase()
      .includes(q)
  );
}

export function getRelatedMods(mod: Mod, limit = 4): Mod[] {
  return mods
    .filter((m) => m.id !== mod.id && m.category === mod.category)
    .slice(0, limit);
}

export function searchMods(query: string): Mod[] {
  const q = query.trim().toLowerCase();
  if (!q) return mods;
  return mods.filter((m) => {
    const haystack = [
      m.name,
      m.nameFa,
      m.tagline,
      m.keywords || '',
      m.catName || '',
      m.author || '',
    ]
      .join(' ')
      .toLowerCase();
    return haystack.includes(q);
  });
}

// === Site config ===
export const siteConfig = {
  name: 'ماین بد (MineBed Farsi)',
  nameEn: 'MineBed Farsi',
  url: 'https://iran-minecraft-wiki.github.io',
  description: 'مرجع فارسی دانلود افزونه، مپ، ریسورس‌پک و سید ماینکرفت بدراک — تست‌شده، رایگان، بدون تبلیغات مزاحم',
  descriptionEn: 'Persian hub for Minecraft Bedrock mods, maps, resource packs, seeds, version guides & tutorials — tested, free, no annoying ads.',
  locale: 'fa_IR',
  localeAlt: 'en_US',
  twitter: '@craftify',
  telegram: 'https://t.me/MineBedWeb',
  instagram: 'https://instagram.com/craftify',
  youtube: 'https://youtube.com/@craftify',
  email: 'contact@minebed.ir',
  author: 'MineBed Farsi Team',
};
