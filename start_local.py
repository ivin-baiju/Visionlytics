#!/usr/bin/env python3
"""
Visionlytics — Local Launcher (No Docker Required)

Starts both the FastAPI backend and Streamlit frontend in a single process.
The backend runs in a background thread; the frontend runs as the main process.

Usage:
    python start_local.py
    # or
    python start_local.py --backend-port 8000 --frontend-port 8501
"""

import argparse
import os
import signal
import subprocess
import sys
import time

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# Automatically find virtualenv Python if present
VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")
PYTHON_EXE = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable


def _start_backend(port: int) -> subprocess.Popen:
    """Start the FastAPI backend via uvicorn in a subprocess."""
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    # Ensure the backend package is importable
    env["PYTHONPATH"] = BACKEND_DIR + os.pathsep + env.get("PYTHONPATH", "")

    cmd = [
        PYTHON_EXE, "-m", "uvicorn",
        "main:app",
        "--host", "127.0.0.1",
        "--port", str(port),
        "--reload",
        "--log-level", "info",
    ]

    print(f"  ▸ Starting FastAPI backend on http://127.0.0.1:{port}")
    proc = subprocess.Popen(
        cmd,
        cwd=BACKEND_DIR,
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    return proc


def _wait_for_backend(port: int, timeout: float = 30.0) -> bool:
    """Wait until the backend /health endpoint responds."""
    import urllib.request
    import urllib.error

    url = f"http://127.0.0.1:{port}/health"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = urllib.request.urlopen(url, timeout=2)
            if resp.status == 200:
                return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(0.5)
    return False


def _start_frontend(port: int, backend_port: int) -> subprocess.Popen:
    """Start the Streamlit frontend as a subprocess."""
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["NEXT_PUBLIC_API_URL"] = f"http://127.0.0.1:{backend_port}"

    cmd = ["npm", "run", "dev", "--", "-p", str(port)]

    print(f"  ▸ Starting Next.js frontend on http://127.0.0.1:{port}")
    proc = subprocess.Popen(
        cmd,
        cwd=FRONTEND_DIR,
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    return proc


def main():
    parser = argparse.ArgumentParser(
        description="Start Visionlytics locally (no Docker required)",
    )
    parser.add_argument(
        "--backend-port", type=int, default=8000,
        help="Port for the FastAPI backend (default: 8000)",
    )
    parser.add_argument(
        "--frontend-port", type=int, default=3000,
        help="Port for the Next.js frontend (default: 3000)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  VISIONLYTICS — Local Launcher")
    print("=" * 60)
    print()

    backend_proc = _start_backend(args.backend_port)

    # Wait for backend to be ready before starting the frontend
    print("  ⏳ Waiting for backend to become ready...")
    if _wait_for_backend(args.backend_port):
        print("  ✓ Backend is ready!")
    else:
        print("  ⚠ Backend didn't respond in time — starting frontend anyway")

    print()
    frontend_proc = _start_frontend(args.frontend_port, args.backend_port)

    print()
    print("─" * 60)
    print(f"  FastAPI Backend:    http://127.0.0.1:{args.backend_port}")
    print(f"  Streamlit Frontend: http://127.0.0.1:{args.frontend_port}")
    print("  Press Ctrl+C to stop both services")
    print("─" * 60)
    print()

    # Graceful shutdown handler
    def _shutdown(signum=None, frame=None):
        print("\n  Shutting down...")
        for proc in (frontend_proc, backend_proc):
            if proc.poll() is None:
                proc.terminate()
        # Give processes a moment to exit gracefully
        for proc in (frontend_proc, backend_proc):
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("  ✓ All services stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    # Wait for the frontend to exit (main blocking call)
    try:
        frontend_proc.wait()
    except KeyboardInterrupt:
        _shutdown()
    finally:
        _shutdown()


if __name__ == "__main__":
    main()
