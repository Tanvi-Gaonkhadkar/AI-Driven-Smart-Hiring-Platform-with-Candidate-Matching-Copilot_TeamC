# ==========================================================
# components/interview/interview_schedule.py
# ==========================================================

import datetime
import sqlite3
import uuid

import streamlit as st

DB_PATH = "database/recruitment.db"


# ==========================================================
# Database
# ==========================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================================
# Generate Meeting Link
# ==========================================================

def generate_meeting_link():

    code = (
        f"{uuid.uuid4().hex[:3]}-"
        f"{uuid.uuid4().hex[:4]}-"
        f"{uuid.uuid4().hex[:3]}"
    )

    return f"https://meet.google.com/{code}"


# ==========================================================
# Load Interview
# ==========================================================

def load_interview(interview_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            interviewer,

            interview_date,

            interview_time,

            meeting_mode,

            meeting_link,

            round_name,

            status

        FROM interviews

        WHERE id=?

        """,
        (interview_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:

        return {

            "interviewer": "",

            "date": "",

            "time": "",

            "mode": "Online",

            "link": "",

            "round": "Interview Round 1",

            "status": "Shortlisted"

        }

    return {

        "interviewer": row[0],

        "date": row[1],

        "time": row[2],

        "mode": row[3],

        "link": row[4],

        "round": row[5],

        "status": row[6]

    }


# ==========================================================
# Save Interview
# ==========================================================

def update_interview(

        interview_id,

        interviewer,

        interview_date,

        interview_time,

        meeting_mode,

        meeting_link

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE interviews

        SET

            interviewer=?,

            interview_date=?,

            interview_time=?,

            meeting_mode=?,

            meeting_link=?

        WHERE id=?
        """,

        (

            interviewer,

            interview_date,

            interview_time,

            meeting_mode,

            meeting_link,

            interview_id

        )

    )

    conn.commit()

    conn.close()


# ==========================================================
# Draw Interview Scheduler
# ==========================================================

def draw_interview_schedule(candidate):

    interview = load_interview(

        candidate["interview_id"]

    )

    st.subheader("📅 Interview Scheduling")

    with st.form(

        f"schedule_{candidate['interview_id']}"

    ):

        col1, col2 = st.columns(2)

        with col1:

            interviewer = st.text_input(

                "Interviewer",

                value=interview["interviewer"] or ""

            )

            mode = st.selectbox(

                "Interview Mode",

                [

                    "Online",

                    "Offline"

                ],

                index=0 if interview["mode"] != "Offline" else 1

            )

        with col2:

            today = datetime.date.today()

            try:

                interview_date = datetime.date.fromisoformat(
                    interview["date"]
                )

            except Exception:

                interview_date = today

            # Prevent Streamlit error
            if interview_date < today:

                interview_date = today

            date = st.date_input(

                "Interview Date",

                value=interview_date,

                min_value=today

            )

            try:

                h, m, *_ = map(

                    int,

                    str(interview["time"]).split(":")

                )

                interview_time = datetime.time(

                    h,

                    m

                )

            except Exception:

                interview_time = datetime.time(

                    10,

                    0

                )

            time = st.time_input(

                "Interview Time",

                value=interview_time

            )

        meeting_link = st.text_input(

            "Meeting Link",

            value=st.session_state.get(

                "generated_link",

                interview["link"] or ""

            )

        )
        if "generated_link" in st.session_state:

            meeting_link = st.session_state.generated_link

        c1, c2 = st.columns(2)

        with c1:

            auto_link = st.form_submit_button(

                "🔗 Generate Link",

                use_container_width=True

            )

        with c2:

            update = st.form_submit_button(

                "💾 Save Schedule",

                type="primary",

                use_container_width=True

            )

        if auto_link:

            st.session_state.generated_link = generate_meeting_link()

        if "generated_link" in st.session_state:

            meeting_link = st.session_state.generated_link

            st.success(

                f"Generated:\n\n{meeting_link}"

            )

        if update:

            if meeting_link.strip() == "":

                meeting_link = generate_meeting_link()

            update_interview(

                candidate["interview_id"],

                interviewer,

                str(date),

                str(time),

                mode,

                meeting_link

            )

            if "generated_link" in st.session_state:

                del st.session_state.generated_link

            st.success(

                "Interview schedule updated successfully."

            )

            st.rerun()

    if interview["link"]:

        st.info(

            f"🔗 Meeting Link\n\n{interview['link']}"

        )

    st.divider()