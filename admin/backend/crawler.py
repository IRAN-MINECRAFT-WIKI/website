"""
MineBed Admin — MCPEDL crawler.

Pure ``requests`` + regex implementation.  No Playwright, no headless browser,
no subprocess — designed to run cleanly on Windows inside pywebview.

How it works
------------
MCPEDL is a Nuxt.js single-page app, so its homepage HTML does not contain
the actual mod cards — they are rendered client-side from a JSON API at
``https://api.mcpedl.com/api/``.  We discovered this API by reading the
Nuxt JS bundles.  Using the API is far more reliable than scraping the
server-rendered HTML, so:

  * ``fetch_top_mods(count)`` calls ``GET /api/submissions?per_page=N``
    and returns the resulting mod URLs (``https://mcpedl.com/{slug}/``).
  * ``crawl_mod(url)`` calls ``GET /api/submissions?slug={slug}`` for the
    structured data, AND fetches the mod page HTML to enrich the
    description via ``og:description`` meta tag.  This way the returned
    dict is always rich even when one of the two sources fails.

Public API
----------
    fetch_top_mods(count, on_progress=None) -> list[str]
    crawl_mod(url, on_progress=None) -> dict | None

The structured dict returned by ``crawl_mod`` has the shape::

    {
        "url":      str,
        "slug":     str,
        "title":    str,
        "author":   str | None,
        "version":  str | None,        # first version tag, if any
        "updated":  str | None,        # YYYY-MM-DD
        "description": str,
        "cover":    str | None,
        "gallery":  list[str],
        "files":    list[dict],        # {name, size, link}
        "categories": list[str],
        "downloadCount": int,
        "rating":   float | None,
        "source":   str | None,         # curseforge / mcpedl / ...
    }
"""
from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
from typing import Callable, Optional

import requests

from . import config

# A progress callback receives (phase: str, message: str).
ProgressFn = Optional[Callable[[str, str], None]]


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------
def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": config.CRAWLER_USER_AGENT,
        "Accept": "application/json,text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": config.MCPEDL_BASE_URL + "/",
    })
    return s


def _get(url: str, session: requests.Session | None = None,
         accept_html: bool = False) -> Optional[str]:
    """GET a URL, return decoded text or None on failure."""
    sess = session or _session()
    try:
        headers = {}
        if accept_html:
            headers["Accept"] = "text/html,application/xhtml+xml,*/*;q=0.8"
        resp = sess.get(url, timeout=config.CRAWLER_TIMEOUT, headers=headers)
        if resp.status_code != 200:
            return None
        resp.encoding = resp.apparent_encoding or "utf-8"
        return resp.text
    except Exception:
        return None


def _get_json(url: str, session: requests.Session | None = None,
              params: dict | None = None) -> Optional[dict]:
    sess = session or _session()
    try:
        resp = sess.get(url, timeout=config.CRAWLER_TIMEOUT, params=params or {})
        if resp.status_code != 200:
            return None
        # MCPEDL API returns JSON with correct content-type; if the body is
        # empty or HTML, bail out gracefully.
        try:
            return resp.json()
        except Exception:
            return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# URL helpers / filters
# ---------------------------------------------------------------------------
MCPEDL_API = "https://api.mcpedl.com/api"

# Slugs that are NOT individual mods.  Anything matching these is excluded
# from the top-mods list.
_NON_MOD_PATHS = {
    "mods", "maps", "texture-packs", "skins", "seeds", "servers",
    "shaders", "datapacks", "resource-packs", "category", "categories",
    "page", "tag", "about", "contact", "privacy", "terms",
    "search", "login", "register", "wp-admin", "wp-login",
    "author", "user", "profile", "addons",
}

# Static asset / well-known slugs we never want to crawl
_ASSET_EXT = (".ico", ".png", ".jpg", ".jpeg", ".gif", ".svg",
              ".webp", ".css", ".js", ".xml", ".json",
              ".woff", ".woff2", ".ttf", ".txt", ".webmanifest")
_STATIC_SLUGS = {"favicon", "apple-touch-icon", "safari-pinned-tab",
                 "robots", "sitemap", "manifest", "browserconfig"}


def _slug_from_url(url: str) -> str:
    """Return the trailing path segment as a slug."""
    path = urllib.parse.urlparse(url).path.rstrip("/")
    return path.rsplit("/", 1)[-1]


def is_mod_url(url: str) -> bool:
    """Heuristic: does this URL look like an individual MCPEDL mod page?"""
    if not url:
        return False
    parsed = urllib.parse.urlparse(url)
    if "mcpedl.com" not in (parsed.netloc or ""):
        return False
    path = parsed.path.strip("/")
    if not path:
        return False
    if re.match(r"page/\d+", path):
        return False
    slug = path.split("/")[-1]
    if slug.lower().endswith(_ASSET_EXT):
        return False
    if slug in _STATIC_SLUGS:
        return False
    first = path.split("/", 1)[0]
    if first in _NON_MOD_PATHS:
        return False
    # Multi-segment paths are navigation, not individual mods
    if "/" in path:
        return False
    if not slug or slug.isdigit():
        return False
    if len(slug) < 4:
        return False
    return True


def _normalize_url(url: str) -> str:
    """Make a relative MCPEDL URL absolute and strip fragments/query."""
    if url.startswith("/") or url.startswith("?"):
        url = urllib.parse.urljoin(config.MCPEDL_BASE_URL + "/", url)
    if url.startswith("http://"):
        url = "https://" + url[len("http://"):]
    if not url.startswith("http"):
        url = config.MCPEDL_BASE_URL.rstrip("/") + "/" + url.lstrip("/")
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc,
                                    parsed.path, "", "", ""))


# ---------------------------------------------------------------------------
# Top mods discovery — via MCPEDL JSON API
# ---------------------------------------------------------------------------
def fetch_top_mods(count: int = 10, on_progress: ProgressFn = None) -> list[str]:
    """
    Return up to ``count`` MCPEDL mod URLs (``https://mcpedl.com/{slug}/``).

    Uses the public JSON API at ``api.mcpedl.com/api/submissions`` — much more
    reliable than scraping the homepage HTML (which is a Nuxt SPA shell).
    """
    def log(msg: str) -> None:
        if on_progress:
            on_progress("discover", msg)

    session = _session()
    urls: list[str] = []
    seen: set[str] = set()

    # The API paginates with ``page`` and ``per_page`` (max per_page ~50).
    per_page = min(max(count, 1), 50)
    page = 1
    max_pages = max(4, (count // per_page) + 2)

    while len(urls) < count and page <= max_pages:
        log(f"Fetching API page {page} (per_page={per_page}) …")
        params = {
            "per_page": per_page,
            "page": page,
            # Only actual mods (not draft versions); matches what the site shows
            "is_actual_version": 1,
        }
        data = _get_json(f"{MCPEDL_API}/submissions", session, params)
        if not data:
            log(f"  ! API returned nothing for page {page}")
            break

        items = data.get("data") or []
        if not isinstance(items, list) or not items:
            log("  ! no more items")
            break

        new = 0
        for item in items:
            slug = item.get("slug")
            if not slug or slug in seen:
                continue
            # Cache the full submission object so crawl_mod can reuse it
            # without an extra round-trip to the API.
            _SUBMISSION_CACHE[slug] = item
            seen.add(slug)
            urls.append(f"{config.MCPEDL_BASE_URL}/{slug}/")
            new += 1
            if len(urls) >= count:
                break
        log(f"  + {new} mods (total {len(urls)})")

        # Honor pagination meta
        meta = data.get("meta") or {}
        last_page = (meta.get("last_page") or meta.get("total_pages") or 1)
        if page >= int(last_page):
            break
        page += 1
        time.sleep(0.3)  # polite delay

    return urls[:count]


# ---------------------------------------------------------------------------
# Single mod crawler — API + HTML enrichment
# ---------------------------------------------------------------------------
def _clean_text(s: str) -> str:
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _api_fetch_submission(slug: str, session: requests.Session) -> Optional[dict]:
    """
    GET the submission object for ``slug`` via the API.

    The MCPEDL API's ``slug`` query parameter is unreliable — it returns the
    first submission regardless of the value.  Instead we do a text search
    with ``?s={slug}`` and pick the item whose slug matches exactly.  We
    also consult a module-level cache populated by ``fetch_top_mods``.
    """
    # 1. Cache lookup
    if slug in _SUBMISSION_CACHE:
        return _SUBMISSION_CACHE[slug]

    # 2. Search via the text-search endpoint
    data = _get_json(f"{MCPEDL_API}/submissions", session,
                     {"s": slug, "per_page": 25})
    if not data:
        return None
    items = data.get("data") or []
    if not isinstance(items, list):
        return None
    # 3. Exact slug match
    for item in items:
        if isinstance(item, dict) and item.get("slug") == slug:
            _SUBMISSION_CACHE[slug] = item
            return item
    # 4. Fallback: first result if its slug is reasonably close
    if items and isinstance(items[0], dict):
        first = items[0]
        if first.get("slug") and slug in first.get("slug", ""):
            _SUBMISSION_CACHE[slug] = first
            return first
    return None


# Module-level cache: slug -> submission dict.  Populated by fetch_top_mods
# (which already has the data) so crawl_mod doesn't need to re-fetch.
_SUBMISSION_CACHE: dict[str, dict] = {}


def _html_enrich(url: str, session: requests.Session) -> dict:
    """
    Fetch the mod page HTML and pull out a long description + any gallery
    images we might have missed.

    MCPEDL mod pages are Nuxt SPAs, but they still ship an
    ``og:description`` meta tag and (often) an ``<noscript>`` block with
    the description text.  We extract whatever we can.
    """
    out = {"description": "", "gallery": [], "categories": []}
    text = _get(url, session, accept_html=True)
    if not text:
        return out

    # og:description (most reliable for Nuxt pages)
    m = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
                  text, flags=re.I)
    if m:
        out["description"] = _clean_text(m.group(1))

    # <meta name="description"> fallback
    if not out["description"]:
        m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
                      text, flags=re.I)
        if m:
            out["description"] = _clean_text(m.group(1))

    # noscript block — MCPEDL ships an HTML description inside <noscript>
    m = re.search(r"<noscript[^>]*>(.*?)</noscript>", text, flags=re.I | re.S)
    if m:
        ns = m.group(1)
        # Pull <p> blocks
        paras = re.findall(r"<p[^>]*>(.*?)</p>", ns, flags=re.I | re.S)
        if paras:
            full = "\n\n".join(_clean_text(re.sub(r"<[^>]+>", " ", p)) for p in paras if p.strip())
            if len(full) > len(out["description"]):
                out["description"] = full[:4000]

    # Gallery images from the noscript / og blocks
    if m:
        for m2 in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', m.group(1), flags=re.I):
            src = m2.group(1)
            if src not in out["gallery"]:
                out["gallery"].append(src)
            if len(out["gallery"]) >= 8:
                break

    # Category / tag links
    for m2 in re.finditer(r'rel=["\']tag["\'][^>]*>(.*?)</a>', text, flags=re.I | re.S):
        cat = _clean_text(re.sub(r"<[^>]+>", "", m2.group(1)))
        if cat and cat not in out["categories"]:
            out["categories"].append(cat)
        if len(out["categories"]) >= 8:
            break

    return out


def crawl_mod(url: str, on_progress: ProgressFn = None) -> Optional[dict]:
    """
    Crawl a single MCPEDL mod page.

    Combines structured data from the JSON API with description / gallery
    enrichment from the page HTML.  Returns ``None`` only if BOTH sources
    fail.
    """
    def log(msg: str) -> None:
        if on_progress:
            on_progress("crawl", msg)

    url = _normalize_url(url)
    slug = _slug_from_url(url)
    session = _session()

    # ---- 1. API data --------------------------------------------------
    log(f"Fetching API data for «{slug}»")
    sub = _api_fetch_submission(slug, session)

    if not sub:
        # Fall back to pure HTML scraping if the API is unavailable
        log("  ! API miss — falling back to HTML-only scraping")
        enriched = _html_enrich(url, session)
        if not enriched["description"] and not url:
            return None
        return {
            "url": url,
            "slug": slug,
            "title": slug.replace("-", " ").title(),
            "author": None,
            "version": None,
            "updated": None,
            "description": enriched["description"] or slug,
            "cover": None,
            "gallery": enriched["gallery"],
            "files": [],
            "categories": enriched["categories"],
            "downloadCount": 0,
            "rating": None,
            "source": None,
        }

    title = (sub.get("title") or slug).strip()
    summary = (sub.get("summary") or "").strip()

    # Author: prefer display_name, then username, then user_nicename
    author = (sub.get("display_name") or sub.get("username")
              or sub.get("user_nicename") or None)

    # Version: first version-tag name (e.g. "1.21.80")
    version = None
    for tag in (sub.get("tags") or []):
        name = tag.get("name") if isinstance(tag, dict) else None
        if name and re.match(r"^\d", name):
            version = name
            break

    updated = None
    sd = sub.get("sort_date") or sub.get("created_at") or sub.get("imported_at")
    if sd:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", str(sd))
        if m:
            updated = m.group(1)

    cover = sub.get("image") or None

    # Gallery
    gallery: list[str] = list(sub.get("submission_images") or [])

    # Files / downloads
    files: list[dict] = []
    for dl in (sub.get("downloads") or []):
        if not isinstance(dl, dict):
            continue
        link = dl.get("downloadUrl") or dl.get("url") or dl.get("link")
        name = dl.get("name") or dl.get("filename")
        size = dl.get("fileLength") or dl.get("file_size") or dl.get("size")
        if link:
            files.append({"name": name, "size": size, "link": link})

    # Categories: derive from tags
    categories: list[str] = []
    for tag in (sub.get("tags") or [])[:8]:
        if isinstance(tag, dict):
            n = tag.get("name")
            if n and n not in categories:
                categories.append(n)

    # Rating / popularity
    rating = None
    if sub.get("average_rating") is not None:
        try:
            rating = float(sub.get("average_rating"))
        except Exception:
            rating = None
    dl_count = 0
    pop = sub.get("popular") or {}
    if isinstance(pop, dict):
        dl_count = int(pop.get("popular_all") or pop.get("popular_month") or 0)
    if not dl_count:
        try:
            dl_count = int(sub.get("downloadCount") or 0)
        except Exception:
            dl_count = 0

    # ---- 2. HTML enrichment (description, extra gallery) ---------------
    if not summary or len(summary) < 80:
        log("  enriching description from page HTML …")
        enriched = _html_enrich(url, session)
        # Use the longer of summary / enriched description
        if len(enriched["description"]) > len(summary):
            summary = enriched["description"]
        for g in enriched["gallery"]:
            if g not in gallery and g != cover:
                gallery.append(g)
            if len(gallery) >= 10:
                break
        for c in enriched["categories"]:
            if c not in categories:
                categories.append(c)
            if len(categories) >= 12:
                break

    if not summary:
        summary = title

    result = {
        "url": url,
        "slug": slug,
        "title": title,
        "author": author,
        "version": version,
        "updated": updated,
        "description": summary,
        "cover": cover,
        "gallery": gallery,
        "files": files,
        "categories": categories,
        "downloadCount": dl_count,
        "rating": rating,
        "source": sub.get("source"),
    }
    log(f"  ✓ {title} (v{version or '?'}, {len(files)} files, "
        f"{dl_count} downloads)")
    return result
