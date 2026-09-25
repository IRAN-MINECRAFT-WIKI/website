"""
config.py — MineBed Pipeline configuration (SECURITY HARDENED)
==============================================================

⚠️  SECURITY:
- No tokens are stored as fallback in this file.
- All secrets MUST be provided via environment variables.
- The original config.py exposed tokens committed to git — those
  tokens must be revoked/rotated IMMEDIATELY.
- Use .env.example as template for local development.
- For GitHub Actions, set the same keys as repo Secrets.

Usage:
    cp .env.example .env
    # edit .env with real values
    # load it before running:  set -a && source .env && set +a
"""

import os
from pathlib import Path

# ═══════════════════════════════════════════════════════
# Paths
# ═══════════════════════════════════════════════════════
BASE_DIR = Path(__file__).parent.resolve()
MODS_DATA_DIR = BASE_DIR / "mods_data"
OUTPUT_DIR = BASE_DIR / "downloaded_mods"
SCREENSHOT_DIR = BASE_DIR / "agent_screenshots"
DEBUG_DIR = BASE_DIR / "debug_dumps"

for d in [MODS_DATA_DIR, OUTPUT_DIR, SCREENSHOT_DIR, DEBUG_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════
# Chrome (for crawler — local dev only)
# ═══════════════════════════════════════════════════════
CDP_PORT = int(os.getenv("CDP_PORT", "9222"))
CHROME_PATH = os.getenv(
    "CHROME_PATH",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
)
USER_DATA_DIR = Path(os.path.expanduser("~")) / "chrome_debug_profile"


# ═══════════════════════════════════════════════════════
# LM Studio (local LLM for Persian content generation)
# ═══════════════════════════════════════════════════════
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "google/gemma-3-4b")


# ═══════════════════════════════════════════════════════
# HuggingFace (for hosting mod files via Dataset)
# ═══════════════════════════════════════════════════════
HF_REPO_ID = os.getenv("HF_REPO_ID", "Habib91700/minebed-mods_")
HF_REPO_TYPE = os.getenv("HF_REPO_TYPE", "dataset")
HF_TOKEN = os.getenv("HF_TOKEN", "")  # REQUIRED — no fallback


# ═══════════════════════════════════════════════════════
# GitHub (for updating mods.json on the Pages site)
# ═══════════════════════════════════════════════════════
GITHUB_USER = os.getenv("GITHUB_USER", "IRAN-MINECRAFT-WIKI")
GITHUB_REPO = os.getenv("GITHUB_REPO", "website")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # REQUIRED — no fallback
GITHUB_MODS_FILE = "website/src/data/mods.json"  # path inside the repo
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")


# ═══════════════════════════════════════════════════════
# Content quality thresholds
# ═══════════════════════════════════════════════════════
MIN_DESC_WORD_COUNT = 250          # reject mod if AI output is shorter
MAX_DUPLICATE_DAYS = 30             # skip re-crawling mods updated < 30 days ago
RATE_LIMIT_PER_DOMAIN = 2.0         # seconds between requests per domain
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


# ═══════════════════════════════════════════════════════
# Categories
# ═══════════════════════════════════════════════════════
CAT_NAMES = {
    "gameplay": "گیم‌پلی",
    "graphics": "گرافیک",
    "maps": "مپ",
    "mobs": "موجودات",
    "decoration": "دکوراسیون",
    "world": "دنیا",
    "utility": "ابزار",
}


# ═══════════════════════════════════════════════════════
# Security check — fail fast if tokens are missing
# ═══════════════════════════════════════════════════════
def _check_tokens():
    """Warn loudly if required tokens are missing (don't fail import)."""
    missing = []
    if not HF_TOKEN:
        missing.append("HF_TOKEN")
    if not GITHUB_TOKEN:
        missing.append("GITHUB_TOKEN")
    if missing:
        print(f"⚠️  WARNING: The following tokens are not set: {', '.join(missing)}")
        print("   Set them in .env (local) or as GitHub Secrets (CI).")
        print("   See .env.example for the full list.")


_check_tokens()
