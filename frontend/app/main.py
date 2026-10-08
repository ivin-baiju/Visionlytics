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

from app.api_client import API_URL, check_api_health_cached
from app.components.icons import BRAND_LOGO_SVG
from app.components.styles import get_custom_css, offline_banner_html
from app.components.theme import DENSITY, INDIGO
from app.database import init_db

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
    ":material/neurology: ML Models": "ml_models",
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
            <div>
                <h2>VISIONLYTICS</h2>
                <p>Crowd Analytics Platform</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        page = st.radio(
            "Navigation",
            list(PAGES.keys()),
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Model status indicator via FastAPI (memoised for HEALTH_CACHE_TTL)
        api_up = check_api_health_cached()
            
        if api_up:
            st.markdown(
                f"""
            <div class="model-status">
                <div class="status-indicator">
                    <span class="status-dot" style="background: {INDIGO};"></span>
                    API Connected
                </div>
                <div class="status-detail">FastAPI Microservice Active</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
            <div class="model-status">
                <div class="status-indicator">
                    <span class="status-dot" style="background: #9CA3AF;"></span>
                    API Offline
                </div>
                <div class="status-detail">Is the backend running?</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.caption(f"Endpoint: `{API_URL}`")
        if st.button(
            "Re-check connection",
            icon=":material/refresh:",
            use_container_width=True,
            help="Clears the cached health result and probes the backend again",
        ):
            st.session_state.pop("_api_health_cache", None)
            st.rerun()

    # ── Page Routing ──────────────────────────────────────────────────
    page_key = PAGES[page]

    # Global connectivity banner: fail loudly and actionably instead of
    # letting each page surface its own "API offline" message.
    if not api_up:
        st.markdown(
            offline_banner_html(
                f"Backend API unreachable at {API_URL}. Start it with "
                "<code>uvicorn main:app --port 8000</code> from the "
                "<code>backend</code> directory to enable detection, "
                "training and dataset features."
            ),
            unsafe_allow_html=True,
        )

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
