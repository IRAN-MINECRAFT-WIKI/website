"""
MineBed Admin — GitHub service.

Pushes the updated ``mods.json`` file to the configured GitHub repo using
the Git Database REST API (reads SHA → PUT blob).  No git CLI required.

Public API
----------
    push_mods_json(content: str, message: str = None) -> dict
        Update mods.json on GitHub. Returns GitHub API response.

    read_remote_mods_json() -> dict | None
        Fetch current mods.json from GitHub (for diffing / SHA lookup).

    test_connection() -> dict
        Verify the token has access to the repo.
"""
from __future__ import annotations

import base64
import datetime as _dt
from typing import Optional

import requests

from . import config

GITHUB_API = "https://api.github.com"


def _headers() -> dict:
    token = config.GITHUB_TOKEN
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "MineBed-Admin/1.0",
    }


def _repo_path() -> str:
    return f"repos/{config.GITHUB_USER}/{config.GITHUB_REPO}"


def _content_url(path: str) -> str:
    return f"{GITHUB_API}/{_repo_path()}/contents/{path.lstrip('/')}"


def _params() -> dict:
    return {"ref": config.GITHUB_BRANCH}


def test_connection() -> dict:
    """Verify token + repo access."""
    if not config.GITHUB_TOKEN:
        return {"ok": False, "error": "GITHUB_TOKEN not set"}
    try:
        r = requests.get(f"{GITHUB_API}/{_repo_path()}",
                         headers=_headers(), timeout=20)
        if r.status_code == 200:
            data = r.json()
            return {
                "ok": True,
                "repo": data.get("full_name"),
                "branch": config.GITHUB_BRANCH,
                "private": data.get("private"),
                "default_branch": data.get("default_branch"),
            }
        return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:200]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def read_remote_mods_json(path: str = "website/src/data/mods.json") -> Optional[dict]:
    """Fetch the current mods.json from GitHub (returns parsed JSON)."""
    try:
        r = requests.get(_content_url(path),
                         headers=_headers(), params=_params(), timeout=20)
        if r.status_code != 200:
            return None
        body = r.json()
        content = base64.b64decode(body.get("content", "") or "").decode("utf-8",
                                                                          errors="replace")
        import json
        return {
            "sha": body.get("sha"),
            "content": json.loads(content) if content else [],
            "path": body.get("path"),
            "html_url": body.get("html_url"),
        }
    except Exception:
        return None


def push_mods_json(content: str,
                   path: str = "website/src/data/mods.json",
                   message: Optional[str] = None) -> dict:
    """
    PUT mods.json to GitHub.

    ``content`` should already be the final JSON string to store.
    """
    if not config.GITHUB_TOKEN:
        return {"ok": False, "error": "GITHUB_TOKEN not set"}

    # 1. Fetch current SHA (required by GitHub for updates)
    try:
        r = requests.get(_content_url(path),
                         headers=_headers(), params=_params(), timeout=20)
        sha = None
        if r.status_code == 200:
            sha = r.json().get("sha")
        elif r.status_code != 404:
            # Real error (not just "file doesn't exist yet")
            return {"ok": False,
                    "error": f"GET {path} → HTTP {r.status_code}: {r.text[:200]}"}
    except Exception as e:
        return {"ok": False, "error": f"GET failed: {e}"}

    # 2. Build the PUT body
    if message is None:
        message = f"chore: update mods.json ({_dt.datetime.now():%Y-%m-%d %H:%M})"

    body = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": config.GITHUB_BRANCH,
    }
    if sha:
        body["sha"] = sha

    try:
        r = requests.put(_content_url(path), headers=_headers(),
                         json=body, timeout=30)
        if r.status_code in (200, 201):
            data = r.json()
            commit = data.get("commit", {})
            return {
                "ok": True,
                "sha": data.get("content", {}).get("sha") or commit.get("sha"),
                "commit_sha": commit.get("sha"),
                "html_url": data.get("content", {}).get("html_url")
                            or commit.get("html_url"),
                "message": message,
            }
        return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:300]}"}
    except Exception as e:
        return {"ok": False, "error": f"PUT failed: {e}"}
