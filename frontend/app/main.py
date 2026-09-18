"""
VISIONLYTICS — Intelligent Visual Crowd Analytics

Main Streamlit application entry point.
Configures the app, manages navigation, and renders pages.

Run with:
    streamlit run app/main.py
"""

import os
import sys

import streamlit as st

# ── macOS Segmentation Fault Workaround ──────────────────────────────
# PyTorch, OpenCV, and Streamlit multithreading on macOS Apple Silicon
# frequently cause segmentation faults due to fork() safety checks.
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
os.environ["OMP_NUM_THREADS"] = "1"

# Add project root to path so all imports work
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.components.icons import BRAND_LOGO_SVG
from app.components.styles import get_custom_css
from app.database import init_db
from app.resources import get_predictor

# ── Page Configuration ───────────────────────────────────────────────────────

st.set_page_config(
    page_title="VISIONLYTICS — Crowd Analytics",
    page_icon=":material/visibility:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize the persistent SQLite database
init_db()

# Inject custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


# ── Navigation ───────────────────────────────────────────────────────────────

PAGES = {
    ":material/dashboard: Dashboard": "dashboard",
    ":material/image: Image analysis": "image_analysis",
    ":material/movie: Video analysis": "video_analysis",
    ":material/videocam: Live camera": "live_camera",
    ":material/psychology: ML models": "ml_models",
    ":material/dataset: Dataset": "dataset_page",
    ":material/info: About": "about",
}


def main():
    """Main application loop."""
    # ── Sidebar ──────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-brand">
            {BRAND_LOGO_SVG}
            <h2>VISIONLYTICS</h2>
            <p>Crowd Analytics Platform</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        page = st.radio(
            "Navigation",
            list(PAGES.keys()),
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Model status indicator
        predictor = get_predictor()
        if predictor is not None:
            st.markdown("""
            <div class="model-status">
                <div class="status-indicator" style="color: #2ECDA7;">
                    <span class="status-dot"></span>
                    Model Loaded
                </div>
                <div class="status-detail">YOLOv8s + ML Pipeline Active</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="model-status">
                <div class="status-indicator" style="color: #FFB347;">
                    <span class="status-dot" style="background: #FFB347; box-shadow: 0 0 6px rgba(255,179,71,0.4);"></span>
                    No Model
                </div>
                <div class="status-detail">Train models to enable predictions</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Page Routing ──────────────────────────────────────────────────
    page_key = PAGES[page]

    if page_key == "dashboard":
        from app.ui.dashboard import render_dashboard
        render_dashboard()
    elif page_key == "image_analysis":
        from app.ui.image_analysis import render_image_analysis
        render_image_analysis()
    elif page_key == "video_analysis":
        from app.ui.video_analysis import render_video_analysis
        render_video_analysis()
    elif page_key == "live_camera":
        from app.ui.live_camera import render_live_camera
        render_live_camera()
    elif page_key == "ml_models":
        from app.ui.ml_models import render_ml_models
        render_ml_models()
    elif page_key == "dataset_page":
        from app.ui.dataset_page import render_dataset_page
        render_dataset_page()
    elif page_key == "about":
        from app.ui.about import render_about
        render_about()


if __name__ == "__main__":
    main()
