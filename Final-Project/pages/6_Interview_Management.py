# ==========================================================
# pages/7_Interview_Management.py
# Version 3
# Part 1
# ==========================================================

import streamlit as st

# ---------------- Components ----------------

from components.candidate_filter import (
    draw_candidate_filter
)

from components.pipeline import (
    draw_pipeline
)

from components.candidate_summary import (
    draw_candidate_summary
)

from components.interview_schedule import (
    draw_interview_schedule,
    load_interview
)

from components.ai_email import (
    draw_ai_email
)

from components.interview_notes import (
    draw_interview_notes
)

from components.ai_feedback import (
    draw_ai_feedback
)

from components.candidate_decision import (
    draw_candidate_decision
)

from components.offer_management import (
    draw_offer_management
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(

    page_title="Interview Management",

    page_icon="🎯",

    layout="wide"

)

# ==========================================================
# LOGIN CHECK
# ==========================================================

if "logged_in" not in st.session_state:

    st.switch_page("Login.py")

if not st.session_state.logged_in:

    st.switch_page("Login.py")

if st.session_state.role != "Recruiter":

    st.error(

        "Only Recruiters can access Interview Management."

    )

    st.stop()

# ==========================================================
# SESSION STATE
# ==========================================================

defaults = {

    "selected_candidate": None,

    "selected_candidate_name": None,

    "selected_role": None,

    "selected_interview_id": None,

    "selected_stage_filter": "All",

    "chat_history": [],

    "ai_interviewer": None,

    "ai_resume_data": None,

    "ai_jd_data": None,

    "current_evaluation": None,

    "final_report": None

}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value

# ==========================================================
# CSS
# ==========================================================

st.markdown("""

<style>

.block-container{

    padding-top:1rem;

}

div[data-testid="metric-container"]{

    border-radius:12px;

    padding:15px;

    border:1px solid #E6E6E6;

}

.pipeline-title{

    font-size:18px;

    font-weight:bold;

}

.section{

    margin-top:20px;

}

</style>

""", unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================

st.title("🎯 Interview Management")

st.caption(

    "Manage Interview Scheduling, AI Interview, Evaluation and Candidate Decisions."

)

st.divider()

# ==========================================================
# LOAD CANDIDATE
# ==========================================================

candidate = draw_candidate_filter()

interview = load_interview(

    candidate["interview_id"]

)

# Store globally for AI Interview page

st.session_state.selected_candidate = candidate

st.session_state.selected_candidate_name = candidate["candidate_name"]

st.session_state.selected_role = candidate["role"]

st.session_state.selected_interview_id = candidate["interview_id"]

# ==========================================================
# PIPELINE
# ==========================================================

draw_pipeline(candidate)

# ==========================================================
# SUMMARY
# ==========================================================

draw_candidate_summary(candidate)

# ==========================================================
# SCHEDULER
# ==========================================================

draw_interview_schedule(candidate)


# ==========================================================
# EMAIL
# ==========================================================

draw_ai_email(

    candidate,

    interview

)
# ==========================================================
# INTERVIEW NOTES
# ==========================================================

draw_interview_notes(

    candidate

)

# ==========================================================
# AI INTERVIEW SHAREABLE LINK
# ==========================================================

st.subheader("🔗 Candidate AI Interview Link")

if st.button(
    "🔗 Generate Candidate Link",
    use_container_width=True
):

    interview_id = candidate["interview_id"]

    # Get current app URL
    base_url = st.context.url.split("?")[0]

    # Remove current page name
    base_url = base_url.rsplit("/", 1)[0]

    candidate_link = (
        f"{base_url}/8_AI_Interview?interview_id={interview_id}"
    )

    st.session_state.candidate_interview_link = candidate_link


if "candidate_interview_link" in st.session_state:

    st.success("✅ Candidate interview link generated.")

    st.code(
        st.session_state.candidate_interview_link,
        language="text"
    )

    st.info(
        "📤 Share this link with the candidate. "
        "The candidate can use it to access the AI Interview."
    )


# ==========================================================
# AI INTERVIEW
# ==========================================================

st.subheader("🎤 AI Interview")

left, right = st.columns([4, 1])

with left:

    st.info(
        """
Conduct a complete AI Interview based on the
candidate's Resume and Job Description.

The interview contains Technical,
HR and Behavioural Questions.

Once completed,
AI will automatically generate
an Interview Assessment Report.
"""
    )

with right:

    st.write("")

    st.write("")

    if st.button(

        "▶ Start AI Interview",

        type="primary",

        use_container_width=True

    ):

        st.session_state.selected_candidate_name = (

            candidate["candidate_name"]

        )

        st.session_state.selected_role = (

            candidate["role"]

        )

        st.session_state.selected_interview_id = (

            candidate["interview_id"]

        )

        st.switch_page(

            "pages/7_AI_Interview.py"

        )

st.divider()

# ==========================================================
# AI FEEDBACK
# ==========================================================

draw_ai_feedback(

    candidate

)

# ==========================================================
# RECRUITER DECISION
# ==========================================================

draw_candidate_decision(

    candidate

)

# ==========================================================
# OFFER MANAGEMENT
# ==========================================================

draw_offer_management(

    candidate

)

# ==========================================================
# QUICK DASHBOARD
# ==========================================================

st.subheader("📊 Interview Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(

        "Candidate",

        candidate["candidate_name"]

    )

with c2:

    st.metric(

        "Role",

        candidate["role"]

    )

with c3:

    st.metric(

        "Current Round",

        candidate["round_name"]

    )

with c4:

    st.metric(

        "Status",

        candidate["status"]

    )

st.divider()

# ==========================================================
# INTERVIEW TIMELINE
# ==========================================================

st.subheader("📅 Recruitment Timeline")

timeline = [

    "Applied",

    "AI Reviewed",

    "Shortlisted",

    "Interview Round 1",

    "Interview Round 2",

    "Interview Round 3",

    "Selected",

    "Offer Sent"

]

current = candidate["round_name"]

if candidate["status"] == "Selected":

    current = "Selected"

elif candidate["status"] == "Offer Sent":

    current = "Offer Sent"

for stage in timeline:

    if stage == current:

        st.success(f"🟢 {stage}")

    else:

        st.write(f"⚪ {stage}")

st.divider()

# ==========================================================
# CANDIDATE ACTIONS
# ==========================================================

st.subheader("⚡ Quick Actions")

a1, a2, a3 = st.columns(3)

with a1:

    if st.button(

        "🔄 Refresh Candidate",

        use_container_width=True

    ):

        st.rerun()

with a2:

    if st.button(

        "📂 Open Resume",

        use_container_width=True,

        disabled=True,

        help="Integrate resume viewer."

    ):

        pass

with a3:

    if st.button(

        "🏠 Back Dashboard",

        use_container_width=True

    ):

        st.switch_page(

            "Dashboard.py"

        )

st.divider()
# ==========================================================
# pages/7_Interview_Management.py
# Part 3 (Final)
# ==========================================================

# ==========================================================
# AI INTERVIEW STATUS
# ==========================================================

st.subheader("🤖 AI Interview Status")

if st.session_state.final_report:

    st.success("✅ AI Interview completed in this session.")

elif candidate["status"] in [

    "Selected",

    "Offer Sent"

]:

    st.success(

        "Candidate has already completed AI Interview."

    )

else:

    st.info(

        "AI Interview has not been completed yet."

    )

st.divider()

# ==========================================================
# COMPLETE CANDIDATE PROFILE
# ==========================================================

with st.expander(

    "📋 Candidate Information",

    expanded=False

):

    st.write(

        f"**Candidate ID :** {candidate['candidate_id']}"

    )

    st.write(

        f"**Interview ID :** {candidate['interview_id']}"

    )

    st.write(

        f"**Candidate Name :** {candidate['candidate_name']}"

    )

    st.write(

        f"**Applied Role :** {candidate['role']}"

    )

    st.write(

        f"**Interview Round :** {candidate['round_name']}"

    )

    st.write(

        f"**Current Status :** {candidate['status']}"

    )

st.divider()

# ==========================================================
# SYSTEM INFORMATION
# ==========================================================

with st.expander(

    "🖥 System Information",

    expanded=False

):

    st.code(

f"""
Current Candidate

{candidate['candidate_name']}

Interview ID

{candidate['interview_id']}

Current Round

{candidate['round_name']}

Current Status

{candidate['status']}

Current Filter

{st.session_state.selected_stage_filter}
"""

    )

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(

"""
AI Recruitment & Talent Acquisition Copilot

Interview Management Module

Version 3
"""
)

# ==========================================================
# OPTIONAL RESET
# ==========================================================

def reset_ai_session():

    keys = [

        "ai_interviewer",

        "chat_history",

        "current_evaluation",

        "final_report",

        "ai_resume_data",

        "ai_jd_data"

    ]

    for key in keys:

        if key in st.session_state:

            st.session_state[key] = None

# ==========================================================
# RESET BUTTON
# ==========================================================

with st.sidebar:

    st.markdown("## Utilities")

    if st.button(

        "♻ Reset AI Interview Session",

        use_container_width=True

    ):

        reset_ai_session()

        st.success(

            "AI Interview session cleared."

        )

        st.rerun()

# ==========================================================
# END OF FILE
# ==========================================================