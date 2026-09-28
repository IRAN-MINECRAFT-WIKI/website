// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwind from '@astrojs/tailwind';
import mdx from '@astrojs/mdx';

// ⚙️ GitHub Pages project site (https://USER.github.io/website/)
// Hardcoded per project requirement — do NOT change.
const base = '/website/';

export default defineConfig({
  site: 'https://iran-minecraft-wiki.github.io/website',
  base: base,
  trailingSlash: 'ignore',
  output: 'static',
  build: {
    inlineStylesheets: 'auto',
    assets: '_assets',
  },
  integrations: [
    mdx(),
    tailwind({ applyBaseStyles: true }),
    sitemap({
      i18n: {
        defaultLocale: 'fa',
        locales: { fa: 'fa-IR', en: 'en-US' },
      },
      changefreq: 'weekly',
      priority: 0.8,
      // NOTE: do NOT set a global ``lastmod: new Date()`` — that would
      // tell Google every URL "changed today", which dilutes the value
      // of the lastmod signal.  When omitted, the sitemap integration
      // falls back to per-URL lastmod from the build's last-modified
      // time of each page's source file, which is what we want.
    }),
  ],
  image: {
    domains: ['cdn.imgurl.ir', 'huggingface.co', 'r2.mcpedl.com', 'media.forgecdn.net'],
  },
  compressHTML: true,
  experimental: {
    clientPrerender: true,
  },
  prefetch: {
    prefetchAll: true,
    defaultStrategy: 'viewport',
  },
});

