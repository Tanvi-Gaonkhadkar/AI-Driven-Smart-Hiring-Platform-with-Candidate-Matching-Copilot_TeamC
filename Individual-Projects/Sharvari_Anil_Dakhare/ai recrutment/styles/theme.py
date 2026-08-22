"""
Central design system for YourTalentPilot.

Every color, spacing value, and font used across the app comes from here.
Never hardcode a hex color or px value directly in a page - add it here
and reference it, so the whole product stays visually consistent.

Light/Dark mode:
    The toggle lives in components/sidebar.py (render_theme_toggle). It sets
    st.session_state["dark_mode"]. COLORS is a single mutable dict that every
    other module imports - inject_global_styles() refreshes its contents in
    place each run, so kpi_card.py / charts.py / tables.py automatically pick
    up the right palette without needing to re-import anything.
"""

import streamlit as st

# ---- Light Mode (Ice Cyan Studio) & Dark Mode (Glowing Violet Space Canvas) ----
LIGHT_PALETTE = {
    "background": "#CBE6FF",        # Luminous Soft Ice-Blue Gradient Base
    "surface": "rgba(255, 255, 255, 0.75)",  # High Visibility Frosted Glass Card
    "surface_muted": "rgba(255, 255, 255, 0.55)", # Translucent Inset Subsection
    "primary": "#2563EB",           # Deep Blue Primary
    "primary_hover": "#1D4ED8",     # Royal Blue Hover
    "secondary": "#3B82F6",         # Soft Ice Blue Accent
    "text_primary": "#0F172A",      # Deep Slate Text
    "text_secondary": "#334155",    # High-Contrast Secondary Slate
    "border": "rgba(255, 255, 255, 0.85)", # Glowing White Glass Border
    "success": "#10B981",           # Mint Green
    "danger": "#EF4444",            # Soft Crimson
    "warning": "#F59E0B",           # Glowing Amber
    "info": "#38BDF8",              # Sky Cyan
}

DARK_PALETTE = {
    "background": "#0A0518",        # Midnight Purple Space Canvas
    "surface": "rgba(20, 14, 38, 0.85)",     # Deep Translucent Glass Card
    "surface_muted": "rgba(32, 22, 58, 0.75)",   # Muted Space Panel
    "primary": "#8B5CF6",           # Electric Violet Primary
    "primary_hover": "#A78BFA",     # Bright Neon Violet Glow
    "secondary": "#C084FC",         # Soft Blue-Violet Glow Accent
    "text_primary": "#F8FAFC",      # High-Contrast Pure White
    "text_secondary": "#CBD5E1",    # Crisp Cool Silver Text
    "border": "rgba(139, 92, 246, 0.35)", # Glowing Violet Glass Border
    "success": "#34D399",           # Soft Mint Green
    "danger": "#F87171",            # Coral Red
    "warning": "#FBBF24",           # Warm Gold Amber
    "info": "#38BDF8",              # Electric Cyan
}

# Mutable dict shared by every component module.
COLORS = dict(LIGHT_PALETTE)

# Dynamic Typography Setup
FONT_FAMILY = "'Space Grotesk', 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

RADIUS = "20px"          # Soft Rounded Glass Geometry
RADIUS_SM = "9999px"     # Pill-Shaped Action Buttons
SHADOW = "0 8px 32px 0 rgba(0, 0, 0, 0.25)"
SHADOW_HOVER = "0 12px 40px 0 rgba(139, 92, 246, 0.35)"

# ---- Spacing scale (4px grid) ----
SPACE_XS = "4px"
SPACE_SM = "8px"
SPACE_MD = "18px"
SPACE_LG = "28px"
SPACE_XL = "40px"

# ---- Typography scale ----
FONT_SIZE_H1 = "34px"   # Page title (page_header)
FONT_SIZE_H2 = "22px"   # Section headings
FONT_SIZE_H3 = "15px"   # Card titles / mini headers
FONT_SIZE_BODY = "14px"
FONT_SIZE_SMALL = "12.5px"


def is_dark_mode() -> bool:
    return st.session_state.get("dark_mode", False)


def _sync_colors():
    """Refresh the shared COLORS dict to match the current mode."""
    COLORS.clear()
    COLORS.update(DARK_PALETTE if is_dark_mode() else LIGHT_PALETTE)


def inject_global_styles():
    """Call once per page, right after st.set_page_config()."""
    _sync_colors()

    # streamlit==1.38.0 (pinned in requirements.txt) has no `key=` support
    # on st.container(), so the floating chat elements are located instead
    # via an invisible marker span placed immediately before each plain
    # st.container() call (see components/global_chat.py) - CSS then finds
    # "the stElementContainer right after the marker's stElementContainer"
    # and pins that to the viewport.
    _gc_fab_sel = 'div[data-testid="stElementContainer"]:has(.gc-fab-marker) + div[data-testid="stElementContainer"]'
    _gc_panel_sel = 'div[data-testid="stElementContainer"]:has(.gc-panel-marker) + div[data-testid="stElementContainer"]'
    _gc_msg_sel = 'div[data-testid="stElementContainer"]:has(.gc-messages-marker) + div[data-testid="stElementContainer"]'

    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

            /* ---- Hide default Streamlit chrome ---- */
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}
            div[data-testid="stDecoration"] {{display: none;}}
            div[data-testid="stToolbar"] {{display: none;}}

            /* ---- Base Typography & Layout Settings ---- */
            html, body, [class*="css"] {{
                font-family: {FONT_FAMILY};
                color: {COLORS["text_primary"]};
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                letter-spacing: -0.011em;
                line-height: 1.55;
            }}

            .stApp {{
                background: {"radial-gradient(circle at 50% 100%, #1E1035 0%, #0A0518 70%)" if is_dark_mode() else "linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 50%, #93C5FD 100%)"};
                background-attachment: fixed;
                font-size: {FONT_SIZE_BODY};
                color: {COLORS["text_primary"]} !important;
            }}

            .main .block-container {{
                max-width: 1400px !important;
                padding-top: 2rem !important;
                padding-bottom: 4rem !important;
                padding-left: 3rem !important;
                padding-right: 3rem !important;
            }}

            /* Custom Web Scrollbar */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            ::-webkit-scrollbar-track {{
                background: {COLORS["background"]};
            }}
            ::-webkit-scrollbar-thumb {{
                background: {COLORS["surface_muted"]};
                border-radius: 4px;
                border: 1px solid {COLORS["border"]};
            }}
            ::-webkit-scrollbar-thumb:hover {{
                background: {COLORS["primary"]};
            }}

            /* ---- Typography Hierarchy ---- */
            div[data-testid="stMarkdownContainer"] h1 {{ 
                font-family: 'Space Grotesk', sans-serif;
                font-size: {FONT_SIZE_H1}; 
                font-weight: 800; 
                letter-spacing: -0.02em; 
                line-height: 1.25;
                color: {COLORS["text_primary"]} !important;
                margin-bottom: {SPACE_MD};
            }}
            div[data-testid="stMarkdownContainer"] h2 {{ 
                font-family: 'Space Grotesk', sans-serif;
                font-size: {FONT_SIZE_H2}; 
                font-weight: 700; 
                letter-spacing: -0.015em; 
                line-height: 1.35;
                color: {COLORS["text_primary"]} !important;
                margin-top: {SPACE_LG};
                margin-bottom: {SPACE_SM};
            }}
            div[data-testid="stMarkdownContainer"] h3,
            div[data-testid="stMarkdownContainer"] h4 {{
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-size: {FONT_SIZE_H3};
                font-weight: 700;
                letter-spacing: -0.012em;
                line-height: 1.4;
                margin-bottom: {SPACE_SM};
                color: {COLORS["text_primary"]} !important;
            }}
            div[data-testid="stMarkdownContainer"] p {{
                font-size: {FONT_SIZE_BODY};
                line-height: 1.6;
                letter-spacing: -0.008em;
                color: {COLORS["text_primary"]} !important;
            }}
            div[data-testid="stMarkdownContainer"] p:has(> strong:only-child) {{
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-size: {FONT_SIZE_H3};
                font-weight: 700;
                letter-spacing: 0.01em;
                margin-bottom: {SPACE_SM};
                display: block;
                color: {COLORS["text_primary"]} !important;
            }}

            /* ---- Sidebar Typography & Navigation ---- */
            section[data-testid="stSidebar"] {{
                background: {COLORS["surface"]};
                backdrop-filter: blur(24px) saturate(180%);
                -webkit-backdrop-filter: blur(24px) saturate(180%);
                border-right: 1px solid {COLORS["border"]};
                box-shadow: 10px 0 30px rgba(0, 0, 0, 0.3);
            }}

            [data-testid="stSidebarNav"] {{ display: none; }}

            .sidebar-brand {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 6px 6px 6px;
            }}
            .plan-badge {{
                display: inline-block;
                background: {"rgba(59, 130, 246, 0.15)" if not is_dark_mode() else "rgba(139, 92, 246, 0.2)"};
                color: {COLORS["text_primary"]} !important;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                padding: 3px 10px;
                border-radius: 9999px;
                border: 1px solid {COLORS["border"]};
                margin: 4px 0 16px 4px;
            }}
            .nav-section-label {{
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: {COLORS["text_secondary"]} !important;
                margin: 20px 0 6px 6px;
            }}
            .nav-badge {{
                display: inline-block;
                background-color: {COLORS["primary"]};
                color: white !important;
                font-size: 11px;
                font-weight: 700;
                padding: 2px 8px;
                border-radius: 9999px;
                margin-top: 6px;
            }}
            .profile-card {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 14px 8px;
                margin-top: 20px;
                border-top: 1px solid {COLORS["border"]};
            }}
            .profile-avatar {{
                width: 36px;
                height: 36px;
                border-radius: 50%;
                background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 14px;
                flex-shrink: 0;
                position: relative;
                box-shadow: 0 0 14px rgba(139, 92, 246, 0.4);
            }}
            .profile-status-dot {{
                width: 9px;
                height: 9px;
                border-radius: 50%;
                background-color: {COLORS["success"]};
                border: 2px solid {COLORS["surface"]};
                position: absolute;
                bottom: -1px;
                right: -1px;
            }}
            .profile-name {{
                font-size: 13px;
                font-weight: 700;
                letter-spacing: -0.01em;
                color: {COLORS["text_primary"]} !important;
                line-height: 1.2;
            }}
            .profile-role {{
                font-size: 12px;
                font-weight: 500;
                color: {COLORS["text_secondary"]} !important;
            }}

            .brand-logo {{ font-size: 22px; color: {COLORS["primary"]}; }}
            .brand-name {{
                font-family: 'Space Grotesk', sans-serif;
                font-size: 18px;
                font-weight: 800;
                letter-spacing: -0.025em;
                color: {COLORS["text_primary"]} !important;
            }}
            .sidebar-divider {{
                border: none;
                border-top: 1px solid {COLORS["border"]};
                margin: 4px 0 12px 0;
            }}

            /* ---- Native Dialog (Employee Profile Modal) Fix ---- */
            div[data-testid="stModal"] > div,
            div[data-testid="stDialog"] > div,
            div[role="dialog"] {{
                background-color: {COLORS["surface"]} !important;
                border: 1px solid {COLORS["border"]} !important;
                color: {COLORS["text_primary"]} !important;
                border-radius: {RADIUS} !important;
                box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4) !important;
            }}
            div[role="dialog"] p, 
            div[role="dialog"] span, 
            div[role="dialog"] div, 
            div[role="dialog"] label, 
            div[role="dialog"] h1, 
            div[role="dialog"] h2, 
            div[role="dialog"] h3,
            div[role="dialog"] h4 {{
                color: {COLORS["text_primary"]} !important;
            }}

            /* ---- Header Typography ---- */
            .page-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 32px;
            }}
            .page-title {{
                font-family: 'Space Grotesk', sans-serif;
                font-size: {FONT_SIZE_H1};
                font-weight: 800;
                letter-spacing: -0.03em;
                color: {COLORS["text_primary"]} !important;
                margin: 0;
                line-height: 1.2;
            }}
            .page-subtitle {{
                font-size: 14px;
                font-weight: 500;
                color: {COLORS["text_secondary"]} !important;
                margin-top: 6px;
                line-height: 1.5;
            }}

            /* ---- Frosted Glass Cards ---- */
            .card {{
                background: {COLORS["surface"]};
                backdrop-filter: blur(20px) saturate(180%);
                -webkit-backdrop-filter: blur(20px) saturate(180%);
                border: 1px solid {COLORS["border"]};
                border-radius: {RADIUS};
                box-shadow: {SHADOW};
                padding: {SPACE_LG} {SPACE_LG};
                margin-bottom: {SPACE_MD};
                transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            }}
            .card:hover {{ 
                box-shadow: {SHADOW_HOVER}; 
                border-color: {COLORS["primary"]};
                transform: translateY(-2px);
            }}

            /* ---- Inset Glass Panels ---- */
            .subsection {{
                background: {COLORS["surface_muted"]};
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid {COLORS["border"]};
                border-radius: {RADIUS_SM};
                padding: {SPACE_MD};
                margin-bottom: {SPACE_MD};
            }}
            .subsection-label {{
                font-size: {FONT_SIZE_SMALL};
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: {COLORS["text_secondary"]} !important;
                margin-bottom: {SPACE_SM};
            }}

            /* ---- Buttons Typography & Micro-Interactions ---- */
            .stButton > button,
            .stFormSubmitButton > button,
            [data-testid="stDownloadButton"] > button,
            [data-testid="stFileUploaderDropzone"] button {{
                font-family: {FONT_FAMILY};
                background: {"linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)" if not is_dark_mode() else "linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)"} !important;
                color: #FFFFFF !important;
                border: {"none" if not is_dark_mode() else "1px solid rgba(255, 255, 255, 0.4)"} !important;
                border-radius: 9999px !important;
                padding: 8px 22px !important;
                font-weight: 600 !important;
                font-size: {FONT_SIZE_BODY} !important;
                letter-spacing: 0.015em !important;
                min-height: 38px !important;
                height: auto !important;
                transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
                box-shadow: {"0 4px 18px rgba(37, 99, 235, 0.35)" if not is_dark_mode() else "0 0 0 6px rgba(139, 92, 246, 0.28), 0 4px 20px rgba(124, 58, 237, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.6)"} !important;
                cursor: pointer !important;
            }}

            .stButton > button p,
            .stButton > button div,
            .stButton > button span,
            .stFormSubmitButton > button p,
            .stFormSubmitButton > button div,
            .stFormSubmitButton > button span,
            [data-testid="stDownloadButton"] > button p,
            [data-testid="stDownloadButton"] > button div,
            [data-testid="stDownloadButton"] > button span {{
                color: #FFFFFF !important;
                font-weight: 600 !important;
                font-size: {FONT_SIZE_BODY} !important;
            }}

            .stButton > button:hover,
            .stFormSubmitButton > button:hover,
            [data-testid="stDownloadButton"] > button:hover,
            [data-testid="stFileUploaderDropzone"] button:hover {{
                background: {"linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)" if not is_dark_mode() else "linear-gradient(135deg, #9333EA 0%, #7C3AED 100%)"} !important;
                border-color: rgba(255, 255, 255, 0.6) !important;
                box-shadow: {"0 6px 24px rgba(37, 99, 235, 0.5)" if not is_dark_mode() else "0 0 0 8px rgba(147, 51, 234, 0.35), 0 6px 28px rgba(147, 51, 234, 0.7), inset 0 1px 2px rgba(255, 255, 255, 0.8)"} !important;
                transform: translateY(-1px) !important;
            }}

            .stButton > button:active,
            .stFormSubmitButton > button:active,
            [data-testid="stDownloadButton"] > button:active,
            [data-testid="stFileUploaderDropzone"] button:active {{
                transform: scale(0.98) !important;
            }}

            .stButton > button:focus-visible,
            .stFormSubmitButton > button:focus-visible,
            [data-testid="stDownloadButton"] > button:focus-visible,
            [data-testid="stFileUploaderDropzone"] button:focus-visible {{
                outline: 2px solid {COLORS["primary"]} !important;
                outline-offset: 2px !important;
            }}

            .stButton > button:disabled,
            .stFormSubmitButton > button:disabled,
            [data-testid="stDownloadButton"] > button:disabled,
            [data-testid="stFileUploaderDropzone"] button:disabled {{
                background: {COLORS["surface_muted"]} !important;
                color: {COLORS["text_secondary"]} !important;
                border-color: {COLORS["border"]} !important;
                opacity: 0.6 !important;
                box-shadow: none !important;
            }}

            /* Remove embedded icons/SVGs inside Streamlit buttons */
            .stButton > button svg,
            .stButton > button i,
            .stButton > button img,
            .stButton > button [data-testid="stIcon"],
            .stButton > button ::before,
            .stButton > button ::after,
            .stFormSubmitButton > button svg,
            .stFormSubmitButton > button i,
            .stFormSubmitButton > button img,
            .stFormSubmitButton > button [data-testid="stIcon"],
            [data-testid="stDownloadButton"] > button svg,
            [data-testid="stDownloadButton"] > button i,
            [data-testid="stDownloadButton"] > button img,
            [data-testid="stDownloadButton"] > button [data-testid="stIcon"] {{
                display: none !important;
                width: 0 !important;
                height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
            }}

            /* ---- Destructive Actions ---- */
            .danger-action .stButton > button {{
                background: transparent !important;
                color: {COLORS["danger"]} !important;
                border: 1px solid {COLORS["danger"]}55 !important;
                box-shadow: none !important;
            }}
            .danger-action .stButton > button:hover {{
                background-color: {COLORS["danger"]}15 !important;
                color: {COLORS["danger"]} !important;
                border-color: {COLORS["danger"]} !important;
            }}

            /* ---- Glass Tabs Typography ---- */
            [data-testid="stTabs"] [data-baseweb="tab-list"] {{
                gap: {SPACE_LG};
                border-bottom: 1px solid {COLORS["border"]};
            }}
            [data-testid="stTabs"] [data-baseweb="tab"] {{
                font-family: {FONT_FAMILY};
                color: {COLORS["text_secondary"]} !important;
                font-weight: 600;
                font-size: {FONT_SIZE_BODY};
                letter-spacing: -0.01em;
                padding-bottom: 12px;
            }}
            [data-testid="stTabs"] [aria-selected="true"] {{
                color: {COLORS["primary"]} !important;
                font-weight: 700;
            }}
            [data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
                background-color: {COLORS["primary"]} !important;
            }}

            /* ---- Form Inputs & Label Typography ---- */
            [data-testid="stWidgetLabel"] p {{
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE_BODY} !important;
                font-weight: 600 !important;
                letter-spacing: -0.01em;
                color: {COLORS["text_primary"]} !important;
            }}
            [data-baseweb="checkbox"] div[aria-checked="false"] {{
                background-color: {COLORS["surface_muted"]} !important;
                border-color: {COLORS["border"]} !important;
            }}

            [data-testid="stTextInput"] input::placeholder,
            [data-testid="stTextArea"] textarea::placeholder {{
                color: {COLORS["text_secondary"]} !important;
                opacity: 0.75;
                font-weight: 400;
            }}

            /* Force High Contrast Legibility Everywhere */
            .card, .subsection, .hero-banner, .kpi-card, .module-card, .ai-chat-box,
            div[data-testid="stMarkdownContainer"],
            div[data-testid="stMarkdownContainer"] p,
            div[data-testid="stMarkdownContainer"] li,
            div[data-testid="stMarkdownContainer"] span:not([style]),
            div[data-testid="stMarkdownContainer"] strong,
            div[data-testid="stCaptionContainer"],
            label, .stTextInput label, .stSelectbox label, .stTextArea label {{
                color: {COLORS["text_primary"]} !important;
                line-height: 1.6;
            }}

            /* Native Input Elements */
            [data-testid="stTextInput"] input,
            [data-testid="stTextArea"] textarea,
            div[data-baseweb="select"] > div,
            div[data-baseweb="popover"],
            [data-testid="stFileUploaderDropzone"],
            [data-testid="stExpander"] {{
                font-family: {FONT_FAMILY};
                background: {COLORS["surface"]} !important;
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
                color: {COLORS["text_primary"]} !important;
                border: 1px solid {COLORS["border"]} !important;
                border-radius: 12px !important;
                transition: border-color 0.2s ease, box-shadow 0.2s ease;
            }}
            [data-testid="stTextInput"] input:focus,
            [data-testid="stTextArea"] textarea:focus {{
                border-color: {COLORS["primary"]} !important;
                box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.3) !important;
            }}
            [data-testid="stExpander"] {{
                border-radius: {RADIUS} !important;
                box-shadow: {SHADOW};
            }}
            [data-testid="stExpander"] summary {{
                font-weight: 600;
                font-size: {FONT_SIZE_BODY};
                letter-spacing: -0.01em;
            }}
            [data-testid="stExpander"] summary:hover {{
                color: {COLORS["primary"]} !important;
            }}

            /* Fix nested text visibility inside dropzone for dark mode */
            [data-testid="stFileUploaderDropzone"] small {{
                color: {COLORS["text_secondary"]} !important;
            }}

            /* ---- Table Typography ---- */
            div[data-testid="stDataFrame"] {{
                background: {COLORS["surface"]};
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid {COLORS["border"]};
                border-radius: {RADIUS};
                overflow: hidden;
            }}
            div[data-testid="stDataFrame"] [role="columnheader"] {{
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE_SMALL} !important;
                font-weight: 700 !important;
                letter-spacing: 0.05em !important;
                text-transform: uppercase !important;
                color: {COLORS["text_secondary"]} !important;
            }}

            /* ---- Progress Bars ---- */
            div[data-testid="stProgress"] > div > div > div > div,
            progress::-webkit-progress-value {{
                background: linear-gradient(90deg, #38BDF8 0%, #818CF8 100%) !important;
                border-radius: 9999px !important;
                box-shadow: 0 0 10px rgba(56, 189, 248, 0.5) !important;
            }}
            div[data-testid="stProgress"] > div > div,
            progress::-webkit-progress-bar {{
                background-color: {COLORS["surface_muted"]} !important;
                border-radius: 9999px !important;
            }}

            /* ---- 📊 CHART THEME BLENDING & TRANSPARENCY OVERRIDES ---- */
            div[data-testid="stVegaLiteChart"],
            div[data-testid="stPlotlyChart"],
            div[data-testid="stPydeckChart"],
            div[data-testid="stBarchart"],
            div[data-testid="stLinechart"],
            div[data-testid="stAreaChart"] {{
                background: {COLORS["surface"]} !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid {COLORS["border"]} !important;
                border-radius: {RADIUS} !important;
                padding: 16px !important;
                box-shadow: {SHADOW} !important;
            }}

            /* Force Plotly, Altair, and Vega SVG canvas transparency */
            .js-plotly-plot .plotly,
            .js-plotly-plot .plotly .main-svg,
            .vega-embed,
            .vega-embed svg {{
                background: transparent !important;
                background-color: transparent !important;
            }}

            /* Chart Text, Labels, and Legend Colors */
            .js-plotly-plot .plotly .gtitle,
            .js-plotly-plot .plotly .g-xtitle,
            .js-plotly-plot .plotly .g-ytitle,
            .js-plotly-plot .plotly .xtick text,
            .js-plotly-plot .plotly .ytick text,
            .js-plotly-plot .plotly .legendtext,
            .vega-embed text {{
                fill: {COLORS["text_primary"]} !important;
                color: {COLORS["text_primary"]} !important;
                font-family: {FONT_FAMILY} !important;
            }}

            /* Grid Lines and Axis Borders */
            .js-plotly-plot .plotly .gridlayer path,
            .vega-embed .role-axis-grid line {{
                stroke: {COLORS["border"]} !important;
                stroke-opacity: 0.5 !important;
            }}

            /* Tooltips */
            .js-plotly-plot .plotly .hoverlayer .hovertext rect,
            .vega-bind, .vg-tooltip {{
                background-color: {COLORS["surface"]} !important;
                border: 1px solid {COLORS["border"]} !important;
                color: {COLORS["text_primary"]} !important;
                border-radius: 8px !important;
                box-shadow: {SHADOW} !important;
            }}

            /* ---- Hero ---- */
            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(12px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .hero-banner {{
                background: {"linear-gradient(135deg, rgba(255, 255, 255, 0.85) 0%, rgba(191, 219, 254, 0.75) 100%)" if not is_dark_mode() else "linear-gradient(135deg, rgba(30, 16, 60, 0.95) 0%, rgba(10, 5, 24, 0.95) 100%)"};
                backdrop-filter: blur(24px);
                -webkit-backdrop-filter: blur(24px);
                border-radius: 20px;
                padding: 40px 44px;
                color: {COLORS["text_primary"]} !important;
                margin-bottom: 28px;
                border: 1px solid {COLORS["border"]};
                box-shadow: {SHADOW};
                animation: fadeInUp 0.5s ease both;
            }}
            .hero-eyebrow {{
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                color: {COLORS["primary"]} !important;
                opacity: 0.9;
                margin-bottom: 10px;
            }}
            .hero-title {{ 
                font-family: 'Space Grotesk', sans-serif;
                font-size: 34px; 
                font-weight: 800; 
                margin: 0 0 8px 0; 
                color: {COLORS["text_primary"]} !important;
            }}
            .hero-subtitle {{ 
                font-size: 15px; 
                opacity: 0.92; 
                max-width: 640px; 
                color: {COLORS["text_primary"]} !important;
            }}
            .hero-stat-value {{ 
                font-family: 'Space Grotesk', sans-serif;
                font-size: 22px; 
                font-weight: 800; 
                color: {COLORS["text_primary"]} !important;
            }}
            .hero-stat-label {{ 
                font-size: 12px; 
                opacity: 0.85; 
                color: {COLORS["text_secondary"]} !important;
            }}

            .module-card {{
                background: {COLORS["surface"]};
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid {COLORS["border"]};
                border-radius: {RADIUS};
                box-shadow: {SHADOW};
                padding: 18px 20px;
                transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1);
                animation: fadeInUp 0.5s ease both;
                height: 100%;
            }}
            .module-card:hover {{
                transform: translateY(-3px);
                box-shadow: {SHADOW_HOVER};
                border-color: {COLORS["primary"]};
            }}
            .module-icon {{ font-size: 22px; margin-bottom: 8px; color: {COLORS["primary"]}; }}
            .module-title {{
                font-size: 15px;
                font-weight: 700;
                color: {COLORS["text_primary"]} !important;
                margin-bottom: 4px;
            }}
            .module-desc {{
                font-size: 13px;
                color: {COLORS["text_secondary"]} !important;
                margin-bottom: 10px;
                min-height: 34px;
            }}
            .top-bar {{ display: flex; justify-content: flex-end; gap: 10px; margin-bottom: 18px; }}

            /* ---- 🔮 GLOWING NEON AI ORB ASSISTANT - floating bubble motion ---- */
            @keyframes orbPulse {{
                0% {{ 
                    box-shadow: 0 0 20px #8B5CF6, 0 0 40px #EC4899, inset 0 0 15px rgba(255, 255, 255, 0.8); 
                    transform: translateY(0) scale(1); 
                }}
                50% {{ 
                    box-shadow: 0 0 32px #3B82F6, 0 0 60px #8B5CF6, inset 0 0 25px rgba(255, 255, 255, 0.9); 
                    transform: translateY(-9px) scale(1.06); 
                }}
                100% {{ 
                    box-shadow: 0 0 20px #8B5CF6, 0 0 40px #EC4899, inset 0 0 15px rgba(255, 255, 255, 0.8); 
                    transform: translateY(0) scale(1); 
                }}
            }}

            div[data-testid="stElementContainer"]:has(.gc-fab-marker),
            div[data-testid="stElementContainer"]:has(.gc-panel-marker),
            div[data-testid="stElementContainer"]:has(.gc-messages-marker) {{
                display: none !important;
            }}
            {_gc_fab_sel} {{
                position: fixed !important;
                bottom: 24px !important;
                right: 24px !important;
                z-index: 10000 !important;
                width: fit-content !important;
                touch-action: none !important;
            }}
            {_gc_fab_sel} .stButton > button {{
                width: 60px !important;
                height: 60px !important;
                min-height: 60px !important;
                border-radius: 50% !important;
                padding: 0 !important;
                background: radial-gradient(circle at 35% 35%, #FFFFFF 0%, #EC4899 30%, #8B5CF6 60%, #1E1B4B 100%) !important;
                border: 2px solid rgba(255, 255, 255, 0.8) !important;
                animation: orbPulse 3.6s infinite ease-in-out !important;
                cursor: grab !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }}
            {_gc_fab_sel}.gc-dragging .stButton > button {{
                animation-play-state: paused !important;
                cursor: grabbing !important;
                transform: scale(1.1) !important;
            }}
            {_gc_fab_sel} .stButton > button p {{
                font-size: 24px !important;
                line-height: 1 !important;
                color: #FFFFFF !important;
            }}
            {_gc_fab_sel} .stButton > button:hover {{
                transform: scale(1.12) !important;
                box-shadow: 0 0 45px #EC4899, 0 0 75px #8B5CF6, inset 0 0 30px rgba(255, 255, 255, 1) !important;
            }}
            {_gc_panel_sel} {{
                position: fixed !important;
                bottom: 96px !important;
                right: 24px !important;
                width: 380px !important;
                max-width: calc(100vw - 48px) !important;
                max-height: 70vh !important;
                display: flex !important;
                flex-direction: column !important;
                background: {"radial-gradient(circle at 100% 0%, rgba(236, 72, 153, 0.22) 0%, rgba(139, 92, 246, 0.18) 40%, rgba(10, 5, 24, 0.94) 100%)" if is_dark_mode() else "radial-gradient(circle at 100% 0%, rgba(59, 130, 246, 0.12) 0%, rgba(255, 255, 255, 0.9) 45%, rgba(255, 255, 255, 0.97) 100%)"};
                backdrop-filter: blur(24px) saturate(180%);
                -webkit-backdrop-filter: blur(24px) saturate(180%);
                border: 1.5px solid {"rgba(236, 72, 153, 0.4)" if is_dark_mode() else COLORS["border"]};
                border-radius: 22px;
                box-shadow: {"0 16px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(236, 72, 153, 0.25)" if is_dark_mode() else "0 16px 50px rgba(30, 58, 138, 0.18), 0 0 0 1px rgba(255, 255, 255, 0.6) inset"};
                padding: {SPACE_MD};
                z-index: 9999 !important;
                overflow: hidden !important;
            }}
            .global-chat-title {{
                font-family: 'Space Grotesk', sans-serif;
                font-size: {FONT_SIZE_H3};
                font-weight: 800;
                padding-top: 6px;
                background: {"linear-gradient(135deg, #FFFFFF 0%, #EC4899 50%, #8B5CF6 100%)" if is_dark_mode() else "linear-gradient(135deg, #1D4ED8 0%, #7C3AED 60%, #EC4899 100%)"};
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            {_gc_msg_sel} {{
                overflow-y: auto !important;
                max-height: 42vh;
                margin: 6px 0 10px 0;
                padding-right: 4px;
            }}
            {_gc_panel_sel} [data-testid="stChatMessage"] {{
                padding: 8px 10px;
                margin-bottom: 4px;
                border-radius: 14px;
                background: {COLORS["surface_muted"]} !important;
                border: 1px solid {COLORS["border"]};
            }}
            {_gc_panel_sel} [data-testid="stChatMessageContent"],
            {_gc_panel_sel} [data-testid="stChatMessage"] p,
            {_gc_panel_sel} [data-testid="stChatMessage"] span {{
                color: {COLORS["text_primary"]} !important;
            }}
            {_gc_panel_sel} .stCaptionContainer,
            {_gc_panel_sel} [data-testid="stCaptionContainer"] {{
                color: {COLORS["text_secondary"]} !important;
            }}
            @keyframes typingBounce {{
                0%, 60%, 100% {{ transform: translateY(0); opacity: 0.5; }}
                30% {{ transform: translateY(-4px); opacity: 1; }}
            }}
            .typing-indicator span {{
                display: inline-block;
                width: 6px;
                height: 6px;
                margin-right: 3px;
                border-radius: 50%;
                background-color: #EC4899;
                animation: typingBounce 1.2s infinite ease-in-out;
            }}
            .typing-indicator span:nth-child(2) {{ animation-delay: 0.15s; }}
            .typing-indicator span:nth-child(3) {{ animation-delay: 0.3s; }}
        </style>
        """,
        unsafe_allow_html=True,
    )