"""
Flat design tokens for the Visionlytics dashboard.

Ronas IT delivery-tracking design language: flat white surfaces, hairline
borders, solid ink text, and lime accents. No gradients, no glass blur,
no animations.

Single source of truth — import these in styles.py / charts.py instead of
hard-coding hex values.
"""

# ── Surfaces ─────────────────────────────────────────────────────────────
SURFACE = "#FFFFFF"      # cards, panels, sidebar rail
CANVAS = "#F5F6F7"       # app background
INK = "#14161A"          # headings, primary text, text on lime
MUTED = "#5B6472"        # secondary text, captions
HAIRLINE = "#E9EAEC"     # 1px borders
HOVER_BG = "#FAFBFC"     # row hover

# ── Accent ───────────────────────────────────────────────────────────────
LIME = "#B4E04C"         # primary accent (badges, highlights)
LIME_DARK = "#8FBF2E"    # buttons, hover / pressed
LIME_TINT = "#EFF6DA"    # active nav row, selected backgrounds

# ── Density semantics ────────────────────────────────────────────────────
DENSITY = {
    "LOW": "#0F9D58",
    "MEDIUM": "#B7791F",
    "HIGH": "#D93025",
}

DENSITY_BG = {
    "LOW": "#E7F5EE",
    "MEDIUM": "#FEF5E5",
    "HIGH": "#FDECEA",
}

# ── Shape & type ─────────────────────────────────────────────────────────
RADIUS_CARD = "8px"
RADIUS_PILL = "999px"
CARD_SHADOW = "0 1px 2px rgba(20, 22, 26, 0.04)"
FONT_STACK = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

# ── Plotly palette (flat) ────────────────────────────────────────────────
CHART_PALETTE = ["#8FBF2E", "#14161A", "#5B6472", "#B4E04C", "#9AA3AF"]
CHART_GRID = HAIRLINE
CHART_FONT = MUTED
CHART_INK = INK


def page_header_html(title: str, subtitle: str = "") -> str:
    """High-density page header: lime tick + ink title + muted subtitle."""
    sub = f'<p class="page-subtitle">{subtitle}</p>' if subtitle else ""
    return f"""
    <div class="page-header">
        <span class="page-tick"></span>
        <div>
            <h2 class="page-title">{title}</h2>
            {sub}
        </div>
    </div>
    """
