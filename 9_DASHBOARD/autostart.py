# -*- coding: utf-8 -*-
"""Auto-start the health dashboard whenever SEOSONA Video is used.

Production entry points (daily_production, queue_processor) call `ensure_running()`
on start — so using the system brings the dashboard up by itself, in the background,
exactly once. It is idempotent (no-op if already serving) and detached (survives the
CLI that launched it). Opt out with SEOSONA_DASHBOARD=0.
"""
import os
import sys
import socket
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PORT = int(os.environ.get("SEOSONA_DASHBOARD_PORT", "5050"))


def is_up(port=PORT):
    """True if something is already serving on the dashboard port."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.4):
            return True
    except OSError:
        return False


def ensure_running(verbose=True):
    """Start the dashboard in the background if it isn't already. No-op when disabled
    (SEOSONA_DASHBOARD=0) or already up. Never raises into the caller."""
    if os.environ.get("SEOSONA_DASHBOARD", "1") == "0":
        return False
    try:
        if is_up():
            if verbose:
                print(f"[dashboard] already live → http://localhost:{PORT}")
            return True
        server = HERE / "server.py"
        kwargs = dict(cwd=str(ROOT), stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        if os.name == "nt":
            # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP → outlives this CLI.
            kwargs["creationflags"] = 0x00000008 | 0x00000200
        else:
            kwargs["start_new_session"] = True
        subprocess.Popen([sys.executable, str(server)], **kwargs)
        if verbose:
            print(f"[dashboard] auto-started → http://localhost:{PORT}")
        return True
    except Exception as e:
        if verbose:
            print(f"[dashboard] auto-start skipped: {e}")
        return False


if __name__ == "__main__":
    ensure_running()
