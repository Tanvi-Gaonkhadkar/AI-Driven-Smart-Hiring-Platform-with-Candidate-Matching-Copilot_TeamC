# ==========================================================
# components/interview/interview_notes.py
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
# Load Notes
# ==========================================================

def load_notes(interview_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            technical_notes,

            communication_notes,

            overall_notes,

            feedback,

            technical_score,

            communication_score,

            recommendation

        FROM interviews

        WHERE id=?

        """,
        (interview_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:

        return {

            "technical_notes": "",

            "communication_notes": "",

            "overall_notes": "",

            "feedback": "",

            "technical_score": 0,

            "communication_score": 0,

            "recommendation": ""

        }

    return {

        "technical_notes": row[0] or "",

        "communication_notes": row[1] or "",

        "overall_notes": row[2] or "",

        "feedback": row[3] or "",

        "technical_score": row[4] or 0,

        "communication_score": row[5] or 0,

        "recommendation": row[6] or ""

    }


# ==========================================================
# Save Notes
# ==========================================================

def save_notes(

        interview_id,

        technical_notes,

        communication_notes,

        overall_notes,

        recruiter_feedback,

        technical_score,

        communication_score,

        recommendation

):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE interviews

        SET

            technical_notes=?,

            communication_notes=?,

            overall_notes=?,

            feedback=?,

            technical_score=?,

            communication_score=?,

            recommendation=?

        WHERE id=?
        """,

        (

            technical_notes,

            communication_notes,

            overall_notes,

            recruiter_feedback,

            technical_score,

            communication_score,

            recommendation,

            interview_id

        )

    )

    conn.commit()

    conn.close()


# ==========================================================
# Draw Notes
# ==========================================================

def draw_interview_notes(candidate):

    notes = load_notes(

        candidate["interview_id"]

    )

    st.subheader("📝 Interview Notes")

    with st.form(

        f"notes_{candidate['interview_id']}"

    ):

        technical_notes = st.text_area(

            "Technical Notes",

            value=notes["technical_notes"],

            height=120

        )

        communication_notes = st.text_area(

            "Communication Notes",

            value=notes["communication_notes"],

            height=120

        )

        overall_notes = st.text_area(

            "Overall Notes",

            value=notes["overall_notes"],

            height=120

        )

        recruiter_feedback = st.text_area(

            "Recruiter Feedback",

            value=notes["feedback"],

            height=120

        )

        c1, c2 = st.columns(2)

        with c1:

            technical_score = st.slider(

                "Technical Score",

                0,

                100,

                int(notes["technical_score"])

            )

        with c2:

            communication_score = st.slider(

                "Communication Score",

                0,

                100,

                int(notes["communication_score"])

            )

        average = round(

            (

                technical_score +

                communication_score

            ) / 2

        )

        # st.metric(

        #     "Overall Score",

        #     f"{average}%"

        # )

        if average >= 85:

            recommendation = "Strong Hire"

            st.success(recommendation)

        elif average >= 70:

            recommendation = "Hire"

            st.info(recommendation)

        elif average >= 50:

            recommendation = "Hold"

            st.warning(recommendation)

        else:

            recommendation = ""

            # st.error(recommendation)

        save = st.form_submit_button(

            "💾 Save Notes",

            type="primary",

            use_container_width=True

        )

        if save:

            save_notes(

                candidate["interview_id"],

                technical_notes,

                communication_notes,

                overall_notes,

                recruiter_feedback,

                technical_score,

                communication_score,

                recommendation

            )

            st.success(

                "Interview notes updated successfully."

            )

            st.rerun()

    st.divider()