# ==========================================================
# components/interview/ai_feedback.py
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
# Load AI Summary
# ==========================================================

def load_ai_summary(interview_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            technical_score,

            communication_score,

            confidence_score,

            overall_score,

            recommendation,

            summary,

            created_at

        FROM ai_interview_summary

        WHERE interview_id=?

        ORDER BY id DESC

        LIMIT 1
        """,
        (interview_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return {

        "technical": row[0],

        "communication": row[1],

        "confidence": row[2],

        "overall": row[3],

        "recommendation": row[4],

        "summary": row[5],

        "created_at": row[6]

    }


# ==========================================================
# Recommendation Color
# ==========================================================

def show_recommendation(text):

    recommendation = text.lower()

    if recommendation.startswith("recommend"):

        st.success(f"✅ {text}")

    elif recommendation.startswith("strong"):

        st.success(f"✅ {text}")

    elif "hold" in recommendation:

        st.warning(f"⚠ {text}")

    elif "reject" in recommendation:

        st.error(f"❌ {text}")

    else:

        st.info(text)


# ==========================================================
# Draw AI Feedback
# ==========================================================

def draw_ai_feedback(candidate):

    st.subheader("🤖 AI Interview Feedback")

    report = load_ai_summary(

        candidate["interview_id"]

    )

    if report is None:

        st.info(
            """
No AI Interview report available.

Complete the AI Interview first to
view detailed AI Assessment.
"""
        )

        st.divider()

        return

    # ------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(

            "Technical",

            f"{report['technical']}%"

        )

    with c2:

        st.metric(

            "Communication",

            f"{report['communication']}%"

        )

    with c3:

        st.metric(

            "Confidence",

            f"{report['confidence']}%"

        )

    with c4:

        st.metric(

            "Overall",

            f"{report['overall']}%"

        )

    st.write("")

    st.markdown("### Recommendation")

    show_recommendation(

        report["recommendation"]

    )

    st.write("")

    st.markdown("### AI Summary")

    st.info(

        report["summary"]

    )

    st.caption(

        f"Generated : {report['created_at']}"

    )

    st.write("")

    with st.expander(

        "📊 Assessment Breakdown",

        expanded=False

    ):

        technical = report["technical"]

        communication = report["communication"]

        confidence = report["confidence"]

        overall = report["overall"]

        st.progress(technical / 100)

        st.caption(

            f"Technical : {technical}%"

        )

        st.progress(communication / 100)

        st.caption(

            f"Communication : {communication}%"

        )

        st.progress(confidence / 100)

        st.caption(

            f"Confidence : {confidence}%"

        )

        st.progress(overall / 100)

        st.caption(

            f"Overall : {overall}%"

        )

    st.divider()