# ==========================================================
# components/interview/pipeline.py
# ==========================================================

import streamlit as st

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


STATUS_COLOR = {

    "completed": "#22c55e",

    "current": "#3b82f6",

    "pending": "#cbd5e1"

}


def get_current_pipeline_stage(candidate):

    """
    Returns current stage index.
    """

    status = candidate["status"]

    round_name = candidate["round_name"]


    # ----------------------------
    # Status Based
    # ----------------------------

    if status == "Applied":

        return 0

    if status == "AI Reviewed":

        return 1

    if status == "Shortlisted":

        return 2

    if status == "Selected":

        return 6

    if status == "Offer Sent":

        return 7


    # ----------------------------
    # Round Based
    # ----------------------------

    if round_name == "Interview Round 1":

        return 3

    if round_name == "Interview Round 2":

        return 4

    if round_name == "Interview Round 3":

        return 5


    return 0


# ==========================================================
# HTML Card
# ==========================================================

def stage_card(title, color):

    return f"""
    <div style="
        background:{color};
        color:white;
        border-radius:12px;
        padding:12px;
        text-align:center;
        font-weight:600;
        min-height:70px;
        display:flex;
        justify-content:center;
        align-items:center;
        font-size:14px;
    ">
        {title}
    </div>
    """


# ==========================================================
# Draw Pipeline
# ==========================================================

def draw_pipeline(candidate):

    st.subheader("📈 Recruitment Pipeline")

    current = get_current_pipeline_stage(candidate)

    cols = st.columns(len(PIPELINE))

    for i, stage in enumerate(PIPELINE):

        if i < current:

            color = STATUS_COLOR["completed"]

        elif i == current:

            color = STATUS_COLOR["current"]

        else:

            color = STATUS_COLOR["pending"]

        with cols[i]:

            st.markdown(

                stage_card(stage, color),

                unsafe_allow_html=True

            )

    st.write("")

    progress = ((current + 1) / len(PIPELINE)) * 100

    st.progress(progress / 100)

    st.caption(

        f"Current Stage : {PIPELINE[current]}"

    )


# ==========================================================
# Next Stage Utility
# ==========================================================

def next_stage(candidate):

    current = get_current_pipeline_stage(candidate)

    if current >= len(PIPELINE) - 1:

        return PIPELINE[-1]

    return PIPELINE[current + 1]


# ==========================================================
# Previous Stage Utility
# ==========================================================

def previous_stage(candidate):

    current = get_current_pipeline_stage(candidate)

    if current <= 0:

        return PIPELINE[0]

    return PIPELINE[current - 1]