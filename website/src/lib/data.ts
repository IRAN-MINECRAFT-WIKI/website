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
  isLatest?: boolean;
  featured?: boolean;
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
export const versions: MCVersion[] = (versionsRaw as { versions: MCVersion[] }).versions;
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
  // Match by major.minor string, e.g. "1.21" → "1-21"
  const v = verId.replace('-', '.');
  return mods.filter((m) => (m.version || '').startsWith(v));
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
