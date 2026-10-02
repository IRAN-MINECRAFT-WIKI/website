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
  redirects: {
    // Backwards-compat for old version URLs (pre Task 21 used unprefixed IDs).
    // Astro static output renders these as HTML meta-refresh stubs.
    // The base `/website/` prefix is required because this is a GitHub
    // Pages project site (astro.config `base`). Without it, the meta
    // refresh would 404 on the production URL.
    '/versions/1-21': '/website/versions/java-1-21',
    '/versions/1-20': '/website/versions/java-1-20',
    '/versions/1-19': '/website/versions/java-1-19',
    '/versions/1-18': '/website/versions/java-1-18',
    '/versions/1-17': '/website/versions/java-1-17',
    '/versions/1-16': '/website/versions/java-1-16',
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

      // ⛔ Exclude the hidden admin panel URL from the sitemap. The
      // panel is also covered by a `noindex` meta tag (set via the
      // `noindex: true` prop on BaseLayout) and a `Disallow:` rule in
      // public/robots.txt. Belt + braces + a third belt.
      filter: (page) => !page.includes('/admin-minebed-control'),
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

