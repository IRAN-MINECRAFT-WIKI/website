REM =========================================================================
REM MineBed Admin — Windows launcher (start.bat)
REM Checks Python -> installs requirements -> runs the desktop app
REM =========================================================================
@echo off
setlocal enableextensions
cd /d "%~dp0"
title MineBed Admin Launcher

echo.
echo ============================================================
echo   MineBed Admin  --  Desktop Launcher
echo ============================================================
echo.

REM ---- 1. Check Python ----
echo [1/3] Checking Python ...
where python >nul 2>nul
if errorlevel 1 (
    where py >nul 2>nul
    if errorlevel 1 (
        echo.
        echo [ERROR] Python is not installed or not in PATH.
        echo Please install Python 3.10+ from https://python.org
        echo.
        pause
        exit /b 1
    )
    set "PY=py"
) else (
    set "PY=python"
)
echo     Using: %PY%
%PY% --version
if errorlevel 1 (
    echo [ERROR] Could not run Python.
    pause
    exit /b 1
)
echo.

REM ---- 2. Install requirements if needed ----
echo [2/3] Ensuring dependencies are installed ...
%PY% -m pip install --upgrade pip >nul 2>nul
%PY% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install requirements.
    echo Try manually:  %PY% -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo     Dependencies OK.
echo.

REM ---- 3. Launch the app ----
echo [3/3] Launching MineBed Admin ...
echo.
start "" %PY% minebed-desktop.py
exit /b 0
