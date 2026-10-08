"""
Top Navigation Bar Component for Visionlytics.

Renders a floating pill navigation bar matching the design in media_1791488384243.png.
Uses base64 data URIs for bulletproof zero-latency rendering in Streamlit.
"""

from app.components.icons import (
    ICON_BELL_DATA_URI,
    ICON_TUNE_DATA_URI,
    ICON_USER_DATA_URI,
    LOGO_DATA_URI,
)

NAV_ITEMS = [
    {"key": "dashboard", "type": "single", "text": "Dashboard"},
    {"key": "image_analysis", "type": "stacked", "top": "Image", "sub": "Analysis"},
    {"key": "video_analysis", "type": "stacked", "top": "Video", "sub": "Analysis"},
    {"key": "live_camera", "type": "stacked", "top": "Live", "sub": "Camera"},
    {"key": "ml_models", "type": "stacked", "top": "ML", "sub": "Models"},
    {"key": "dataset_page", "type": "single", "text": "Dataset"},
    {"key": "about", "type": "single", "text": "About"},
]


def get_navbar_html(active_page: str = "dashboard") -> str:
    """Generate the compact single-line HTML for the top navigation bar."""
    items_html = []
    for item in NAV_ITEMS:
        key = item["key"]
        is_active = (key == active_page)
        active_class = " active" if is_active else ""

        if item["type"] == "single":
            label = f'<span class="vl-nav-single">{item["text"]}</span>'
        else:
            label = f'<span class="vl-nav-stack"><span class="nav-top">{item["top"]}</span><span class="nav-sub">{item["sub"]}</span></span>'

        items_html.append(
            f'<a href="/?page={key}" target="_self" class="vl-nav-btn{active_class}">{label}</a>'
        )

    nav_links = "".join(items_html)

    return (
        f'<div class="vl-top-accent-line"></div>'
        f'<div class="vl-navbar-container">'
        f'<a href="/?page=dashboard" target="_self" class="vl-brand-pill" title="Visionlytics Home">'
        f'<div class="vl-brand-icon-wrap"><img src="{LOGO_DATA_URI}" alt="Visionlytics Logo" class="brand-logo-img" /></div>'
        f'<span class="vl-brand-name">VISIONLYTICS</span>'
        f'</a>'
        f'<nav class="vl-nav-pill">'
        f'<div class="vl-nav-links">{nav_links}</div>'
        f'<div class="vl-nav-controls">'
        f'<div class="vl-nav-icon-btn" title="System Settings"><img src="{ICON_TUNE_DATA_URI}" alt="Settings" width="19" height="19" /></div>'
        f'<div class="vl-nav-icon-btn" title="Notifications"><img src="{ICON_BELL_DATA_URI}" alt="Notifications" width="19" height="19" /></div>'
        f'<div class="vl-nav-avatar-btn" title="User Profile"><img src="{ICON_USER_DATA_URI}" alt="User" width="20" height="20" /></div>'
        f'</div>'
        f'</nav>'
        f'</div>'
    )
