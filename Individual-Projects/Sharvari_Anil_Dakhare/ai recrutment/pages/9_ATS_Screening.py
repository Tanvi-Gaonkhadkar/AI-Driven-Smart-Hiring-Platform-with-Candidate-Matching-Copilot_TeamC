import streamlit as st
from styles.theme import inject_global_styles, COLORS
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from components.header import page_header
from utils.auth import require_login
from utils.text_extraction import extract_text
from utils.ats_scoring import score_resume, parse_skills
from services import database

st.set_page_config(page_title="ATS Screening | YourTalentPilot", layout="wide")

inject_global_styles()
require_login()
render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()
page_header("ATS Candidate Screening", "Compare resumes against a job opening's requirements and auto-shortlist")

database.init_db()
jobs = database.get_all_job_openings()

if not jobs:
    st.warning("No job openings yet. Create one on the **Job Openings** page first.")
    st.page_link("pages/8_Job_Openings.py", label="Go to Job Openings →")
    render_global_chat()
    st.stop()

job_options = {f"{j['job_code']} — {j['title']}": j for j in jobs}
selected_label = st.selectbox("Select a Job Opening", list(job_options.keys()))
job = job_options[selected_label]

with st.container(border=True):
    st.markdown(f"**{job['title']}**  ·  {job['department']}")
    st.caption(f"Required Skills: {job['required_skills']}  ·  Minimum ATS Score: {job['min_ats_score']}")

st.write("")

# ---- Upload resumes to screen against this job ----
with st.container(border=True):
    st.markdown("**Screen a Resume**")
    col1, col2 = st.columns(2)
    with col1:
        candidate_name = st.text_input("Candidate Name")
        candidate_email = st.text_input("Candidate Email")
    with col2:
        candidate_phone = st.text_input("Candidate Phone")
        resume_file = st.file_uploader("Resume (PDF or DOCX)", type=["pdf", "docx"], key="ats_resume_upload")

    if st.button("Run ATS Screening", type="primary", use_container_width=True):
        if not candidate_name.strip():
            st.error("Candidate name is required.")
        elif not resume_file:
            st.error("Please upload a resume.")
        else:
            try:
                resume_text = extract_text(resume_file)
            except ValueError as e:
                st.error(str(e))
                resume_text = None

            if resume_text:
                ats_score, matched, missing = score_resume(resume_text, job["required_skills"])
                status = "Shortlisted" if ats_score >= job["min_ats_score"] else "Rejected"
                database.add_job_candidate(
                    job_id=job["id"],
                    name=candidate_name,
                    email=candidate_email,
                    phone=candidate_phone,
                    resume_filename=resume_file.name,
                    resume_text=resume_text,
                    ats_score=ats_score,
                    matched_skills=matched,
                    missing_skills=missing,
                    status=status,
                )
                icon = "✅" if status == "Shortlisted" else "❌"
                st.success(f"{icon} **{candidate_name}** → ATS {ats_score} — **{status}**")
                st.rerun()

st.write("")

# ---- Results for this job ----
st.markdown(f"**Screened Candidates — {job['job_code']}**")
candidates = database.get_candidates_for_job(job["id"])

if not candidates:
    st.info("No candidates screened for this job yet.")
else:
    for c in candidates:
        with st.container(border=True):
            cols = st.columns([2, 1, 2, 2, 1.2])
            cols[0].markdown(f"**{c['name']}**  \n{c['email'] or '—'}")
            icon = "✅" if c["status"] == "Shortlisted" else ("❌" if c["status"] == "Rejected" else "🟡")
            score_color = COLORS.get("success") if c["status"] == "Shortlisted" else COLORS.get("danger")
            cols[1].markdown(
                f"<div style='font-weight:800; font-size:20px; color:{score_color};'>{c['ats_score']}</div>",
                unsafe_allow_html=True,
            )
            cols[2].markdown(
                "Matched: " + (", ".join(c["matched_skills"].split(",")) if c["matched_skills"] else "—")
            )
            cols[3].markdown(
                "Missing: " + (", ".join(c["missing_skills"].split(",")) if c["missing_skills"] else "—")
            )
            cols[4].markdown(f"{icon} **{c['status']}**")

render_global_chat()
