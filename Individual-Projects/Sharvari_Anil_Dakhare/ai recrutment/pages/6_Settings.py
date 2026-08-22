import streamlit as st
from styles.theme import inject_global_styles
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from components.header import page_header

from utils.auth import require_login

st.set_page_config(page_title="Settings | YourTalentPilot", layout="wide")

inject_global_styles()
require_login()
render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()
page_header("Settings", "Manage your profile and preferences")

tab1, tab2, tab3 = st.tabs(["Profile", "Notifications", "Security"])

with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.text_input("Full Name", value="Sharvari Dakhare")
    st.write("")
    st.text_input("Email", value="sharvaridakhare@yourtalentpilot.com")
    st.write("")
    st.text_input("Organization", value="YourTalentPilot Inc.")
    st.write("")
    st.button("Save Changes", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.toggle("Email notifications", value=True)
    st.toggle("New candidate alerts", value=True)
    st.toggle("Interview reminders", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.text_input("Current Password", type="password")
    st.write("")
    st.text_input("New Password", type="password")
    st.write("")
    st.button("Update Password", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

render_global_chat()
