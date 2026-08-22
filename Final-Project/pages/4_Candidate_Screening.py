
"""
Candidate Screening - AI Recruitment Copilot
Connected with backend Candidate Service
"""

import os

import streamlit as st
import pandas as pd
from backend.hiring_recommend import hiring_recommendation
from backend.resume_comparison import compare_candidates
from backend.candidate_service import candidate_service

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Login.py")

if st.session_state.role != "Recruiter":
    st.error("🚫 Access Denied. This module is available only to Recruiters.")
    st.stop()
st.set_page_config(page_title="Candidate Screening", page_icon="👥", layout="wide")

st.title("👥 Candidate Screening")
st.caption("AI-powered candidate screening with backend integration.")

UPLOAD_DIR = "uploads"

from database.database import (
    get_candidates,
    bulk_update_candidate_status,
    get_jobs
)
candidates = get_candidates()

resume_files = [
    path
    for path in candidates["resume_path"]
    if isinstance(path, str) and os.path.exists(path)
]
# st.write(candidates[["name", "resume_path"]])

# st.write(resume_files)

# for i, r in enumerate(resume_files):
#     st.write(i, r, type(r))

# jd_file = os.path.join(UPLOAD_DIR, "AI_EngineerJD.pdf")from database.database import get_jobs

jobs = get_jobs()

ai_engineer_job = jobs[
    jobs["job_title"].str.strip().str.lower() == "ai engineer"
]

if ai_engineer_job.empty:
    st.error("AI Engineer job not found in database.")
    st.stop()

job_id = int(ai_engineer_job.iloc[0]["id"])
with st.sidebar:
    st.header("🤖 AI Modules")
    st.success("Candidate Ranking AI")
    st.success("Hiring Recommendation AI")
    st.success("Resume Comparison AI")

# @st.cache_data(show_spinner=False)
# def load_data():
#     return candidate_service(resume_files, jd_file)
   
# @st.cache_data(show_spinner=False)
# def get_comparison(r1, r2):
#     return compare_candidates(r1, r2)
@st.cache_data(show_spinner=False)
def load_data(resume_files, job_id):
    return candidate_service(list(resume_files), job_id)


@st.cache_data(show_spinner=False)
def get_recommendation(result):
    return hiring_recommendation(result)


@st.cache_data(show_spinner=False)
def get_comparison(r1, r2):
    return compare_candidates(r1, r2)   

with st.spinner("Running AI Candidate Screening..."):
    result = load_data(
    tuple(resume_files),
    job_id
)

# st.write("========== DATABASE ==========")
# st.write(candidates["name"].tolist())

# st.write("========== AI ==========")
# st.write([c["name"] for c in result["ranking"]])

rows = []
for c in result["ranking"]:
    experience = c["result"]["resume_json"].get("experience", [])

    if isinstance(experience, list):
        experience = ", ".join(experience)

    filtered = candidates[
        candidates["name"].str.strip() ==
        c["name"].replace("_", " ").strip()
    ]

    if filtered.empty:
        st.warning(f"Candidate not found: {c['name']}")
        continue

    db_candidate = filtered.iloc[0]
    
    rows.append({
                    "Name": db_candidate["name"],
                    "Role": db_candidate["role_applied"],
                    "Experience": db_candidate["experience"],
                    "ATS Score": c["ATS Score"],
                    "Rank": c["rank"],
                    "Status": db_candidate["status"]
                })
        
data = pd.DataFrame(rows)

c1, c2, c3 = st.columns([2, 1, 1.2])

with c1:
    search = st.text_input("🔍 Search Candidate")

with c2:
    status_list = ["All"] + sorted(candidates["status"].unique().tolist())

    status = st.selectbox(
        "Filter Status",
        status_list
    )

with c3:
    selected = st.selectbox(
        "Select Candidate",
        data["Name"]
    )

# ==========================
# Apply Filters
# ==========================

df = data.copy()

if search:
    df = df[df["Name"].str.contains(search, case=False)]

if status != "All":
    df = df[df["Status"] == status]

candidate = next(
    (
        c
        for c in result["ranking"]
        if c["name"].replace("_", " ").strip() == selected.strip()
    ),
    None
)

if candidate is None:
    st.error("Selected candidate not found in AI results.")
    st.stop()

# ==========================
# Main Layout
# ==========================

left, right = st.columns([1.4, 1])
df["Select"] = False
with left:
    st.subheader("📋 Candidate List")
    edited_df = st.data_editor(

        df,

        hide_index=True,

        use_container_width=True,

        disabled=[
            "Name",
            "Role",
            "Experience",
            "ATS Score",
            "Rank",
            "Status"
        ]
    )
    selected_candidates = edited_df[
        edited_df["Select"]
    ]["Name"].tolist()

    st.info(f"{len(selected_candidates)} candidate(s) selected")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Shortlist Selected"):
            bulk_update_candidate_status(
                selected_candidates,
                "Shortlisted"
            )
            st.success("Candidates shortlisted.")
            st.rerun()

    with col2:
        if st.button("❌ Reject Selected"):
            bulk_update_candidate_status(
                selected_candidates,
                "Rejected"
            )
            st.success("Candidates rejected.")
            st.rerun()

    with col3:
        if st.button("🎯 Technical Round"):
            bulk_update_candidate_status(
                selected_candidates,
                "Technical Interview"
            )
            st.success("Candidates moved to Technical Round.")
            st.rerun()

with right:

    st.subheader("👤 Candidate Details")

    selected_candidate = candidates[
        candidates["name"] == selected
    ].iloc[0]

    st.write(f"**Role:** {selected_candidate['role_applied']}")
    st.write(f"**Rank:** #{candidate['rank']}")

    st.progress(
        candidate["ATS Score"],
        text=f"ATS Score {candidate['ATS Score']}%"
    )

    st.write("### Experience")

    for e in candidate["result"]["resume_json"].get("experience", []):
        st.write("-", e)

    st.write("### Education")

    for e in candidate["result"]["resume_json"].get("education", []):
        st.write("-", e)

tabs = st.tabs([
    "🏆 Ranking AI",
    "🤖 Hiring Recommendation",
    "⚖️ Resume Comparison"
    
])

with tabs[0]:
    a,b,c,d = st.columns(4)
    a.metric("Rank", f"#{candidate['rank']}")
    b.metric("ATS Score", f"{candidate['ATS Score']}%")
    c.metric("Matched", candidate["result"]["matching"]["matched_count"])
    d.metric("Missing", len(candidate["result"]["matching"]["missing"]))
    st.success(f"Candidate ranked #{candidate['rank']} with ATS Score of {candidate['ATS Score']}%.")

with tabs[1]:
    @st.cache_data(show_spinner=False)
    def get_recommendation(result):
        return hiring_recommendation(result)
    with st.spinner("Generating AI Recommendation..."):

        rec = get_recommendation(
            candidate["result"]
        )

    st.markdown(rec)
with tabs[2]:

    st.subheader("⚖️ AI Resume Comparison")

    candidate_names = data["Name"].tolist()

    col1, col2 = st.columns(2)

    with col1:
        candidate1 = st.selectbox(
            "Candidate 1",
            candidate_names,
            key="candidate1"
        )

    with col2:

        candidate2 = st.selectbox(
            "Candidate 2",
            [c for c in candidate_names if c != candidate1],
            key="candidate2"
        )

    result1 = next(
        c["result"]
        for c in result["ranking"]
        if c["name"].replace("_", " ") == candidate1
    )

    result2 = next(
        c["result"]
        for c in result["ranking"]
        if c["name"].replace("_", " ") == candidate2
    )

    with st.spinner("Comparing candidates..."):

        comparison = get_comparison(
            result1,
            result2
        )

    st.markdown(comparison)
# with tabs[2]:

#     st.subheader("⚖️ AI Resume Comparison")

#     candidate_names = data["Name"].tolist()

#     col1, col2 = st.columns(2)

#     with col1:
#         candidate1 = st.selectbox(
#             "Candidate 1",
#             candidate_names,
#             key="candidate1"
#         )

#     with col2:
#         candidate2 = st.selectbox(
#             "Candidate 2",
#             [c for c in candidate_names if c != candidate1],
#             key="candidate2"
#         )

#     result1 = next(
#         c["result"]
#         for c in result["ranking"]
#         if c["name"].replace("_", " ").strip() == candidate1.strip()
#     )

#     result2 = next(
#         c["result"]
#         for c in result["ranking"]
#         if c["name"].replace("_", " ").strip() == candidate2.strip()
#     )

#     if st.button(
#         "⚖️ Compare Candidates",
#         key="compare_candidates"
#     ):

#         with st.spinner("Comparing candidates..."):

#             import time

#             start = time.perf_counter()

#             comparison = get_comparison(
#                 result1,
#                 result2
#             )

#             elapsed = time.perf_counter() - start

#         st.success(
#             f"Comparison generated in {elapsed:.2f} seconds."
#         )

#         st.markdown(comparison)

st.divider()
