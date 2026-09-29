"""
Flat CSS for the Visionlytics dashboard.

Ronas IT delivery-tracking design language: flat white surfaces, hairline
borders, solid ink text, lime accents. No gradients, no glass blur,
no keyframe animations.
"""

from app.components.theme import DENSITY, DENSITY_BG


def get_custom_css() -> str:
    """Return the flat custom CSS for the Visionlytics dashboard."""
    return """
    <style>
    /* ── App canvas ──────────────────────────────────────────────── */
    .stApp {
        background: #F5F6F7;
        color: #14161A;
        font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .block-container {
        padding-top: 1.25rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E9EAEC;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── Page header ─────────────────────────────────────────────── */
    .hero-section {
        background: #FFFFFF;
        border: 1px solid #E9EAEC;
        border-left: 4px solid #B4E04C;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(20, 22, 26, 0.04);
        padding: 1rem 1.25rem;
        margin-bottom: 1.25rem;
        text-align: left;
    }
    .hero-section h1 {
        color: #14161A;
        font-family: Inter, sans-serif;
        font-size: 1.35rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.06em;
    }
    .hero-section p {
        color: #5B6472;
        font-size: 0.8rem;
        margin: 0.25rem 0 0;
        font-weight: 500;
        letter-spacing: 0.04em;
    }
    .page-header {
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
        margin: 0 0 1rem;
    }
    .page-tick {
        width: 4px;
        align-self: stretch;
        background: #B4E04C;
        border-radius: 2px;
        flex: none;
    }
    .page-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #14161A;
        margin: 0;
    }
    .page-subtitle {
        font-size: 0.8rem;
        color: #5B6472;
        margin: 0.15rem 0 0;
    }
    /* ── Cards ───────────────────────────────────────────────────── */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E9EAEC;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(20, 22, 26, 0.04);
        padding: 0.9rem 1rem;
    }
    .metric-card .metric-label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #5B6472;
    }
    .metric-card .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #14161A;
        margin-top: 0.15rem;
    }
    .status-card {
        background: #FFFFFF;
        border: 1px solid #E9EAEC;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(20, 22, 26, 0.04);
        padding: 0.9rem 1rem;
    }
    .status-card .status-label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #5B6472;
    }
    .status-card .status-value {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        font-size: 1rem;
        font-weight: 700;
        color: #14161A;
        margin-top: 0.2rem;
    }
    .status-dot {
        width: 8px; height: 8px;
        border-radius: 999px;
        background: #0F9D58;
        flex: none;
    }
    .feature-card {
        background: #FFFFFF;
        border: 1px solid #E9EAEC;
        border-top: 3px solid var(--card-accent, #8FBF2E);
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(20, 22, 26, 0.04);
        padding: 1.1rem 1.2rem;
    }
    .feature-card .card-icon {
        width: 34px; height: 34px;
        border-radius: 8px;
        background: #F5F6F7;
        border: 1px solid #E9EAEC;
        color: var(--card-accent, #5B6472);
        display: inline-flex;
        align-items: center; justify-content: center;
        margin-bottom: 0.6rem;
    }
    .feature-card .card-icon svg {
        width: 20px; height: 20px;
    }
    .feature-card .card-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #14161A;
        margin-bottom: 0.3rem;
    }
    .feature-card .card-desc {
        font-size: 0.82rem;
        color: #5B6472;
        line-height: 1.5;
    }
    .arch-card {
        background: #FFFFFF;
        border: 1px solid #E9EAEC;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(20, 22, 26, 0.04);
        padding: 1.1rem 1.2rem;
    }
    .arch-card .arch-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.95rem;
        font-weight: 700;
        color: #14161A;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid #E9EAEC;
        margin-bottom: 0.6rem;
    }
    .arch-card .arch-title svg {
        width: 18px; height: 18px;
        color: var(--accent, #8FBF2E);
    }
    .arch-item {
        font-size: 0.82rem;
        color: #14161A;
        padding: 0.3rem 0 0.3rem 0.8rem;
        border-left: 2px solid #E9EAEC;
        margin: 0.25rem 0;
    }
    /* ── Badges, sections, tables ──────────────────────────────── */
    .density-badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        border: 1px solid #E9EAEC;
    }
    .density-low {
        background: #E7F5EE;
        color: #0F9D58;
        border-color: #C9E7D6;
    }
    .density-medium {
        background: #FEF5E5;
        color: #B7791F;
        border-color: #F3DFB8;
    }
    .density-high {
        background: #FDECEA;
        color: #D93025;
        border-color: #F5C6C1;
    }
    .section-container {
        background: #FFFFFF;
        border: 1px solid #E9EAEC;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(20, 22, 26, 0.04);
        padding: 1.1rem 1.25rem;
        margin-bottom: 1rem;
    }
    .section-container h3, .section-container h4 {
        color: #14161A;
    }
    .info-box {
        background: #F5F6F7;
        border: 1px solid #E9EAEC;
        border-left: 3px solid #8FBF2E;
        border-radius: 0 8px 8px 0;
        padding: 0.85rem 1rem;
        font-size: 0.85rem;
        color: #14161A;
    }
    .warning-box {
        background: #FEF5E5;
        border: 1px solid #F3DFB8;
        border-left: 3px solid #B7791F;
        border-radius: 0 8px 8px 0;
        padding: 0.85rem 1rem;
        font-size: 0.85rem;
        color: #14161A;
    }
    .stats-table, .model-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }
    .stats-table th, .model-table th {
        text-align: left;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #5B6472;
        padding: 0.55rem 0.9rem;
        border-bottom: 1px solid #E9EAEC;
    }
    .stats-table td, .model-table td {
        padding: 0.55rem 0.9rem;
        border-bottom: 1px solid #E9EAEC;
        color: #14161A;
    }
    .stats-table tr:last-child td, .model-table tr:last-child td {
        border-bottom: none;
    }
    .stats-table tr:hover td, .model-table tr:hover td {
        background: #FAFBFC;
    }
    /* ── Sidebar rail, Streamlit controls ────────────────────────── */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.5rem 0.25rem 0.75rem;
        border-bottom: 1px solid #E9EAEC;
        margin-bottom: 0.5rem;
    }
    .sidebar-brand .brand-logo-svg {
        width: 30px; height: 30px;
        color: #14161A;
        flex: none;
    }
    .sidebar-brand h2 {
        font-size: 0.95rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #14161A;
        margin: 0;
    }
    .sidebar-brand p {
        font-size: 0.7rem;
        color: #5B6472;
        margin: 0;
    }
    .model-status {
        background: #FFFFFF;
        border: 1px solid #E9EAEC;
        border-radius: 8px;
        padding: 0.7rem 0.8rem;
    }
    .model-status .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        font-size: 0.82rem;
        font-weight: 700;
        color: #14161A;
    }
    .model-status .status-detail {
        font-size: 0.72rem;
        color: #5B6472;
        margin-top: 0.2rem;
    }
    .analyses-panel {
        background: #FFFFFF;
        border: 1px solid #E9EAEC;
        border-radius: 8px;
        padding: 0.9rem 1rem;
    }
    .analyses-panel h4 {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #5B6472;
        margin: 0 0 0.6rem;
    }
    /* Streamlit buttons: solid ink primary, flat secondary */
    .stButton > button[kind="primary"], .stButton > button[kind="primaryFormSubmit"] {
        background: #14161A;
        color: #FFFFFF;
        border: 1px solid #14161A;
        border-radius: 6px;
        font-weight: 600;
    }
    .stButton > button[kind="primary"]:hover, .stButton > button[kind="primaryFormSubmit"]:hover {
        background: #2A2E35;
        border-color: #2A2E35;
    }
    .stButton > button[kind="secondary"] {
        background: #FFFFFF;
        color: #14161A;
        border: 1px solid #E9EAEC;
        border-radius: 6px;
        font-weight: 600;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #8FBF2E;
    }
    .stButton > button:focus-visible, .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        outline: 2px solid #B4E04C;
        outline-offset: 1px;
    }
    /* Tabs / radio: underline + lime active state */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #5B6472;
    }
    .stTabs [aria-selected="true"] {
        color: #14161A;
        border-bottom: 2px solid #8FBF2E;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background: #EFF6DA;
        border-color: #B4E04C;
        border-radius: 6px;
    }
    /* File uploader + progress: flat */
    [data-testid="stFileUploader"] section {
        border-radius: 8px;
        border: 1px dashed #E9EAEC;
        background: #FFFFFF;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #8FBF2E;
    }
    .stProgress > div > div > div > div {
        background: #8FBF2E;
    }
    hr {
        border: none;
        height: 1px;
        background: #E9EAEC;
        margin: 1.25rem 0;
    }
/*__P4__*/
/*__P3__*/
/*__P2__*/
    </style>
    """


# ── Density Color Utilities (re-exported from theme) ──────────────────────────

DENSITY_COLORS = dict(DENSITY)

DENSITY_BG_COLORS = dict(DENSITY_BG)


def header_html() -> str:
    """Return HTML for the flat header section."""
    return """
    <div class="hero-section">
        <h1>VISIONLYTICS</h1>
        <p>Intelligent Visual Crowd Analytics</p>
    </div>
    """


def density_badge_html(density: str) -> str:
    """Return HTML for a flat pill density badge."""
    css_class = f"density-{density.lower()}"
    return f'<span class="density-badge {css_class}">{density}</span>'


def metric_card_html(label: str, value: str, color: str = "#14161A") -> str:
    """Return HTML for a flat metric card."""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color}">{value}</div>
    </div>
    """


def status_card_html(label: str, value: str, is_online: bool = True) -> str:
    """Return HTML for a flat system status card."""
    dot_color = "#0F9D58" if is_online else "#B7791F"
    return f"""
    <div class="status-card">
        <div class="status-label">{label}</div>
        <div class="status-value">
            <span class="status-dot" style="background: {dot_color};"></span>
            {value}
        </div>
    </div>
    """


def feature_card_html(icon: str, title: str, description: str, accent_color: str = "#8FBF2E") -> str:
    """Return HTML for a flat feature card."""
    return f"""
    <div class="feature-card" style="--card-accent: {accent_color};">
        <div class="card-icon">{icon}</div>
        <div class="card-title">{title}</div>
        <div class="card-desc">{description}</div>
    </div>
    """


def arch_card_html(icon: str, title: str, items: list, accent_color: str = "#8FBF2E") -> str:
    """Return HTML for a flat architecture card."""
    items_html = "\n".join(
        f'<div class="arch-item">{item}</div>' for item in items
    )
    return f"""
    <div class="arch-card" style="--accent: {accent_color};">
        <div class="arch-title">{icon} {title}</div>
        <div class="arch-list">
            {items_html}
        </div>
    </div>
    """
