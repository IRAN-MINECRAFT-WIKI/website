import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { siteConfig } from '@/lib/data';

/**
 * RSS 2.0 feed for the MineBed Farsi blog.
 *
 * Endpoint: /rss.xml  →  /website/rss.xml on the live GitHub Pages URL.
 *
 * Source for items: `src/content/blog/*.mdx` (filtering out drafts).
 *
 * ── Why we use `import.meta.env.BASE_URL` to build each item link ──
 *
 * The site is hosted at the GitHub Pages project URL
 *   https://iran-minecraft-wiki.github.io/website/
 * so `astro.config.mjs` sets `site: 'https://...github.io/website'` AND
 * `base: '/website/'`.
 *
 * `@astrojs/rss` v4 joins an item `link` with the `site` URL via
 *   new URL(link, site).href
 * — and because every `link` we pass starts with `/`, that ABSOLUTE path
 * overwrites the site's pathname (which is `/website`), producing
 *   https://iran-minecraft-wiki.github.io/blog/<slug>/
 * instead of the correct
 *   https://iran-minecraft-wiki.github.io/website/blog/<slug>/
 *
 * Fix: prefix each link with `import.meta.env.BASE_URL` (which is the
 * Astro-resolved base path, `/website/` here) so the resulting link is
 *   `/website/blog/<slug>/`
 * — an absolute path that, when joined against `site`, preserves the base.
 *
 * Verified on the live feed: the channel <link> already shows
 * `.../website/` correctly, but item links were previously missing the
 * `/website/` segment, which broke every <guid> and <link> in readers.
 */
export async function GET(context) {
  // Pull every non-draft blog post, newest-first by publication date.
  const posts = (await getCollection('blog', ({ data }) => !data.draft)).sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );

  // `import.meta.env.BASE_URL` reflects astro.config.mjs `base` ("/website/").
  // Trailing slash is guaranteed by Astro for non-root bases.
  const base = import.meta.env.BASE_URL;

  return rss({
    title: siteConfig.name,
    description: siteConfig.description,
    site: context.site,
    items: posts.map((post) => {
      const item = {
        title: post.data.title,
        pubDate: post.data.pubDate,
        description: post.data.description,
        author: post.data.author,
        categories: post.data.tags,
        // Prepend the base path so @astrojs/rss doesn't strip it
        // when joining the link with the site URL.
        link: `${base}blog/${post.id}/`,
      };

      // RSS 2.0 supports <lastBuildDate> per item — @astrojs/rss maps the
      // `modDate` field to it. Lets readers see when a post was edited
      // after first publication (e.g. typo fixes, content updates).
      if (post.data.modDate) {
        item.modDate = post.data.modDate;
      }

      return item;
    }),
    customData: `<language>fa-IR</language>`,
    stylesheet: true,
  });
}
