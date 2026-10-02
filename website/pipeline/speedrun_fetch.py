#!/usr/bin/env python3
"""
speedrun_fetch.py — Fetches Minecraft Java + Bedrock speedrun records
from the Speedrun.com public API and writes per-category JSON files
that the MineBed website consumes.

Output layout::

    website/src/data/speedrun/
    ├── config.json      (game IDs, category IDs, variable IDs, value labels)
    ├── summary.json     (run-summary from the most recent fetch)
    ├── java/
    │   ├── any-glitchless.json
    │   ├── any-percent.json
    │   └── ...
    └── bedrock/
        ├── any-glitchless.json
        └── ...

Per-run record schema::

    {
      "id":            "y84ogqdz",
      "weblink":       "https://www.speedrun.com/mc/runs/y84ogqdz",
      "category":      "Any% Glitchless",
      "platform":     "Java" | "Bedrock",
      "time_primary":  661.333,
      "time_display":  "11m 1s 333ms",
      "date":          "2026-10-02",
      "players":       ["HiiKun_"],
      "seed":          "-3061201730034849961" | null,
      "verified":      true
    }

By design we DO NOT store ``video_url`` (per spec).  We DO additionally
store ``version`` and ``seed_type`` (resolved from the run's ``values``
dict using cached variable/value labels) — these are useful for the
leaderboard UI and are safe to expose.

SAFETY:
    * Rate-limited to one request every 700 ms (~85 req/min, under
      Speedrun.com's 100 req/min ceiling).
    * User-Agent set to project identity.
    * Retries 3× on network errors / 5xx / 429 with exponential
      backoff.
    * If the API returns *no data* for a category (network failure),
      we DO NOT overwrite the existing per-category JSON file — the
      previous good data is preserved on disk.
    * Writes are atomic (tmp file + os.replace) — a crash mid-write
      never produces a half-written JSON.

Usage::

    # Top 100 verified runs per category (default — the website's
    # initial dataset as requested in the task brief):
    python website/pipeline/speedrun_fetch.py \\
        --output website/src/data/speedrun/

    # Top 50 most-recently submitted verified runs for Bedrock only,
    # including miscellaneous sub-categories:
    python website/pipeline/speedrun_fetch.py \\
        --output website/src/data/speedrun/ \\
        --top 50 --game bedrock --include-misc

CI cron: ``.github/workflows/speedrun.yml`` runs this nightly at
03:00 Iran time and commits the result with ``[skip ci]`` so the
deploy workflow isn't triggered in a loop.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path
from typing import Optional

import requests

# Optional: load .env for local dev (CI uses raw env).
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_BASE = "https://www.speedrun.com/api/v1"
USER_AGENT = "iran-minecraft-wiki/1.0 (github.com/IRAN-MINECRAFT-WIKI/website)"
REQUEST_DELAY = 0.7          # seconds between requests — ~85 req/min
MAX_RETRIES = 3              # per-request retry budget
HTTP_TIMEOUT = 30            # seconds

# Verified game IDs (per the Phase 3 task brief).
GAMES = {
    "java":    {"id": "j1npme6p", "label": "Java",    "abbreviation": "mc"},
    "bedrock": {"id": "yd4ovvg1", "label": "Bedrock", "abbreviation": "mcbe"},
}

# seed:-12345  / seed:12345  / seed = 12345  / سید:-12345  / سید:12345
SEED_RE = re.compile(r"(?:seed|سید)\s*[:=]\s*(-?\d+)", re.IGNORECASE)

# Match the "primary" ISO-8601 duration that Speedrun.com returns, e.g.
#   PT11M1.333S    ->  11 minutes 1.333 seconds
#   PT1H2M3S       ->  1 hour 2 minutes 3 seconds
#   PT45.5S        ->  45.5 seconds
ISO_DURATION_RE = re.compile(
    r"^PT(?:(?P<h>\d+)H)?(?:(?P<m>\d+)M)?(?:(?P<s>\d+(?:\.\d+)?)S)?$"
)

_SLUG_STRIP_RE = re.compile(r"[^a-z0-9]+")


# Single shared HTTP session — keeps TCP keep-alive between requests.
_session = requests.Session()
_session.headers.update({
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
})


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    """``Any% Glitchless`` → ``any-glitchless``.

    Strips non-alphanumerics, collapses runs of them to a single hyphen,
    lowercases.  Empty input → ``"unknown"`` (never an empty string,
    so we never produce a hidden ``.json`` filename).
    """
    s = (name or "").lower().strip()
    s = _SLUG_STRIP_RE.sub("-", s).strip("-")
    return s or "unknown"


def format_time_display(iso_duration: Optional[str]) -> str:
    """``PT11M1.333S`` → ``"11m 1s 333ms"``.

    Falls back to the raw string if the regex doesn't match (rare but
    happens for unusual unit combinations the API might emit).
    """
    if not iso_duration:
        return ""
    m = ISO_DURATION_RE.match(iso_duration)
    if not m:
        return iso_duration
    parts = []
    if m.group("h"):
        parts.append(f"{int(m.group('h'))}h")
    if m.group("m"):
        parts.append(f"{int(m.group('m'))}m")
    s = m.group("s")
    if s:
        if "." in s:
            whole, frac = s.split(".")
            frac = (frac + "000")[:3]  # pad / truncate to milliseconds
            parts.append(f"{int(whole)}s {int(frac)}ms")
        else:
            parts.append(f"{int(s)}s")
    return " ".join(parts) or "0s"


def extract_seed(comment: Optional[str]) -> Optional[str]:
    """Pull a Minecraft world seed out of a run's free-text ``comment``.

    Returns the seed as a string (preserves leading minus sign for
    negative seeds, which are common).  Returns ``None`` if no seed
    is mentioned.
    """
    if not comment:
        return None
    m = SEED_RE.search(comment)
    return m.group(1) if m else None


def parse_player_names(players_block) -> list:
    """Return a list of human-readable player display names.

    Handles the embedded-players shape ``{"data": [ {...}, {...} ]}``.
    For each player we prefer ``names.international`` (registered
    Speedrun.com accounts) and fall back to ``name`` (guests).
    """
    if not players_block or not isinstance(players_block, dict):
        return []
    data = players_block.get("data", [])
    names = []
    for p in data:
        if not isinstance(p, dict):
            continue
        intl = ((p.get("names") or {}).get("international"))
        guest = p.get("name")
        names.append(intl or guest or "Anonymous")
    return names


# ---------------------------------------------------------------------------
# HTTP layer (rate-limited + retrying)
# ---------------------------------------------------------------------------

def _sleep_for_rate_limit() -> None:
    time.sleep(REQUEST_DELAY)


def api_get(path_or_url: str, params: Optional[dict] = None) -> Optional[dict]:
    """GET ``path_or_url`` (relative to API_BASE, or absolute).

    Returns parsed JSON ``{"data": ..., "pagination": ...}`` on success
    or ``None`` on persistent failure (after MAX_RETRIES attempts).

    Retry policy:
      * 429 Too Many Requests → exponential backoff 5/10/20s
      * 5xx server errors    → exponential backoff 2/4/8s
      * Network/timeout/JSON-decode → exponential backoff 2/4/8s
      * 404 → return None silently (legitimate "no data")
      * Other 4xx → raise_for_status() (likely a programmer error)
    """
    url = (path_or_url if path_or_url.startswith("http")
           else f"{API_BASE}/{path_or_url.lstrip('/')}")
    last_exc: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            _sleep_for_rate_limit()
            r = _session.get(url, params=params, timeout=HTTP_TIMEOUT)

            if r.status_code == 404:
                # Soft-fail: not an error, just nothing here.
                return None

            if r.status_code == 429:
                wait = 5 * (2 ** (attempt - 1))
                print(f"  ! 429 rate-limited — backoff {wait}s "
                      f"(attempt {attempt}/{MAX_RETRIES})", file=sys.stderr)
                time.sleep(wait)
                continue

            if 500 <= r.status_code < 600:
                wait = 2 ** attempt
                print(f"  ! HTTP {r.status_code} server error — retry in {wait}s "
                      f"(attempt {attempt}/{MAX_RETRIES})", file=sys.stderr)
                time.sleep(wait)
                continue

            r.raise_for_status()
            return r.json()

        except requests.Timeout as e:
            last_exc = e
            wait = 2 ** attempt
            print(f"  ! timeout — retry in {wait}s "
                  f"(attempt {attempt}/{MAX_RETRIES})", file=sys.stderr)
            time.sleep(wait)

        except requests.ConnectionError as e:
            last_exc = e
            wait = 2 ** attempt
            print(f"  ! connection error: {e} — retry in {wait}s "
                  f"(attempt {attempt}/{MAX_RETRIES})", file=sys.stderr)
            time.sleep(wait)

        except json.JSONDecodeError as e:
            last_exc = e
            wait = 2 ** attempt
            print(f"  ! bad JSON from API — retry in {wait}s "
                  f"(attempt {attempt}/{MAX_RETRIES})", file=sys.stderr)
            time.sleep(wait)

    print(f"  ✗ giving up on {url} after {MAX_RETRIES} attempts: "
          f"{type(last_exc).__name__ if last_exc else 'unknown'}",
          file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# Domain fetches
# ---------------------------------------------------------------------------

def fetch_categories(game_id: str) -> list:
    """Return the full list of category dicts for ``game_id``."""
    print(f"  → GET games/{game_id}/categories")
    data = api_get(f"games/{game_id}/categories")
    return (data or {}).get("data", []) if data else []


def fetch_category_variables(cat_id: str) -> list:
    """Return variables visible to a category.

    The Speedrun.com ``categories/{id}/variables`` endpoint already
    includes game-level variables (those without a ``category`` field)
    alongside category-scoped ones — so a single call is enough.
    """
    data = api_get(f"categories/{cat_id}/variables")
    return (data or {}).get("data", []) if data else []


def fetch_runs_for_category(cat_id: str, top_n: int = 100,
                            status: str = "verified") -> Optional[list]:
    """Fetch up to ``top_n`` runs for a category, newest-submitted first.

    Returns:
      * a list of run dicts (possibly empty) on success,
      * ``None`` if the very first page failed after all retries —
        in that case the caller MUST NOT overwrite the existing file.

    Paginates with max=200 (the API ceiling).  Stops early when we
    reach ``top_n`` or when the API returns a short page (signal that
    we're at the end of the result set).
    """
    runs: list = []
    offset = 0
    page_size = min(200, max(1, top_n))
    first_call = True

    while offset < top_n:
        params = {
            "category": cat_id,
            "max": page_size,
            "offset": offset,
            "orderby": "submitted",
            "direction": "desc",
            "embed": "players,platform",
        }
        if status:
            params["status"] = status

        print(f"    → GET runs?category={cat_id}&offset={offset}&max={page_size}"
              + (f"&status={status}" if status else ""))
        data = api_get("runs", params=params)
        if data is None:
            # Persistent failure.
            if first_call:
                return None
            return runs  # subsequent page failed — return partial.
        first_call = False

        page = data.get("data", []) or []
        if not page:
            break  # legitimately empty (end of result set)

        runs.extend(page)

        if len(runs) >= top_n:
            runs = runs[:top_n]
            break
        if len(page) < page_size:
            break  # short page ⇒ no more results
        offset += len(page)

    return runs


# ---------------------------------------------------------------------------
# Run transformation
# ---------------------------------------------------------------------------

def transform_run(raw: dict, game_label: str, cat_name: str,
                  var_id_to_name: dict, val_label_cache: dict) -> dict:
    """Map a raw Speedrun.com run dict to the website record schema.

    ``val_label_cache`` maps ``(variable_id, value_id) -> human label``,
    so we can resolve ``raw["values"]`` (which contains only IDs) to
    readable strings like ``"1.16.1"`` or ``"Random Seed"``.
    """
    times = raw.get("times") or {}
    primary_t = float(times.get("primary_t") or 0.0)
    primary_disp = format_time_display(times.get("primary"))

    status_obj = raw.get("status") or {}
    verified = (status_obj.get("status") == "verified")

    comment = raw.get("comment") or ""
    seed = extract_seed(comment)

    # Resolve variable values to human-readable labels where possible.
    version = None
    seed_type = None
    raw_values = raw.get("values") or {}
    for var_id, val_id in raw_values.items():
        var_name = (var_id_to_name.get(var_id) or "").lower()
        label = val_label_cache.get((var_id, val_id), val_id)
        if "version" in var_name and not version:
            version = label
        elif "seed" in var_name and not seed_type:
            seed_type = label

    return {
        "id":           raw.get("id"),
        "weblink":      raw.get("weblink"),
        "category":     cat_name,
        "platform":     game_label,        # "Java" | "Bedrock"
        "time_primary": primary_t,
        "time_display": primary_disp,
        "date":         raw.get("date"),
        "players":      parse_player_names(raw.get("players")),
        "seed":         seed,
        "verified":     verified,
        # Bonus fields (NOT video_url — that's deliberately excluded):
        "version":      version,
        "seed_type":    seed_type,
    }


# ---------------------------------------------------------------------------
# Safe file IO (atomic + never-overwrite-on-failure)
# ---------------------------------------------------------------------------

def safe_write_json(path: Path, payload) -> bool:
    """Atomically write ``payload`` to ``path``.

    Writes to a ``.tmp`` sidecar first, then ``os.replace`` onto the
    target — so a SIGKILL / disk-full mid-write never leaves a
    half-written JSON.  On any IO error, returns False WITHOUT
    touching the existing file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        return True
    except Exception as e:
        print(f"  ✗ write to {path} failed: {e}", file=sys.stderr)
        try:
            if tmp.exists():
                tmp.unlink()
        except Exception:
            pass
        return False


def load_existing_config(config_path: Path) -> dict:
    """Load the previous config.json so we can merge (never blow away
    unknown future keys the website may have added)."""
    if not config_path.exists():
        return {}
    try:
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--output", default="website/src/data/speedrun/",
                   help="Output directory (default: website/src/data/speedrun/)")
    p.add_argument("--top", type=int, default=100,
                   help="Max runs per category (default 100)")
    p.add_argument("--status", default="verified",
                   help="Run-status filter: verified|new|rejected|'' (all)")
    p.add_argument("--include-misc", action="store_true",
                   help="Include miscellaneous sub-categories (default: skip)")
    p.add_argument("--game", default=None,
                   help="Only fetch the named game (java|bedrock); default: both")
    args = p.parse_args(argv)

    out_root = Path(args.output).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    config_path = out_root / "config.json"

    started_at = _dt.datetime.now(_dt.timezone.utc)
    print(f"🚀  Speedrun fetcher")
    print(f"    Output dir: {out_root}")
    print(f"    Top per category: {args.top}")
    print(f"    Status filter: {args.status or 'none (all)'}")
    print(f"    Include misc:    {args.include_misc}")
    if args.game:
        print(f"    Only game: {args.game}")

    summary = {
        "fetched_at":     started_at.isoformat(),
        "top_per_cat":    args.top,
        "status_filter":  args.status,
        "include_misc":   args.include_misc,
        "games":           {},
        "categories":      {"java": [], "bedrock": []},
        "runs_total":      0,
        "files_written":   0,
        "files_preserved": 0,  # existing files we didn't overwrite
        "errors":          [],
    }

    config = {
        "generated_at": started_at.isoformat(),
        "api_base":     API_BASE,
        "games":        GAMES,
        "categories":   {"java": [], "bedrock": []},
        "variables":    {"java": {}, "bedrock": {}},  # cat_id -> [var,...]
    }

    # Merge in any unknown future keys from the prior config.json.
    existing_config = load_existing_config(config_path)
    for k, v in existing_config.items():
        if k not in config:
            config[k] = v

    for game_key, game_info in GAMES.items():
        if args.game and args.game != game_key:
            continue

        print(f"\n=== {game_info['label']} (game_id={game_info['id']}) ===")
        cats = fetch_categories(game_info["id"])
        print(f"  {len(cats)} categories found")

        cat_records = []
        var_records: dict = {}
        val_label_cache: dict = {}    # (var_id, val_id) -> label
        runs_collected = 0
        files_written = 0
        files_preserved = 0

        for cat in cats:
            cat_id   = cat["id"]
            cat_name = cat["name"]
            is_misc  = bool(cat.get("miscellaneous", False))
            slug     = slugify(cat_name)

            if is_misc and not args.include_misc:
                print(f"  • skip misc: {cat_name}")
                cat_records.append({
                    "id":            cat_id,
                    "name":          cat_name,
                    "slug":          slug,
                    "miscellaneous": True,
                    "runs_file":     None,
                    "runs_count":    0,
                    "skipped":       True,
                })
                continue

            print(f"  • {cat_name} ({cat_id})  [misc={is_misc}]")

            # Fetch variables (cache labels for run transformation).
            variables = fetch_category_variables(cat_id)
            var_id_to_name: dict = {}
            cat_var_record = []
            for v in variables:
                v_id   = v["id"]
                v_name = v.get("name", "")
                var_id_to_name[v_id] = v_name
                # Speedrun.com wraps the value-id mapping in
                # ``v["values"]["values"]`` (the outer ``values`` is a
                # deprecation envelope that also carries ``_note``,
                # ``choices`` (legacy), and ``default``).  Drill in.
                values_outer = v.get("values") or {}
                if isinstance(values_outer, dict):
                    values_map = values_outer.get("values") or {}
                else:
                    values_map = {}
                value_labels = {}
                for val_id, val_obj in values_map.items():
                    if isinstance(val_obj, dict):
                        label = val_obj.get("label", val_id)
                    else:
                        label = str(val_obj)
                    value_labels[val_id] = label
                    val_label_cache[(v_id, val_id)] = label
                cat_var_record.append({
                    "id":     v_id,
                    "name":   v_name,
                    "scope":  "category" if v.get("category") else "game",
                    "values": value_labels,
                })
            var_records[cat_id] = cat_var_record

            # Fetch runs.
            runs_raw = fetch_runs_for_category(
                cat_id, top_n=args.top, status=args.status,
            )

            if runs_raw is None:
                # API failure — preserve the previous JSON if any.
                existing_file = out_root / game_key / f"{slug}.json"
                if existing_file.exists():
                    files_preserved += 1
                    print(f"    ✗ API failed — preserved existing "
                          f"{existing_file.relative_to(out_root)}")
                else:
                    print(f"    ✗ API failed — no previous file to preserve")
                summary["errors"].append({
                    "game":     game_key,
                    "category": cat_name,
                    "cat_id":   cat_id,
                    "error":    "API failure on first page (preserved existing)",
                })
                cat_records.append({
                    "id":            cat_id,
                    "name":          cat_name,
                    "slug":          slug,
                    "miscellaneous": is_misc,
                    "runs_file":     f"{game_key}/{slug}.json" if existing_file.exists() else None,
                    "runs_count":    0,
                    "preserved":     existing_file.exists(),
                })
                continue

            runs_clean = [
                transform_run(r, game_info["label"], cat_name,
                               var_id_to_name, val_label_cache)
                for r in runs_raw
            ]
            runs_collected += len(runs_clean)
            print(f"    fetched {len(runs_raw)} runs → "
                  f"{len(runs_clean)} clean records")

            out_file = out_root / game_key / f"{slug}.json"
            payload = {
                "game":           game_key,
                "game_label":     game_info["label"],
                "category_id":    cat_id,
                "category_name":  cat_name,
                "category_slug":  slug,
                "miscellaneous":  is_misc,
                "fetched_at":     started_at.isoformat(),
                "count":          len(runs_clean),
                "runs":           runs_clean,
            }
            if safe_write_json(out_file, payload):
                files_written += 1
                rel = out_file.relative_to(out_root)
                print(f"    ✓ wrote {rel} ({len(runs_clean)} runs)")
            cat_records.append({
                "id":            cat_id,
                "name":          cat_name,
                "slug":          slug,
                "miscellaneous": is_misc,
                "runs_file":     f"{game_key}/{slug}.json",
                "runs_count":    len(runs_clean),
            })

        config["categories"][game_key] = cat_records
        config["variables"][game_key]   = var_records

        summary["games"][game_key] = {
            "label":              game_info["label"],
            "game_id":            game_info["id"],
            "categories_count":   len(cats),
            "categories_processed": sum(1 for c in cat_records
                                        if not c.get("skipped")),
            "runs_collected":     runs_collected,
            "files_written":      files_written,
            "files_preserved":    files_preserved,
        }
        summary["runs_total"]      += runs_collected
        summary["files_written"]   += files_written
        summary["files_preserved"] += files_preserved
        summary["categories"][game_key] = [
            {
                "id":         c["id"],
                "name":       c["name"],
                "slug":       c["slug"],
                "misc":       c.get("miscellaneous", False),
                "runs_file":  c.get("runs_file"),
                "runs_count": c.get("runs_count", 0),
            }
            for c in cat_records if not c.get("skipped")
        ]

    # Always safe to (over)write config.json — it's metadata, not run data.
    safe_write_json(config_path, config)
    print(f"\n✓ wrote {config_path.relative_to(out_root) if config_path.is_relative_to(out_root) else config_path}")

    summary_path = out_root / "summary.json"
    safe_write_json(summary_path, summary)
    print(f"✓ wrote {summary_path.relative_to(out_root) if summary_path.is_relative_to(out_root) else summary_path}")

    print(f"\n✅ Done. {summary['runs_total']} runs across "
          f"{summary['files_written']} files "
          f"({summary['files_preserved']} preserved on failure).")

    if summary["errors"]:
        print(f"⚠ {len(summary['errors'])} errors:")
        for e in summary["errors"][:10]:
            print(f"  - [{e.get('game', '?')}] {e.get('category', '?')}: "
                  f"{e.get('error', '?')}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
