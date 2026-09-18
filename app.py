"""
Entry point for hosting platforms like Hugging Face Spaces or Render.
Redirects to the actual Streamlit app in app/main.py.
"""
import os
import sys

# Add the project root to the python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import main

if __name__ == "__main__":
    main()
