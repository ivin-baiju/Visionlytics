"""
Shared pytest configuration for the Visionlytics test suite.

Puts `backend/` and `frontend/` on sys.path so the suite can import both
`main` (FastAPI) and `app` (Streamlit) without requiring an editable install
layout. The repository root is intentionally NOT added, so `import app`
resolves to the `frontend/app` package and never to the root `app.py` wrapper.
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(REPO_ROOT, "frontend")
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")

# Backend first so `import main` resolves; frontend inserted last so it wins
# at index 0 for the `app` package lookup.
for path in (BACKEND_DIR, FRONTEND_DIR):
    if path in sys.path:
        sys.path.remove(path)
    sys.path.insert(0, path)
