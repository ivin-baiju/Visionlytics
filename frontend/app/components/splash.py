"""
Splash screen components for Visionlytics.

Provides:
  - A fullscreen WiFi-ish SVG preloader that plays on first visit
  - A looping background video behind the main content
"""

import os


def _read_preloader_svg() -> str:
    """Read the preloader SVG file from the static directory."""
    svg_path = os.path.join(
        os.path.dirname(__file__), "..", "static", "preloader.svg"
    )
    try:
        with open(svg_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def get_preloader_html() -> str:
    """Preloader has been removed per user request."""
    return ""


    return f"""
    <style>
    /* ── Preloader Overlay ─────────────────────────────────────────── */
    #vl-preloader {{
        position: fixed;
        inset: 0;
        z-index: 999999;
        background: #0B0F19;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        pointer-events: auto;
    }}
    #vl-preloader.vl-fade-out {{
        opacity: 0;
        pointer-events: none;
    }}
    #vl-preloader .preloader-svg-wrap {{
        width: min(520px, 85vw);
        height: min(400px, 55vh);
        overflow: visible;
        filter: drop-shadow(0 0 50px rgba(57, 203, 206, 0.4));
    }}
    #vl-preloader .preloader-svg-wrap svg {{
        width: 100%;
        height: 100%;
        overflow: visible;
    }}
    #vl-preloader .preloader-brand {{
        margin-top: 1rem;
        text-align: center;
    }}
    #vl-preloader .preloader-brand h2 {{
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        margin: 0;
        text-shadow: 0 0 40px rgba(57, 203, 206, 0.6),
                     0 0 80px rgba(57, 203, 206, 0.3);
    }}
    #vl-preloader .preloader-brand p {{
        color: rgba(57, 203, 206, 0.85) !important;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        letter-spacing: 0.1em;
        margin-top: 0.5rem;
    }}
    </style>

    <div id="vl-preloader">
        <div class="preloader-svg-wrap">
            {svg_content}
        </div>
        <div class="preloader-brand">
            <h2>VISIONLYTICS</h2>
            <p>Intelligent Visual Crowd Analytics</p>
        </div>
    </div>

    <script>
    (function() {{
        // Only show preloader once per session
        if (sessionStorage.getItem('vl_loaded')) {{
            var el = document.getElementById('vl-preloader');
            if (el) el.remove();
            return;
        }}
        sessionStorage.setItem('vl_loaded', '1');

        // Fade out after ~3s (the SVG's key action completes by then)
        setTimeout(function() {{
            var el = document.getElementById('vl-preloader');
            if (el) {{
                el.classList.add('vl-fade-out');
                setTimeout(function() {{ el.remove(); }}, 700);
            }}
        }}, 2800);
    }})();
    </script>
    """


def get_video_background_html() -> str:
    """Return HTML/CSS for the looping background video.

    The video sits behind all Streamlit content with a translucent
    overlay so text remains readable over the footage.
    """
    return """
    <style>
    /* ── Video Background ──────────────────────────────────────────── */
    #vl-video-bg {
        position: fixed;
        inset: 0;
        z-index: -2;
        overflow: hidden;
    }
    #vl-video-bg video {
        position: absolute;
        top: 50%;
        left: 50%;
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        transform: translate(-50%, -50%);
        object-fit: cover;
    }
    /* Semi-transparent overlay for text readability */
    #vl-video-overlay {
        position: fixed;
        inset: 0;
        z-index: -1;
        background: rgba(233, 235, 240, 0.82);
        backdrop-filter: blur(2px);
        -webkit-backdrop-filter: blur(2px);
    }
    </style>

    <div id="vl-video-bg">
        <video autoplay muted loop playsinline>
            <source src="app/static/bg_video.mp4" type="video/mp4">
        </video>
    </div>
    <div id="vl-video-overlay"></div>
    """
