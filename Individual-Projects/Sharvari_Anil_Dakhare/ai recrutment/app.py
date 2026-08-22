import streamlit as st
from styles.theme import inject_global_styles, COLORS
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from data import mock_data as data
from utils.auth import require_login, current_user, logout

st.set_page_config(
    page_title="YourTalentPilot",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()
require_login()  # Module 1: Recruiter/HR Login - blocks everything below until logged in

render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()

# ---- Top bar: search, notifications, profile ----
top_left, top_search, top_bell, top_profile = st.columns([2, 4, 0.6, 0.6])

with top_search:
    query = st.text_input(
        "Search",
        placeholder="Search candidates, roles, or skills...",
        label_visibility="collapsed",
        key="global_search",
    )
    if query:
        st.session_state["screening_query"] = query
        st.switch_page("pages/3_Candidate_Screening.py")

with top_bell:
    with st.popover("Notifications"):
        st.markdown("**Notifications**")
        for item in data.RECENT_ACTIVITY:
            st.markdown(item['text'])
            st.caption(item["time"])

with top_profile:
    user = current_user()
    with st.popover("Profile"):
        st.markdown(f"**{user['full_name']}**")
        st.caption(user["role"])
        st.page_link("pages/6_Settings.py", label="Settings")
        if st.button("Log Out", key="app_logout_btn", use_container_width=True):
            logout()


# ---- Hero ----
# Built as one unindented block: Markdown treats 4+ leading spaces at the
# start of a line as a preformatted code block, so an indented multi-line
# HTML string was at risk of the same "</div>" literal-text bug found in
# the KPI card.
hero_html = (
    '<div class="hero-banner">'
    '<div class="hero-eyebrow">AI Recruitment &amp; Talent Management</div>'
    '<div class="hero-title">Welcome back, Sharvari</div>'
    f'<div class="hero-subtitle">Your hiring pipeline is moving fast — {data.KPIS[1]["value"]} active candidates, '
    f'{data.KPIS[2]["value"]} interviews on the calendar, and an average time to hire down to {data.KPIS[3]["value"]}.</div>'
    '<br>'
    '<div style="display:flex; gap:36px;">'
    f'<div><div class="hero-stat-value">{data.KPIS[0]["value"]}</div><div class="hero-stat-label">Open Positions</div></div>'
    f'<div><div class="hero-stat-value">{data.KPIS[1]["value"]}</div><div class="hero-stat-label">Active Candidates</div></div>'
    f'<div><div class="hero-stat-value">{data.OFFER_ACCEPTANCE_RATE}</div><div class="hero-stat-label">Offer Acceptance</div></div>'
    f'<div><div class="hero-stat-value">{data.TIME_TO_HIRE_DAYS} days</div><div class="hero-stat-label">Avg. Time to Hire</div></div>'
    '</div>'
    '</div>'
)
st.markdown(hero_html, unsafe_allow_html=True)

# ---- Module grid ----
st.markdown("#### Quick Access")

modules = [
    ("Dashboard", "Your hiring pipeline at a glance", "pages/1_Dashboard.py"),
    ("Resume Analyzer", "Upload and evaluate resumes with AI", "pages/2_Resume_Analyzer.py"),
    ("Candidate Screening", "Search, filter, and shortlist candidates", "pages/3_Candidate_Screening.py"),
    ("Interview Copilot", "Prepare questions and evaluate interviews", "pages/4_Interview_Copilot.py"),
    ("Hiring Analytics", "Track recruitment performance and trends", "pages/5_Hiring_Analytics.py"),
    ("Settings", "Manage your profile and preferences", "pages/6_Settings.py"),
    ("Job Openings", "Post a role with required skills & ATS threshold", "pages/8_Job_Openings.py"),
    ("ATS Scoring", "Score resumes against a job's requirements", "pages/9_ATS_Screening.py"),
    ("Interview Management", "The full pipeline — Applied through Onboarding, in one place", "pages/10_Interview_Scheduling.py"),
]

cols = st.columns(3)
for i, (title, desc, page) in enumerate(modules):
    with cols[i % 3]:
        module_html = (
            f'<div class="module-card" style="animation-delay:{i * 0.05}s;">'
            f'<div class="module-title">{title}</div>'
            f'<div class="module-desc">{desc}</div>'
            f'</div>'
        )
        st.markdown(module_html, unsafe_allow_html=True)
        st.page_link(page, label="Open →", use_container_width=True)
        st.write("")

# ---- Recent activity ----
st.markdown("#### Recent Activity")
st.markdown('<div class="card">', unsafe_allow_html=True)
for item in data.RECENT_ACTIVITY:
    st.markdown(
        f"<div style='padding:6px 0; font-size:14px;'>{item['text']}"
        f"<div style='font-size:12px; color:{COLORS['text_secondary']};'>{item['time']}</div></div>",
        unsafe_allow_html=True,
    )
st.markdown('</div>', unsafe_allow_html=True)

render_global_chat()
