"""
Job Description store.

No database yet (that's Phase 2 on the roadmap), so JDs live in
st.session_state for the current browser session, seeded from the mock
data on first load. Every function here is the ONLY place that touches
st.session_state["job_descriptions"] - pages should call these helpers
rather than reading session_state directly, so swapping in a real DB
later only means rewriting this one file.
"""

import streamlit as st
from data.mock_data import JOB_DESCRIPTIONS_SEED


def _ensure_seeded():
    if "job_descriptions" not in st.session_state:
        st.session_state["job_descriptions"] = [dict(jd) for jd in JOB_DESCRIPTIONS_SEED]
    if "jd_next_id" not in st.session_state:
        st.session_state["jd_next_id"] = len(st.session_state["job_descriptions"]) + 1


def get_all():
    _ensure_seeded()
    return st.session_state["job_descriptions"]


def get_by_id(jd_id: str):
    return next((jd for jd in get_all() if jd["id"] == jd_id), None)


def add(title, department, level, employment_type, description, required_skills, nice_to_have_skills):
    _ensure_seeded()
    new_id = f"jd-{st.session_state['jd_next_id']:03d}"
    st.session_state["jd_next_id"] += 1
    jd = {
        "id": new_id,
        "title": title,
        "department": department,
        "level": level,
        "employment_type": employment_type,
        "description": description,
        "required_skills": required_skills,
        "nice_to_have_skills": nice_to_have_skills,
        "created": "Just now",
    }
    st.session_state["job_descriptions"].append(jd)
    return jd


def delete(jd_id: str):
    _ensure_seeded()
    st.session_state["job_descriptions"] = [
        jd for jd in st.session_state["job_descriptions"] if jd["id"] != jd_id
    ]