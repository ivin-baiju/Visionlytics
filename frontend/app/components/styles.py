"""
Custom CSS Styles for Visionlytics Dashboard.

Provides a premium, modern light-themed interface with glassmorphism,
soft gradients, micro-animations, and clean typography for the
Streamlit application. All custom styling is injected via st.markdown().
"""


def get_custom_css() -> str:
    """Return the custom CSS for the Visionlytics dashboard."""
    return """
    <style>
    /* ── Keyframe Animations ───────────────────────────────────────── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeInScale {
        from { opacity: 0; transform: scale(0.96); }
        to { opacity: 1; transform: scale(1); }
    }

    @keyframes softFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-4px); }
    }

    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes dotPulse {
        0%, 100% { opacity: 0.5; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.3); }
    }

    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    /* ── Hero Section ──────────────────────────────────────────────── */
    .hero-section {
        background: linear-gradient(135deg, #4A7DFF 0%, #6B9FFF 30%, #A78BFA 60%, #F472B6 100%);
        background-size: 300% 300%;
        animation: gradientFlow 10s ease infinite;
        padding: 2.8rem 3rem;
        border-radius: 20px;
        margin-bottom: 1.8rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(74, 125, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at 30% 40%, rgba(255,255,255,0.15) 0%, transparent 50%),
                    radial-gradient(circle at 70% 60%, rgba(255,255,255,0.1) 0%, transparent 40%);
        pointer-events: none;
    }
    .hero-section h1 {
        color: #ffffff;
        font-family: 'Outfit', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 3px;
        text-shadow: 0 2px 12px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }
    .hero-section p {
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.95rem;
        margin: 0.5rem 0 0;
        font-weight: 400;
        letter-spacing: 2px;
        text-transform: uppercase;
        position: relative;
        z-index: 1;
    }

    /* ── Glass Card ────────────────────────────────────────────────── */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 1.6rem;
        border: 1px solid rgba(74, 125, 255, 0.08);
        box-shadow:
            0 4px 24px rgba(26, 35, 64, 0.06),
            0 1px 3px rgba(26, 35, 64, 0.04);
        transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
        animation: fadeInScale 0.5s ease-out both;
        position: relative;
        overflow: hidden;
    }
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow:
            0 12px 40px rgba(74, 125, 255, 0.12),
            0 4px 12px rgba(26, 35, 64, 0.06);
        border-color: rgba(74, 125, 255, 0.15);
    }

    /* ── Metric Card ───────────────────────────────────────────────── */
    .metric-card {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        border: 1px solid rgba(74, 125, 255, 0.06);
        box-shadow: 0 2px 16px rgba(26, 35, 64, 0.05);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        animation: fadeInUp 0.4s ease-out both;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(74, 125, 255, 0.1);
    }
    .metric-card .metric-label {
        font-size: 0.72rem;
        color: #7b8794;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .metric-card .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a2340;
        line-height: 1.2;
    }

    /* ── Feature Card ──────────────────────────────────────────────── */
    .feature-card {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 18px;
        padding: 2rem 1.6rem;
        border: 1px solid rgba(74, 125, 255, 0.06);
        box-shadow: 0 4px 20px rgba(26, 35, 64, 0.05);
        transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
        animation: fadeInScale 0.5s ease-out both;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .feature-card::after {
        content: '';
        position: absolute;
        bottom: 0; left: 50%;
        transform: translateX(-50%);
        width: 0%;
        height: 3px;
        background: linear-gradient(90deg, var(--card-accent, #4A7DFF), transparent);
        border-radius: 3px;
        transition: width 0.4s ease;
    }
    .feature-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 40px rgba(74, 125, 255, 0.12);
        border-color: rgba(74, 125, 255, 0.12);
    }
    .feature-card:hover::after {
        width: 60%;
    }
    .feature-card .card-icon {
        width: 52px; height: 52px;
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(74, 125, 255, 0.08), rgba(167, 139, 250, 0.06));
        border: 1px solid rgba(74, 125, 255, 0.1);
        display: inline-flex;
        align-items: center; justify-content: center;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .feature-card:hover .card-icon {
        background: linear-gradient(135deg, rgba(74, 125, 255, 0.15), rgba(167, 139, 250, 0.1));
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(74, 125, 255, 0.15);
    }
    .feature-card .card-icon svg {
        width: 26px; height: 26px;
        display: block;
    }
    .feature-card .card-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.85rem;
        color: #1a2340;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .feature-card .card-desc {
        color: #7b8794;
        font-size: 0.85rem;
        line-height: 1.6;
    }

    /* ── Architecture Card ─────────────────────────────────────────── */
    .arch-card {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        padding: 1.6rem;
        border: 1px solid rgba(74, 125, 255, 0.06);
        box-shadow: 0 2px 16px rgba(26, 35, 64, 0.04);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        animation: fadeInUp 0.5s ease-out both;
        position: relative;
        overflow: hidden;
    }
    .arch-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
        background: linear-gradient(180deg, var(--accent, #4A7DFF), transparent);
        border-radius: 3px 0 0 3px;
    }
    .arch-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(74, 125, 255, 0.1);
    }
    .arch-card .arch-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: #1a2340;
        margin-bottom: 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(74, 125, 255, 0.08);
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .arch-card .arch-title svg {
        width: 20px; height: 20px;
        flex-shrink: 0;
    }
    .arch-card .arch-list {
        color: #5a6578;
        font-size: 0.85rem;
        line-height: 1.9;
    }
    .arch-card .arch-list .arch-item {
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .arch-card .arch-list .arch-item::before {
        content: '▸';
        color: var(--accent, #4A7DFF);
        font-size: 0.7rem;
    }

    /* ── Status Card ───────────────────────────────────────────────── */
    .status-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        border: 1px solid rgba(46, 205, 167, 0.1);
        box-shadow: 0 2px 12px rgba(26, 35, 64, 0.04);
        transition: all 0.25s ease;
        animation: fadeInUp 0.4s ease-out both;
        text-align: center;
    }
    .status-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 205, 167, 0.08);
    }
    .status-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #2ECDA7;
        margin-right: 6px;
        animation: dotPulse 2s ease-in-out infinite;
        box-shadow: 0 0 6px rgba(46, 205, 167, 0.4);
    }
    .status-label {
        font-size: 0.68rem;
        color: #7b8794;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .status-value {
        font-size: 0.95rem;
        font-weight: 700;
        color: #2ECDA7;
    }

    /* ── Density Badges ────────────────────────────────────────────── */
    .density-badge {
        display: inline-block;
        padding: 0.4rem 1.3rem;
        border-radius: 24px;
        font-weight: 700;
        font-size: 0.8rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        transition: all 0.25s ease;
    }
    .density-badge:hover {
        transform: scale(1.05);
    }
    .density-low {
        background: linear-gradient(135deg, rgba(46, 205, 167, 0.15), rgba(46, 205, 167, 0.08));
        color: #1a9a7a;
        border: 1px solid rgba(46, 205, 167, 0.2);
    }
    .density-medium {
        background: linear-gradient(135deg, rgba(255, 179, 71, 0.15), rgba(255, 179, 71, 0.08));
        color: #cc7a00;
        border: 1px solid rgba(255, 179, 71, 0.2);
    }
    .density-high {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.15), rgba(255, 107, 107, 0.08));
        color: #cc3333;
        border: 1px solid rgba(255, 107, 107, 0.2);
    }

    /* ── Section Container ─────────────────────────────────────────── */
    .section-container {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 1.6rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(74, 125, 255, 0.06);
        box-shadow: 0 2px 12px rgba(26, 35, 64, 0.03);
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out both;
    }
    .section-container:hover {
        border-color: rgba(74, 125, 255, 0.1);
        box-shadow: 0 4px 20px rgba(26, 35, 64, 0.06);
    }
    .section-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: #1a2340;
        margin-bottom: 0.8rem;
    }

    /* ── Info / Warning Boxes ──────────────────────────────────────── */
    .info-box {
        background: linear-gradient(135deg, rgba(74, 125, 255, 0.06), rgba(74, 125, 255, 0.02));
        border-left: 3px solid #4A7DFF;
        border-radius: 0 14px 14px 0;
        padding: 1.2rem 1.6rem;
        margin: 1rem 0;
        color: #3a4560;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }
    .info-box:hover {
        background: linear-gradient(135deg, rgba(74, 125, 255, 0.1), rgba(74, 125, 255, 0.04));
    }
    .warning-box {
        background: linear-gradient(135deg, rgba(255, 179, 71, 0.08), rgba(255, 179, 71, 0.02));
        border-left: 3px solid #FFB347;
        border-radius: 0 14px 14px 0;
        padding: 1.2rem 1.6rem;
        margin: 1rem 0;
        color: #3a4560;
        font-size: 0.9rem;
    }

    /* ── Stats Table ───────────────────────────────────────────────── */
    .stats-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
    }
    .stats-table tr {
        transition: all 0.2s ease;
    }
    .stats-table tr:hover {
        background: rgba(74, 125, 255, 0.04);
    }
    .stats-table td {
        padding: 0.65rem 0.9rem;
        border-bottom: 1px solid rgba(74, 125, 255, 0.06);
    }
    .stats-table td:first-child {
        color: #5a6578;
        font-size: 0.85rem;
    }
    .stats-table td:last-child {
        color: #1a2340;
        font-weight: 600;
        text-align: right;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── Model Comparison Table ─────────────────────────────────────── */
    .model-table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 14px;
        overflow: hidden;
    }
    .model-table th {
        background: linear-gradient(135deg, #eef3fb, #e4eaf6);
        color: #3a4560;
        padding: 0.9rem 1rem;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    .model-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(74, 125, 255, 0.06);
        color: #1a2340;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88rem;
        transition: all 0.2s ease;
    }
    .model-table tr:hover td {
        background: rgba(74, 125, 255, 0.04);
    }
    .model-table tr.best-model {
        background: rgba(46, 205, 167, 0.06);
        border-left: 3px solid #2ECDA7;
    }

    /* ── Sidebar Styling ───────────────────────────────────────────── */
    .sidebar-brand {
        text-align: center;
        padding: 1.2rem 0;
    }
    .sidebar-brand .brand-logo-svg {
        width: 44px; height: 44px;
        margin: 0 auto 0.6rem;
        display: block;
        filter: drop-shadow(0 2px 8px rgba(74, 125, 255, 0.3));
    }
    .sidebar-brand h2 {
        color: #ffffff;
        margin: 0;
        letter-spacing: 3px;
        font-size: 1.2rem;
        font-weight: 700;
        font-family: 'Outfit', sans-serif;
    }
    .sidebar-brand p {
        color: rgba(255, 255, 255, 0.45);
        font-size: 0.68rem;
        margin-top: 0.25rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* ── Model Status Widget ───────────────────────────────────────── */
    .model-status {
        text-align: center;
        padding: 0.9rem;
        margin: 0.5rem;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .model-status .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .model-status .status-detail {
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.7rem;
        margin-top: 0.25rem;
    }

    /* ── Button Overrides ──────────────────────────────────────────── */
    .stButton > button {
        border-radius: 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74, 125, 255, 0.25);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* ── Progress Bar ──────────────────────────────────────────────── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4A7DFF, #A78BFA, #4A7DFF);
        background-size: 200% 100%;
        animation: shimmer 2s linear infinite;
        border-radius: 10px;
    }

    /* ── Section Dividers ──────────────────────────────────────────── */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(74, 125, 255, 0.15), transparent);
        margin: 1.5rem 0;
    }

    /* ── Scrollbar ─────────────────────────────────────────────────── */
    ::-webkit-scrollbar {
        width: 6px; height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #f0f3f9;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, rgba(74, 125, 255, 0.25), rgba(167, 139, 250, 0.25));
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, rgba(74, 125, 255, 0.45), rgba(167, 139, 250, 0.45));
    }

    /* ── Hide Branding ─────────────────────────────────────────────── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── File Uploader ─────────────────────────────────────────────── */
    [data-testid="stFileUploader"] section {
        border-radius: 16px;
        border-color: rgba(74, 125, 255, 0.12);
        transition: border-color 0.3s ease;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: rgba(74, 125, 255, 0.25);
    }

    /* ── Dataframe ─────────────────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }

    /* ── Animation Stagger Delays ──────────────────────────────────── */
    .stagger-1 { animation-delay: 0.05s; }
    .stagger-2 { animation-delay: 0.1s; }
    .stagger-3 { animation-delay: 0.15s; }
    .stagger-4 { animation-delay: 0.2s; }

    </style>
    """


# ── Density Color Utilities ──────────────────────────────────────────────────

DENSITY_COLORS = {
    "LOW": "#2ECDA7",
    "MEDIUM": "#FFB347",
    "HIGH": "#FF6B6B",
}

DENSITY_BG_COLORS = {
    "LOW": "rgba(46, 205, 167, 0.1)",
    "MEDIUM": "rgba(255, 179, 71, 0.1)",
    "HIGH": "rgba(255, 107, 107, 0.1)",
}


def header_html() -> str:
    """Return HTML for the hero header section."""
    return """
    <div class="hero-section">
        <h1>VISIONLYTICS</h1>
        <p>Intelligent Visual Crowd Analytics</p>
    </div>
    """


def density_badge_html(density: str) -> str:
    """Return HTML for a density badge."""
    css_class = f"density-{density.lower()}"
    return f'<span class="density-badge {css_class}">{density}</span>'


def metric_card_html(label: str, value: str, color: str = "#1a2340") -> str:
    """Return HTML for a metric card."""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color}">{value}</div>
    </div>
    """


def status_card_html(label: str, value: str, is_online: bool = True) -> str:
    """Return HTML for a system status card."""
    dot_color = "#2ECDA7" if is_online else "#FFB347"
    value_color = "#2ECDA7" if is_online else "#FFB347"
    return f"""
    <div class="status-card">
        <div class="status-label">{label}</div>
        <div class="status-value" style="color: {value_color}">
            <span class="status-dot" style="background: {dot_color}; box-shadow: 0 0 6px {dot_color};"></span>
            {value}
        </div>
    </div>
    """


def feature_card_html(icon: str, title: str, description: str, accent_color: str = "#4A7DFF") -> str:
    """Return HTML for a feature card."""
    return f"""
    <div class="feature-card" style="--card-accent: {accent_color};">
        <div class="card-icon">{icon}</div>
        <div class="card-title">{title}</div>
        <div class="card-desc">{description}</div>
    </div>
    """


def arch_card_html(icon: str, title: str, items: list, accent_color: str = "#4A7DFF") -> str:
    """Return HTML for an architecture card."""
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
