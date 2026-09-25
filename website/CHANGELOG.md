# CHANGELOG — MineBed Astro v3

All notable changes to MineBed Astro are documented here.
Format follows Keep a Changelog — semantic versioning.

---

## [3.0.0] — 2026-09-22 — "Visual Identity Restoration + Automation"

### ✨ Added — Section 1 (Restored Visual Features)

- **Cube3D component** — 3D rotating Minecraft cube with 7 block textures
  generated procedurally via Canvas (grass, dirt, stone, brick, gold, diamond,
  leaf). Click to swap block + pixel particle burst on hit. Name shown in
  Persian.
- **MusicPlayer component** — fixed bottom-left floating player with Play/Pause
  + Next buttons. Loads tracks from `/data/music.json`. Starts after first
  user interaction (per browser autoplay policy).
- **BackToTop component** — pixel green button appears when `scrollY > 500`,
  smooth scroll to top on click.
- **Preloader component** — full-screen pixel loader with progress bar + logo
  + "در حال بارگذاری..." text. Fades out after window load.
- **ParticleEffects component** — click-triggered pixel particle burst +
  mouse trail. Colors match site palette. Uses `#fxLayer` global canvas.
- **Floating blocks** in hero section — 16 pixel blocks floating slowly.
- **Animated stat counter** — homepage stats fetch from `mods.json` and count
  up from 0.

### 🔧 Added — Section 2 (Pipeline Automation)

- **`pipeline/config.py` updated** — `GITHUB_MODS_FILE` now points to
  `src/data/mods.json` (Astro's expected location).
- **`pipeline/urls.txt`** — newline-separated MCPEDL URLs to crawl daily.
- **`.github/workflows/pipeline.yml`** — daily cron at 02:00 UTC:
  1. Reads `pipeline/urls.txt`
  2. Runs `pipeline.py` with each URL
  3. Auto-commits updated `mods.json`
  4. Triggers `deploy.yml` workflow
- **GitHub Secrets required**: `HF_TOKEN`, `GITHUB_TOKEN`, `LM_STUDIO_URL` (optional)

### 🔧 Added — Section 3 (Professional Improvements)

- **Pagefind search** — client-side full-text search. Runs after `astro build`.
  `SearchBox` component in header (mobile + desktop).
- **View Transitions API** — Astro's `<ClientRouter />` enables smooth
  page transitions. Music player uses `transition:persist` so audio
  continues across navigation.
- **Image optimization** — `astro:assets` `<Image>` component used for
  local images. AVIF/WebP auto-generated. Remote CDN images lazy-loaded.
- **RSS feed** — `src/pages/rss.xml.js` produces `/rss.xml` with the latest
  20 blog posts.
- **OpenSearch** — `public/opensearch.xml` lets users add MineBed as a
  browser search engine.
- **PWA** — full manifest + service worker via `@vite-pwa/astro`.
  Installable on mobile + works offline.

### 🔧 Added — Section 4 (Content)

- **Pagination** for mods listing: `/mods/page/[page]`
- **Tag pages**: `/tags/[tag]/`
- **Author pages**: `/authors/[author]/`
- **Dedicated search page**: `/search`
- **More content added**:
  - Seeds: 6 → 20 (added 14 new with diverse biomes + structures)
  - Wiki: 1 → 10 (redstone, blocks, mobs, mechanics, biomes, items, etc.)
  - Blog: 2 → 7 (news, guides, version overviews)
  - Tutorials: 2 → 12 (beginner → advanced, varied topics)
- **Advanced Schema.org**:
  - `HowTo` schema for tutorials
  - `Review` + `AggregateRating` for mods
  - `VideoObject` placeholder for future video embeds
  - `Recipe` for crafting recipes

### 🔧 Added — Section 5 (Roadmap, not implemented)

- Telegram Bot (auto-notify on new mods)
- Cloudflare Workers live visitor counter
- Bilingual i18n (fa/en) with hreflang
- Dark/Light mode toggle
- Giscus comments

### 🛠️ Fixed

- `astro.config.mjs`: `trailingSlash` changed from `'always'` to `'ignore'`
- `astro.config.mjs`: `base` hardcoded to `/website/` (was auto-detected)
- Removed broken CubeStage placeholder from homepage — replaced with real
  `Cube3D` component

### ⚠️ Breaking Changes

- All internal URLs no longer require trailing slash (works both ways)
- `mods.json` location moved from repo root to `src/data/mods.json`
  (pipeline auto-updates new location)

### 📊 Stats

- Total pages built: 49 → 75+
- Components: 7 → 14
- Python pipeline files: 3 → 4 (added `urls.txt` data file)
- Workflows: 2 → 3 (added `pipeline.yml`)

---

## [2.0.0] — 2026-09-22 — "Astro Migration"

Initial Astro migration. See README.md for details.

---

## [1.0.0] — Original static HTML site

Pre-Astro era.
