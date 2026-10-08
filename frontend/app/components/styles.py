"""
Mono-Clay design system for Visionlytics.

Soft embossed grayscale surfaces, generous radii, tactile controls and one
restrained indigo accent. Class names are unchanged from the previous flat
system so pages need no edits. Density is encoded with ink shades only.
"""

from app.components.icons import BRAND_LOGO_SVG
from app.components.theme import DENSITY, DENSITY_BG


def get_custom_css() -> str:
    """Return the Mono-Clay custom CSS."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Clay Canvas & Theme Reset ───────────────────────────────── */
    :root, .stApp, [data-testid="stAppViewContainer"], [data-theme="dark"], [data-theme="light"] {
        --background-color: #E9EBF0 !important;
        --secondary-background-color: #FFFFFF !important;
        --text-color: #14161A !important;
        --primary-color: #1877F2 !important;
    }

    .stApp {
        background-color: transparent !important;
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
        color: #1877F2 !important;
    }

    :focus-visible {
        outline: 2px solid #1877F2 !important;
        outline-offset: 2px;
    }

    /* ── Streamlit Top Header & Chrome ───────────────────────────── */
    header[data-testid="stHeader"], [data-testid="stHeader"] {
        background: transparent !important;
        background-color: transparent !important;
        color: #14161A !important;
    }
    header[data-testid="stHeader"] * {
        color: #14161A !important;
    }

    /* ── Top Glowing Accent Line ─────────────────────────────────── */
    .vl-top-accent-line {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 3.5px;
        background: linear-gradient(90deg, #6366F1 0%, #1877F2 45%, #38BDF8 100%);
        z-index: 99999;
        box-shadow: 0 1px 6px rgba(24, 119, 242, 0.4);
    }

    /* ── Top Navigation Bar Container ────────────────────────────── */
    .vl-navbar-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 14px;
        margin-bottom: 1.8rem;
        padding: 4px 0;
        width: 100%;
        box-sizing: border-box;
    }

    /* ── Brand Pill (Left) ───────────────────────────────────────── */
    .vl-brand-pill {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: #F1F3F7;
        padding: 7px 16px 7px 10px;
        border-radius: 16px;
        border: 1px solid rgba(0, 0, 0, 0.05);
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
        text-decoration: none !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
        flex-shrink: 0;
    }
    .vl-brand-pill:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    }
    .vl-brand-icon-wrap {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .vl-brand-icon-wrap img, .brand-logo-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
    }
    .vl-brand-name {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        color: #14161A !important;
    }


    /* ── Main Navigation Pill (Center/Right) ──────────────────────── */
    .vl-nav-pill {
        display: inline-flex;
        align-items: center;
        justify-content: space-between;
        background: #F1F3F7;
        border-radius: 18px;
        padding: 5px 12px;
        border: 1px solid rgba(0, 0, 0, 0.05);
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
        flex: 1;
        max-width: 980px;
    }
    .vl-nav-links {
        display: flex;
        align-items: center;
        gap: 6px;
        flex-wrap: nowrap;
    }
    .vl-nav-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        text-decoration: none !important;
        border-radius: 12px;
        padding: 7px 15px;
        color: #4B5563 !important;
        transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        min-height: 42px;
        box-sizing: border-box;
    }
    .vl-nav-btn:hover {
        color: #1877F2 !important;
        background: rgba(24, 119, 242, 0.07);
    }
    .vl-nav-btn.active {
        background: #1877F2 !important;
        color: #FFFFFF !important;
        box-shadow: 0 3px 12px rgba(24, 119, 242, 0.35);
        padding: 8px 22px;
    }
    .vl-nav-btn.active * {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    .vl-nav-single {
        font-size: 0.92rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        line-height: 1;
    }
    .vl-nav-stack {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        line-height: 1.15;
    }
    .vl-nav-stack .nav-top {
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: -0.01em;
    }
    .vl-nav-stack .nav-sub {
        font-size: 0.77rem;
        font-weight: 500;
        opacity: 0.92;
    }

    /* ── Right Utility Controls ──────────────────────────────────── */
    .vl-nav-controls {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-left: 10px;
        padding-left: 12px;
        border-left: 1px solid rgba(0, 0, 0, 0.08);
    }
    .vl-nav-icon-btn {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #4B5563;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.18s ease;
    }
    .vl-nav-icon-btn:hover {
        background: rgba(0, 0, 0, 0.05);
        color: #1877F2;
    }
    .vl-nav-avatar-btn {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #1877F2;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(24, 119, 242, 0.35);
        cursor: pointer;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .vl-nav-avatar-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(24, 119, 242, 0.45);
    }

    /* ── Sidebar Clay Rail ───────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: rgba(233, 235, 240, 0.88) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-right: none !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── Modern Hero Header ──────────────────────────────────────── */
    .hero-section {
        background: #FFFFFF;
        border: none;
        border-radius: 22px;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
        padding: 1.6rem 2rem;
        margin-bottom: 1.75rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1.25rem;
    }
    .hero-content-wrap {
        display: flex;
        align-items: center;
        gap: 1.25rem;
    }
    .hero-brand-badge {
        width: 52px;
        height: 52px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(24, 119, 242, 0.25);
        overflow: hidden;
    }
    .hero-brand-badge svg, .hero-brand-badge img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
    }

    .hero-text-block h1 {
        color: #14161A !important;
        font-size: 1.75rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .hero-text-block p {
        color: #6B7280 !important;
        font-size: 0.95rem;
        margin: 0.25rem 0 0;
        font-weight: 500;
    }
    .hero-badges-row {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }
    .hero-pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 999px;
        background: #F3F4F6;
        color: #4B5563;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid rgba(0, 0, 0, 0.04);
    }
    .hero-pill-badge.active {
        background: #ECFDF5;
        color: #047857;
        border-color: rgba(16, 185, 129, 0.2);
    }
    .hero-pill-badge .badge-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #10B981;
        display: inline-block;
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

    /* ── Segmented Control Filters (Analyses & Filters) ──────────── */
    [data-testid="stSegmentedControl"],
    div[data-testid="stSegmentedControl"] {
        background: transparent !important;
    }
    [data-testid="stSegmentedControl"] button,
    div[data-testid="stSegmentedControl"] button,
    div[data-baseweb="button-group"] button {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #14161A !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 12px !important;
        padding: 0.45rem 1rem !important;
        box-shadow: 2px 2px 5px rgba(15, 23, 42, 0.06),
                    -2px -2px 5px rgba(255, 255, 255, 0.8) !important;
    }
    [data-testid="stSegmentedControl"] button *,
    div[data-testid="stSegmentedControl"] button *,
    div[data-baseweb="button-group"] button * {
        color: #14161A !important;
        font-weight: 600 !important;
    }
    [data-testid="stSegmentedControl"] button[aria-checked="true"],
    [data-testid="stSegmentedControl"] button[data-checked="true"],
    [data-testid="stSegmentedControl"] button[aria-pressed="true"],
    div[data-baseweb="button-group"] button[aria-checked="true"],
    div[data-baseweb="button-group"] button[aria-pressed="true"] {
        background: #1877F2 !important;
        background-color: #1877F2 !important;
        color: #FFFFFF !important;
        border-color: #1877F2 !important;
        box-shadow: 0 2px 8px rgba(24, 119, 242, 0.35) !important;
    }
    [data-testid="stSegmentedControl"] button[aria-checked="true"] *,
    [data-testid="stSegmentedControl"] button[data-checked="true"] *,
    [data-testid="stSegmentedControl"] button[aria-pressed="true"] *,
    div[data-baseweb="button-group"] button[aria-checked="true"] *,
    div[data-baseweb="button-group"] button[aria-pressed="true"] * {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* ── Clay Buttons & Controls ─────────────────────────────────── */
    .stButton > button,
    button[data-testid="baseButton-secondary"],
    button[data-testid="stBaseButton-secondary"],
    [data-testid="stBaseButton-secondary"] {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #14161A !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        box-shadow: 4px 4px 8px rgba(15, 23, 42, 0.08),
                    -3px -3px 7px rgba(255, 255, 255, 0.9) !important;
        transition: transform 220ms cubic-bezier(0.34, 1.56, 0.64, 1),
                    box-shadow 220ms cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    }
    .stButton > button *,
    button[data-testid="baseButton-secondary"] *,
    button[data-testid="stBaseButton-secondary"] *,
    [data-testid="stBaseButton-secondary"] * {
        color: #14161A !important;
    }
    .stButton > button:hover,
    button[data-testid="baseButton-secondary"]:hover,
    button[data-testid="stBaseButton-secondary"]:hover {
        background: #F9FAFB !important;
        border-color: #9CA3AF !important;
        transform: translateY(-2px);
    }
    .stButton > button:active,
    button[data-testid="baseButton-secondary"]:active,
    button[data-testid="stBaseButton-secondary"]:active {
        transform: translateY(0) scale(0.97);
        box-shadow: inset 3px 3px 6px rgba(15, 23, 42, 0.10),
                    inset -3px -3px 6px rgba(255, 255, 255, 0.9) !important;
    }
    .stButton > button[kind="primary"],
    .stButton > button[kind="primaryFormSubmit"],
    button[data-testid="stBaseButton-primary"],
    button[data-testid="baseButton-primary"] {
        background: #4F46E5 !important;
        background-color: #4F46E5 !important;
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
    .stButton > button[kind="primary"] *,
    button[data-testid="stBaseButton-primary"] * {
        color: #FFFFFF !important;
    }
    .stButton > button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {
        background: #4338CA !important;
        border: none !important;
        transform: translateY(-2px);
    }

    /* ── Radio Navigation (Sidebar) ───────────────────────────────── */
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] p,
    [data-testid="stRadio"] span {
        color: #14161A !important;
        font-weight: 500 !important;
    }
    [data-testid="stRadio"] [role="radiogroup"] [aria-checked="true"] {
        color: #4F46E5 !important;
    }
    [data-testid="stRadio"] [role="radiogroup"] [aria-checked="true"] > div:first-child {
        border-color: #4F46E5 !important;
        background-color: #4F46E5 !important;
    }

    /* ── Code Badges ─────────────────────────────────────────────── */
    code {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #14161A !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 6px !important;
        padding: 0.15rem 0.45rem !important;
        font-weight: 600 !important;
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
    """Return HTML for the updated hero banner with brand mark and stats."""
    return (
        f'<div class="hero-section">'
        f'<div class="hero-content-wrap">'
        f'<div class="hero-brand-badge"><img src="app/static/logo.svg" alt="Visionlytics Logo" class="brand-logo-img" /></div>'
        f'<div class="hero-text-block">'
        f'<h1>VISIONLYTICS</h1>'
        f'<p>Intelligent Visual Crowd Analytics & Machine Learning Platform</p>'
        f'</div>'
        f'</div>'

        f'<div class="hero-badges-row">'
        f'<span class="hero-pill-badge active"><span class="badge-dot"></span> System Live</span>'
        f'<span class="hero-pill-badge">YOLOv8s Detector</span>'
        f'<span class="hero-pill-badge">Multi-Model ML</span>'
        f'<span class="hero-pill-badge">Spatial Density Map</span>'
        f'</div>'
        f'</div>'
    )


def density_badge_html(density: str) -> str:
    """Return HTML for a crisp pill density badge."""
    css_class = f"density-{density.lower()}"
    return f'<span class="density-badge {css_class}">{density}</span>'


def metric_card_html(label: str, value: str, color: str = "#14161A") -> str:
    """Return HTML for a clay metric card."""
    return f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value" style="color: {color} !important;">{value}</div></div>'


def status_card_html(label: str, value: str, is_online: bool = True) -> str:
    """Return HTML for a clay system status card."""
    dot_color = "#10B981" if is_online else "#9CA3AF"
    return f'<div class="status-card"><div class="status-label">{label}</div><div class="status-value"><span class="status-dot" style="background: {dot_color};"></span>{value}</div></div>'




def feature_card_html(icon: str, title: str, description: str, accent_color: str = "#14161A") -> str:
    """Return HTML for a clay feature card."""
    return f'<div class="feature-card"><div class="card-icon">{icon}</div><div class="card-title">{title}</div><div class="card-desc">{description}</div></div>'


def arch_card_html(icon: str, title: str, items: list, accent_color: str = "#14161A") -> str:
    """Return HTML for a clay architecture card."""
    items_html = "".join(f'<div class="arch-item">{item}</div>' for item in items)
    return f'<div class="arch-card"><div class="arch-title">{icon} {title}</div><div class="arch-list">{items_html}</div></div>'


def offline_banner_html(message: str) -> str:
    """Return HTML for a mono-clay connectivity banner (no alert washes)."""
    return f'<div class="clay-banner"><span class="clay-banner-dot"></span><div>{message}</div></div>'

