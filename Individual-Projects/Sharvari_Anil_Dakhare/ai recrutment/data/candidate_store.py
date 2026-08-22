"""
Candidate store.

This is what makes candidate data "real" within a session instead of a
frozen table: every candidate lives in st.session_state, seeded once from
mock_data on first load. From then on:

  - Resume Analyzer's Shortlist / Schedule Interview / Reject buttons add
    or update a real candidate record here (built from the actual AI
    analysis, not a hardcoded row)
  - Candidate Screening's action buttons update a candidate's stage here,
    and the table/timeline reflect it immediately
  - AI ranking, comparison, and skill-gap features all read from here

No database yet (Phase 2 on the roadmap) - this file is the only place
that touches st.session_state["candidates"], so swapping in a real DB
later only means rewriting this one file.
"""

import datetime
import pandas as pd
import streamlit as st
from data.mock_data import ALL_CANDIDATES, CANDIDATE_TIMELINE

# Fields added for Talent Management. Any candidate created without these
# (e.g. via Resume Analyzer's Shortlist/Interview buttons, which don't know
# about Experience/Location/etc.) gets these defaults filled in instead of
# showing blank/NaN in the table or skewing the average performance stat.
_NEW_FIELD_DEFAULTS = {
    "Experience": 0,
    "PerformanceRating": 3.0,
    "Location": "Unassigned",
}


def _next_employee_id() -> str:
    existing_ids = [c.get("EmployeeID", "") for c in st.session_state["candidates"]]
    nums = [int(i.split("-")[1]) for i in existing_ids if i.startswith("EMP-") and i.split("-")[1].isdigit()]
    return f"EMP-{(max(nums) + 1) if nums else 1001}"


def _fill_defaults(candidate: dict):
    for field, default in _NEW_FIELD_DEFAULTS.items():
        candidate.setdefault(field, default)
    if not candidate.get("EmployeeID"):
        candidate["EmployeeID"] = _next_employee_id()


def _ensure_seeded():
    if "candidates" not in st.session_state:
        st.session_state["candidates"] = ALL_CANDIDATES.copy().to_dict("records")
    if "candidate_timeline" not in st.session_state:
        st.session_state["candidate_timeline"] = {k: list(v) for k, v in CANDIDATE_TIMELINE.items()}


def get_all_df() -> pd.DataFrame:
    """Returns the full live candidate pool as a DataFrame."""
    _ensure_seeded()
    if not st.session_state["candidates"]:
        return pd.DataFrame(columns=[
            "Candidate", "Role", "Department", "Match", "Stage", "Skills", "Applied",
            "EmployeeID", "Experience", "PerformanceRating", "Location",
        ])
    return pd.DataFrame(st.session_state["candidates"])


def get_by_name(name: str):
    _ensure_seeded()
    return next((c for c in st.session_state["candidates"] if c["Candidate"] == name), None)


def add_or_update(candidate: dict, note: str = None):
    """
    candidate needs keys: Candidate, Role, Department, Match, Stage, Skills, Applied.
    (EmployeeID, Experience, PerformanceRating, Location are optional - if
    omitted, sensible defaults are filled in automatically.)
    If a candidate with this name already exists, it's updated in place
    (so re-analyzing the same person's resume refreshes their record
    instead of duplicating it). Also logs a timeline entry.
    """
    _ensure_seeded()
    existing = get_by_name(candidate["Candidate"])
    if existing:
        existing.update(candidate)
        _fill_defaults(existing)
    else:
        _fill_defaults(candidate)
        st.session_state["candidates"].append(candidate)

    timeline = st.session_state["candidate_timeline"].setdefault(candidate["Candidate"], [])
    timeline.append({
        "stage": candidate["Stage"],
        "date": datetime.date.today().strftime("%b %d, %Y"),
        "note": note or f"Moved to {candidate['Stage']}.",
    })


def update_stage(name: str, new_stage: str, note: str = None):
    """Updates just the stage of an existing candidate and logs a timeline entry."""
    _ensure_seeded()
    c = get_by_name(name)
    if c:
        c["Stage"] = new_stage
        timeline = st.session_state["candidate_timeline"].setdefault(name, [])
        timeline.append({
            "stage": new_stage,
            "date": datetime.date.today().strftime("%b %d, %Y"),
            "note": note or f"Moved to {new_stage}.",
        })


def get_timeline(name: str) -> list:
    _ensure_seeded()
    return st.session_state["candidate_timeline"].get(name, [])
