import streamlit as st
import sqlite3

DB_PATH = "database/recruitment.db"

PIPELINE_STAGES = [
    "All",
    "Applied",
    "AI Reviewed",
    "Shortlisted",
    "Interview Round 1",
    "Interview Round 2",
    "Interview Round 3",
    "Selected",
    "Offer Sent",
    "Rejected",
    "Hold"
]


def get_connection():
    return sqlite3.connect(DB_PATH)


def load_candidates(stage_filter="All"):
    """
    Returns all interview candidates.

    Returns
    -------
    [
        {
            interview_id,
            candidate_id,
            candidate_name,
            role,
            round_name,
            status,
            interview_date,
            interviewer
        }
    ]
    """

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT

        interviews.id,

        candidates.id,

        candidates.name,

        candidates.role_applied,
        candidates.email,

        interviews.round_name,

        interviews.status,

        interviews.interview_date,

        interviews.interviewer

    FROM interviews

    INNER JOIN candidates

    ON candidates.id = interviews.candidate_id
    """

    params = []

    if stage_filter != "All":

        if stage_filter in (
            "Applied",
            "AI Reviewed",
            "Shortlisted"
        ):

            query += """
            WHERE interviews.status=?
            """

            params.append(stage_filter)

        else:

            query += """
            WHERE interviews.round_name=?
            """

            params.append(stage_filter)

    query += """
    ORDER BY candidates.name
    """

    cursor.execute(query, params)

    rows = cursor.fetchall()

    conn.close()

    candidates = []

    for row in rows:

        candidates.append({

            "interview_id": row[0],

            "candidate_id": row[1],

            "candidate_name": row[2],

            "role": row[3],
            "email": row[4],
            "round_name": row[5],
            "status": row[6],
            "interview_date": row[7],
            "interviewer": row[8],

                    })

    return candidates


def draw_candidate_filter():
    """
    Draws stage filter and candidate selector.

    Returns
    -------
    selected_interview_id
    """

    if "selected_stage_filter" not in st.session_state:
        st.session_state.selected_stage_filter = "All"

    stage = st.selectbox(

        "Filter Candidates",

        PIPELINE_STAGES,

        index=PIPELINE_STAGES.index(
            st.session_state.selected_stage_filter
        )

    )

    st.session_state.selected_stage_filter = stage

    candidates = load_candidates(stage)

    if len(candidates) == 0:

        st.warning(
            "No candidates found."
        )

        st.stop()

    labels = []

    mapping = {}

    for c in candidates:

        label = (

            f"{c['candidate_name']}"

            f" | {c['role']}"

            f" | {c['round_name']}"

            f" | {c['status']}"

        )

        labels.append(label)

        mapping[label] = c

    if "selected_candidate_label" not in st.session_state:

        st.session_state.selected_candidate_label = labels[0]

    if st.session_state.selected_candidate_label not in labels:

        st.session_state.selected_candidate_label = labels[0]

    selected = st.selectbox(

        "Active Candidate",

        labels,

        key="selected_candidate_label"

    )

    data = mapping[selected]

    st.session_state.selected_candidate = data

    st.session_state.selected_candidate_name = data["candidate_name"]

    st.session_state.selected_role = data["role"]

    st.session_state.selected_interview_id = data["interview_id"]

    return data