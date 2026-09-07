"""
Custom CSS Styles for Visionlytics Dashboard.

Provides a premium, futuristic dark-themed interface with rich animations,
glassmorphism, neon accent lighting, and micro-interactions for the
Streamlit application. All custom styling is injected via st.markdown().
"""


def get_custom_css() -> str:
    """Return the custom CSS for the Visionlytics dashboard."""
    return """
    <style>
    /* ── Import Google Fonts ──────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── Keyframe Animations ───────────────────────────────────────── */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 4px 20px rgba(99, 110, 230, 0.15); }
        50% { box-shadow: 0 4px 35px rgba(99, 110, 230, 0.35); }
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    @keyframes badgePulse {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.2); }
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }

    @keyframes borderGlow {
        0%, 100% { border-color: rgba(99, 110, 230, 0.15); }
        50% { border-color: rgba(99, 110, 230, 0.4); }
    }

    @keyframes slideInScale {
        from {
            opacity: 0;
            transform: scale(0.92) translateY(12px);
        }
        to {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }

    @keyframes neonPulse {
        0%, 100% { text-shadow: 0 0 5px rgba(99, 110, 230, 0.5), 0 0 20px rgba(99, 110, 230, 0.2); }
        50% { text-shadow: 0 0 10px rgba(99, 110, 230, 0.8), 0 0 40px rgba(99, 110, 230, 0.4), 0 0 60px rgba(99, 110, 230, 0.15); }
    }

    @keyframes scanline {
        0% { top: -100%; }
        100% { top: 200%; }
    }

    @keyframes dotPulse {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.5); }
    }

    /* ── Global Overrides ───────────────────────────────────────────── */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ── Header Styling ─────────────────────────────────────────────── */
    .main-header {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1040 25%, #0d1b3e 50%, #151030 75%, #0a0a1a 100%);
        background-size: 400% 400%;
        animation: gradientShift 12s ease infinite;
        padding: 2.5rem 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow:
            0 12px 50px rgba(99, 110, 230, 0.15),
            0 0 0 1px rgba(99, 110, 230, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(99, 110, 230, 0.15);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 40%, rgba(99, 110, 230, 0.06) 0%, transparent 50%),
                    radial-gradient(circle at 70% 60%, rgba(162, 155, 254, 0.04) 0%, transparent 40%);
        animation: gradientShift 15s ease infinite;
        pointer-events: none;
    }
    .main-header::after {
        content: '';
        position: absolute;
        top: -100%;
        left: 0;
        width: 100%;
        height: 50%;
        background: linear-gradient(transparent, rgba(99, 110, 230, 0.03), transparent);
        animation: scanline 8s linear infinite;
        pointer-events: none;
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2.6rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: 6px;
        animation: neonPulse 4s ease-in-out infinite;
        position: relative;
        z-index: 1;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.55);
        font-size: 0.95rem;
        margin: 0.6rem 0 0 0;
        font-weight: 400;
        letter-spacing: 3px;
        text-transform: uppercase;
        position: relative;
        z-index: 1;
    }

    /* ── Metric Cards (Glassmorphism 2.0) ────────────────────────────── */
    .metric-card {
        background: linear-gradient(145deg,
            rgba(20, 20, 40, 0.8) 0%,
            rgba(15, 25, 50, 0.7) 50%,
            rgba(20, 15, 45, 0.8) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 18px;
        padding: 1.5rem 1.8rem;
        border: 1px solid rgba(99, 110, 230, 0.1);
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.04);
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        animation: slideInScale 0.6s ease-out both;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(99, 110, 230, 0.5), transparent);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    .metric-card:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow:
            0 16px 48px rgba(99, 110, 230, 0.2),
            0 0 0 1px rgba(99, 110, 230, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.06);
        border-color: rgba(99, 110, 230, 0.3);
    }
    .metric-card:hover::before {
        opacity: 1;
    }
    .metric-card .metric-label {
        font-size: 0.7rem;
        color: rgba(255, 255, 255, 0.45);
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    .metric-card .metric-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.2;
    }

    /* ── Feature Cards (Quick Start, Architecture) ──────────────────── */
    .feature-card {
        background: linear-gradient(145deg,
            rgba(20, 20, 40, 0.7) 0%,
            rgba(15, 25, 50, 0.6) 100%);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 2rem 1.6rem;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 6px 30px rgba(0, 0, 0, 0.2);
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        animation: slideInScale 0.6s ease-out both;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .feature-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60%;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--card-accent, #636ee6), transparent);
        opacity: 0;
        transition: all 0.4s ease;
    }
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow:
            0 16px 50px rgba(99, 110, 230, 0.15),
            0 0 0 1px rgba(99, 110, 230, 0.2);
        border-color: rgba(99, 110, 230, 0.2);
    }
    .feature-card:hover::after {
        opacity: 1;
        width: 80%;
    }
    .feature-card .card-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.9rem;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        filter: drop-shadow(0 4px 12px rgba(99, 110, 230, 0.25));
    }
    .feature-card:hover .card-icon {
        background: rgba(99, 110, 230, 0.12);
        border-color: rgba(99, 110, 230, 0.35);
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 0 20px rgba(99, 110, 230, 0.3);
    }
    .feature-card .card-icon svg {
        width: 26px;
        height: 26px;
        display: block;
    }
    .feature-card .card-title {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.8);
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .feature-card .card-desc {
        color: rgba(255, 255, 255, 0.45);
        font-size: 0.82rem;
        line-height: 1.5;
    }

    /* ── Architecture Cards ─────────────────────────────────────────── */
    .arch-card {
        background: linear-gradient(145deg,
            rgba(15, 15, 30, 0.85) 0%,
            rgba(20, 30, 55, 0.75) 100%);
        backdrop-filter: blur(12px);
        border-radius: 18px;
        padding: 1.8rem;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
        transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
        animation: fadeInUp 0.6s ease-out both;
        position: relative;
        overflow: hidden;
    }
    .arch-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: linear-gradient(180deg, var(--accent, #636ee6), transparent);
        border-radius: 3px 0 0 3px;
    }
    .arch-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 40px rgba(99, 110, 230, 0.15);
        border-color: rgba(99, 110, 230, 0.15);
    }
    .arch-card .arch-title {
        font-size: 1rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        display: flex;
        align-items: center;
        gap: 0.65rem;
    }
    .arch-card .arch-title svg {
        width: 20px;
        height: 20px;
        flex-shrink: 0;
        display: inline-block;
        vertical-align: middle;
    }
    .arch-card .arch-list {
        color: rgba(255, 255, 255, 0.55);
        font-size: 0.83rem;
        line-height: 1.8;
    }
    .arch-card .arch-list .arch-item {
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .arch-card .arch-list .arch-item::before {
        content: '▸';
        color: var(--accent, #636ee6);
        font-size: 0.7rem;
    }

    /* ── Density Badges (Animated) ─────────────────────────────────── */
    .density-badge {
        display: inline-block;
        padding: 0.45rem 1.4rem;
        border-radius: 24px;
        font-weight: 700;
        font-size: 0.82rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        animation: badgePulse 2.5s ease-in-out infinite;
        transition: all 0.3s ease;
        position: relative;
    }
    .density-badge:hover {
        transform: scale(1.08);
        filter: brightness(1.15);
    }
    .density-low {
        background: linear-gradient(135deg, #00b894, #00cec9);
        color: #0a0a1a;
        box-shadow: 0 4px 20px rgba(0, 184, 148, 0.35), inset 0 1px 0 rgba(255,255,255,0.2);
    }
    .density-medium {
        background: linear-gradient(135deg, #f39c12, #e17055);
        color: #0a0a1a;
        box-shadow: 0 4px 20px rgba(243, 156, 18, 0.35), inset 0 1px 0 rgba(255,255,255,0.2);
    }
    .density-high {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: #ffffff;
        box-shadow: 0 4px 20px rgba(231, 76, 60, 0.35), inset 0 1px 0 rgba(255,255,255,0.15);
    }

    /* ── Section Containers ──────────────────────────────────────────── */
    .section-container {
        background: linear-gradient(145deg,
            rgba(14, 17, 23, 0.9) 0%,
            rgba(22, 22, 42, 0.7) 100%);
        backdrop-filter: blur(10px);
        border-radius: 18px;
        padding: 1.8rem;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(255, 255, 255, 0.06);
        transition: all 0.35s ease;
        animation: fadeInUp 0.6s ease-out both;
        position: relative;
        overflow: hidden;
    }
    .section-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99, 110, 230, 0.3), transparent);
    }
    .section-container:hover {
        border-color: rgba(99, 110, 230, 0.15);
        box-shadow: 0 6px 30px rgba(0, 0, 0, 0.2);
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(99, 110, 230, 0.3);
    }

    /* ── Status Indicator ───────────────────────────────────────────── */
    .status-card {
        background: linear-gradient(145deg,
            rgba(0, 184, 148, 0.06) 0%,
            rgba(15, 15, 30, 0.8) 100%);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        border: 1px solid rgba(0, 184, 148, 0.15);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        animation: slideInScale 0.5s ease-out both;
        text-align: center;
    }
    .status-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 184, 148, 0.1);
    }
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00b894;
        margin-right: 6px;
        animation: dotPulse 2s ease-in-out infinite;
        box-shadow: 0 0 8px rgba(0, 184, 148, 0.5);
    }
    .status-label {
        font-size: 0.68rem;
        color: rgba(255, 255, 255, 0.4);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .status-value {
        font-size: 1rem;
        font-weight: 700;
        color: #00b894;
    }

    /* ── Stats Table ────────────────────────────────────────────────── */
    .stats-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
    }
    .stats-table tr {
        transition: all 0.25s ease;
    }
    .stats-table tr:hover {
        background: rgba(99, 110, 230, 0.06);
    }
    .stats-table td {
        padding: 0.7rem 0.9rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }
    .stats-table td:first-child {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.85rem;
    }
    .stats-table td:last-child {
        color: #ffffff;
        font-weight: 600;
        text-align: right;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── Model Comparison Table ──────────────────────────────────────── */
    .model-table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 14px;
        overflow: hidden;
    }
    .model-table th {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        color: rgba(255, 255, 255, 0.7);
        padding: 1rem;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    .model-table td {
        padding: 0.8rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        color: #ffffff;
        transition: all 0.25s ease;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88rem;
    }
    .model-table tr:hover td {
        background: rgba(99, 110, 230, 0.06);
    }
    .model-table tr.best-model {
        background: rgba(0, 184, 148, 0.08);
        border-left: 3px solid #00b894;
    }

    /* ── Info Boxes ──────────────────────────────────────────────────── */
    .info-box {
        background: linear-gradient(135deg, rgba(99, 110, 230, 0.06) 0%, rgba(99, 110, 230, 0.02) 100%);
        border-left: 3px solid #636ee6;
        border-radius: 0 14px 14px 0;
        padding: 1.2rem 1.6rem;
        margin: 1rem 0;
        color: rgba(255, 255, 255, 0.75);
        font-size: 0.9rem;
        backdrop-filter: blur(6px);
        transition: all 0.3s ease;
        animation: fadeInLeft 0.5s ease-out both;
    }
    .info-box:hover {
        background: linear-gradient(135deg, rgba(99, 110, 230, 0.1) 0%, rgba(99, 110, 230, 0.04) 100%);
        border-left-color: #a29bfe;
    }
    .warning-box {
        background: linear-gradient(135deg, rgba(243, 156, 18, 0.06) 0%, rgba(243, 156, 18, 0.02) 100%);
        border-left: 3px solid #f39c12;
        border-radius: 0 14px 14px 0;
        padding: 1.2rem 1.6rem;
        margin: 1rem 0;
        color: rgba(255, 255, 255, 0.75);
        font-size: 0.9rem;
        backdrop-filter: blur(6px);
    }

    /* ── Sidebar Styling ────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,
            #080818 0%,
            #0e0e28 30%,
            #0a0a20 60%,
            #080818 100%);
        border-right: 1px solid rgba(99, 110, 230, 0.08);
    }
    [data-testid="stSidebar"] .stRadio label {
        font-weight: 500;
        letter-spacing: 0.5px;
        transition: all 0.25s ease;
        padding: 0.15rem 0;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        color: #a29bfe !important;
        padding-left: 4px;
    }

    /* ── Sidebar Brand ──────────────────────────────────────────────── */
    .sidebar-brand {
        text-align: center;
        padding: 1.5rem 0;
        position: relative;
    }
    .sidebar-brand .brand-logo-svg {
        width: 46px;
        height: 46px;
        margin: 0 auto 0.6rem auto;
        display: block;
        filter: drop-shadow(0 0 16px rgba(99, 110, 230, 0.45));
        animation: pulseGlow 4s ease-in-out infinite;
    }
    .sidebar-brand h2 {
        color: #ffffff;
        margin: 0;
        letter-spacing: 4px;
        font-size: 1.3rem;
        font-weight: 800;
    }
    .sidebar-brand p {
        color: rgba(255, 255, 255, 0.35);
        font-size: 0.68rem;
        margin-top: 0.3rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* ── Model Status Widget ────────────────────────────────────────── */
    .model-status {
        text-align: center;
        padding: 1rem;
        margin: 0.5rem;
        background: linear-gradient(145deg, rgba(15, 15, 30, 0.6), rgba(20, 20, 45, 0.4));
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }
    .model-status .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-weight: 600;
        font-size: 0.88rem;
    }
    .model-status .status-detail {
        color: rgba(255, 255, 255, 0.35);
        font-size: 0.7rem;
        margin-top: 0.3rem;
        letter-spacing: 0.5px;
    }

    /* ── Button Overrides ───────────────────────────────────────────── */
    .stButton > button {
        border-radius: 14px;
        font-weight: 700;
        letter-spacing: 0.8px;
        transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
        overflow: hidden;
    }
    .stButton > button::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        transition: width 0.5s, height 0.5s, top 0.5s, left 0.5s;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(99, 110, 230, 0.35);
    }
    .stButton > button:hover::after {
        width: 200px;
        height: 200px;
        top: calc(50% - 100px);
        left: calc(50% - 100px);
    }
    .stButton > button:active {
        transform: translateY(-1px);
    }

    /* ── Progress Bar Override ──────────────────────────────────────── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #636ee6, #a29bfe, #636ee6);
        background-size: 200% 100%;
        animation: shimmer 2s linear infinite;
        border-radius: 10px;
    }

    /* ── Expander Styling ──────────────────────────────────────────── */
    .streamlit-expanderHeader {
        font-weight: 600;
        letter-spacing: 0.3px;
    }

    /* ── Tab Styling ───────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.25s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #a29bfe !important;
    }

    /* ── Section Dividers ─────────────────────────────────────────── */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99, 110, 230, 0.2), transparent);
        margin: 1.5rem 0;
    }

    /* ── Smooth Scrollbar ──────────────────────────────────────────── */
    ::-webkit-scrollbar {
        width: 5px;
        height: 5px;
    }
    ::-webkit-scrollbar-track {
        background: #080818;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, rgba(99, 110, 230, 0.3), rgba(162, 155, 254, 0.3));
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, rgba(99, 110, 230, 0.5), rgba(162, 155, 254, 0.5));
    }

    /* ── Hide Streamlit Branding ────────────────────────────────────── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── File Uploader ──────────────────────────────────────────────── */
    [data-testid="stFileUploader"] {
        border-radius: 16px;
    }
    [data-testid="stFileUploader"] section {
        border-radius: 16px;
        border-color: rgba(99, 110, 230, 0.15);
        transition: border-color 0.3s ease;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: rgba(99, 110, 230, 0.3);
    }

    /* ── Dataframe Overrides ──────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }

    /* ── Animation Delays for Staggered Reveal ─────────────────────── */
    .stagger-1 { animation-delay: 0.05s; }
    .stagger-2 { animation-delay: 0.1s; }
    .stagger-3 { animation-delay: 0.15s; }
    .stagger-4 { animation-delay: 0.2s; }

    </style>
    """


# ── Density Color Utilities ──────────────────────────────────────────────────

DENSITY_COLORS = {
    "LOW": "#00b894",
    "MEDIUM": "#f39c12",
    "HIGH": "#e74c3c",
}

DENSITY_BG_COLORS = {
    "LOW": "rgba(0, 184, 148, 0.12)",
    "MEDIUM": "rgba(243, 156, 18, 0.12)",
    "HIGH": "rgba(231, 76, 60, 0.12)",
}


def density_badge_html(density: str) -> str:
    """Return HTML for a density badge."""
    css_class = f"density-{density.lower()}"
    return f'<span class="density-badge {css_class}">{density}</span>'


def metric_card_html(label: str, value: str, color: str = "#ffffff") -> str:
    """Return HTML for a metric card."""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color}">{value}</div>
    </div>
    """


def status_card_html(label: str, value: str, is_online: bool = True) -> str:
    """Return HTML for a system status card."""
    dot_color = "#00b894" if is_online else "#f39c12"
    value_color = "#00b894" if is_online else "#f39c12"
    return f"""
    <div class="status-card">
        <div class="status-label">{label}</div>
        <div class="status-value" style="color: {value_color}">
            <span class="status-dot" style="background: {dot_color}; box-shadow: 0 0 8px {dot_color};"></span>
            {value}
        </div>
    </div>
    """


def feature_card_html(icon: str, title: str, description: str, accent_color: str = "#636ee6") -> str:
    """Return HTML for a feature card (Quick Start, etc)."""
    return f"""
    <div class="feature-card" style="--card-accent: {accent_color};">
        <div class="card-icon">{icon}</div>
        <div class="card-title">{title}</div>
        <div class="card-desc">{description}</div>
    </div>
    """


def arch_card_html(icon: str, title: str, items: list, accent_color: str = "#636ee6") -> str:
    """Return HTML for an architecture card."""
    items_html = "\n".join(f'<div class="arch-item">{item}</div>' for item in items)
    return f"""
    <div class="arch-card" style="--accent: {accent_color};">
        <div class="arch-title">{icon}<span>{title}</span></div>
        <div class="arch-list">{items_html}</div>
    </div>
    """


def header_html() -> str:
    """Return the main application header HTML."""
    return """
    <div class="main-header">
        <h1>VISIONLYTICS</h1>
        <p>Intelligent Visual Crowd Analytics</p>
    </div>
    """
