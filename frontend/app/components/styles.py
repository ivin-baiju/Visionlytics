"""
Mono-Clay design system for Visionlytics.

Soft embossed grayscale surfaces, generous radii, tactile controls and one
restrained indigo accent. Class names are unchanged from the previous flat
system so pages need no edits. Density is encoded with ink shades only.
"""

from app.components.theme import DENSITY, DENSITY_BG


def get_custom_css() -> str:
    """Return the Mono-Clay custom CSS."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Clay Canvas ─────────────────────────────────────────────── */
    .stApp {
        background-color: #E9EBF0 !important;
        color: #14161A !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .block-container {
        padding-top: 1.75rem;
        padding-bottom: 3rem;
        max-width: 1240px;
        animation: clay-rise 220ms cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    @keyframes clay-rise {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Streamlit core text overrides to ensure total legibility */
    .stApp p, .stApp span, .stApp label, .stApp div {
        color: #14161A;
    }
    .stApp a {
        color: #4F46E5 !important;
    }

    :focus-visible {
        outline: 2px solid #4F46E5 !important;
        outline-offset: 2px;
    }

    /* ── Sidebar Clay Rail ───────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: #E9EBF0 !important;
        border-right: none !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── Clay Hero Header ────────────────────────────────────────── */
    .hero-section {
        background: #FFFFFF;
        border: none;
        border-radius: 22px;
        box-shadow: 8px 8px 16px rgba(15, 23, 42, 0.10),
                    -8px -8px 16px rgba(255, 255, 255, 0.9);
        padding: 1.6rem 1.9rem;
        margin-bottom: 1.75rem;
    }
    .hero-section h1 {
        color: #14161A !important;
        font-size: 1.7rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .hero-section p {
        color: #6B7280 !important;
        font-size: 0.95rem;
        margin: 0.35rem 0 0;
        font-weight: 500;
    }

    .page-header {
        margin: 0 0 1.25rem;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
    }
    .page-header .page-tick {
        width: 6px;
        align-self: stretch;
        border-radius: 999px;
        background: #14161A;
        flex: none;
    }
    .page-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #14161A !important;
        margin: 0;
    }
    .page-subtitle {
        font-size: 0.9rem;
        color: #6B7280 !important;
        margin: 0.25rem 0 0;
    }

    /* ── Clay Metric Cards ────────────────────────────────────────── */
    .metric-card {
        background: #FFFFFF;
        border: none;
        border-radius: 18px;
        padding: 1.15rem 1.3rem;
        box-shadow: 8px 8px 16px rgba(15, 23, 42, 0.10),
                    -8px -8px 16px rgba(255, 255, 255, 0.9);
        transition: transform 220ms cubic-bezier(0.34, 1.56, 0.64, 1),
                    box-shadow 220ms cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 12px 12px 24px rgba(15, 23, 42, 0.12),
                    -12px -12px 24px rgba(255, 255, 255, 0.95);
    }
    .metric-card:active {
        transform: translateY(0) scale(0.99);
        box-shadow: inset 4px 4px 8px rgba(15, 23, 42, 0.10),
                    inset -4px -4px 8px rgba(255, 255, 255, 0.9);
    }
    .metric-card .metric-label {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #6B7280 !important;
    }
    .metric-card .metric-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #14161A !important;
        margin-top: 0.3rem;
        letter-spacing: -0.02em;
    }

    /* ── Clay Status Cards ────────────────────────────────────────── */
    .status-card {
        background: #FFFFFF;
        border: none;
        border-radius: 18px;
        padding: 1rem 1.25rem;
        box-shadow: 5px 5px 10px rgba(15, 23, 42, 0.08),
                    -5px -5px 10px rgba(255, 255, 255, 0.9);
    }
    .status-card .status-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #6B7280 !important;
    }
    .status-card .status-value {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.05rem;
        font-weight: 700;
        color: #14161A !important;
        margin-top: 0.3rem;
    }
    .status-dot {
        width: 10px; height: 10px;
        border-radius: 999px;
        background: #14161A;
        box-shadow: inset 1px 1px 2px rgba(255, 255, 255, 0.5),
                    1px 1px 2px rgba(15, 23, 42, 0.25);
        flex: none;
    }

    /* ── Clay Feature Cards ───────────────────────────────────────── */
    .feature-card {
        background: #FFFFFF;
        border: none;
        border-radius: 18px;
        padding: 1.3rem 1.4rem;
        box-shadow: 8px 8px 16px rgba(15, 23, 42, 0.10),
                    -8px -8px 16px rgba(255, 255, 255, 0.9);
        transition: transform 220ms cubic-bezier(0.34, 1.56, 0.64, 1),
                    box-shadow 220ms cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 12px 12px 24px rgba(15, 23, 42, 0.12),
                    -12px -12px 24px rgba(255, 255, 255, 0.95);
    }
    .feature-card .card-icon {
        width: 44px; height: 44px;
        border-radius: 14px;
        background: #E9EBF0;
        border: none;
        box-shadow: inset 3px 3px 6px rgba(15, 23, 42, 0.10),
                    inset -3px -3px 6px rgba(255, 255, 255, 0.9);
        color: #14161A;
        display: inline-flex;
        align-items: center; justify-content: center;
        margin-bottom: 0.8rem;
    }
    .feature-card .card-icon svg {
        width: 22px; height: 22px;
    }
    .feature-card .card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #14161A !important;
        margin-bottom: 0.35rem;
    }
    .feature-card .card-desc {
        font-size: 0.88rem;
        color: #6B7280 !important;
        line-height: 1.5;
    }

    /* ── Clay Architecture Cards ──────────────────────────────────── */
    .arch-card {
        background: #FFFFFF;
        border: none;
        border-radius: 18px;
        padding: 1.3rem 1.4rem;
        box-shadow: 8px 8px 16px rgba(15, 23, 42, 0.10),
                    -8px -8px 16px rgba(255, 255, 255, 0.9);
    }
    .arch-card .arch-title {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 1.05rem;
        font-weight: 700;
        color: #14161A !important;
        padding-bottom: 0.7rem;
        border-bottom: none;
        box-shadow: 0 1px 0 rgba(15, 23, 42, 0.08);
        margin-bottom: 0.75rem;
    }
    .arch-card .arch-title svg {
        width: 20px; height: 20px;
        color: #14161A;
    }
    .arch-item {
        font-size: 0.88rem;
        color: #2A2E35 !important;
        padding: 0.4rem 0 0.4rem 0.9rem;
        background: #E9EBF0;
        border-radius: 10px;
        box-shadow: inset 2px 2px 4px rgba(15, 23, 42, 0.08),
                    inset -2px -2px 4px rgba(255, 255, 255, 0.9);
        margin: 0.35rem 0;
    }

    /* ── Mono Density Badges (ink shades, never hue) ──────────────── */
    .density-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        box-shadow: inset 2px 2px 4px rgba(15, 23, 42, 0.10),
                    inset -2px -2px 4px rgba(255, 255, 255, 0.7);
    }
    .density-low {
        background: #F3F4F6 !important;
        color: #6B7280 !important;
        border: none;
    }
    .density-medium {
        background: #D1D5DB !important;
        color: #2A2E35 !important;
        border: none;
    }
    .density-high {
        background: #14161A !important;
        color: #FFFFFF !important;
        border: none;
        box-shadow: 3px 3px 6px rgba(15, 23, 42, 0.25),
                    -2px -2px 5px rgba(255, 255, 255, 0.7);
    }

    /* ── Clay Containers & Information Boxes ─────────────────────── */
    .section-container {
        background: #FFFFFF;
        border: none;
        border-radius: 18px;
        box-shadow: 8px 8px 16px rgba(15, 23, 42, 0.10),
                    -8px -8px 16px rgba(255, 255, 255, 0.9);
        padding: 1.3rem 1.5rem;
        margin-bottom: 1.2rem;
    }
    .section-container h3, .section-container h4 {
        color: #14161A !important;
    }
    .info-box {
        background: #EEF0FE;
        border: none;
        border-radius: 14px;
        box-shadow: inset 3px 3px 6px rgba(79, 70, 229, 0.12),
                    inset -3px -3px 6px rgba(255, 255, 255, 0.9);
        padding: 1rem 1.25rem;
        font-size: 0.9rem;
        color: #2A2E35 !important;
    }
    .warning-box {
        background: #E9EBF0;
        border: none;
        border-radius: 14px;
        box-shadow: inset 3px 3px 6px rgba(15, 23, 42, 0.10),
                    inset -3px -3px 6px rgba(255, 255, 255, 0.9);
        padding: 1rem 1.25rem;
        font-size: 0.9rem;
        color: #2A2E35 !important;
    }
    /* Mono-clay offline banner (replaces yellow/blue native alerts). */
    .clay-banner {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        background: #FFFFFF;
        border: none;
        border-radius: 18px;
        box-shadow: 5px 5px 10px rgba(15, 23, 42, 0.08),
                    -5px -5px 10px rgba(255, 255, 255, 0.9);
        padding: 1rem 1.25rem;
        margin-bottom: 1.25rem;
        font-size: 0.92rem;
        color: #2A2E35 !important;
    }
    .clay-banner .clay-banner-dot {
        width: 10px; height: 10px;
        border-radius: 999px;
        background: #9CA3AF;
        box-shadow: inset 1px 1px 2px rgba(255, 255, 255, 0.5),
                    1px 1px 2px rgba(15, 23, 42, 0.25);
        flex: none;
        margin-top: 0.35rem;
    }
    .clay-banner code {
        background: #E9EBF0;
        border-radius: 6px;
        padding: 0.1rem 0.35rem;
        font-size: 0.85em;
    }
    .stats-table, .model-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
    }
    .stats-table th, .model-table th {
        text-align: left;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #6B7280 !important;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #E5E7EB;
        background: #E9EBF0;
    }
    .stats-table td, .model-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #E5E7EB;
        color: #14161A !important;
    }
    .stats-table tr:hover td, .model-table tr:hover td {
        background: #E9EBF0;
    }

    /* ── Clay Sidebar Brand ──────────────────────────────────────── */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.85rem 1rem 1rem;
        background: #FFFFFF;
        border: none;
        border-radius: 18px;
        box-shadow: 5px 5px 10px rgba(15, 23, 42, 0.08),
                    -5px -5px 10px rgba(255, 255, 255, 0.9);
        margin-bottom: 0.85rem;
    }
    .sidebar-brand .brand-logo-svg {
        width: 34px; height: 34px;
        flex: none;
    }
    .sidebar-brand h2 {
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        color: #14161A !important;
        margin: 0;
    }
    .sidebar-brand p {
        font-size: 0.75rem;
        color: #6B7280 !important;
        margin: 0;
    }
    .model-status {
        background: #FFFFFF;
        border: none;
        border-radius: 16px;
        box-shadow: 5px 5px 10px rgba(15, 23, 42, 0.08),
                    -5px -5px 10px rgba(255, 255, 255, 0.9);
        padding: 0.85rem 1rem;
    }
    .model-status .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.88rem;
        font-weight: 700;
        color: #14161A !important;
    }
    .model-status .status-detail {
        font-size: 0.76rem;
        color: #6B7280 !important;
        margin-top: 0.2rem;
    }

    /* ── Clay Buttons & Controls ─────────────────────────────────── */
    .stButton > button[kind="primary"], .stButton > button[kind="primaryFormSubmit"] {
        background: #4F46E5 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.4rem !important;
        box-shadow: 4px 4px 8px rgba(79, 70, 229, 0.35),
                    -2px -2px 6px rgba(255, 255, 255, 0.7);
        transition: transform 220ms cubic-bezier(0.34, 1.56, 0.64, 1),
                    box-shadow 220ms cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    }
    .stButton > button[kind="primary"]:hover, .stButton > button[kind="primaryFormSubmit"]:hover {
        background: #4338CA !important;
        border: none !important;
        transform: translateY(-2px);
    }
    .stButton > button[kind="primary"]:active, .stButton > button[kind="primaryFormSubmit"]:active {
        transform: translateY(0) scale(0.97);
        box-shadow: inset 3px 3px 6px rgba(0, 0, 0, 0.25) !important;
    }
    .stButton > button[kind="secondary"] {
        background: #FFFFFF !important;
        color: #14161A !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        box-shadow: 4px 4px 8px rgba(15, 23, 42, 0.10),
                    -3px -3px 7px rgba(255, 255, 255, 0.9) !important;
        transition: transform 220ms cubic-bezier(0.34, 1.56, 0.64, 1),
                    box-shadow 220ms cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        transform: translateY(-2px);
    }
    .stButton > button[kind="secondary"]:active {
        transform: translateY(0) scale(0.97);
        box-shadow: inset 3px 3px 6px rgba(15, 23, 42, 0.10),
                    inset -3px -3px 6px rgba(255, 255, 255, 0.9) !important;
    }

    /* Clay file uploader dropzone */
    [data-testid="stFileUploader"] section {
        border-radius: 18px !important;
        border: 2px dashed #9CA3AF !important;
        background: #FFFFFF !important;
        box-shadow: inset 4px 4px 8px rgba(15, 23, 42, 0.06),
                    inset -4px -4px 8px rgba(255, 255, 255, 0.9) !important;
        padding: 1.5rem !important;
        transition: border-color 220ms ease !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #4F46E5 !important;
    }

    /* ── Skeleton shimmer (loading placeholders) ──────────────────── */
    .clay-skeleton {
        border-radius: 18px;
        background: #E9EBF0;
        box-shadow: inset 4px 4px 8px rgba(15, 23, 42, 0.08),
                    inset -4px -4px 8px rgba(255, 255, 255, 0.9);
        min-height: 88px;
        animation: clay-pulse 1.4s ease-in-out infinite;
    }
    @keyframes clay-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.55; }
    }

    @media (prefers-reduced-motion: reduce) {
        .block-container { animation: none; }
        .clay-skeleton { animation: none; }
        .metric-card, .feature-card,
        .stButton > button { transition: none !important; }
    }

    hr {
        border: none;
        height: 1px;
        background: #E5E7EB;
        margin: 1.5rem 0;
    }
    </style>
    """


# ── Density Color Utilities ──────────────────────────────────────────────────

DENSITY_COLORS = dict(DENSITY)
DENSITY_BG_COLORS = dict(DENSITY_BG)


def header_html() -> str:
    """Return HTML for the clean hero banner."""
    return """
    <div class="hero-section">
        <h1>VISIONLYTICS</h1>
        <p>Intelligent Visual Crowd Analytics & Machine Learning Platform</p>
    </div>
    """


def density_badge_html(density: str) -> str:
    """Return HTML for a crisp pill density badge."""
    css_class = f"density-{density.lower()}"
    return f'<span class="density-badge {css_class}">{density}</span>'


def metric_card_html(label: str, value: str, color: str = "#14161A") -> str:
    """Return HTML for a clay metric card."""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color} !important;">{value}</div>
    </div>
    """


def status_card_html(label: str, value: str, is_online: bool = True) -> str:
    """Return HTML for a clay system status card."""
    dot_color = "#4F46E5" if is_online else "#9CA3AF"
    return f"""
    <div class="status-card">
        <div class="status-label">{label}</div>
        <div class="status-value">
            <span class="status-dot" style="background: {dot_color};"></span>
            {value}
        </div>
    </div>
    """


def feature_card_html(icon: str, title: str, description: str, accent_color: str = "#14161A") -> str:
    """Return HTML for a clay feature card."""
    return f"""
    <div class="feature-card">
        <div class="card-icon">{icon}</div>
        <div class="card-title">{title}</div>
        <div class="card-desc">{description}</div>
    </div>
    """


def arch_card_html(icon: str, title: str, items: list, accent_color: str = "#14161A") -> str:
    """Return HTML for a clay architecture card."""
    items_html = "\n".join(
        f'<div class="arch-item">{item}</div>' for item in items
    )
    return f"""
    <div class="arch-card">
        <div class="arch-title">{icon} {title}</div>
        <div class="arch-list">
            {items_html}
        </div>
    </div>
    """


def offline_banner_html(message: str) -> str:
    """Return HTML for a mono-clay connectivity banner (no alert washes)."""
    return f"""
    <div class="clay-banner">
        <span class="clay-banner-dot"></span>
        <div>{message}</div>
    </div>
    """
