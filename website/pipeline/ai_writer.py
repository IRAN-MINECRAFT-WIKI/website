"""
ai_writer.py — Persian content generation with quality check

Improvements over original:
- Auto-loads .env via python-dotenv
- Validates output (word count, required fields)
- Retries up to 3 times if quality fails
- Better JSON cleaning (handles trailing commas + code fences)
- Outputs reasoning for debugging
"""

import json
import os
import re
import time
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from openai import OpenAI
from config import LM_STUDIO_URL, MODEL_NAME, CAT_NAMES, MIN_DESC_WORD_COUNT

client = OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")

# ═══════════════════════════════════════════════════════
# Prompt — Persian-friendly system instructions
# ═══════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are a Persian content writer for a Minecraft Bedrock mods website (MineBed).
Your goal: turn raw English mod info into RICH, ENGAGING Persian content that makes users want to download the mod.

Output STRICT JSON with these fields:
{
  "nameFa": "Persian name (short, no emoji)",
  "tagline": "One-line Persian description (max 100 chars, catchy)",
  "keywords": "Persian keywords separated by space (8-15 words for search)",
  "desc": "FULL Persian description — MINIMUM 300 WORDS (this is critical!)",
  "category": "one of: gameplay, graphics, maps, mobs, decoration, world, utility"
}

The desc field MUST be structured like this in Persian:

1. **مقدمه‌ی جذاب** (3-4 sentences) — یه سوال یا سناریو که کاربر رو درگیر کنه
2. **این مود چیه؟** (پاراگراف 4-5 جمله‌ای)
3. **چی رو توی بازی عوض می‌کنه؟** (پاراگراف 3-4 جمله)
4. **✨ ویژگی‌های اصلی** (لیست 6-10 آیتم با توضیح کوتاه)
5. **🎮 چطور ازش استفاده کنم؟** (اگه مود دستورالعمل داره)
6. **چرا این مود رو دانلود کنی؟** (پاراگراف 2-3 جمله)

Rules:
1. Reply ONLY with valid JSON. No markdown fences.
2. Persian must be NATURAL, casual gamer tone — not machine translation
3. از کلمات محاوره‌ای استفاده کن: "می‌تونی" نه "می‌توانید"
4. Category mapping:
   - weapons/combat/survival → gameplay
   - shaders/textures/visual → graphics
   - world/maps/adventure → maps
   - creatures/mobs/animals → mobs
   - furniture/decoration → decoration
   - terrain/biomes → world
   - tools/utility/redstone → utility

REMEMBER: desc MUST be at least 300 Persian words. Short descriptions are NOT acceptable."""


def clean_json(text: str) -> Optional[dict]:
    """More aggressive JSON cleaning than the original."""
    if not text:
        return None
    # Remove markdown fences
    text = re.sub(r"```(?:json)?\s*", "", text).replace("```", "")
    # Find the outermost JSON object
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e == -1:
        return None
    candidate = text[s : e + 1]
    # Try parsing directly
    try:
        return json.loads(candidate)
    except Exception:
        pass
    # Fix common issues: trailing commas
    cleaned = re.sub(r",\s*}", "}", candidate)
    cleaned = re.sub(r",\s*]", "]", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        # Last resort: try to find balanced braces
        depth = 0
        start = -1
        for i, ch in enumerate(text):
            if ch == "{":
                if depth == 0:
                    start = i
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0 and start != -1:
                    try:
                        return json.loads(text[start : i + 1])
                    except Exception:
                        continue
        return None


def validate_ai_output(result: dict) -> tuple[bool, str]:
    """Returns (is_valid, error_message)."""
    required = ["nameFa", "tagline", "keywords", "desc", "category"]
    for field in required:
        if field not in result or not result[field]:
            return False, f"Missing or empty field: {field}"
    # Check word count
    word_count = len(result["desc"].split())
    if word_count < MIN_DESC_WORD_COUNT:
        return False, f"desc too short ({word_count} words, need {MIN_DESC_WORD_COUNT})"
    # Validate category
    if result["category"] not in CAT_NAMES:
        result["category"] = "gameplay"
    return True, ""


def generate_persian_content(page_data: dict, max_retries: int = 3) -> Optional[dict]:
    """Generate Persian content from raw English page data, with retries."""

    prompt = f"""Raw data from MCPEDL mod page:

TITLE: {page_data.get('title', '')}
TAGLINE: {page_data.get('tagline', '')}
AUTHOR: {page_data.get('author', '')}
VERSION: {page_data.get('version', '')}
TAGS: {', '.join(page_data.get('tags', []))}

DESCRIPTION:
{page_data.get('description', '')[:5000]}

FULL PAGE TEXT (for context):
{page_data.get('full_text', '')[:4000]}

Now produce the Persian JSON as instructed. The "desc" field MUST be at least 300 Persian words."""

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=4000,
                temperature=0.6 if attempt > 1 else 0.5,
            )
            raw = response.choices[0].message.content
            result = clean_json(raw)

            if not result:
                print(f"  ⚠️  Attempt {attempt}: invalid JSON")
                continue

            is_valid, err = validate_ai_output(result)
            if is_valid:
                word_count = len(result["desc"].split())
                print(f"  ✅ {result.get('nameFa', '?')} — {word_count} words")
                return result

            print(f"  ⚠️  Attempt {attempt} validation failed: {err}")
            # If too short, ask AI to expand in next attempt
            if "too short" in err:
                prompt += f"\n\nNOTE: previous attempt was too short ({len(result.get('desc', '').split())} words). Please make desc at least 400 words this time."

        except Exception as e:
            print(f"  ❌ Attempt {attempt} error: {e}")
            time.sleep(1)

    return None


def ask_ai_which_files(page_data: dict, files: list) -> list:
    """Returns list of 0-based indices into `files` to download."""
    if not files:
        return []
    if len(files) == 1:
        return [0]

    files_list = "\n".join(
        f"{i+1}. {f['filename']}" for i, f in enumerate(files)
    )
    prompt = f"""Minecraft Bedrock addon: "{page_data.get('title', 'Unknown')}"

Available download files:
{files_list}

Minecraft Bedrock addons usually have TWO parts:
- Behavior Pack (.mcpack) — adds logic/features
- Resource Pack (.mcpack) — adds textures/models
Or sometimes a single combined file (.mcaddon).

Rules:
1. If you see BOTH Behavior Pack AND Resource Pack → download BOTH
2. If you see a combined .mcaddon → download ONLY that
3. If you see multiple VERSIONS of the same pack → download ONLY the LATEST
4. Do NOT download older versions

Reply EXACTLY with this JSON (no markdown):
{{"indices": [1, 2], "reason": "brief reason in English"}}"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.1,
        )
        raw = response.choices[0].message.content
        result = clean_json(raw)
        if not result or "indices" not in result:
            print("  ⚠️  AI returned no indices, downloading all")
            return list(range(len(files)))
        indices = [i - 1 for i in result["indices"] if 1 <= i <= len(files)]
        if not indices:
            return list(range(len(files)))
        print(f"  ✅ Reason: {result.get('reason', '')}")
        return indices
    except Exception as e:
        print(f"  ❌ File selection error: {e}")
        return list(range(len(files)))


if __name__ == "__main__":
    # Quick test
    test_data = {
        "title": "Test Mod",
        "description": "A test mod for unit testing.",
        "full_text": "Test content.",
    }
    result = generate_persian_content(test_data)
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Test failed")
