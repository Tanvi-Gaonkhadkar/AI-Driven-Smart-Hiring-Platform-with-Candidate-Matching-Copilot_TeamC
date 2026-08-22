import streamlit as st
from styles.theme import inject_global_styles
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from components.header import page_header
from data import jd_store
from data import candidate_store
from services import ai_service

from utils.auth import require_login

st.set_page_config(page_title="Job Descriptions | YourTalentPilot", layout="wide")

inject_global_styles()
require_login()
render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()
page_header("Job Description Manager", "Create roles and let AI extract the key requirements")

if not ai_service.is_configured():
    st.warning(
        "AI features aren't active yet. Add your Gemini API key to a `.env` file "
        "in the project root (see `.env.example`) and restart the app to enable "
        "AI requirement extraction.",
    )

# ---- Create new JD ----
with st.expander("Create New Job Description", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Job Title", placeholder="e.g. Senior Backend Developer")
        department = st.selectbox("Department", ["Engineering", "AI/ML", "Sales", "Design", "Operations"])
    with col2:
        level = st.selectbox("Experience Level", ["Entry", "Mid", "Senior", "Lead"])
        employment_type = st.selectbox("Employment Type", ["Full-time", "Part-time", "Contract", "Internship"])

    description = st.text_area(
        "Job Description",
        placeholder="Paste or write the full job description here...",
        height=180,
    )

    extract_col, _ = st.columns([1, 3])
    with extract_col:
        extract_clicked = st.button("Extract Requirements with AI", use_container_width=True)

    if extract_clicked:
        if not description.strip():
            st.error("Write a job description first, then extract requirements.")
        elif not ai_service.is_configured():
            st.error("AI isn't configured yet — see the setup notice above.")
        else:
            with st.spinner("Analyzing job description..."):
                try:
                    result = ai_service.extract_jd_requirements(description)
                    st.session_state["jd_extracted"] = result
                except ai_service.AIServiceError as e:
                    st.error(f"AI extraction failed: {e}")

    extracted = st.session_state.get("jd_extracted")
    required_skills, nice_to_have_skills = [], []

    if extracted:
        st.markdown("**AI-extracted requirements** — edit before saving if needed:")
        c1, c2 = st.columns(2)
        with c1:
            required_skills = st.multiselect(
                "Required Skills", options=extracted.get("required_skills", []),
                default=extracted.get("required_skills", []),
            )
        with c2:
            nice_to_have_skills = st.multiselect(
                "Nice-to-have Skills", options=extracted.get("nice_to_have_skills", []),
                default=extracted.get("nice_to_have_skills", []),
            )
        if extracted.get("key_responsibilities"):
            st.caption("Key responsibilities identified: " + " · ".join(extracted["key_responsibilities"]))

    st.write("")
    if st.button("Save Job Description", type="primary", use_container_width=True):
        if not title.strip() or not description.strip():
            st.error("Job title and description are required.")
        else:
            jd_store.add(
                title=title, department=department, level=level,
                employment_type=employment_type, description=description,
                required_skills=required_skills, nice_to_have_skills=nice_to_have_skills,
            )
            st.session_state.pop("jd_extracted", None)
            st.success(f"'{title}' saved.")
            st.rerun()

st.write("")
st.markdown("#### Open Roles")

all_jds = jd_store.get_all()
if not all_jds:
    st.markdown(
        '<div class="empty-state"><div>No job descriptions yet — create one above.</div></div>',
        unsafe_allow_html=True,
    )
else:
    for jd in all_jds:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        top_left, top_right = st.columns([5, 1])
        with top_left:
            st.markdown(f"### {jd['title']}")
            st.caption(f"{jd['department']} · {jd['level']} · {jd['employment_type']} · Posted {jd['created']}")
        with top_right:
            st.markdown('<div class="danger-action">', unsafe_allow_html=True)
            if st.button("Delete", key=f"del_{jd['id']}"):
                jd_store.delete(jd["id"])
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("View full description"):
            st.write(jd["description"])

        skills_html = " ".join(
            f"<span style='background:#E4EDE1;color:#4C6B49;padding:4px 10px;border-radius:16px;"
            f"font-size:13px;margin-right:6px;display:inline-block;margin-bottom:6px;'>{s}</span>"
            for s in jd.get("required_skills", [])
        )
        nice_html = " ".join(
            f"<span style='background:#EFE7D8;color:#635B51;padding:4px 10px;border-radius:16px;"
            f"font-size:13px;margin-right:6px;display:inline-block;margin-bottom:6px;'>{s}</span>"
            for s in jd.get("nice_to_have_skills", [])
        )
        if skills_html:
            st.markdown(f"Required<br>{skills_html}", unsafe_allow_html=True)
        if nice_html:
            st.markdown(f"Nice to have<br>{nice_html}", unsafe_allow_html=True)

        st.write("")
        rec_clicked = st.button(
            "Get Hiring Recommendation", key=f"rec_{jd['id']}",
            disabled=not ai_service.is_configured(),
        )
        if rec_clicked:
            with st.spinner("AI is reviewing the candidate pool for this role..."):
                try:
                    pool = candidate_store.get_all_df()
                    if len(pool):
                        pool_summary = "\n".join(
                            f"- {r['Candidate']}: {r['Role']}, skills: {r['Skills']}, "
                            f"match: {r['Match']}%, stage: {r['Stage']}"
                            for _, r in pool.iterrows()
                        )
                    else:
                        pool_summary = "No candidates currently in the pipeline."
                    rec = ai_service.hiring_recommendation(jd["description"], pool_summary)
                    st.session_state[f"hiring_rec_{jd['id']}"] = rec
                except ai_service.AIServiceError as e:
                    st.error(f"Hiring recommendation failed: {e}")

        rec = st.session_state.get(f"hiring_rec_{jd['id']}")
        if rec:
            st.write(rec.get("overall_recommendation", ""))
            if rec.get("recommended_candidates"):
                st.markdown("**Prioritize:**")
                for c in rec["recommended_candidates"]:
                    st.markdown(f"- **{c.get('name','')}** — {c.get('reason','')}")
            if rec.get("should_source_more"):
                st.warning(f"Consider sourcing more candidates: {rec.get('sourcing_suggestion','')}")

        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")

render_global_chat()
