/**
 * Post-build sitemap generator.
 *
 * The @astrojs/sitemap integration creates sitemap-index.xml + sitemap-0.xml,
 * but Google Search Console (and Bing) often look for /sitemap.xml directly.
 * On a GitHub Pages project site (base path /website/), the root
 * /sitemap.xml already points to /website/sitemap.xml — but that file
 * didn't exist (404), causing "Sitemap could not be read" in Google.
 *
 * This script:
 *   1. Reads the Astro-generated sitemap-0.xml (which has all URLs)
 *   2. Writes a clean sitemap.xml with the same URLs (simple <urlset>,
 *      no extra namespaces, no index indirection)
 *   3. Also writes a clean sitemap-index.xml that points to sitemap.xml
 *
 * The result: /website/sitemap.xml is a valid, simple sitemap that Google
 * can read directly, following Google's own documentation format.
 * https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'fs';
import { join } from 'path';

const DIST = join(process.cwd(), 'dist');
const SITE = 'https://iran-minecraft-wiki.github.io/website';

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

// Build a clean sitemap.xml following Google's format:
// https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
for (const url of urls) {
  // Ensure the URL is properly escaped (& → &amp; for XML)
  const safeUrl = url.replace(/&/g, '&amp;');
  xml += `  <url>\n    <loc>${safeUrl}</loc>\n  </url>\n`;
}
xml += '</urlset>\n';

const smPath = join(DIST, 'sitemap.xml');
writeFileSync(smPath, xml, 'utf-8');
console.log(`[sitemap] wrote sitemap.xml (${urls.length} URLs, ${Buffer.byteLength(xml)} bytes)`);

// Write a clean sitemap-index.xml that points to sitemap.xml
let idx = '<?xml version="1.0" encoding="UTF-8"?>\n';
idx += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
idx += `  <sitemap>\n    <loc>${SITE}/sitemap.xml</loc>\n  </sitemap>\n`;
idx += '</sitemapindex>\n';

const idxPath = join(DIST, 'sitemap-index.xml');
writeFileSync(idxPath, idx, 'utf-8');
console.log('[sitemap] wrote sitemap-index.xml (points to sitemap.xml)');
console.log('[sitemap] done ✓');
