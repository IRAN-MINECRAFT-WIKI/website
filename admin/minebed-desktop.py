"""
MineBed Admin — desktop entry point.

Starts a FastAPI server in a daemon thread (uvicorn) and opens a native
pywebview window pointed at ``http://127.0.0.1:8000``.  The window has a
real browser engine, so there are no CORS / script-tag limitations — the
front-end can use direct DOM manipulation and fetch() against localhost.

Usage::

    python minebed-desktop.py

Environment
-----------
The ``admin/../.env`` file is loaded automatically by ``backend.config``.
"""
from __future__ import annotations

import logging
import socket
import sys
import threading
import time
from pathlib import Path

# Make sure the local ``backend`` package is importable when this file is
# executed directly (``python minebed-desktop.py``).
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uvicorn  # noqa: E402

from backend import config  # noqa: E402


# ---------------------------------------------------------------------------
# Logging — write to stdout + a log file next to this script
# ---------------------------------------------------------------------------
LOG_PATH = Path(__file__).resolve().parent / "minebed-desktop.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
    ],
)
log = logging.getLogger("minebed")


# ---------------------------------------------------------------------------
# Port discovery — if 8000 is taken, bump up to 8001…8010
# ---------------------------------------------------------------------------
def _port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


def _pick_port(preferred: int = 8000) -> int:
    for p in range(preferred, preferred + 10):
        if not _port_in_use(p):
            return p
    raise RuntimeError("No free port in range 8000-8009")


# ---------------------------------------------------------------------------
# Server thread
# ---------------------------------------------------------------------------
def _run_server(port: int, ready: threading.Event) -> None:
    """
    Run uvicorn (with our FastAPI app) in this daemon thread.

    We use ``uvicorn.run`` directly with ``log_level=info`` and the
    ``backend.main:app`` import path so reload works without needing
    a separate process.
    """
    log.info("Starting FastAPI on http://127.0.0.1:%d", port)
    # Defer the import so config is loaded first
    from backend.main import app  # noqa: WPS433

    config_obj = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info",
        access_log=False,
        reload=False,
        workers=1,
        loop="asyncio",
    )
    server = uvicorn.Server(config_obj)

    # signal that we're about to start serving
    ready.set()

    try:
        server.run()
    except Exception:
        log.exception("uvicorn crashed")
        raise


# ---------------------------------------------------------------------------
# Window
# ---------------------------------------------------------------------------
def _wait_for_server(url: str, timeout: float = 20.0) -> bool:
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url + "/api/health", timeout=1.0) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def _open_window(url: str) -> None:
    """Open the pywebview window; this blocks until the window is closed."""
    import webview  # type: ignore

    log.info("Opening window → %s", url)
    window = webview.create_window(
        title="MineBed Admin",
        url=url,
        width=1200,
        height=800,
        resizable=True,
        frameless=False,
        easy_drag=False,
        min_size=(960, 640),
        text_select=False,
    )
    webview.start(debug=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    port = _pick_port(int(getattr(config, "PORT", 8000)) or 8000)
    base_url = f"http://127.0.0.1:{port}"

    ready = threading.Event()
    server_thread = threading.Thread(
        target=_run_server, args=(port, ready),
        name="uvicorn-server", daemon=True,
    )
    server_thread.start()

    # Wait until the server thread has started uvicorn, then poll the URL.
    ready.wait(timeout=10)
    if not _wait_for_server(base_url, timeout=25.0):
        log.error("Server did not become ready in time — aborting.")
        # Still try to open the window; the user can see the error.
        try:
            _open_window(base_url)
        except Exception:
            pass
        return 1

    log.info("Server is up — opening window")
    try:
        _open_window(base_url)
    finally:
        # When the window closes, pywebview returns.  The uvicorn thread is
        # a daemon so it will be killed automatically on process exit.
        log.info("Window closed — shutting down.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
