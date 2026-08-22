import streamlit as st
from styles.theme import inject_global_styles
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from components.header import page_header
from components.charts import gauge_chart
from components.clipboard import copy_to_clipboard_button
from data import mock_data as data
from data import jd_store
from data import candidate_store
from services import ai_service
from utils.text_extraction import extract_text
from utils.duplicate_detection import check_duplicate

from utils.auth import require_login

st.set_page_config(page_title="Resume Analyzer | YourTalentPilot", layout="wide")

inject_global_styles()
require_login()
render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()
page_header("Resume Analyzer", "Upload a resume and match it against a job description with AI")

if not ai_service.is_configured():
    st.warning(
        "AI matching isn't active yet. Add your Gemini API key to a `.env` file "
        "in the project root (see `.env.example`) and restart the app. "
        "Showing demo mode below in the meantime.",
    )

all_jds = jd_store.get_all()

col_upload, col_jd = st.columns([1, 1])
with col_upload:
    uploaded = st.file_uploader("Upload resume", type=["pdf", "docx"])
    pasted_text = st.text_area(
        "Or paste resume text manually",
        placeholder="If your PDF is a designed/graphic resume (e.g. from Canva), "
                    "text extraction may fail — paste the text here instead.",
        height=100,
    )
with col_jd:
    if all_jds:
        jd_labels = [f"{jd['title']} · {jd['department']}" for jd in all_jds]
        jd_index = st.selectbox("Match against Job Description", range(len(jd_labels)),
                                 format_func=lambda i: jd_labels[i])
        selected_jd = all_jds[jd_index]
    else:
        st.info("No job descriptions yet — create one in Job Descriptions first.")
        selected_jd = None

analyze_clicked = st.button(
    "Analyze Resume", type="primary",
    disabled=not ((uploaded or pasted_text.strip()) and selected_jd and ai_service.is_configured()),
)

if analyze_clicked and (uploaded or pasted_text.strip()) and selected_jd:
    resume_text = None
    if pasted_text.strip():
        resume_text = pasted_text.strip()
    elif uploaded:
        with st.spinner("Extracting resume text..."):
            try:
                resume_text = extract_text(uploaded)
            except ValueError as e:
                st.error(
                    f"{e} Try pasting the resume text into the box above instead, "
                    f"then click 'Analyze Resume' again."
                )
                resume_text = None

    if resume_text:
        with st.spinner("Running AI analysis..."):
            try:
                profile = ai_service.parse_resume_profile(resume_text)
                match = ai_service.match_resume_to_jd(resume_text, selected_jd["description"])

                new_entry = {
                    "name": profile.get("name"), "email": profile.get("email"),
                    "phone": profile.get("phone"), "resume_text": resume_text,
                }
                st.session_state.setdefault("analyzed_resumes", [])
                duplicates = check_duplicate(new_entry, st.session_state["analyzed_resumes"])
                st.session_state["analyzed_resumes"].append(new_entry)

                st.session_state["resume_analysis"] = {
                    "profile": profile, "match": match, "jd": selected_jd,
                    "resume_text": resume_text, "duplicates": duplicates,
                }
            except ai_service.AIServiceError as e:
                st.error(f"AI analysis failed: {e}")

result = st.session_state.get("resume_analysis")

# ---- Real AI result ----
if result:
    profile, match, jd = result["profile"], result["match"], result["jd"]

    if result.get("duplicates"):
        with st.container():
            st.markdown('<div class="card" style="background-color:#FFFBEB; border-color:#FDE68A;">', unsafe_allow_html=True)
            st.markdown("**Possible Duplicate Application**")
            for d in result["duplicates"]:
                st.markdown(f"- Matches **{d['match_name']}** — {', '.join(d['reasons'])}")
            st.markdown('</div>', unsafe_allow_html=True)
        st.write("")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    top_left, top_right = st.columns([3, 1])
    with top_left:
        st.markdown(f"### {profile.get('name') or 'Candidate'}")
        st.caption(f"Matched against **{jd['title']}**  ·  {profile.get('location', '')}")
        st.markdown(
            f"{profile.get('email', '—')}  &nbsp;&nbsp; {profile.get('phone', '—')}",
            unsafe_allow_html=True,
        )
    with top_right:
        score = match.get("match_score", 0)
        label = "Strong" if score >= 80 else "Moderate" if score >= 60 else "Weak"
        # Match badge colors now also vary by label (this used to always
        # render green regardless of Strong/Moderate/Weak - a small
        # pre-existing inconsistency fixed here while updating the palette)
        MATCH_BADGE_STYLES = {
            "Strong": ("#E4EDE1", "#4C6B49"),
            "Moderate": ("#F3E9D4", "#755729"),
            "Weak": ("#F5E1DA", "#A54A34"),
        }
        match_bg, match_text = MATCH_BADGE_STYLES[label]
        st.markdown(
            f"<div style='text-align:right; padding-top:10px;'>"
            f"<span style='background:{match_bg}; color:{match_text}; padding:4px 12px; "
            f"border-radius:20px; font-size:13px; font-weight:600;'>{label} Match</span></div>",
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**AI Match Score**")
        fig = gauge_chart(match.get("match_score", 0), title="")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Skills**")
        st.write("")
        matched = " ".join(
            f"<span style='background:#E4EDE1;color:#4C6B49;padding:4px 10px;border-radius:16px;"
            f"font-size:13px;margin-right:6px;display:inline-block;margin-bottom:6px;'>{s}</span>"
            for s in match.get("matched_skills", [])
        )
        missing = " ".join(
            f"<span style='background:#F5E1DA;color:#A54A34;padding:4px 10px;border-radius:16px;"
            f"font-size:13px;margin-right:6px;display:inline-block;margin-bottom:6px;'>{s}</span>"
            for s in match.get("missing_skills", [])
        )
        st.markdown(f"Matched<br>{matched or '<i>None identified</i>'}", unsafe_allow_html=True)
        st.write("")
        st.markdown(f"Missing<br>{missing or '<i>None identified</i>'}", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Experience**")
        for exp in profile.get("experience", []):
            st.markdown(f"**{exp.get('title', '')}** — {exp.get('company', '')}")
            st.caption(exp.get("duration", ""))
            st.write(exp.get("desc", ""))
            st.write("")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Education**")
        for edu in profile.get("education", []):
            st.markdown(f"**{edu.get('degree', '')}**")
            st.caption(f"{edu.get('school', '')} · {edu.get('year', '')}")
        st.write("")
        if profile.get("certifications"):
            st.markdown("**Certifications**")
            for cert in profile["certifications"]:
                st.write(cert)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**AI Summary**")
    st.write(match.get("summary", ""))
    if match.get("strengths"):
        st.markdown("**Strengths:** " + " · ".join(match["strengths"]))
    if match.get("concerns"):
        st.markdown("**Concerns to probe in interview:** " + " · ".join(match["concerns"]))
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Recruiter Notes**")
        st.text_area("Notes", placeholder="Add your notes about this candidate...", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Actions**")

        def _save_candidate(stage, note):
            candidate_store.add_or_update({
                "Candidate": profile.get("name") or "Unnamed Candidate",
                "Role": jd["title"],
                "Department": jd["department"],
                "Match": match.get("match_score", 0),
                "Stage": stage,
                "Skills": ", ".join(profile.get("skills", [])) or "—",
                "Applied": "Just now",
            }, note=note)

        if st.button("Shortlist Candidate", use_container_width=True):
            _save_candidate("Shortlisted", "Shortlisted directly from Resume Analyzer.")
            st.success(f"{profile.get('name','Candidate')} added to Candidate Screening as Shortlisted.")
        if st.button("Schedule Interview", use_container_width=True):
            _save_candidate("Interview", "Moved to interview directly from Resume Analyzer.")
            st.success(f"{profile.get('name','Candidate')} added to Candidate Screening in Interview stage.")
        if st.button("Reject", use_container_width=True):
            _save_candidate("Rejected", "Rejected directly from Resume Analyzer.")
            st.success(f"{profile.get('name','Candidate')} added to Candidate Screening as Rejected.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- AI Email Generator ----
    st.write("")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**AI Email Generator**")

    st.markdown('<div class="subsection">', unsafe_allow_html=True)
    st.markdown('<div class="subsection-label">Prompt</div>', unsafe_allow_html=True)
    ecol1, ecol2, ecol3 = st.columns([1.2, 1, 1])
    with ecol1:
        email_type = st.selectbox("Email Type", ["Interview Invitation", "Rejection", "Offer Letter"])
    with ecol2:
        email_tone = st.selectbox("Tone", ["Professional", "Warm", "Formal", "Casual"])
    with ecol3:
        st.write("")
        gen_email_clicked = st.button("Generate Email", use_container_width=True, disabled=not ai_service.is_configured())
    st.markdown('</div>', unsafe_allow_html=True)

    if gen_email_clicked:
        with st.spinner("Drafting email..."):
            try:
                email_text = ai_service.generate_email(
                    profile.get("name") or "Candidate", jd["title"], email_type, email_tone,
                )
                st.session_state["generated_email"] = {"candidate": profile.get("name"), "text": email_text}
            except ai_service.AIServiceError as e:
                st.error(f"Email generation failed: {e}")

    generated = st.session_state.get("generated_email")
    if generated and generated["candidate"] == profile.get("name"):
        st.markdown('<div class="subsection">', unsafe_allow_html=True)
        label_col, copy_col = st.columns([3, 1])
        with label_col:
            st.markdown('<div class="subsection-label">Generated Email</div>', unsafe_allow_html=True)
        with copy_col:
            copy_to_clipboard_button(generated["text"], key=f"resume_email_{profile.get('name','candidate')}")
        st.text_area("Draft (copy and send from your email client)", value=generated["text"], height=220, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="ai-chat-box">', unsafe_allow_html=True)
    st.markdown('<span class="ai-chat-badge">AI ASSISTANT</span>', unsafe_allow_html=True)
    st.markdown("### Chat about this candidate")
    st.caption("Ask anything about this specific resume — the AI answers only from what's in it.")

    chat_key = f"resume_chat_{profile.get('name', 'candidate')}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    for msg in st.session_state[chat_key]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Note: intentionally st.text_input + st.form here, not st.chat_input.
    # st.chat_input always renders fixed/pinned to the bottom of the browser
    # viewport regardless of where it's placed in the layout - it can't be
    # made to scroll with the page. A form field gives the same "type and
    # press Enter (or click Send)" behavior while staying in normal page flow.
    with st.form(key=f"{chat_key}_form", clear_on_submit=True, border=False):
        form_col, btn_col = st.columns([5, 1])
        with form_col:
            user_question = st.text_input(
                "Ask about this candidate",
                placeholder="e.g. Does this candidate have leadership experience?",
                label_visibility="collapsed",
            )
        with btn_col:
            submitted = st.form_submit_button("Send", use_container_width=True)

    if submitted and user_question.strip():
        question = user_question.strip()
        st.session_state[chat_key].append({"role": "user", "content": question})
        with st.spinner("Thinking..."):
            try:
                answer = ai_service.resume_chat(
                    result.get("resume_text", ""), jd["description"],
                    st.session_state[chat_key][:-1], question,
                )
            except ai_service.AIServiceError as e:
                answer = f"Sorry, I couldn't answer that: {e}"
        st.session_state[chat_key].append({"role": "assistant", "content": answer})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---- Demo mode fallback (no API key configured) ----
elif not ai_service.is_configured():
    st.write("")
    st.caption("Demo preview using sample data — connect your API key to analyze real resumes.")
    r = data.SAMPLE_RESUME
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"### {r['name']}")
    st.caption(f"Applied for **{r['role_applied']}**  ·  {r['location']}")
    st.markdown('</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        fig = gauge_chart(r["ats_score"], title="")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with col2:
        st.write(r["ai_summary"])

else:
    st.markdown(
        '<div class="empty-state"><div>Upload a resume and select a job description, then click "Analyze Resume".</div></div>',
        unsafe_allow_html=True,
    )

render_global_chat()
