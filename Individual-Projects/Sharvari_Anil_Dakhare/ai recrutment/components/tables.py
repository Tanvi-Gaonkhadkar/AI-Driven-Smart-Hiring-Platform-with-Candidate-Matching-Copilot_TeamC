import streamlit as st
from styles.theme import COLORS, is_dark_mode


def styled_table(df):
    """
    Renders a table styled with a soft light-blue / dark ice-blue tone in dark mode.
    """
    if df is None or (hasattr(df, "empty") and df.empty):
        st.info("No records to display.")
        return

    # Choose a soft ice-blue tint for Dark Mode, standard translucency for Light Mode
    if is_dark_mode():
        table_bg = "#1E293B"       # Dark slate blue base
        header_bg = "#334155"      # Light slate blue header
        text_color = "#F8FAFC"     # Clean white text
        border_col = "#475569"     # Muted blue border
    else:
        table_bg = COLORS.get("surface", "#FFFFFF")
        header_bg = COLORS.get("surface_muted", "#F1F5F9")
        text_color = COLORS.get("text_primary", "#0F172A")
        border_col = COLORS.get("border", "#E2E8F0")

    st.markdown(
        f"""
        <style>
            div[data-testid="stTable"] {{
                background-color: {table_bg} !important;
                border-radius: 12px !important;
                border: 1px solid {border_col} !important;
                overflow: hidden !important;
            }}
            div[data-testid="stTable"] table {{
                background-color: transparent !important;
                color: {text_color} !important;
            }}
            div[data-testid="stTable"] th {{
                background-color: {header_bg} !important;
                color: {text_color} !important;
                border-bottom: 1px solid {border_col} !important;
                font-weight: 700 !important;
            }}
            div[data-testid="stTable"] td {{
                background-color: transparent !important;
                color: {text_color} !important;
                border-bottom: 1px solid {border_col} !important;
            }}
            div[data-testid="stDataFrame"] {{
                background-color: {table_bg} !important;
                border: 1px solid {border_col} !important;
                border-radius: 12px !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.table(df)