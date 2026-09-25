"""
MineBed Admin — configuration loader.

Reads the .env file located one directory above the `admin/` package root
and exposes all settings as module-level constants.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
# This file lives at: admin/backend/config.py
# Project layout:
#   <repo>/
#     .env                 <-- shared config
#     admin/
#       minebed-desktop.py
#       backend/
#         config.py        <-- here
#       ui/
# The spec says "one level up from admin/" but the file-structure tree
# also shows .env inside admin/. We look in BOTH locations, preferring
# the one that exists. This makes the loader robust to either layout.
# ---------------------------------------------------------------------------
_THIS_DIR = Path(__file__).resolve().parent          # .../admin/backend
_ADMIN_DIR = _THIS_DIR.parent                         # .../admin
_REPO_DIR = _ADMIN_DIR.parent                         # <repo>

ENV_PATHS = [_REPO_DIR / ".env", _ADMIN_DIR / ".env"]
ENV_PATH = next((p for p in ENV_PATHS if p.exists()), _REPO_DIR / ".env")

# Load .env if present (silent otherwise — falls back to OS env)
for _candidate in ENV_PATHS:
    if _candidate.exists():
        load_dotenv(dotenv_path=_candidate, override=False)
        ENV_PATH = _candidate
        break


def _get(key: str, default: str = "") -> str:
    """Return a config value from env (already loaded from .env)."""
    return os.getenv(key, default).strip()


def _get_bool(key: str, default: bool = False) -> bool:
    val = _get(key, "").lower()
    if not val:
        return default
    return val in ("1", "true", "yes", "on")


# ---------------------------------------------------------------------------
# Agnes AI
# ---------------------------------------------------------------------------
AGNES_API_KEY: str = _get("AGNES_API_KEY")
AGNES_BASE_URL: str = _get("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1")
AGNES_MODEL: str = _get("AGNES_MODEL", "agnes-3.0-flash")

# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------
GITHUB_TOKEN: str = _get("GITHUB_TOKEN")
GITHUB_USER: str = _get("GITHUB_USER", "IRAN-MINECRAFT-WIKI")
GITHUB_REPO: str = _get("GITHUB_REPO", "website")
GITHUB_BRANCH: str = _get("GITHUB_BRANCH", "main")

# ---------------------------------------------------------------------------
# Hugging Face
# ---------------------------------------------------------------------------
HF_TOKEN: str = _get("HF_TOKEN")

# ---------------------------------------------------------------------------
# Data paths
# ---------------------------------------------------------------------------
# Relative paths are resolved relative to the repo root.
def _resolve(p: str) -> Path:
    path = Path(p)
    if not path.is_absolute():
        path = (_REPO_DIR / path).resolve()
    return path


ASTRO_DATA_PATH: Path = _resolve(_get("ASTRO_DATA_PATH", "website/src/data"))
MODS_JSON_PATH: Path = _resolve(_get("MODS_JSON_PATH", "website/src/data/mods.json"))

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
HOST: str = _get("HOST", "127.0.0.1")
PORT: int = int(_get("PORT", "8000"))

# ---------------------------------------------------------------------------
# Crawler
# ---------------------------------------------------------------------------
MCPEDL_BASE_URL: str = "https://mcpedl.com"
CRAWLER_USER_AGENT: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
CRAWLER_TIMEOUT: int = 30  # seconds per HTTP request


def as_dict() -> dict:
    """Return a JSON-friendly snapshot of the current configuration."""
    return {
        "AGNES_API_KEY": AGNES_API_KEY,
        "AGNES_BASE_URL": AGNES_BASE_URL,
        "AGNES_MODEL": AGNES_MODEL,
        "GITHUB_TOKEN": GITHUB_TOKEN,
        "GITHUB_USER": GITHUB_USER,
        "GITHUB_REPO": GITHUB_REPO,
        "GITHUB_BRANCH": GITHUB_BRANCH,
        "HF_TOKEN": HF_TOKEN,
        "ASTRO_DATA_PATH": str(ASTRO_DATA_PATH),
        "MODS_JSON_PATH": str(MODS_JSON_PATH),
        "HOST": HOST,
        "PORT": PORT,
    }


def update_from_dict(values: dict) -> None:
    """
    Update environment variables in-memory and persist them to the .env file.

    This lets the Settings page save tokens without restarting the app —
    subsequent code that reads module-level config will NOT pick up changes
    automatically, so consumers should re-read via ``config.as_dict()`` or
    the helper getters at runtime.  For the things that matter here
    (crawler, agnes, github) we call into this module fresh each request.
    """
    import re

    # 1. Update OS env so live requests pick up new values
    for k, v in values.items():
        if v is None:
            continue
        os.environ[k] = str(v)

    # 2. Re-read module-level constants (cheap; just re-evaluate env)
    g = globals()
    g["AGNES_API_KEY"] = _get("AGNES_API_KEY")
    g["AGNES_BASE_URL"] = _get("AGNES_BASE_URL")
    g["AGNES_MODEL"] = _get("AGNES_MODEL")
    g["GITHUB_TOKEN"] = _get("GITHUB_TOKEN")
    g["GITHUB_USER"] = _get("GITHUB_USER")
    g["GITHUB_REPO"] = _get("GITHUB_REPO")
    g["GITHUB_BRANCH"] = _get("GITHUB_BRANCH")
    g["HF_TOKEN"] = _get("HF_TOKEN")
    g["ASTRO_DATA_PATH"] = _resolve(_get("ASTRO_DATA_PATH", "website/src/data"))
    g["MODS_JSON_PATH"] = _resolve(_get("MODS_JSON_PATH", "website/src/data/mods.json"))

    # 3. Persist to .env file (preserves comments, updates known keys)
    lines: list[str] = []
    existing: dict[str, str] = {}

    if ENV_PATH.exists():
        raw = ENV_PATH.read_text(encoding="utf-8", errors="replace")
        for line in raw.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                lines.append(line)
                continue
            if "=" in stripped:
                k, _, v = stripped.partition("=")
                existing[k.strip()] = v
                lines.append(line)
        # append a blank separator if file did not end with one
        if lines and lines[-1].strip():
            lines.append("")

    known_keys = [
        "AGNES_API_KEY", "AGNES_BASE_URL", "AGNES_MODEL",
        "GITHUB_TOKEN", "GITHUB_USER", "GITHUB_REPO", "GITHUB_BRANCH",
        "HF_TOKEN", "ASTRO_DATA_PATH", "MODS_JSON_PATH",
        "HOST", "PORT",
    ]

    seen: set[str] = set()
    new_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#"):
            k, _, _ = stripped.partition("=")
            k = k.strip()
            if k in known_keys:
                new_val = os.environ.get(k, "")
                new_lines.append(f"{k}={new_val}")
                seen.add(k)
                continue
        new_lines.append(line)

    for k in known_keys:
        if k not in seen:
            new_lines.append(f"{k}={os.environ.get(k, '')}")

    ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
    ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def mask(value: str, keep: int = 6) -> str:
    """Mask a secret for display — shows first ``keep`` chars + ***."""
    if not value:
        return ""
    if len(value) <= keep:
        return value[0] + "*" * (len(value) - 1)
    return value[:keep] + "*" * (len(value) - keep)
