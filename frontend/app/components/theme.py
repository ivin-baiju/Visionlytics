"""
Mono-Clay design tokens for Visionlytics.

Strict grayscale surfaces plus ONE restrained indigo accent reserved for
primary actions, links, toggles-on and focus rings. Density semantics
(LOW/MEDIUM/HIGH) are encoded with ink shades and shapes, never hue.
"""

# ── Clay Surfaces & Canvas ───────────────────────────────────────────────
SURFACE = "#FFFFFF"                     # Clay-white cards & panels
SURFACE_SOLID = "#FFFFFF"
CANVAS = "#E9EBF0"                      # Neutral clay canvas
INK = "#14161A"                         # Jet ink: primary text + chrome
INK_SOFT = "#2A2E35"                    # Raised clay text
MUTED = "#6B7280"                       # Muted gray secondary text
FAINT = "#9CA3AF"                       # Faint gray tertiary text
HAIRLINE = "#E9EAEC"                    # Legacy border grey (kept for compat)
HOVER_BG = "#F1F5F9"                    # Soft grey hover state

# ── The One Accent: Indigo ───────────────────────────────────────────────
# Indigo is reserved for interactivity only (never for status/density).
INDIGO = "#4F46E5"                      # Primary actions, links, focus rings
INDIGO_DARK = "#4338CA"                # Pressed / hover indigo
INDIGO_TINT = "#EEF0FE"                # Tinted indigo wash
ACCENT_PRIMARY = "#14161A"              # Deep ink primary (legacy alias)
ACCENT_BLUE = "#4F46E5"                 # Re-pointed at indigo (legacy alias)
LIME = "#14161A"                        # Legacy alias, kept for imports
LIME_DARK = "#2A2E35"                   # Legacy alias, kept for imports
LIME_TINT = "#F1F5F9"                   # Legacy alias, kept for imports

# ── Density Semantics (ink ramp + shape, never hue) ──────────────────────
DENSITY = {
    "LOW": "#9CA3AF",       # Light ink
    "MEDIUM": "#4B5563",    # Mid ink
    "HIGH": "#14161A",      # Full ink
}

DENSITY_BG = {
    "LOW": "#F3F4F6",
    "MEDIUM": "#E5E7EB",
    "HIGH": "#D1D5DB",
}

DENSITY_SHAPE = {
    "LOW": "circle",
    "MEDIUM": "triangle-up",
    "HIGH": "square",
}

# ── Clay Shape & Shadow ──────────────────────────────────────────────────
RADIUS_CARD = "18px"
RADIUS_XL = "22px"
RADIUS_LG = "18px"
RADIUS_PILL = "999px"
CARD_SHADOW = (
    "8px 8px 16px rgba(15, 23, 42, 0.10), "
    "-8px -8px 16px rgba(255, 255, 255, 0.9)"
)
CARD_SHADOW_SM = (
    "5px 5px 10px rgba(15, 23, 42, 0.08), "
    "-5px -5px 10px rgba(255, 255, 255, 0.9)"
)
SHADOW_LIGHT = "-8px -8px 16px rgba(255, 255, 255, 0.9)"
SHADOW_DARK = "8px 8px 16px rgba(15, 23, 42, 0.10)"
SHADOW_INSET = (
    "inset 4px 4px 8px rgba(15, 23, 42, 0.10), "
    "inset -4px -4px 8px rgba(255, 255, 255, 0.9)"
)
FONT_STACK = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"

# ── Motion (single-sourced easing) ───────────────────────────────────────
MOTION_EASE = "cubic-bezier(0.34, 1.56, 0.64, 1)"
MOTION_DURATION = "220ms"

# ── Plotly Palette (monochrome + indigo) ─────────────────────────────────
CHART_PALETTE = ["#14161A", "#4B5563", "#9CA3AF", "#4F46E5", "#2A2E35"]
CHART_GRID = "#E5E7EB"
CHART_FONT = "#6B7280"
CHART_INK = "#14161A"


def page_header_html(title: str, subtitle: str = "") -> str:
    """Clay page header with soft indicator tick."""
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
