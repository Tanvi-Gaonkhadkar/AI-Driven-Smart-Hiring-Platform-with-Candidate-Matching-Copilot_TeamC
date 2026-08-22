import streamlit as st
from data import mock_data as data
from data import candidate_store


def render_sidebar_branding():
    """Logo + plan badge at the top of the sidebar."""
    # Built as one unindented block on purpose - see kpi_card.py for why:
    # indented multi-line HTML risks Markdown rendering it as a literal
    # code block instead of parsing the tags.
    branding_html = (
        '<div class="sidebar-brand">'
        '<div class="brand-name">YourTalentPilot</div>'
        '</div>'
        '<div class="plan-badge">ENTERPRISE PLAN</div>'
        '<hr class="sidebar-divider">'
    )
    st.sidebar.markdown(branding_html, unsafe_allow_html=True)


def render_theme_toggle():
    """
    Sidebar light/dark toggle. Persists to st.session_state["dark_mode"].

    Streamlit has a known bug where a widget bound via key= to a session_state
    value does not reliably re-sync its displayed value when that same widget
    is recreated on a *different* page in a multipage app (the widget can
    visually reset even though session_state itself is still correct).

    Fix: keep "dark_mode" as our own persisted value, and never let the
    widget's own key be the source of truth. We explicitly hand the toggle
    its current value via value=, and only update our persisted value through
    on_change - so every page always renders the toggle from the value we
    control, not from Streamlit's per-page widget state.
    """
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False

    def _apply_toggle():
        st.session_state["dark_mode"] = st.session_state["dark_mode_widget"]

    st.sidebar.toggle(
        "Dark Mode",
        value=st.session_state["dark_mode"],
        key="dark_mode_widget",
        on_change=_apply_toggle,
    )


def render_nav():
    """
    Custom grouped navigation, replacing Streamlit's flat auto-generated
    page list (hidden via CSS). Grouped sections read like a real product's
    IA, and a couple of items carry live badge counts pulled from mock data.
    """
    live_df = candidate_store.get_all_df()
    new_applicants = int((live_df["Stage"] == "Applied").sum()) if len(live_df) else 0
    upcoming_interviews = len(data.INTERVIEW_SCHEDULE)

    open_jobs_count = None
    pending_onboarding_count = None
    try:
        from services import database
        open_jobs_count = sum(1 for j in database.get_all_job_openings() if j["status"] == "Open") or None
        selected = [
            c for c in database.get_all_job_candidates()
            if c["status"] == "Selected" and not database.is_candidate_onboarded(c["id"])
        ]
        pending_onboarding_count = len(selected) or None
    except Exception:
        pass

    sections = [
        ("Recruitment", [
            ("Dashboard", "pages/1_Dashboard.py", None),
            ("Job Descriptions", "pages/7_Job_Description.py", len(data.JOB_DESCRIPTIONS_SEED)),
            ("Resume Analyzer", "pages/2_Resume_Analyzer.py", None),
            ("Candidate Screening", "pages/3_Candidate_Screening.py", new_applicants),
            ("Interview Copilot", "pages/4_Interview_Copilot.py", upcoming_interviews),
        ]),
        ("HR Workflow", [
            ("Job Openings", "pages/8_Job_Openings.py", open_jobs_count),
            ("ATS Scoring", "pages/9_ATS_Screening.py", None),
            ("Interview Management", "pages/10_Interview_Scheduling.py", pending_onboarding_count),
        ]),
        ("Insights", [
            ("Hiring Analytics", "pages/5_Hiring_Analytics.py", None),
        ]),
        ("Admin", [
            ("Settings", "pages/6_Settings.py", None),
        ]),
    ]

    for label, items in sections:
        st.sidebar.markdown(f'<div class="nav-section-label">{label}</div>', unsafe_allow_html=True)
        for title, page, badge in items:
            if badge:
                col1, col2 = st.sidebar.columns([4, 1])
                col1.page_link(page, label=title)
                col2.markdown(f'<div class="nav-badge">{badge}</div>', unsafe_allow_html=True)
            else:
                st.sidebar.page_link(page, label=title)


def render_profile_card():
    """Small identity footer, always visible in the sidebar across every page."""
    user = st.session_state.get("auth_user") or {"full_name": "Guest", "role": "Not logged in"}
    initials = "".join(w[0] for w in user["full_name"].split()[:2]).upper() or "?"
    profile_html = (
        '<div class="profile-card">'
        f'<div class="profile-avatar">{initials}<div class="profile-status-dot"></div></div>'
        '<div>'
        f'<div class="profile-name">{user["full_name"]}</div>'
        f'<div class="profile-role">{user["role"]}</div>'
        '</div>'
        '</div>'
    )
    st.sidebar.markdown(profile_html, unsafe_allow_html=True)
