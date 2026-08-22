"""
Visual workflow progress indicator for the 8-step HR workflow:
HR Login -> Job Opening -> Candidate Screening -> Interview Scheduling ->
Interview Tracking -> Onboarding -> Talent Management -> Document
Management.

Completion state is derived live from the SQLite tables in
services/database.py on every render - it is never stored as a separate
flag, so it can't drift out of sync with what's actually in the database
(e.g. deleting the only job opening would correctly un-complete "Job
Opening" the next time this renders).

Usage - call once near the top of each of the 6 new workflow pages
(pages/8 through 13), right after page_header():

    from components.step_tracker import render_step_tracker
    render_step_tracker("Job Opening")   # this page's own step name
"""

import streamlit as st
from styles.theme import COLORS
from services import database

STEPS = [
    "HR Login",
    "Job Opening",
    "Candidate Screening",
    "Interview Scheduling",
    "Interview Tracking",
    "Onboarding",
    "Talent Management",
    "Document Management",
]


def _completed_steps() -> set:
    """Which steps are fully done, based on real data - see module docstring."""
    # If this is rendering at all, require_login() already passed for this
    # session, so Step 1 is always complete here.
    done = {"HR Login"}

    if database.get_all_job_openings():
        done.add("Job Opening")

    candidates = database.get_all_job_candidates()
    # "Selected" implies the candidate passed through Shortlisted earlier,
    # so both count - but a pool that's only ever been auto-Rejected by
    # the ATS score does not, matching the spec ("only shortlisted
    # candidates should proceed").
    if any(c["status"] in ("Shortlisted", "Selected") for c in candidates):
        done.add("Candidate Screening")

    interviews = database.get_all_interviews()
    if interviews:
        done.add("Interview Scheduling")
    if any(iv["status"] != "Scheduled" for iv in interviews):
        done.add("Interview Tracking")

    employees = database.get_all_employees()
    if employees:
        done.add("Onboarding")
        # Talent Management is an ongoing step, not a one-time gate - once
        # there's at least one employee it's considered "in use".
        done.add("Talent Management")

    if any(database.get_documents_for_employee(e["id"]) for e in employees):
        done.add("Document Management")

    return done


def render_step_tracker(current: str):
    """
    current: this page's own step name, exactly matching one entry in
    STEPS. Marked as the active step regardless of its own completion
    check (e.g. you're ON the Job Opening page before creating your first
    job, but it should still show as active, not locked).
    """
    completed = _completed_steps()

    pills_html = []
    for step in STEPS:
        if step == current:
            bg, fg, border, prefix = COLORS["primary"], "#FFFFFF", COLORS["primary"], "\u25b6"  # ▶
        elif step in completed:
            bg, fg, border, prefix = COLORS["surface_muted"], COLORS["success"], COLORS["success"], "\u2713"  # ✓
        else:
            bg, fg, border, prefix = COLORS["surface_muted"], COLORS["text_secondary"], COLORS["border"], "\U0001F512"  # 🔒
        pills_html.append(
            f'<div style="display:flex; align-items:center; gap:6px; background:{bg}; color:{fg}; '
            f'border:1px solid {border}; border-radius:999px; padding:6px 14px; font-size:12.5px; '
            f'font-weight:600; white-space:nowrap;">{prefix} {step}</div>'
        )

    # One unindented block, and the wrapping div uses flex-wrap so it
    # degrades gracefully on narrow/mobile widths instead of clipping.
    tracker_html = (
        '<div style="display:flex; flex-wrap:wrap; gap:10px; margin-bottom:20px;">'
        + "".join(pills_html) +
        '</div>'
    )
    st.markdown(tracker_html, unsafe_allow_html=True)
