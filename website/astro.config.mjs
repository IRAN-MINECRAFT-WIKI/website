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
      changefreq: 'daily',
      priority: 0.8,
      lastmod: new Date(),
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

