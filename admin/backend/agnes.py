"""
MineBed Admin — Agnes AI content generator.

Uses the OpenAI-compatible ``openai`` Python SDK pointed at the Agnes API.
Generates Persian (Farsi) metadata for a crawled MCPEDL mod.

Public API
----------
    generate_mod_content(page_data: dict) -> dict
        Returns a dict with keys:
            nameFa     — Persian mod name
            tagline    — short Persian tagline
            keywords   — list of Persian/English keywords
            desc       — long Persian description (Markdown)
            category   — Persian category name
            download   — download instructions in Persian
"""
from __future__ import annotations

import json
import time
from typing import Optional

from . import config


# ---------------------------------------------------------------------------
# Lazy client — we don't import openai at module load so the app still runs
# even if the package isn't installed yet.
# ---------------------------------------------------------------------------
_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return None
    if not config.AGNES_API_KEY:
        return None
    _client = OpenAI(
        api_key=config.AGNES_API_KEY,
        base_url=config.AGNES_BASE_URL,
        timeout=60.0,
    )
    return _client


def _build_prompt(page_data: dict) -> tuple[str, str]:
    """
    Build (system, user) prompts for the model.

    The system prompt instructs Agnes to act as a Persian Minecraft mod
    translator/writer.  The user prompt provides the crawled data and
    demands strict JSON output.
    """
    title = (page_data.get("title") or "").strip()
    author = page_data.get("author") or ""
    version = page_data.get("version") or ""
    description = (page_data.get("description") or "").strip()[:2500]
    cats = ", ".join(page_data.get("categories") or [])
    files = page_data.get("files") or []
    file_names = ", ".join(f.get("name", "") for f in files[:6])
    cover = page_data.get("cover") or ""

    system = (
        "تو یک ویراستار و نویسنده حرفه‌ای سایت دانلود ماینکرفت به فارسی هستی. "
        "وظیفه تو این است که مشخصات یک ماد انگلیسی را بگیری و یک بستهٔ کامل "
        "و جذاب به فارسی بسازی. همیشه فقط خروجی JSON معتبر بده، بدون توضیح اضافه."
    )

    user = (
        "لطفاً برای ماد زیر یک بستهٔ محتوایی فارسی بساز و فقط به‌صورت JSON معتبر "
        "با کلیدهای زیر پاسخ بده:\n"
        "  nameFa     : نام فارسی ماد (کوتاه و جذاب)\n"
        "  tagline    : یک جمله کوتاه فارسی برای جذاب کردن ماد\n"
        "  keywords   : آرایه‌ای از ۵ تا ۸ کلمه کلیدی فارسی/انگلیسی\n"
        "  desc       : توضیح کامل فارسی ماد (۳ تا ۶ پاراگراف، با مارک‌داون)\n"
        "  category   : دسته‌بندی فارسی (مثلاً: ماد، نقشه، اسکین، شیپ، شیدوِر)\n"
        "  download   : دستورالعمل نصب فارسی\n\n"
        f"عنوان انگلیسی: {title}\n"
        f"سازنده: {author}\n"
        f"نسخه: {version}\n"
        f"دسته‌بندی‌های انگلیسی: {cats}\n"
        f"نام فایل‌ها: {file_names}\n"
        f"آدرس کاور: {cover}\n\n"
        f"توضیح انگلیسی:\n{description}\n\n"
        "یادت باشد: فقط JSON خروجی بده."
    )
    return system, user


def _parse_response(text: str) -> dict:
    """Extract a JSON object from the model response (handles ``` fences)."""
    if not text:
        return {}
    # strip ```json ... ``` fences if present
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    raw = fenced.group(1) if fenced else text
    # find the first balanced { ... }
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        raw = raw[start:end + 1]
    try:
        return json.loads(raw)
    except Exception:
        return {}


import re  # noqa: E402  (placed late so import block above stays clean)


def _fallback(page_data: dict) -> dict:
    """Build a minimal Persian content block from raw crawled data."""
    title = (page_data.get("title") or "ماد ماینکرفت").strip()
    desc = (page_data.get("description") or "").strip()
    cats = page_data.get("categories") or []
    return {
        "nameFa": title,
        "tagline": "دانلود ماد برای ماینکرفت بِدراک",
        "keywords": (cats or ["ماد", "minecraft", "addon"])[:6],
        "desc": f"**{title}**\n\n{desc}" if desc else f"**{title}**",
        "category": "ماد",
        "download": "فایل را دانلود کرده و در ماینکرفت نصب کنید.",
    }


def _empty_ai() -> dict:
    return {
        "nameFa": "",
        "tagline": "",
        "keywords": [],
        "desc": "",
        "category": "",
        "download": "",
        "_ai_used": False,
    }


def generate_mod_content(page_data: dict, on_progress=None) -> dict:
    """
    Generate Persian content for a crawled mod.

    Returns a dict shaped like::

        {
          nameFa, tagline, keywords: [...],
          desc, category, download,
          _ai_used: bool,
          _raw: <original page_data for reference>,
          _error: <optional error string>
        }
    """
    def log(msg: str) -> None:
        if on_progress:
            on_progress("ai", msg)

    client = _get_client()
    if client is None:
        log("Agnes AI not configured — using raw page data")
        out = _fallback(page_data)
        out["_ai_used"] = False
        out["_raw"] = page_data
        return out

    system, user = _build_prompt(page_data)
    last_err: Optional[str] = None

    for attempt in range(1, 4):
        try:
            log(f"Agnes AI: attempt {attempt}/3 …")
            resp = client.chat.completions.create(
                model=config.AGNES_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.7,
                max_tokens=1500,
            )
            text = resp.choices[0].message.content or ""
            parsed = _parse_response(text)
            if parsed and ("nameFa" in parsed or "desc" in parsed):
                # Merge with fallback for any missing keys
                merged = _fallback(page_data)
                merged.update(parsed)
                merged["_ai_used"] = True
                merged["_raw"] = page_data
                log(f"Agnes AI: success ({len(str(parsed))} bytes)")
                return merged
            last_err = "Empty / unparseable response"
        except Exception as e:
            last_err = str(e)
            log(f"Agnes AI: error attempt {attempt}: {e}")
            time.sleep(1.5 * attempt)

    log(f"Agnes AI: giving up after 3 attempts ({last_err})")
    out = _fallback(page_data)
    out["_ai_used"] = False
    out["_raw"] = page_data
    out["_error"] = last_err or ""
    return out


def test_connection() -> dict:
    """Send a tiny ping to verify the Agnes endpoint/key works."""
    client = _get_client()
    if client is None:
        return {"ok": False, "error": "API key not set or openai package missing"}
    try:
        resp = client.chat.completions.create(
            model=config.AGNES_MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=4,
        )
        return {"ok": True, "model": config.AGNES_MODEL,
                "reply": (resp.choices[0].message.content or "")[:80]}
    except Exception as e:
        return {"ok": False, "error": str(e)}
