"""
Brand and vector assets for Visionlytics.

Provides the animated brand logo and component icons.
"""

# HTML embedding the animated SVG logo with fallbacks
BRAND_LOGO_HTML = '<img class="brand-logo-img" src="app/static/logo.svg" alt="Visionlytics" width="48" height="48" />'

# Inline SVG string kept for backward compatibility with existing imports
BRAND_LOGO_SVG = BRAND_LOGO_HTML

# ── Feature Icons ─────────────────────────────────────────────────────────
ICON_IMAGE_ANALYSIS = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect x="3" y="3" width="18" height="18" rx="3"/>
  <circle cx="9" cy="9" r="1.8"/>
  <path d="M21 15l-5-5L5 21"/>
</svg>"""

ICON_VIDEO_ANALYSIS = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect x="2" y="4" width="20" height="16" rx="3"/>
  <path d="M10 9l5 3-5 3z"/>
</svg>"""

ICON_LIVE_CAMERA = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M23 7l-7 5 7 5V7z"/>
  <rect x="1" y="5" width="15" height="14" rx="3"/>
  <circle cx="8.5" cy="12" r="2.4"/>
</svg>"""

# ── Architecture Card Icons ──────────────────────────────────────────────
ICON_COMPUTER_VISION = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/>
  <circle cx="12" cy="12" r="3"/>
</svg>"""

ICON_FEATURE_ENGINEERING = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <polygon points="12 2 2 7 12 12 22 7 12 2"/>
  <polyline points="2 17 12 22 22 17"/>
  <polyline points="2 12 12 17 22 12"/>
</svg>"""

ICON_MACHINE_LEARNING = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <circle cx="5" cy="6" r="2"/>
  <circle cx="5" cy="18" r="2"/>
  <circle cx="12" cy="12" r="2"/>
  <circle cx="19" cy="6" r="2"/>
  <circle cx="19" cy="18" r="2"/>
  <line x1="7" y1="6.5" x2="10" y2="11"/>
  <line x1="7" y1="17.5" x2="10" y2="13"/>
  <line x1="14" y1="11" x2="17" y2="7"/>
  <line x1="14" y1="13" x2="17" y2="17"/>
</svg>"""

# ── General Purpose Icons ────────────────────────────────────────────────
ICON_TARGET = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <circle cx="12" cy="12" r="9"/>
  <circle cx="12" cy="12" r="5"/>
  <circle cx="12" cy="12" r="1.2" fill="currentColor"/>
</svg>"""

ICON_OBJECTIVES = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
  <line x1="4" y1="22" x2="4" y2="15"/>
</svg>"""
