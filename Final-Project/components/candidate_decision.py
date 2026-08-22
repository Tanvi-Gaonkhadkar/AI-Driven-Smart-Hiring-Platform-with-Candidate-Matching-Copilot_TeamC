# ==========================================================
# components/interview/candidate_decision.py
# ==========================================================

import sqlite3
import streamlit as st

DB_PATH = "database/recruitment.db"


# ==========================================================
# Database
# ==========================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================================
# Pipeline
# ==========================================================

PIPELINE = [

    "Applied",

    "AI Reviewed",

    "Shortlisted",

    "Interview Round 1",

    "Interview Round 2",

    "Interview Round 3",

    "Selected",

    "Offer Sent"

]


def get_next_round(round_name):

    mapping = {

        "Interview Round 1": "Interview Round 2",

        "Interview Round 2": "Interview Round 3",

        "Interview Round 3": "Selected"

    }

    return mapping.get(round_name, "Interview Round 1")


# ==========================================================
# Update Functions
# ==========================================================

def promote_candidate(candidate):

    conn = get_connection()

    cursor = conn.cursor()

    current_round = candidate["round_name"]

    next_round = get_next_round(current_round)

    if next_round == "Selected":

        cursor.execute(
            """
            UPDATE interviews

            SET

                round_name=?,

                status='Selected'

            WHERE id=?
            """,

            (

                next_round,

                candidate["interview_id"]

            )

        )

        cursor.execute(
            """
            UPDATE candidates

            SET status='Selected'

            WHERE id=?
            """,

            (

                candidate["candidate_id"],

            )

        )

    else:

        cursor.execute(
            """
            UPDATE interviews

            SET

                round_name=?,

                status='Passed'

            WHERE id=?
            """,

            (

                next_round,

                candidate["interview_id"]

            )

        )

        cursor.execute(
            """
            UPDATE candidates

            SET status=?

            WHERE id=?
            """,

            (

                next_round,

                candidate["candidate_id"]

            )

        )

    conn.commit()

    conn.close()


def hold_candidate(candidate):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE interviews

        SET status='Hold'

        WHERE id=?
        """,

        (

            candidate["interview_id"],

        )

    )

    cursor.execute(
        """
        UPDATE candidates

        SET status='Hold'

        WHERE id=?
        """,

        (

            candidate["candidate_id"],

        )

    )

    conn.commit()

    conn.close()


def reject_candidate(candidate):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE interviews

        SET status='Rejected'

        WHERE id=?
        """,

        (

            candidate["interview_id"],

        )

    )

    cursor.execute(
        """
        UPDATE candidates

        SET status='Rejected'

        WHERE id=?
        """,

        (

            candidate["candidate_id"],

        )

    )

    conn.commit()

    conn.close()


def select_candidate(candidate):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE interviews

        SET

            round_name='Selected',

            status='Selected'

        WHERE id=?
        """,

        (

            candidate["interview_id"],

        )

    )

    cursor.execute(
        """
        UPDATE candidates

        SET status='Selected'

        WHERE id=?
        """,

        (

            candidate["candidate_id"],

        )

    )

    conn.commit()

    conn.close()


# ==========================================================
# Draw Decision Panel
# ==========================================================

def draw_candidate_decision(candidate):

    st.subheader("⚖ Candidate Decision")

    st.info(
        f"""
Current Round : **{candidate['round_name']}**

Current Status : **{candidate['status']}**
"""
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        if st.button(

            "⬆ Promote",

            use_container_width=True,

            type="primary"

        ):

            promote_candidate(candidate)

            st.success(

                "Candidate promoted successfully."

            )

            st.rerun()

    with c2:

        if st.button(

            "🏆 Select",

            use_container_width=True

        ):

            select_candidate(candidate)

            st.balloons()

            st.success(

                "Candidate Selected."

            )

            st.rerun()

    with c3:

        if st.button(

            "⏸ Hold",

            use_container_width=True

        ):

            hold_candidate(candidate)

            st.warning(

                "Candidate moved to Hold."

            )

            st.rerun()

    with c4:

        if st.button(

            "❌ Reject",

            use_container_width=True

        ):

            reject_candidate(candidate)

            st.error(

                "Candidate Rejected."

            )

            st.rerun()

    st.divider()