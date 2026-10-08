"""
Entry point for hosting platforms like Hugging Face Spaces or Render.
Redirects to the actual Streamlit app in frontend/app/main.py.
"""
import os
import sys

# Add project root, frontend, and backend to python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

# Ensure FRONTEND_DIR is at the head of sys.path so 'app' resolves
# to frontend/app package and is not shadowed by this app.py file.
for p in (PROJECT_ROOT, BACKEND_DIR, FRONTEND_DIR):
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

from app.main import main

main()
