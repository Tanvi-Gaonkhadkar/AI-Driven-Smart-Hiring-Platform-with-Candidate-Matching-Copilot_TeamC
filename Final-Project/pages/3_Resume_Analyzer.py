"""
Resume Analyzer - AI Recruitment Copilot
Frontend + Backend Integration
"""

import os

import streamlit as st
from backend.resume_service import analyze_resume
from database.database import (
    get_job_by_id,
    save_resume_analysis,
    update_candidate_status,
    add_candidate,
    candidate_exists,
    get_jobs
)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Login.py")

if st.session_state.role != "Recruiter":
    st.error("🚫 Access Denied. This module is available only to Recruiters.")
    st.stop()
st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="wide")

st.title("📄 Resume Analyzer")
st.caption("AI-powered Resume Analysis using local Ollama backend")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

with st.sidebar:
    st.header("🤖 AI Modules")
    st.success("JD Analyzer AI")
    st.success("Resume Matching AI")
    st.success("Skill Gap AI")
    st.success("Hiring Recommendation AI")
    # st.success("Resume Chat AI")

c1, c2 = st.columns(2)

# with c1:
#     resume_file = st.file_uploader(
#         "Upload Resume",
#         type=["pdf"]
#     )
# with c2:
#     jd_file = st.file_uploader("Upload Job Description", type=["pdf"])
with c1:

    resume_file = st.file_uploader(
        "Upload Resume",
        type=["pdf"]
    )

with c2:

    jobs = get_jobs()

    if jobs.empty:

        st.warning("No job roles available. Please create a job first.")

        selected_job_id = None

    else:

        job_options = {
            f"{row['job_title']} — Job ID: {row['id']}": row["id"]
            for _, row in jobs.iterrows()
        }

        selected_job = st.selectbox(
            "Select Job Role",
            list(job_options.keys())
        )

        selected_job_id = job_options[selected_job]
        
if st.button("🤖 Analyze Resume", width="stretch"):

    if resume_file is None:
        st.warning("Please upload a resume.")
        st.stop()

    if selected_job_id is None:
        st.warning("Please select a job role.")
        st.stop()

    resume_path = os.path.join(
        UPLOAD_DIR,
        resume_file.name
    )

    with open(resume_path, "wb") as f:
        f.write(resume_file.getbuffer())

    with st.spinner("Analyzing..."):

        try:

            st.session_state.analysis_result = analyze_resume(
                resume_path,
                selected_job_id
            )

            st.session_state.resume_name = resume_file.name

            result = st.session_state.analysis_result

            score = result["matching"]["skill_score"]

            if score >= 90:
                recommendation = "Highly Recommended"

            elif score >= 75:
                recommendation = "Recommended"

            else:
                recommendation = "Needs Improvement"

            save_resume_analysis(
                resume_file.name,
                result["job_title"],
                score,
                ", ".join(result["matching"]["matched"]),
                ", ".join(result["matching"]["missing"]),
                result["analysis"][:300],
                recommendation,
                result["analysis"]
            )

            st.success("Analysis Complete")

        except Exception as e:

            st.error(
                f"Analysis Failed: {e}"
            )
st.divider()

st.subheader("📂 Bulk Resume Upload")

bulk_resume_files = st.file_uploader(
    "Upload Multiple Resumes",
    type=["pdf"],
    accept_multiple_files=True,
    key="bulk_resume_uploader"
)            
if st.button("📂 Add Bulk Resumes", width="stretch"):

    if not bulk_resume_files:
        st.warning("Please upload at least one resume.")
        st.stop()

    added = 0
    skipped = 0

    for resume in bulk_resume_files:

        candidate_name = (
            os.path.splitext(resume.name)[0]
            .replace("_", " ")
        )

        if candidate_exists(candidate_name):
            skipped += 1
            continue

        resume_path = os.path.join(
            UPLOAD_DIR,
            resume.name
        )

        try:

            with open(resume_path, "wb") as f:
                f.write(resume.getbuffer())

            add_candidate(
                name=candidate_name,
                email="",
                phone="",
                role_applied="AI Engineer",
                experience="Not Analyzed",
                skills="",
                resume_path=resume_path,
                status="Applied"
            )

            added += 1

        except Exception as e:
            skipped += 1
            st.warning(
                f"Could not add {resume.name}: {e}"
            )

    if added > 0:
        st.success(
            f"✅ {added} resume(s) added successfully."
        )

    if skipped > 0:
        st.info(
            f"ℹ️ {skipped} resume(s) skipped "
            f"(already existing or could not be added)."
        )
if st.session_state.analysis_result is not None:

    result = st.session_state.analysis_result
    resume_name = st.session_state.get("resume_name")

    if not resume_name:
        st.warning("Please analyze a resume first.")
        st.stop()

    candidate_name = (
        resume_name
        .replace(".pdf", "")
        .replace("_", " ")
    )
    left, right = st.columns([1,2])

    with left:
                st.metric("ATS Score", f"{result['matching']['skill_score']}%")

                st.subheader("Experience")
                for x in result["resume_json"].get("experience", []):
                    st.write("•", x)

                st.subheader("Education")
                for x in result["resume_json"].get("education", []):
                    st.write("•", x)

                st.subheader("Projects")
                for x in result["resume_json"].get("projects", []):
                    st.write("•", x)

    with right:
                t1,t2,t3,t4= st.tabs([
                    "Resume Match",
                    "Matched Skills",
                    "Missing Skills",
                    "AI Report",
                    # "Resume Chat"
                ])

                with t1:
                    a,b,c,d = st.columns(4)
                    a.metric("ATS Score", f"{result['matching']['skill_score']}%")
                    b.metric("Matched", result["matching"]["matched_count"])
                    c.metric("Missing", len(result["matching"]["missing"]))
                    d.metric("Resume Skills", result["matching"]["resume_skill_count"])

                with t2:
                    for s in result["matching"]["matched"]:
                        st.success(s)
                    st.subheader("Extra Skills")
                    for s in result["matching"]["extra"]:
                        st.info(s)

                with t3:
                    for s in result["matching"]["missing"]:
                        st.warning(s)

                with t4:
                    st.markdown(result["analysis"])
                    st.download_button(
                        "Download AI Report",
                        result["analysis"],
                        file_name="AI_Report.md",
                        width="stretch"
                    )
                
    st.divider()

    x, y, z = st.columns(3)

    with x:

        if st.button("✅ Shortlist", width="stretch"):

            update_candidate_status(
                candidate_name,
                "Shortlisted"
            )

            st.success("Candidate has been shortlisted successfully.")

            st.balloons()

    with y:

        if st.button("📅 Schedule Interview", width="stretch"):

            update_candidate_status(
                candidate_name,
                "Interview Scheduled"
            )

            st.success("Interview scheduled successfully.")

            st.info("""
    ### Interview Details

    📅 Date : Monday

    🕙 Time : 10:00 AM

    💻 Mode : Virtual

    👨‍💼 Panel : Technical + HR
    """)

    with z:

        if st.button("❌ Reject", width="stretch"):

            update_candidate_status(
                candidate_name,
                "Rejected"
            )

            st.error("Candidate has been rejected.")

            st.info("AI can generate a rejection email for the candidate.")


