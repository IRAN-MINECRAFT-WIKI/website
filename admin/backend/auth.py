"""
MineBed Admin — Lightweight authentication module.

Provides a simple shared-secret API key check. The desktop app pywebview
points at 127.0.0.1:8000 from the same machine, so this is primarily
defence-in-depth against accidental exposure on a shared host.

The admin token is read from environment variable ``ADMIN_API_KEY`` (or
``.env``). If unset, the admin runs in "no-auth" mode and emits a
warning at startup — useful for local dev but should never be used in
any kind of network-accessible deployment.

Usage (in main.py):

    from . import auth
    app.include_router(auth.router)
    # OR for direct middleware:
    @app.middleware("http")
    async def auth_middleware(request, call_next):
        return await auth.middleware(request, call_next)
"""
from __future__ import annotations

import os
import secrets
from typing import Optional

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
def get_admin_token() -> Optional[str]:
    """Return the admin API token from env, or None if not set."""
    return os.getenv("ADMIN_API_KEY") or None


def is_auth_enabled() -> bool:
    return get_admin_token() is not None


def _extract_token(request: Request) -> Optional[str]:
    """Pull token from header ``Authorization: Bearer <token>``
    OR ``X-Admin-Key: <token>`` OR query string ``?key=<token>``."""
    auth_header = request.headers.get("authorization") or ""
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    x_key = request.headers.get("x-admin-key")
    if x_key:
        return x_key.strip()
    return request.query_params.get("key")


# ---------------------------------------------------------------------------
# Public paths (don't require auth)
# ---------------------------------------------------------------------------
PUBLIC_PATHS = (
    "/", "/style.css", "/app.js", "/favicon.ico",
    "/api/health",       # basic liveness probe
    "/api/auth/login",   # token exchange
)
PUBLIC_PATH_PREFIXES = (
    "/fonts/",           # static fonts
    "/ui/",              # static UI assets
    "/_debug",           # debug
)


def is_public(path: str) -> bool:
    if path in PUBLIC_PATHS:
        return True
    return any(path.startswith(p) for p in PUBLIC_PATH_PREFIXES)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
async def auth_middleware(request: Request, call_next):
    """Starlette/FastAPI middleware that checks the admin token on every request."""
    if not is_auth_enabled():
        # No token configured → open mode (local dev only)
        return await call_next(request)

    if is_public(request.url.path):
        return await call_next(request)

    token = _extract_token(request)
    expected = get_admin_token()
    if not token or not secrets.compare_digest(token or "", expected or ""):
        return JSONResponse(
            status_code=401,
            content={"ok": False, "error": "Unauthorized — admin token required"},
        )

    return await call_next(request)


# ---------------------------------------------------------------------------
# Manual login endpoint (returns masked-OK to confirm token works)
# ---------------------------------------------------------------------------
def check_login(token: str) -> dict:
    """Verify a token — returns ok/fail dict for the UI."""
    expected = get_admin_token()
    if not expected:
        # No token configured → "open mode" — always return ok
        return {"ok": True, "mode": "open", "message": "No ADMIN_API_KEY set — running in open mode"}
    if not token:
        return {"ok": False, "error": "Missing token"}
    if secrets.compare_digest(token, expected):
        return {"ok": True, "mode": "token", "message": "Authenticated"}
    return {"ok": False, "error": "Invalid token"}
