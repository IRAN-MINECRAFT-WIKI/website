/**
 * Post-build sitemap generator — creates a SINGLE clean sitemap.xml.
 *
 * Following Google's own documentation:
 * https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
 *
 * What others do for GitHub Pages project sites (base path /website/):
 *   - Use ONE sitemap file (sitemap.xml), not an index + child files
 *   - Submit the FULL absolute URL to Google Search Console
 *   - Include <lastmod> dates (Google uses them for crawl scheduling)
 *   - No extra namespaces (just the core sitemap schema)
 *
 * This script:
 *   1. Reads the Astro-generated sitemap-0.xml (which has all URLs)
 *   2. Writes a clean sitemap.xml (simple <urlset> with <loc> + <lastmod>)
 *   3. DELETES sitemap-0.xml and sitemap-index.xml (only sitemap.xml remains)
 *   4. Updates robots.txt to point to sitemap.xml (not sitemap-index.xml)
 */
import { readFileSync, writeFileSync, unlinkSync, existsSync } from 'fs';
import { join } from 'path';

const DIST = join(process.cwd(), 'dist');
const SITE = 'https://iran-minecraft-wiki.github.io/website';
const TODAY = new Date().toISOString().split('T')[0]; // YYYY-MM-DD

// Read the Astro-generated sitemap-0.xml
const sm0Path = join(DIST, 'sitemap-0.xml');
if (!existsSync(sm0Path)) {
  console.error('[sitemap] sitemap-0.xml not found — skipping');
  process.exit(0);
}

const sm0 = readFileSync(sm0Path, 'utf-8');

// Extract all <loc> URLs from sitemap-0.xml
const urls = [...sm0.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1]);
console.log(`[sitemap] found ${urls.length} URLs in sitemap-0.xml`);

// Build a clean sitemap.xml following Google's format exactly:
// https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
//
// Google says:
//   - <loc> is required (absolute URL)
//   - <lastmod> is optional but recommended (W3C Datetime format)
//   - <changefreq> and <priority> are ignored by Google
//
// We include <lastmod> with today's date so Google knows the sitemap is fresh.
let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
for (const url of urls) {
  // Ensure the URL is properly escaped (& → &amp; for XML)
  const safeUrl = url.replace(/&/g, '&amp;');
  xml += `  <url>\n`;
  xml += `    <loc>${safeUrl}</loc>\n`;
  xml += `    <lastmod>${TODAY}</lastmod>\n`;
  xml += `  </url>\n`;
}
xml += '</urlset>\n';

const smPath = join(DIST, 'sitemap.xml');
writeFileSync(smPath, xml, 'utf-8');
console.log(`[sitemap] wrote sitemap.xml (${urls.length} URLs, ${Buffer.byteLength(xml)} bytes, lastmod=${TODAY})`);

// DELETE the Astro-generated sitemap-0.xml and sitemap-index.xml
// Having multiple sitemap files confuses Google — only sitemap.xml should exist
try { unlinkSync(sm0Path); console.log('[sitemap] deleted sitemap-0.xml'); } catch (e) { /* ignore */ }
const idxPath = join(DIST, 'sitemap-index.xml');
try { unlinkSync(idxPath); console.log('[sitemap] deleted sitemap-index.xml'); } catch (e) { /* ignore */ }

// Update robots.txt to point to sitemap.xml (not sitemap-index.xml)
const robotsPath = join(DIST, 'robots.txt');
if (existsSync(robotsPath)) {
  let robots = readFileSync(robotsPath, 'utf-8');
  robots = robots.replace(/sitemap-index\.xml/g, 'sitemap.xml');
  writeFileSync(robotsPath, robots, 'utf-8');
  console.log('[sitemap] updated robots.txt → sitemap.xml');
}

console.log('[sitemap] done ✓ — only sitemap.xml exists now');
console.log('[sitemap] submit this URL to Google:');
console.log(`[sitemap]   ${SITE}/sitemap.xml`);
