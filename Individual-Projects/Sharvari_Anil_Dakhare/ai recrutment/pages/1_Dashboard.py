import streamlit as st
from styles.theme import inject_global_styles, COLORS
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from components.header import page_header
from components.kpi_card import kpi_card
from components.charts import hiring_trend_chart, recruitment_funnel_chart
from components.tables import styled_table
from data import mock_data as data

from utils.auth import require_login

st.set_page_config(page_title="Dashboard | YourTalentPilot", layout="wide")

inject_global_styles()
require_login()
render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()
page_header("Dashboard", "Your hiring pipeline at a glance")

# ---- KPI row ----
cols = st.columns(len(data.KPIS))
for col, kpi in zip(cols, data.KPIS):
    with col:
        kpi_card(kpi["label"], kpi["value"], kpi["delta"], kpi["icon"])

st.write("")

# ---- Trend + Funnel ----
left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Hiring Trends**")
    fig = hiring_trend_chart(data.TREND_MONTHS, data.TREND_APPLICATIONS, data.TREND_HIRES)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Recruitment Funnel**")
    fig = recruitment_funnel_chart(data.FUNNEL_STAGES, data.FUNNEL_VALUES)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ---- Recent candidates + Activity/Interviews ----
left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Recent Candidates**")
    styled_table(data.RECENT_CANDIDATES)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Recent Activity**")
    for item in data.RECENT_ACTIVITY:
        st.markdown(
            f"<div style='padding:6px 0; font-size:14px;'>{item['icon']} {item['text']}"
            f"<div style='font-size:12px; color:{COLORS['text_secondary']};'>{item['time']}</div></div>",
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("**Upcoming Interviews**")
styled_table(data.UPCOMING_INTERVIEWS)
st.markdown('</div>', unsafe_allow_html=True)

render_global_chat()
