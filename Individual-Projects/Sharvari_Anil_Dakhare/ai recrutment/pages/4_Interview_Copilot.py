import pandas as pd
import streamlit as st
from styles.theme import inject_global_styles
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from components.header import page_header
from components.tables import styled_table
from data import mock_data as data
from data import jd_store
from data import candidate_store
from services import ai_service

from utils.auth import require_login

st.set_page_config(page_title="Interview Copilot | YourTalentPilot", layout="wide")

inject_global_styles()
require_login()
render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()
page_header("Interview Copilot", "Prepare and evaluate interviews with AI assistance")

if not ai_service.is_configured():
    st.warning(
        "AI question generation needs a Gemini API key. Add one to your `.env` "
        "file and restart the app to enable it — showing sample questions below "
        "in the meantime.",
    )

# ---- Build the live schedule: seed demo rows + any candidate you've moved to Interview ----
seed_schedule = data.INTERVIEW_SCHEDULE.copy()
live_candidates = candidate_store.get_all_df()
in_interview = live_candidates[live_candidates["Stage"] == "Interview"] if len(live_candidates) else live_candidates

extra_rows = []
for _, c in in_interview.iterrows():
    if c["Candidate"] not in seed_schedule["Candidate"].values:
        extra_rows.append({
            "Candidate": c["Candidate"], "Role": c["Role"], "Type": "Technical",
            "Interviewer": "Unassigned", "Time": "To be scheduled",
        })

schedule = pd.concat([seed_schedule, pd.DataFrame(extra_rows)], ignore_index=True) if extra_rows else seed_schedule

# ---- Upcoming schedule ----
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("**Interview Schedule**")
if len(schedule):
    styled_table(schedule)
else:
    st.caption("No interviews scheduled yet. Move a candidate to the Interview stage in Candidate Screening to see them here.")
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ---- Candidate + question generator ----
left, right = st.columns([1, 2])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Select Interview**")
    if len(schedule):
        candidate = st.selectbox("Candidate", schedule["Candidate"])
        row = schedule[schedule["Candidate"] == candidate].iloc[0]
        st.caption(f"{row['Role']}  ·  {row['Type']} Round")
        st.caption(f"Interviewer: {row['Interviewer']}  ·  {row['Time']}")
        question_type = st.radio("Question Type", ["Technical", "HR Questions", "Coding"])
        generate = st.button("Generate Questions", use_container_width=True)
    else:
        candidate, row, question_type, generate = None, None, None, False
        st.info("No candidates in the Interview stage yet.")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if candidate:
        st.markdown(f"**{question_type} Questions for {candidate}**")
        if generate:
            if ai_service.is_configured():
                with st.spinner("Analyzing candidate profile and generating questions..."):
                    try:
                        matching_jd = next((jd for jd in jd_store.get_all() if jd["title"] == row["Role"]), None)
                        jd_text = matching_jd["description"] if matching_jd else ""
                        result = ai_service.generate_interview_questions(candidate, row["Role"], question_type, jd_text)
                        st.session_state["interview_questions"] = {
                            "candidate": candidate, "type": question_type,
                            "questions": result.get("questions", []),
                        }
                    except ai_service.AIServiceError as e:
                        st.error(f"AI question generation failed: {e}")
            else:
                st.session_state["interview_questions"] = {
                    "candidate": candidate, "type": question_type,
                    "questions": data.INTERVIEW_QUESTIONS[question_type],
                }

        stored = st.session_state.get("interview_questions")
        if stored and stored["candidate"] == candidate and stored["type"] == question_type:
            for i, q in enumerate(stored["questions"], start=1):
                st.markdown(f"{i}. {q}")
        else:
            st.markdown(
                '<div class="empty-state"><div>Click "Generate Questions" to prepare tailored interview questions.</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ---- Evaluation ----
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("**Evaluation**")

e1, e2, e3 = st.columns(3)
e1.slider("Technical Skills", 1, 5, 3)
e2.slider("Communication", 1, 5, 3)
e3.slider("Culture Fit", 1, 5, 3)

st.text_area("Interview Notes", placeholder="Record observations from the interview...")

recommendation = st.radio(
    "Recommendation", ["Strong Hire", "Hire", "Neutral", "No Hire"], horizontal=True
)
st.button("Submit Evaluation", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

render_global_chat()
