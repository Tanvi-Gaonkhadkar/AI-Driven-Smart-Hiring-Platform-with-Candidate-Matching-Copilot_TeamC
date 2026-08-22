import streamlit as st


def page_header(title: str, subtitle: str = ""):
    """Consistent title block used at the top of every page."""
    subtitle_html = f'<div class="page-subtitle">{subtitle}</div>' if subtitle else ""
    header_html = (
        '<div class="page-header"><div>'
        f'<div class="page-title">{title}</div>'
        f'{subtitle_html}'
        '</div></div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)
