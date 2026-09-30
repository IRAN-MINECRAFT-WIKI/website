"""
MineBed Admin — FastAPI application.

Serves the static UI (HTML/CSS/JS) and exposes a small JSON API that the
front-end talks to.  All routes are designed to be called from the same
origin (pywebview points at 127.0.0.1:8000), so there are no CORS concerns.
"""
from __future__ import annotations

import contextlib
import datetime as _dt
import json
import os
import threading
import time
import traceback
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    PlainTextResponse,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config, crawler, agnes, github_service, mods, auth, uploader


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
UI_DIR = (Path(__file__).resolve().parent.parent / "ui").resolve()


# ---------------------------------------------------------------------------
# Autofetch background-task state
# ---------------------------------------------------------------------------
class AutofetchState:
    """
    Single shared state object for the background autofetch worker.

    We don't use Celery or a queue — just a thread + a lock + a log buffer.
    The front-end polls ``GET /api/autofetch/status`` to read the latest
    log lines + review queue.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.reset()

    def reset(self) -> None:
        self.running: bool = False
        self.stop_requested: bool = False
        self.log: list[dict] = []      # [{t, phase, msg}]
        self.queue: list[dict] = []    # review queue of built mod records
        self.processed: int = 0
        self.total: int = 0
        self.started_at: Optional[float] = None
        self.finished_at: Optional[float] = None
        self.error: Optional[str] = None

    # ---- log -----------------------------------------------------------
    def append_log(self, phase: str, msg: str) -> None:
        with self._lock:
            self.log.append({
                "t": _dt.datetime.now().isoformat(timespec="seconds"),
                "phase": phase,
                "msg": msg,
            })
            # keep the last 500 entries
            if len(self.log) > 500:
                self.log = self.log[-500:]

    # ---- queue ---------------------------------------------------------
    def enqueue(self, mod: dict) -> None:
        with self._lock:
            # avoid dupes by id
            mid = str(mod.get("id") or mod.get("slug") or "")
            for i, q in enumerate(self.queue):
                if str(q.get("id") or q.get("slug") or "") == mid:
                    self.queue[i] = mod
                    return
            self.queue.append(mod)

    def remove_from_queue(self, mod_id: str) -> None:
        with self._lock:
            self.queue = [q for q in self.queue
                          if str(q.get("id") or q.get("slug") or "") != str(mod_id)]

    # ---- snapshot ------------------------------------------------------
    def snapshot(self) -> dict:
        with self._lock:
            return {
                "running": self.running,
                "processed": self.processed,
                "total": self.total,
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "error": self.error,
                "log": list(self.log[-200:]),
                "queue": list(self.queue),
            }

    # ---- progress (worker-only writes; lock-guarded) -------------------
    def set_progress(self, processed: int, total: Optional[int] = None) -> None:
        """Update processed/total counters under the lock."""
        with self._lock:
            self.processed = int(processed)
            if total is not None:
                self.total = int(total)

    # ---- start ---------------------------------------------------------
    def start(self, count: int) -> bool:
        with self._lock:
            if self.running:
                return False
            self.reset()
            self.running = True
            self.stop_requested = False
            self.total = int(count)
            self.started_at = time.time()
        t = threading.Thread(target=_autofetch_worker, args=(self, int(count)),
                             daemon=True, name="autofetch")
        t.start()
        return True

    def stop(self) -> None:
        with self._lock:
            self.stop_requested = True

    def is_stop_requested(self) -> bool:
        with self._lock:
            return self.stop_requested

    def mark_done(self, error: Optional[str] = None) -> None:
        with self._lock:
            self.running = False
            self.finished_at = time.time()
            self.error = error


STATE = AutofetchState()


# ---------------------------------------------------------------------------
# Autofetch worker (background thread)
# ---------------------------------------------------------------------------
def _autofetch_worker(state: AutofetchState, count: int) -> None:
    """Runs in a daemon thread; mutates ``state`` as it progresses.

    For each discovered MCPEDL URL the worker:
      1. Crawls the mod page (JSON API + HTML enrichment)
      2. Generates Persian content via Agnes AI
      3. Builds a mod record (in the website's Mod shape)
      4. Mirrors cover/gallery/mod-file to HuggingFace (so Iranian users
         aren't dependent on MCPEDL's CDN)
      5. Enqueues the enriched record for review
    """
    try:
        state.append_log("init", f"Auto-Fetch started for {count} mods")
        # 1. Discover URLs
        def progress(phase: str, msg: str) -> None:
            state.append_log(phase, msg)

        urls = crawler.fetch_top_mods(count=count, on_progress=progress)
        state.append_log("discover",
                         f"Found {len(urls)} candidate URLs from MCPEDL")
        # Dedup against already-saved mods
        existing = {m.get("slug") or m.get("id") for m in mods.list_all()}
        urls = [u for u in urls if crawler._slug_from_url(u) not in existing]
        state.append_log("discover",
                         f"{len(urls)} URLs left after dedup (skipped "
                         f"{count - len(urls)} already-saved)")

        if not urls:
            state.append_log("done", "No new mods to fetch — all already saved.")
            state.mark_done()
            return

        state.set_progress(processed=0, total=len(urls))
        for i, url in enumerate(urls, 1):
            if state.is_stop_requested():
                state.append_log("stop", "User requested stop")
                break
            state.set_progress(processed=i - 1)
            state.append_log("crawl", f"[{i}/{len(urls)}] {url}")
            try:
                page = crawler.crawl_mod(url, on_progress=progress)
                if not page:
                    state.append_log("crawl", "  ! empty page, skipping")
                    continue
                state.append_log("ai", f"  → generating Persian content …")
                ai = agnes.generate_mod_content(page, on_progress=progress)
                record = mods.build_mod_record(page, ai)

                # Mirror assets to HuggingFace (non-fatal on failure)
                if config.HF_TOKEN and uploader.HF_AVAILABLE:
                    state.append_log("upload",
                                     f"  → mirroring assets to HuggingFace …")
                    try:
                        record = uploader.process_mod_assets(
                            record, on_progress=progress,
                        )
                    except Exception as ue:
                        state.append_log("upload",
                                         f"  ! asset mirror failed: {ue}")
                else:
                    state.append_log("upload",
                                     "  ~ HuggingFace not configured — "
                                     "keeping MCPEDL URLs")

                state.enqueue(record)
                state.append_log("ai",
                                 f"  ✓ queued «{record.get('nameFa')}» "
                                 f"(AI={'yes' if ai.get('_ai_used') else 'no'})")
            except Exception as e:
                state.append_log("error", f"  ! error: {e}")
                state.append_log("error", traceback.format_exc()[-300:])

            state.set_progress(processed=i)

        state.append_log("done",
                         f"Finished — {len(state.queue)} mods ready for review")
    except Exception as e:
        state.append_log("fatal", f"Worker crashed: {e}")
        state.append_log("fatal", traceback.format_exc()[-400:])
        state.mark_done(error=str(e))
        return
    state.mark_done()


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
def _make_app() -> FastAPI:
    """Build the FastAPI app with a lifespan handler (replaces deprecated
    ``@app.on_event("startup")``)."""
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        # ---- startup ----
        if not auth.is_auth_enabled():
            print("\n" + "=" * 60)
            print("⚠️  WARNING: ADMIN_SECRET is not set — admin running in OPEN mode")
            print("   Anyone with localhost access can read/update mods.json + tokens.")
            print("   Set ADMIN_SECRET in .env to enable auth.")
            print("=" * 60 + "\n")
        try:
            config.MODS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
            if not config.MODS_JSON_PATH.exists():
                config.MODS_JSON_PATH.write_text('{"mods": []}', encoding="utf-8")
        except Exception:
            pass
        yield
        # ---- shutdown ---- (daemon threads die with us — nothing to clean up)

    return FastAPI(title="MineBed Admin", version="1.1.0", lifespan=lifespan)


app = _make_app()


# ---------------------------------------------------------------------------
# Authentication middleware — protects all /api/* routes with a shared
# secret if ADMIN_SECRET env var is set. Open mode (no token) is allowed
# for local dev convenience but logs a warning.
# ---------------------------------------------------------------------------
@app.middleware("http")
async def _auth_mw(request: Request, call_next):
    return await auth.auth_middleware(request, call_next)


# ---------------------------------------------------------------------------
# Pydantic models for request bodies
# ---------------------------------------------------------------------------
class AutofetchStart(BaseModel):
    count: int = Field(10, ge=1, le=50)


class CrawlRequest(BaseModel):
    url: str


class ApproveRequest(BaseModel):
    """Approve a single mod record (already enriched with AI content)."""
    mod: dict
    push: bool = True


class SettingsUpdate(BaseModel):
    AGNES_API_KEY: Optional[str] = None
    AGNES_BASE_URL: Optional[str] = None
    AGNES_MODEL: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_USER: Optional[str] = None
    GITHUB_REPO: Optional[str] = None
    GITHUB_BRANCH: Optional[str] = None
    HF_TOKEN: Optional[str] = None
    HF_REPO_ID: Optional[str] = None
    ADMIN_SECRET: Optional[str] = None
    ASTRO_DATA_PATH: Optional[str] = None
    MODS_JSON_PATH: Optional[str] = None


# ---------------------------------------------------------------------------
# UI routes — serve the SPA shell + static assets
# ---------------------------------------------------------------------------
@app.get("/")
def ui_index() -> FileResponse:
    return FileResponse(UI_DIR / "index.html", media_type="text/html")


@app.get("/style.css")
def ui_style() -> FileResponse:
    return FileResponse(UI_DIR / "style.css", media_type="text/css")


@app.get("/app.js")
def ui_script() -> FileResponse:
    return FileResponse(UI_DIR / "app.js",
                        media_type="application/javascript")


# Fonts (optional; may not exist)
@app.get("/fonts/{name}")
def ui_font(name: str) -> FileResponse:
    p = UI_DIR / "fonts" / name
    if not p.exists():
        raise HTTPException(404, "font not found")
    media = "font/woff2" if name.endswith(".woff2") else "application/octet-stream"
    return FileResponse(p, media_type=media)


# Static mounts (so any other asset under /ui is reachable)
app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui-static")


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "ts": _dt.datetime.now().isoformat(timespec="seconds"),
        "auth_enabled": auth.is_auth_enabled(),
    }


# ---- Authentication --------------------------------------------------------
class LoginRequest(BaseModel):
    token: str


@app.post("/api/auth/login")
def auth_login(body: LoginRequest) -> dict:
    """Verify an admin token. Returns ok/fail + mode."""
    return auth.check_login(body.token)


@app.get("/api/auth/status")
def auth_status() -> dict:
    """Check whether the admin requires authentication."""
    return {
        "auth_enabled": auth.is_auth_enabled(),
        "mode": "token" if auth.is_auth_enabled() else "open",
    }


@app.get("/api/dashboard")
def dashboard() -> dict:
    """Stats cards + service badges for the dashboard page."""
    all_mods = mods.list_all()
    ai_count = sum(1 for m in all_mods if m.get("aiGenerated"))

    # Service status probes (cheap, non-fatal)
    agnes_status = agnes.test_connection()
    gh_status = github_service.test_connection()

    # Seeds: if a seeds.json exists in the same dir, count it.
    # The Astro website stores seeds as ``{"seeds": [...]}`` (same shape
    # as mods.json), so we have to unwrap the wrapper before counting.
    seeds_path = config.MODS_JSON_PATH.parent / "seeds.json"
    seeds_count = 0
    if seeds_path.exists():
        try:
            raw = json.loads(seeds_path.read_text("utf-8"))
            if isinstance(raw, dict):
                seeds_count = len(raw.get("seeds") or raw.get("data") or [])
            elif isinstance(raw, list):
                seeds_count = len(raw)
        except Exception:
            seeds_count = 0

    # Versions count (same wrapper pattern)
    versions_path = config.MODS_JSON_PATH.parent / "versions.json"
    versions_count = 0
    if versions_path.exists():
        try:
            raw = json.loads(versions_path.read_text("utf-8"))
            if isinstance(raw, dict):
                versions_count = len(raw.get("versions") or raw.get("data") or [])
            elif isinstance(raw, list):
                versions_count = len(raw)
        except Exception:
            versions_count = 0

    return {
        "mods_count": len(all_mods),
        "ai_mods_count": ai_count,
        "seeds_count": seeds_count,
        "versions_count": versions_count,
        "services": {
            "agnes": {
                "ok": agnes_status.get("ok", False),
                "detail": agnes_status,
            },
            "github": {
                "ok": gh_status.get("ok", False),
                "detail": gh_status,
            },
            "huggingface": {
                "ok": bool(config.HF_TOKEN),
                "detail": {"configured": bool(config.HF_TOKEN),
                           "repo": os.getenv("HF_REPO_ID", "")},
            },
        },
        "data_path": str(config.MODS_JSON_PATH),
        "astro_data_path": str(config.ASTRO_DATA_PATH),
        "autofetch_running": STATE.running,
    }


# ---- Auto-Fetch --------------------------------------------------------
@app.post("/api/autofetch/start")
def autofetch_start(body: AutofetchStart) -> dict:
    started = STATE.start(body.count)
    return {"ok": started, "running": STATE.running,
            "total": STATE.total, "message": "Already running" if not started else "Started"}


@app.post("/api/autofetch/stop")
def autofetch_stop() -> dict:
    STATE.stop()
    return {"ok": True, "message": "Stop requested"}


@app.get("/api/autofetch/status")
def autofetch_status() -> dict:
    return STATE.snapshot()


@app.post("/api/autofetch/reset")
def autofetch_reset() -> dict:
    STATE.reset()
    return {"ok": True}


# ---- Single URL crawl --------------------------------------------------
@app.post("/api/crawl")
def crawl_single(body: CrawlRequest) -> dict:
    """Crawl one MCPEDL URL and run Agnes AI; return the built record."""
    url = (body.url or "").strip()
    if not url:
        raise HTTPException(400, "url is required")
    if "mcpedl.com" not in url:
        # Accept bare slug too
        url = config.MCPEDL_BASE_URL.rstrip("/") + "/" + url.lstrip("/")
    page = crawler.crawl_mod(url)
    if not page:
        raise HTTPException(502, "Failed to fetch the page")
    ai = agnes.generate_mod_content(page)
    record = mods.build_mod_record(page, ai)
    return {"ok": True, "mod": record, "page": page, "ai": ai}


# ---- Mods CRUD ---------------------------------------------------------
@app.get("/api/mods")
def mods_list() -> dict:
    return {"mods": mods.list_all(), "count": mods.count()}


@app.get("/api/mods/{mod_id}")
def mods_get(mod_id: str) -> dict:
    m = mods.get(mod_id)
    if not m:
        raise HTTPException(404, "mod not found")
    return {"mod": m}


@app.delete("/api/mods/{mod_id}")
def mods_delete(mod_id: str) -> dict:
    ok = mods.delete(mod_id)
    return {"ok": ok}


# ---- Approve a queued/edited mod --------------------------------------
@app.post("/api/mods/approve")
def mods_approve(body: ApproveRequest) -> dict:
    """Save a mod to mods.json (and optionally push to GitHub).

    The mod record is normalized to the website's ``Mod`` shape before
    saving — this prevents accidentally storing an array ``keywords``
    field or a missing ``catName``.
    """
    normalized = mods.normalize_mod(body.mod)
    saved = mods.add(normalized)
    push_result = None
    if body.push:
        push_result = github_service.push_mods_json(
            mods.export_json(),
            message=f"chore: add/updated mod «{saved.get('nameFa') or saved.get('id')}»"
                    f" ({_dt.datetime.now():%Y-%m-%d %H:%M})",
        )
    return {"ok": True, "mod": saved, "push": push_result}


@app.post("/api/mods/save-all")
def mods_save_all() -> dict:
    """Persist the current mods.json to GitHub."""
    push_result = github_service.push_mods_json(
        mods.export_json(),
        message=f"chore: update mods.json ({_dt.datetime.now():%Y-%m-%d %H:%M})",
    )
    return push_result


@app.post("/api/mods/{mod_id}/reject")
def mods_reject(mod_id: str) -> dict:
    STATE.remove_from_queue(mod_id)
    return {"ok": True}


# ---- Bulk operations --------------------------------------------------
class BulkAction(BaseModel):
    """Request body for ``POST /api/mods/bulk``.

    ``action`` is one of: delete | feature | unfeature | setNew | unsetNew
    | setCategory.  ``ids`` is a list of mod IDs.  ``value`` is the new
    value for setCategory (e.g. ``"gameplay"``).
    """
    action: str = Field(..., description="delete|feature|unfeature|setNew|unsetNew|setCategory")
    ids: list[str] = Field(default_factory=list)
    value: Optional[str] = None  # for setCategory
    push: bool = True


@app.post("/api/mods/bulk")
def mods_bulk(body: BulkAction) -> dict:
    """Apply a bulk action to multiple mods.

    Returns ``{"ok": bool, "affected": int, "push": dict | None}``.
    """
    all_mods = mods.list_all()
    id_set = {str(i) for i in body.ids}
    if not id_set:
        return {"ok": False, "error": "no ids provided", "affected": 0}

    affected = 0

    if body.action == "delete":
        kept: list[dict] = []
        for m in all_mods:
            mid = str(m.get("id") or m.get("slug") or "")
            if mid in id_set:
                affected += 1
            else:
                kept.append(m)
        mods._save(kept)
    elif body.action in ("feature", "unfeature", "setNew", "unsetNew"):
        if body.action in ("feature", "unfeature"):
            field = "featured"
        else:
            field = "isNew"
        is_on = body.action in ("feature", "setNew")
        for m in all_mods:
            mid = str(m.get("id") or m.get("slug") or "")
            if mid in id_set:
                m[field] = is_on
                affected += 1
        mods._save(all_mods)
    elif body.action == "setCategory":
        if not body.value:
            return {"ok": False, "error": "value required for setCategory",
                    "affected": 0}
        cat_map = {
            "gameplay": "گیم\u200cپلی", "graphics": "گرافیک",
            "maps": "مپ", "mobs": "موجودات", "decoration": "دکوراسیون",
            "world": "دنیا", "utility": "ابزار",
        }
        cat_name = cat_map.get(body.value, body.value)
        for m in all_mods:
            mid = str(m.get("id") or m.get("slug") or "")
            if mid in id_set:
                m["category"] = body.value
                m["catName"] = cat_name
                affected += 1
        mods._save(all_mods)
    else:
        return {"ok": False, "error": f"unknown action: {body.action}",
                "affected": 0}

    push_result = None
    if body.push and affected:
        push_result = github_service.push_mods_json(
            mods.export_json(),
            message=f"chore: bulk {body.action} on {affected} mods "
                    f"({_dt.datetime.now():%Y-%m-%d %H:%M})",
        )
    return {"ok": True, "affected": affected, "push": push_result}


# ---- Settings ---------------------------------------------------------
def _masked_settings() -> dict:
    """Return config.as_dict() with all secret fields masked (for UI display)."""
    cfg = config.as_dict()
    masked = dict(cfg)
    masked["AGNES_API_KEY"] = config.mask(cfg.get("AGNES_API_KEY", ""))
    masked["GITHUB_TOKEN"] = config.mask(cfg.get("GITHUB_TOKEN", ""))
    masked["HF_TOKEN"] = config.mask(cfg.get("HF_TOKEN", ""))
    masked["ADMIN_SECRET"] = config.mask(cfg.get("ADMIN_SECRET", ""))
    return masked


@app.get("/api/settings")
def settings_get() -> dict:
    return {
        "settings": _masked_settings(),
        "env_path": str(config.ENV_PATH),
        "env_exists": config.ENV_PATH.exists(),
    }


@app.put("/api/settings")
def settings_put(body: SettingsUpdate) -> dict:
    """Update settings — but never accept masked (``***``) values for
    secret fields, since those are placeholder redactions from the UI."""
    raw = body.model_dump(exclude_none=True)
    cleaned: dict = {}
    secret_fields = {"AGNES_API_KEY", "GITHUB_TOKEN", "HF_TOKEN", "ADMIN_SECRET"}
    for k, v in raw.items():
        if k in secret_fields and isinstance(v, str) and "*" in v:
            # Skip — user submitted the masked placeholder unchanged
            continue
        if v is None or (isinstance(v, str) and not v.strip()):
            # Don't blank out a setting
            continue
        cleaned[k] = v
    if cleaned:
        config.update_from_dict(cleaned)
        # Refresh live clients
        agnes._client = None
    return {"ok": True, "settings": _masked_settings()}


# ---- Crawler helpers --------------------------------------------------
@app.get("/api/crawler/preview")
def crawler_preview(count: int = 10) -> dict:
    """Return the URLs that would be fetched (no crawling).

    Also marks which ones are already saved so the UI can show a "skip" badge.
    """
    urls = crawler.fetch_top_mods(count=count)
    existing = {m.get("slug") or m.get("id") for m in mods.list_all()}
    enriched = [
        {"url": u, "slug": crawler._slug_from_url(u),
         "saved": crawler._slug_from_url(u) in existing}
        for u in urls
    ]
    return {"urls": urls, "items": enriched, "count": len(urls)}


# ---- Stats endpoint ---------------------------------------------------
@app.get("/api/stats")
def stats() -> dict:
    """Aggregate stats for the Stats page (downloads, AI usage, etc.)."""
    all_mods = mods.list_all()
    by_cat: dict[str, int] = {}
    by_version: dict[str, int] = {}
    ai_count = 0
    featured_count = 0
    new_count = 0
    total_downloads = 0

    for m in all_mods:
        cat = m.get("category") or "unknown"
        by_cat[cat] = by_cat.get(cat, 0) + 1
        v = m.get("version") or "unknown"
        by_version[v] = by_version.get(v, 0) + 1
        if m.get("aiGenerated"):
            ai_count += 1
        if m.get("featured"):
            featured_count += 1
        if m.get("isNew"):
            new_count += 1
        # downloads is stored as a string ("0" by default) — coerce safely
        try:
            total_downloads += int(m.get("downloads") or 0)
        except (TypeError, ValueError):
            pass

    # Try to load seeds & versions counts (best-effort)
    seeds_path = config.MODS_JSON_PATH.parent / "seeds.json"
    versions_path = config.MODS_JSON_PATH.parent / "versions.json"
    seeds_count = _count_data_file(seeds_path, "seeds")
    versions_count = _count_data_file(versions_path, "versions")

    return {
        "totals": {
            "mods": len(all_mods),
            "ai_mods": ai_count,
            "featured": featured_count,
            "new": new_count,
            "seeds": seeds_count,
            "versions": versions_count,
            "total_downloads": total_downloads,
        },
        "by_category": by_cat,
        "by_version": by_version,
        "services": {
            "agnes": agnes.test_connection(),
            "github": github_service.test_connection(),
            "huggingface": {"configured": bool(config.HF_TOKEN)},
        },
        "ts": _dt.datetime.now().isoformat(timespec="seconds"),
    }


def _count_data_file(path: Path, key: str) -> int:
    """Best-effort count of records in a JSON data file."""
    if not path.exists():
        return 0
    try:
        raw = json.loads(path.read_text("utf-8"))
        if isinstance(raw, dict):
            return len(raw.get(key) or raw.get("data") or [])
        if isinstance(raw, list):
            return len(raw)
    except Exception:
        pass
    return 0


# ---- Log viewer (tail of admin server log) ----------------------------
@app.get("/api/logs")
def logs_tail(lines: int = 200) -> dict:
    """Return the last N lines of the admin server's log file.

    The desktop launcher writes to ``admin/minebed-desktop.log``; when
    running via ``uvicorn`` directly, we fall back to capturing stderr
    via a rotating buffer (set up in main.py module init).
    """
    out: list[str] = []
    log_path = Path(__file__).resolve().parent.parent / "minebed-desktop.log"
    if log_path.exists():
        try:
            all_lines = log_path.read_text(encoding="utf-8",
                                            errors="replace").splitlines()
            out = all_lines[-int(lines):]
        except Exception:
            out = [f"(failed to read log: {log_path})"]
    # Also include the in-memory log buffer (autofetch worker logs)
    if STATE.log:
        out.append("")
        out.append("---- autofetch log ----")
        with STATE._lock:
            for entry in STATE.log[-int(lines):]:
                out.append(f"[{entry.get('t','')}] [{entry.get('phase','')}] "
                            f"{entry.get('msg','')}")
    return {"lines": out, "count": len(out), "log_path": str(log_path)}


@app.get("/api/logs/stream")
async def logs_stream():
    """Server-sent events stream of new log lines (best-effort)."""
    import asyncio
    async def gen():
        last_seen = 0
        while True:
            try:
                lines = []
                log_path = Path(__file__).resolve().parent.parent / "minebed-desktop.log"
                if log_path.exists():
                    all_lines = log_path.read_text(encoding="utf-8",
                                                   errors="replace").splitlines()
                    if len(all_lines) > last_seen:
                        lines = all_lines[last_seen:]
                        last_seen = len(all_lines)
                for ln in lines:
                    yield f"data: {ln}\n\n"
                # Also flush autofetch log entries
                if STATE.log:
                    with STATE._lock:
                        af_lines = [f"[{e.get('t','')}] [{e.get('phase','')}] {e.get('msg','')}"
                                    for e in STATE.log]
                    for ln in af_lines:
                        yield f"data: [autofetch] {ln}\n\n"
            except Exception as e:
                yield f"data: [error] {e}\n\n"
            await asyncio.sleep(2.0)
    return StreamingResponse(gen(), media_type="text/event-stream")


# ---- Mod field update (inline editing) --------------------------------
class FieldUpdate(BaseModel):
    field: str
    value: Any
    push: bool = False


@app.patch("/api/mods/{mod_id}/field")
def mods_update_field(mod_id: str, body: FieldUpdate) -> dict:
    """Update a single field on a mod (used for inline editing).

    Only allows known mod fields to prevent injection of arbitrary keys.
    """
    allowed = {
        "name", "nameFa", "keywords", "category", "catName",
        "tagline", "desc", "icon", "version", "size", "downloads",
        "downloadUrl", "cover", "gallery", "featured", "isNew",
        "author", "updated", "source", "aiGenerated",
    }
    if body.field not in allowed:
        raise HTTPException(400, f"field '{body.field}' is not editable")
    m = mods.get(mod_id)
    if not m:
        raise HTTPException(404, "mod not found")
    m[body.field] = body.value
    # If category changes, also recompute catName
    if body.field == "category":
        cat_map = {
            "gameplay": "گیم\u200cپلی", "graphics": "گرافیک",
            "maps": "مپ", "mobs": "موجودات", "decoration": "دکوراسیون",
            "world": "دنیا", "utility": "ابزار",
        }
        m["catName"] = cat_map.get(str(body.value), str(body.value))
    saved = mods.add(m)
    push_result = None
    if body.push:
        push_result = github_service.push_mods_json(
            mods.export_json(),
            message=f"chore: inline update «{mod_id}».{body.field} "
                    f"({_dt.datetime.now():%Y-%m-%d %H:%M})",
        )
    return {"ok": True, "mod": saved, "push": push_result}


# ---------------------------------------------------------------------------
# Fallback SPA route (so #/dashboard etc. work on refresh)
# IMPORTANT: this catches ALL paths — but we must never serve index.html
# for ``/api/*`` paths (those should 404 cleanly so a typo doesn't
# silently return HTML and confuse the SPA's fetch()).
# ---------------------------------------------------------------------------
@app.get("/{full_path:path}")
def spa_fallback(full_path: str) -> FileResponse:
    if full_path.startswith("api/"):
        raise HTTPException(404, f"API endpoint /{full_path} not found")
    p = UI_DIR / full_path
    if p.is_file():
        return FileResponse(p)
    return FileResponse(UI_DIR / "index.html", media_type="text/html")
