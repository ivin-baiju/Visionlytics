"""
VISIONLYTICS — Intelligent Visual Crowd Analytics.

Main Streamlit application entry point. Configures the app, manages navigation,
and renders the individual dashboard pages.

Run with:
    streamlit run app/main.py
"""

import os
import sys

# macOS/OpenCV/PyTorch fork-safety workaround.
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
os.environ["OMP_NUM_THREADS"] = "1"

# Allow the application to be launched directly with `streamlit run app/main.py`.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from app.components.icons import BRAND_LOGO_SVG
from app.components.styles import get_custom_css
from app.database import init_db
from app.resources import get_predictor


st.set_page_config(
    page_title="VISIONLYTICS — Crowd Analytics",
    page_icon=":material/visibility:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize the local analysis-history database.
init_db()

# Inject the shared visual system once at application startup.
st.markdown(get_custom_css(), unsafe_allow_html=True)


PAGES = {
    ":material/dashboard: Dashboard": "dashboard",
    ":material/image: Image Analysis": "image_analysis",
    ":material/movie: Video Analysis": "video_analysis",
    ":material/videocam: Live Camera": "live_camera",
    ":material/psychology: ML Models": "ml_models",
    ":material/dataset: Dataset": "dataset_page",
    ":material/info: About": "about",
}


def main() -> None:
    """Render the VISIONLYTICS application."""
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-brand">
                {BRAND_LOGO_SVG}
                <h2>VISIONLYTICS</h2>
                <p>Crowd Analytics Platform</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        page = st.radio(
            "Navigation",
            list(PAGES.keys()),
            label_visibility="collapsed",
        )
        st.markdown("---")

        predictor = get_predictor()
        if predictor is not None:
            st.markdown(
                """
                <div class="model-status">
                    <div class="status-indicator" style="color: #00b894;">
                        <span class="status-dot"></span>
                        Model Loaded
                    </div>
                    <div class="status-detail">YOLOv8s + ML Pipeline Active</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="model-status">
                    <div class="status-indicator" style="color: #f39c12;">
                        <span class="status-dot" style="background: #f39c12; box-shadow: 0 0 8px rgba(243,156,18,0.5);"></span>
                        No Model
                    </div>
                    <div class="status-detail">Train models to enable predictions</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

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
