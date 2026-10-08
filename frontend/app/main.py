"""
VISIONLYTICS — Intelligent Visual Crowd Analytics

Main Streamlit application entry point.
Configures the app, manages top pill navigation bar, and renders pages.

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
from app.components.navbar import get_navbar_html
from app.components.splash import get_video_background_html
from app.components.styles import get_custom_css, offline_banner_html
from app.components.theme import INDIGO
from app.database import init_db

# ── Page Configuration ───────────────────────────────────────────────────────

st.set_page_config(
    page_title="VISIONLYTICS — Crowd Analytics",
    page_icon=":material/visibility:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize the persistent SQLite database
init_db()

# Looping background video
st.markdown(get_video_background_html(), unsafe_allow_html=True)

# Custom styles & design system
st.markdown(get_custom_css(), unsafe_allow_html=True)


# ── Navigation Mapping ───────────────────────────────────────────────────────

PAGES_MAP = {
    "dashboard": "Dashboard",
    "image_analysis": "Image Analysis",
    "video_analysis": "Video Analysis",
    "live_camera": "Live Camera",
    "ml_models": "ML Models",
    "dataset_page": "Dataset",
    "about": "About",
}

SIDEBAR_LABELS = {
    "dashboard": ":material/dashboard: Dashboard",
    "image_analysis": ":material/image: Image analysis",
    "video_analysis": ":material/movie: Video analysis",
    "live_camera": ":material/videocam: Live camera",
    "ml_models": ":material/neurology: ML Models",
    "dataset_page": ":material/dataset: Dataset",
    "about": ":material/info: About",
}
SIDEBAR_TO_KEY = {v: k for k, v in SIDEBAR_LABELS.items()}


def main():
    """Main application loop."""
    # ── Page Routing (Top Bar query params + session state) ─────────
    query_page = st.query_params.get("page", None)
    if query_page in PAGES_MAP:
        active_page = query_page
        st.session_state["active_page"] = query_page
    elif "active_page" in st.session_state and st.session_state["active_page"] in PAGES_MAP:
        active_page = st.session_state["active_page"]
    else:
        active_page = "dashboard"
        st.session_state["active_page"] = "dashboard"

    # ── Render Floating Top Pill Navigation Bar ──────────────────────
    st.html(get_navbar_html(active_page))

    # ── Sidebar (Collapsible rail with status & secondary nav) ───────
    with st.sidebar:
        st.html('<div class="sidebar-brand"><img src="app/static/logo.svg" alt="Visionlytics Logo" class="brand-logo-img" style="width:36px; height:36px;" /><div><h2>VISIONLYTICS</h2><p>Crowd Analytics Platform</p></div></div>')



        st.markdown("---")

        current_label = SIDEBAR_LABELS.get(active_page, SIDEBAR_LABELS["dashboard"])
        sidebar_options = list(SIDEBAR_LABELS.values())
        default_index = sidebar_options.index(current_label) if current_label in sidebar_options else 0

        selected_label = st.radio(
            "Navigation",
            sidebar_options,
            index=default_index,
            label_visibility="collapsed",
            key="_sidebar_nav",
        )
        selected_key = SIDEBAR_TO_KEY.get(selected_label, "dashboard")
        if selected_key != active_page:
            st.query_params["page"] = selected_key
            st.session_state["active_page"] = selected_key
            st.rerun()

        st.markdown("---")

        # Model status indicator via FastAPI
        api_up = check_api_health_cached()
            
        if api_up:
            st.html(
                f'<div class="model-status">'
                f'<div class="status-indicator"><span class="status-dot" style="background: #10B981;"></span>API Connected</div>'
                f'<div class="status-detail">FastAPI Microservice Active</div>'
                f'</div>'
            )
        else:
            st.html(
                f'<div class="model-status">'
                f'<div class="status-indicator"><span class="status-dot" style="background: #9CA3AF;"></span>API Offline</div>'
                f'<div class="status-detail">Is the backend running?</div>'
                f'</div>'
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

    # ── Page Routing Execution ────────────────────────────────────────
    api_up = check_api_health_cached()
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

    if active_page == "dashboard":
        from app.ui.dashboard import render_dashboard
        render_dashboard()
    elif active_page == "image_analysis":
        from app.ui.image_analysis import render_image_analysis
        render_image_analysis()
    elif active_page == "video_analysis":
        from app.ui.video_analysis import render_video_analysis
        render_video_analysis()
    elif active_page == "live_camera":
        from app.ui.live_camera import render_live_camera
        render_live_camera()
    elif active_page == "ml_models":
        from app.ui.ml_models import render_ml_models
        render_ml_models()
    elif active_page == "dataset_page":
        from app.ui.dataset_page import render_dataset_page
        render_dataset_page()
    elif active_page == "about":
        from app.ui.about import render_about
        render_about()


if __name__ == "__main__":
    main()
