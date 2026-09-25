#!/usr/bin/env bash
# =========================================================================
# MineBed Admin — Linux/macOS launcher (start.sh)
# Checks Python -> installs requirements -> runs the desktop app
# =========================================================================
set -e
cd "$(dirname "$0")"
echo
echo "============================================================"
echo "   MineBed Admin  --  Desktop Launcher"
echo "============================================================"
echo

# ---- 1. Detect Python ----
echo "[1/3] Checking Python ..."
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "[ERROR] Python is not installed or not in PATH."
    echo "Please install Python 3.10+ from https://python.org"
    exit 1
fi
echo "    Using: $PY"
$PY --version

# ---- 2. Install requirements ----
echo
echo "[2/3] Ensuring dependencies are installed ..."
$PY -m pip install --upgrade pip >/dev/null 2>&1 || true
$PY -m pip install -r requirements.txt
echo "    Dependencies OK."

# ---- 3. Launch the app ----
echo
echo "[3/3] Launching MineBed Admin ..."
echo
exec $PY minebed-desktop.py
