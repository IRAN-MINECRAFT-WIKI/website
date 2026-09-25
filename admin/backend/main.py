"""
MineBed Admin — FastAPI application.

Serves the static UI (HTML/CSS/JS) and exposes a small JSON API that the
front-end talks to.  All routes are designed to be called from the same
origin (pywebview points at 127.0.0.1:8000), so there are no CORS concerns.
"""
from __future__ import annotations

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
)
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config, crawler, agnes, github_service, mods, auth


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
    """Runs in a daemon thread; mutates ``state`` as it progresses."""
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

        state.total = len(urls)
        for i, url in enumerate(urls, 1):
            if state.stop_requested:
                state.append_log("stop", "User requested stop")
                break
            state.processed = i - 1
            state.append_log("crawl", f"[{i}/{state.total}] {url}")
            try:
                page = crawler.crawl_mod(url, on_progress=progress)
                if not page:
                    state.append_log("crawl", "  ! empty page, skipping")
                    continue
                state.append_log("ai", f"  → generating Persian content …")
                ai = agnes.generate_mod_content(page, on_progress=progress)
                record = mods.build_mod_record(page, ai)
                state.enqueue(record)
                state.append_log("ai",
                                 f"  ✓ queued «{record.get('nameFa')}» "
                                 f"(AI={'yes' if ai.get('_ai_used') else 'no'})")
            except Exception as e:
                state.append_log("error", f"  ! error: {e}")
                state.append_log("error", traceback.format_exc()[-300:])

            state.processed = i

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
app = FastAPI(title="MineBed Admin", version="1.0.0")


# ---------------------------------------------------------------------------
# Authentication middleware — protects all /api/* routes with a shared
# secret if ADMIN_API_KEY env var is set. Open mode (no token) is allowed
# for local dev convenience but logs a warning.
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def _warn_open_mode() -> None:
    if not auth.is_auth_enabled():
        print("\n" + "=" * 60)
        print("⚠️  WARNING: ADMIN_API_KEY is not set — admin running in OPEN mode")
        print("   Anyone with localhost access can read/update mods.json + tokens.")
        print("   Set ADMIN_API_KEY in .env to enable auth.")
        print("=" * 60 + "\n")


@app.middleware("http")
async def _auth_mw(request: Request, call_next):
    return await auth.auth_middleware(request, call_next)


@app.on_event("startup")
async def _on_startup() -> None:
    # Ensure mods.json + data dir exist
    try:
        config.MODS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not config.MODS_JSON_PATH.exists():
            config.MODS_JSON_PATH.write_text("[]", encoding="utf-8")
    except Exception:
        pass


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

    # Seeds: if a seeds.json exists in the same dir, count it
    seeds_path = config.MODS_JSON_PATH.parent / "seeds.json"
    seeds_count = 0
    if seeds_path.exists():
        try:
            seeds_count = len(json.loads(seeds_path.read_text("utf-8")))
        except Exception:
            seeds_count = 0

    return {
        "mods_count": len(all_mods),
        "ai_mods_count": ai_count,
        "seeds_count": seeds_count,
        "services": {
            "agnes": {
                "ok": agnes_status.get("ok", False),
                "detail": agnes_status,
            },
            "github": {
                "ok": gh_status.get("ok", False),
                "detail": gh_status,
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
    """Save a mod to mods.json (and optionally push to GitHub)."""
    saved = mods.add(body.mod)
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


# ---- Settings ---------------------------------------------------------
@app.get("/api/settings")
def settings_get() -> dict:
    cfg = config.as_dict()
    # Mask secrets for display
    masked = dict(cfg)
    masked["AGNES_API_KEY"] = config.mask(cfg["AGNES_API_KEY"])
    masked["GITHUB_TOKEN"] = config.mask(cfg["GITHUB_TOKEN"])
    masked["HF_TOKEN"] = config.mask(cfg["HF_TOKEN"])
    return {
        "settings": masked,
        "env_path": str(config.ENV_PATH),
        "env_exists": config.ENV_PATH.exists(),
    }


@app.put("/api/settings")
def settings_put(body: SettingsUpdate) -> dict:
    values = body.model_dump(exclude_none=True)
    config.update_from_dict(values)
    # Refresh live clients
    agnes._client = None
    return {"ok": True, "settings": config.as_dict()}


# ---- Crawler helpers --------------------------------------------------
@app.get("/api/crawler/preview")
def crawler_preview(count: int = 10) -> dict:
    """Return the URLs that would be fetched (no crawling)."""
    urls = crawler.fetch_top_mods(count=count)
    return {"urls": urls, "count": len(urls)}


# ---------------------------------------------------------------------------
# Fallback SPA route (so #/dashboard etc. work on refresh)
# ---------------------------------------------------------------------------
@app.get("/{full_path:path}")
def spa_fallback(full_path: str) -> FileResponse:
    p = UI_DIR / full_path
    if p.is_file():
        return FileResponse(p)
    return FileResponse(UI_DIR / "index.html", media_type="text/html")
