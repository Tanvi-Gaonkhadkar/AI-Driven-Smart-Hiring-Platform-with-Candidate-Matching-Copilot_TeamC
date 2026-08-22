# ==========================================================
# components/interview/candidate_summary.py
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
# Load Candidate Details
# ==========================================================

def load_candidate_details(candidate_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            id,

            name,

            email,

            phone,

            role_applied,

            experience,

            skills,

            resume_path,

            status

        FROM candidates

        WHERE id=?

        """,
        (candidate_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return {

        "candidate_id": row[0],

        "name": row[1],

        "email": row[2],

        "phone": row[3],

        "role": row[4],

        "experience": row[5],

        "skills": row[6],

        "resume_path": row[7],

        "status": row[8]

    }


# ==========================================================
# Load Recruiter Scores
# ==========================================================

def load_interview_scores(interview_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            technical_score,

            communication_score,

            recommendation,

            feedback

        FROM interviews

        WHERE id=?

        """,
        (interview_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:

        return {

            "technical": 0,

            "communication": 0,

            "recommendation": "",

            "feedback": ""

        }

    return {

        "technical": row[0] or 0,

        "communication": row[1] or 0,

        "recommendation": row[2] or "",

        "feedback": row[3] or ""

    }


# ==========================================================
# Candidate Summary UI
# ==========================================================

def draw_candidate_summary(candidate):

    details = load_candidate_details(

        candidate["candidate_id"]

    )

    scores = load_interview_scores(

        candidate["interview_id"]

    )

    st.subheader("👤 Candidate Summary")

    left, right = st.columns([3, 2])

    with left:

        st.markdown(
            f"## {details['name']}"
        )

        st.write(
            f"**Role Applied :** {details['role']}"
        )

        st.write(
            f"**Experience :** {details['experience']}"
        )

        st.write(
            f"**Email :** {details['email']}"
        )

        st.write(
            f"**Phone :** {details['phone']}"
        )

        st.write(
            f"**Current Stage :** {candidate['round_name']}"
        )

        st.write(
            f"**Status :** {candidate['status']}"
        )

        st.write("")

        st.markdown("### Skills")

        if details["skills"]:

            skills = [

                s.strip()

                for s in

                details["skills"].split(",")

                if s.strip()

            ]

            cols = st.columns(3)

            index = 0

            for skill in skills:

                with cols[index]:

                    st.success(skill)

                index += 1

                if index == 3:

                    cols = st.columns(3)

                    index = 0

        else:

            st.info("No skills available.")

    with right:

        st.metric(

            "Technical Score",

            f"{scores['technical']}"

        )

        st.metric(

            "Communication",

            f"{scores['communication']}"

        )

        average = round(

            (

                scores["technical"]

                +

                scores["communication"]

            ) / 2

        )

        # st.metric(

        #     "Overall",

        #     f"{average}%"

        # )

        if average >= 85:

            st.success("Excellent Candidate")

        elif average >= 70:

            st.info("Good Candidate")

        elif average >= 50:

            st.warning("Average Candidate")

        # else:

        #     st.error("Needs Improvement")

    st.divider()