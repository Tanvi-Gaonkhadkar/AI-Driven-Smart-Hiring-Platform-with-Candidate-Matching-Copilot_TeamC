import streamlit as st
from styles.theme import inject_global_styles
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from components.header import page_header
from utils.auth import require_login, current_user
from services import database

st.set_page_config(page_title="Job Openings | YourTalentPilot", layout="wide")

inject_global_styles()
require_login()
render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()
page_header("Job Openings", "Create a job opening with required skills and a minimum ATS score")

database.init_db()

# ---- Create a new job opening ----
with st.container(border=True):
    st.markdown("**Post a New Job Opening**")
    with st.form("new_job_opening_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Job Title", placeholder="e.g. Python Developer")
            department = st.text_input("Department", placeholder="e.g. Engineering")
        with col2:
            required_skills = st.text_input(
                "Required Skills (comma-separated)", placeholder="e.g. Python, Flask, SQL"
            )
            min_ats_score = st.number_input("Minimum ATS Score", min_value=0, max_value=100, value=75, step=5)
        submitted = st.form_submit_button("Create Job Opening", use_container_width=True)

    if submitted:
        if not title.strip() or not required_skills.strip():
            st.error("Job Title and Required Skills are required.")
        else:
            job = database.create_job_opening(
                title=title,
                department=department or "General",
                required_skills=required_skills,
                min_ats_score=min_ats_score,
                created_by=current_user()["full_name"],
            )
            st.success(f"Created **{job['job_code']}** — {job['title']} (min ATS score: {job['min_ats_score']}).")
            st.rerun()

st.write("")

# ---- Existing job openings ----
st.markdown("**All Job Openings**")
jobs = database.get_all_job_openings()

if not jobs:
    st.info("No job openings yet — create one above.")
else:
    for job in jobs:
        with st.container(border=True):
            top = st.columns([2.5, 1.5, 1.2, 1.2, 1.6])
            top[0].markdown(f"**{job['title']}**  \n`{job['job_code']}` · {job['department']}")
            top[1].markdown(f"Required Skills:  \n{job['required_skills']}")
            top[2].markdown(f"Min ATS Score  \n**{job['min_ats_score']}**")
            status_color = "🟢" if job["status"] == "Open" else "⚪"
            top[3].markdown(f"Status  \n{status_color} {job['status']}")
            with top[4]:
                candidate_count = len(database.get_candidates_for_job(job["id"]))
                st.caption(f"{candidate_count} candidate(s) screened")
                if job["status"] == "Open":
                    if st.button("Close Opening", key=f"close_{job['id']}", use_container_width=True):
                        database.set_job_status(job["id"], "Closed")
                        st.rerun()
                else:
                    if st.button("Reopen", key=f"reopen_{job['id']}", use_container_width=True):
                        database.set_job_status(job["id"], "Open")
                        st.rerun()

render_global_chat()
