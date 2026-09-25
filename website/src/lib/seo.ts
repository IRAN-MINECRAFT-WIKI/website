/**
 * lib/seo.ts — SEO helpers (meta tags, JSON-LD structured data, breadcrumbs)
 *
 * All structured data follows schema.org specifications that Google
 * rewards in rich results.
 */
import { siteConfig } from './data';

export type SeoMeta = {
  title: string;
  description: string;
  image?: string;
  canonical?: string;
  type?: 'website' | 'article' | 'product';
  publishedTime?: string;
  modifiedTime?: string;
  tags?: string[];
  noindex?: boolean;
};

/** Build standard <meta> + OpenGraph + Twitter card strings */
export function buildHeadMeta(meta: SeoMeta, path: string) {
  const url = `${siteConfig.url}${path}`;
  const canonical = meta.canonical || url;
  const image = meta.image || `${siteConfig.url}/website/web-app-manifest-512x512.png`;
  const type = meta.type || 'website';

  return {
    title: `${meta.title} | ${siteConfig.name}`,
    description: meta.description,
    canonical,
    openGraph: {
      type,
      url,
      title: meta.title,
      description: meta.description,
      image,
      siteName: siteConfig.name,
      locale: siteConfig.locale,
    },
    twitter: {
      card: 'summary_large_image',
      title: meta.title,
      description: meta.description,
      image,
      site: siteConfig.twitter,
    },
    robots: meta.noindex ? 'noindex, nofollow' : 'index, follow',
  };
}

/** JSON-LD: WebSite + SearchAction (sitelinks search box) */
export function websiteJsonLd() {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: "ماین بد (MineBed)",
    alternateName: ["MineBed", "MineBed Farsi", "ماین بد", "ماینبد", siteConfig.nameEn],
    url: siteConfig.url,
    inLanguage: 'fa-IR',
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${siteConfig.url}/mods?q={search_term_string}`,
      },
      'query-input': 'required name=search_term_string',
    },
  };
}

/** JSON-LD: BreadcrumbList for breadcrumbs */
export function breadcrumbJsonLd(items: { name: string; url: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, idx) => ({
      '@type': 'ListItem',
      position: idx + 1,
      name: item.name,
      item: `${siteConfig.url}${item.url}`,
    })),
  };
}

/** JSON-LD: SoftwareApplication for a mod page */
export function modJsonLd(mod: {
  name: string;
  nameFa?: string;
  tagline?: string;
  desc: string;
  downloadUrl?: string;
  cover?: string;
  author?: string;
  version?: string;
  size?: string;
  category?: string;
  updated?: string;
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: mod.nameFa || mod.name,
    alternateName: mod.name,
    description: mod.desc.slice(0, 300),
    applicationCategory: 'Game',
    operatingSystem: 'Cross-platform (Minecraft Bedrock)',
    softwareVersion: mod.version,
    fileSize: mod.size,
    author: {
      '@type': 'Person',
      name: mod.author || 'Unknown',
    },
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'IRR',
      availability: 'https://schema.org/InStock',
    },
    contentUrl: mod.downloadUrl,
    downloadUrl: mod.downloadUrl,
    thumbnailUrl: mod.cover,
    image: mod.cover,
    inLanguage: 'fa-IR',
    dateModified: mod.updated,
    keywords: mod.tagline,
    // aggregateRating removed — fabricated ratings violate Google's structured data spam policy.
    // Add real aggregateRating only when an actual review system exists.
  };
}

/** JSON-LD: FAQPage for FAQ sections */
export function faqJsonLd(faqs: { q: string; a: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((f) => ({
      '@type': 'Question',
      name: f.q,
      acceptedAnswer: {
        '@type': 'Answer',
        text: f.a,
      },
    })),
  };
}

/** JSON-LD: Article for blog posts */
export function articleJsonLd(article: {
  title: string;
  description: string;
  image?: string;
  datePublished: string;
  dateModified?: string;
  authorName?: string;
  url: string;
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: article.title,
    description: article.description,
    image: article.image || `${siteConfig.url}/website/web-app-manifest-512x512.png`,
    datePublished: article.datePublished,
    dateModified: article.dateModified || article.datePublished,
    author: {
      '@type': 'Organization',
      name: article.authorName || siteConfig.author,
    },
    publisher: {
      '@type': 'Organization',
      name: "ماین بد (MineBed)",
      alternateName: ["MineBed", "MineBed Farsi", "ماین بد", "ماینبد"],
      logo: {
        '@type': 'ImageObject',
        url: `${siteConfig.url}/website/web-app-manifest-512x512.png`,
      },
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': `${siteConfig.url}${article.url}`,
    },
    inLanguage: 'fa-IR',
  };
}

/** JSON-LD: HowTo for tutorials */
export function howToJsonLd(howto: {
  title: string;
  description: string;
  totalTime: string; // ISO 8601 duration, e.g. "PT30M"
  steps: { name: string; text: string }[];
  url: string;
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'HowTo',
    name: howto.title,
    description: howto.description,
    totalTime: howto.totalTime,
    step: howto.steps.map((s, idx) => ({
      '@type': 'HowToStep',
      position: idx + 1,
      name: s.name,
      text: s.text,
    })),
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': `${siteConfig.url}${howto.url}`,
    },
    inLanguage: 'fa-IR',
  };
}

/** JSON-LD: Organization for footer / sitewide */
export function organizationJsonLd() {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: "ماین بد (MineBed)",
    alternateName: ["MineBed", "MineBed Farsi", "ماین بد", "ماینبد"],
    url: siteConfig.url,
    logo: `${siteConfig.url}/website/web-app-manifest-512x512.png`,
    sameAs: [
      siteConfig.telegram,
      siteConfig.instagram,
      siteConfig.youtube,
    ],
  };
}
