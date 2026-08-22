import streamlit as st
from utils.session_manager import initialize_session

from styles import load_css

from login import login_page

from dashboard import dashboard_page
from job_description_analyzer import job_description_analyzer_page
from resume_matching import resume_matching_page
from ai_hr_assistant import ai_hr_assistant
from candidate_ranking_comparison import candidate_ranking_comparison_page
from interview_management import interview_management_page
from talent_management import talent_management_page
from ai_email_generator import ai_email_generator_page
from settings import settings_page

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="AI Recruitment & Talent Management Copilot",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

initialize_session()

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -------------------------------------------------
# LOAD CSS
# -------------------------------------------------

st.markdown(
    load_css(st.session_state.theme),
    unsafe_allow_html=True
)

# -------------------------------------------------
# LOGIN PAGE
# -------------------------------------------------

if not st.session_state.logged_in:
    login_page()
    st.stop()

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.title("AI Recruitment")
st.sidebar.title("Talent Management Copilot")

st.sidebar.markdown("")

st.sidebar.subheader("Appearance")

theme = st.sidebar.radio(
    "",
    ["Light", "Dark"],
    index=0 if st.session_state.theme == "Light" else 1,
    label_visibility="collapsed"
)

st.session_state.theme = theme

st.markdown(load_css(theme), unsafe_allow_html=True)

st.sidebar.markdown("")

# -------------------------------
# Logout
# -------------------------------

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("")

st.sidebar.subheader("Navigation")

page = st.sidebar.radio(
    "",
    [
        "Dashboard",
        "Job Description Analyzer AI",
        "Resume Matching",
        "AI HR Assistant",
        "Candidate Ranking & Comparison",
        "Interview Management",
        "Talent Management",
        "AI Email Generator",
        "Settings",
    ],
    label_visibility="collapsed"
)

# -------------------------------------------------
# PAGE ROUTING
# -------------------------------------------------

pages = {
    "Dashboard": dashboard_page,
    "Job Description Analyzer AI": job_description_analyzer_page,
    "Resume Matching": resume_matching_page,
    "AI HR Assistant": ai_hr_assistant,
    "Candidate Ranking & Comparison": candidate_ranking_comparison_page,
    "Interview Management": interview_management_page,
    "Talent Management": talent_management_page,
    "AI Email Generator": ai_email_generator_page,
    "Settings": settings_page,
}

pages[page]()

# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.markdown(
    """
    <hr>
    <div class='footer'>
        AI Recruitment & Talent Management Copilot
    </div>
    """,
    unsafe_allow_html=True
)