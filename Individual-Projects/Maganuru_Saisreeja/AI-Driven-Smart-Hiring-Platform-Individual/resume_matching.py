import streamlit as st

from utils.ai import ask_ai_json, ask_ai_jd_analysis
from utils.resume_parser import (
    extract_resume_text,
    extract_candidate_info,
    extract_skills,
    infer_skills_from_role_title,
)


# ==========================================================
# Resume Matching Page
# ==========================================================
#
# Skill matching/missing is computed deterministically by running the
# same extract_skills() parser against both the resume and the job
# description, then taking a set intersection/difference. This is
# what actually fixes the "random skills" problem: there is no LLM
# step involved in deciding *which skills* match or are missing, so
# there's nothing for the model to hallucinate or phrase ambiguously.
#
# The LLM (ask_ai_json) is only used for the things that genuinely
# need judgment: match score, recommended role, improvement notes,
# a summary, and the hiring recommendation.

def resume_matching_page():

    st.title("Resume Matching AI")
    st.caption("Match candidate resumes with AI-powered analysis.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF / DOCX)",
            type=["pdf", "docx"]
        )

    with col2:
        job_description = st.text_area(
            "Paste Job Description",
            height=180
        )

    if "candidates" not in st.session_state:
        st.session_state["candidates"] = []

    if st.button("Match Resume", use_container_width=True):

        if uploaded_file is None:
            st.warning("Please upload a resume.")
            return

        if not job_description.strip():
            st.warning("Please paste a job description.")
            return

        resume_text = extract_resume_text(uploaded_file)
        candidate = extract_candidate_info(resume_text)

        # Extract skills directly from resume text
        candidate_skills = extract_skills(resume_text)

# Save back into candidate object
        candidate["skills"] = candidate_skills

        candidate_skills_str = (
    ", ".join(candidate_skills)
    if candidate_skills
    else "None listed"
)

        # --------------------------------------------------------
        # Deterministic skill matching — the actual fix.
        # Same extractor, run on both texts, then plain set math.
        # --------------------------------------------------------

        jd_skills = extract_skills(job_description)

        # --------------------------------------------------------
        # Handle bare role-title job descriptions ("SDE", "AI Engineer",
        # etc). extract_skills() only matches literal skill keywords —
        # a one/two-word role name has nothing for it to find, so
        # jd_skills comes back empty (or near-empty). That "0 required
        # skills / not calculable" state is what was confusing the
        # local model downstream: the prompt told it to anchor
        # match_score to a skill-coverage number that didn't exist,
        # which is why results looked fine for a full paste-in JD but
        # broke for just a role name.
        #
        # Fix: if the deterministic parser found fewer than 2 skills
        # AND the JD text itself is short (a title, not a real
        # description), ask the AI to expand the role name into a
        # typical skill/requirement profile first, then re-run the
        # SAME deterministic extractor against that expanded text.
        # Matching is still 100% deterministic — the AI is only used
        # to fill in "what a Job Description would normally say",
        # never to decide which skills the candidate has or matches.
        # --------------------------------------------------------

        jd_was_expanded = False

        if len(jd_skills) < 2 and len(job_description.split()) <= 12:

            with st.spinner("Job description looks like just a role title — expanding it..."):
                jd_analysis = ask_ai_jd_analysis(job_description)

            if not jd_analysis.get("ai_error"):

                expanded_parts = [job_description]

                if jd_analysis.get("required_skills"):
                    expanded_parts.append(
                        "Required Skills: " + ", ".join(jd_analysis["required_skills"])
                    )

                if jd_analysis.get("preferred_qualifications"):
                    expanded_parts.append(
                        "Preferred Qualifications: " + ", ".join(jd_analysis["preferred_qualifications"])
                    )

                if jd_analysis.get("important_keywords"):
                    expanded_parts.append(
                        "Keywords: " + ", ".join(jd_analysis["important_keywords"])
                    )

                if jd_analysis.get("key_responsibilities"):
                    expanded_parts.append(
                        "Responsibilities: " + "; ".join(jd_analysis["key_responsibilities"])
                    )

                expanded_jd_text = "\n".join(expanded_parts)
                new_jd_skills = extract_skills(expanded_jd_text)

                if new_jd_skills:
                    jd_skills = new_jd_skills
                    jd_was_expanded = True

        # --------------------------------------------------------
        # Deterministic floor: if we STILL have fewer than 2 JD
        # skills (the AI expansion above either failed, or the model
        # phrased skills in words that don't match SKILL_DB), fall
        # back to the role-title lookup. This never depends on the
        # local model succeeding, so common titles like "SDE-1" or
        # "AI Engineer" always get a real skill set to match against.
        # --------------------------------------------------------

        jd_role_matched = False

        if len(jd_skills) < 2:

            role_skills = infer_skills_from_role_title(job_description)

            if role_skills:
                jd_skills = sorted(set(jd_skills) | set(role_skills))
                jd_role_matched = True
                jd_was_expanded = False  # role lookup takes precedence in the UI note

        candidate_skills_lower = {s.lower() for s in candidate_skills}
        jd_skills_lower = {s.lower() for s in jd_skills}

        matching_skills = sorted(
            s for s in jd_skills if s.lower() in candidate_skills_lower
        )
        missing_skills = sorted(
            s for s in jd_skills if s.lower() not in candidate_skills_lower
        )

        # --------------------------------------------------------
        # AI only handles judgment calls, not skill identification.
        # --------------------------------------------------------

        # --------------------------------------------------------
        # Skill coverage numbers, computed from the same deterministic
        # matching/missing lists shown in the UI. These are handed to
        # the AI so match_score is grounded in reality instead of the
        # model's own loose re-reading of the raw skills/JD text,
        # which could (and did) diverge from what's actually displayed
        # as "Missing Skills" below.
        # --------------------------------------------------------

        total_jd_skills = len(jd_skills)
        matched_count = len(matching_skills)
        missing_count = len(missing_skills)

        if total_jd_skills > 0:
            skill_coverage_percent = round(
                (matched_count / total_jd_skills) * 100
            )
        else:
            skill_coverage_percent = None

        candidate_prompt = f"""
Name:
{candidate.get("name")}

Education:
{candidate.get("education")}

Experience:
{candidate.get("experience")}

Skills:
{candidate_skills_str}

Job Description:
{job_description}

Computed Skill Coverage (already calculated separately — do not
recompute or contradict these numbers):
- Required skills identified in the JD: {total_jd_skills}
- Skills the candidate has that match: {matched_count}
- Skills the candidate is missing: {missing_count}
- Skill coverage: {
    f"{skill_coverage_percent}%" if skill_coverage_percent is not None
    else "Not calculable (no recognized skills found in JD text)"
}

Scoring guidance:
{
    f'''- Use the skill coverage percentage above as the primary anchor for
  match_score — do not assign a high score (85+) if skill coverage
  is well below that, even if education/experience look strong.
- You may adjust the score up or down from the skill coverage number
  by roughly 10-15 points based on experience level, education
  relevance, and project quality — but the final score should stay
  broadly consistent with how many required skills are actually
  missing.
- A candidate missing several required skills should not score in
  the "Excellent Match" (90-100) range regardless of other strengths.'''
    if skill_coverage_percent is not None
    else '''- No skill coverage percentage could be calculated because the Job
  Description text does not name specific required skills. Score the
  match using only the candidate's education, experience level, and
  project relevance against the stated role/title above — do not
  refuse to score and do not leave match_score at 0 just because a
  coverage number is unavailable.'''
}

Note: skill matching has already been computed separately. Do not
list specific skill names in your response — focus only on match
score, recommended role, general strengths/weaknesses (education,
experience level, project relevance, resume quality — not specific
tools/technologies), a short summary, and hiring recommendation.
If the number of matching skills above is 0, do not claim the
candidate has "relevant skills" or "strong technical skills" in the
summary or strengths — base those instead only on education,
experience, and project relevance.
"""

        with st.spinner("Analyzing resume with Llama 3.2..."):
            result = ask_ai_json(candidate_prompt)

        if result.get("ai_error"):
            st.error(
                "The AI analysis failed, so score, recommended role, "
                "summary, and improvement areas below are placeholders "
                "— skill matching still worked since that's computed "
                "separately. Check that Ollama is running "
                "(`ollama serve`) and that the `llama3.2` model is "
                "pulled. See the terminal running Streamlit for the "
                "exact error."
            )

        score = result["match_score"]
        candidate["recommended_role"] = result["recommended_role"]

        weaknesses = [
            w.strip() for w in result.get("weaknesses", [])
            if isinstance(w, str) and w.strip()
        ]

        candidate["matching_skills"] = matching_skills
        candidate["missing_skills"] = missing_skills
        candidate["improvement_areas"] = (
            ", ".join(weaknesses) if weaknesses else "No specific improvement areas identified."
        )
        candidate["summary"] = result.get("summary", "")

        skill_gap_sections = [
            "### Matching Skills\n" + (
                ", ".join(matching_skills) if matching_skills else "None identified."
            ),
            "### Missing Skills\n" + (
                ", ".join(missing_skills) if missing_skills else "None identified."
            ),
            "### Improvement Areas\n" + candidate["improvement_areas"],
        ]

        if candidate["summary"]:
            skill_gap_sections.append("### Summary\n" + candidate["summary"])

        candidate["skill_gap_analysis"] = "\n\n".join(skill_gap_sections)
        candidate["hiring_recommendation"] = result["hiring_recommendation"]
        candidate["score"] = score

        # ==================================================
        # Save / Update Candidate
        # ==================================================

        updated = False

        for index, old_candidate in enumerate(st.session_state["candidates"]):

            same_name = old_candidate.get("name") == candidate.get("name")
            same_email = (
                candidate.get("email")
                and old_candidate.get("email") == candidate.get("email")
            )

            if same_name or same_email:
                st.session_state["candidates"][index] = candidate
                updated = True
                break

        if not updated:
            st.session_state["candidates"].append(candidate)

        st.success("Candidate saved successfully.")

        if jd_role_matched:
            st.caption(
                "Note: the job description looked like just a role title "
                "(e.g. \"SDE-1\"), so a typical skill set for that role "
                "was used for matching. For more precise results, paste "
                "the full job description instead."
            )
        elif jd_was_expanded:
            st.caption(
                "Note: the job description looked like just a role title, "
                "so it was expanded into a typical skill/requirement "
                "profile for that role before matching. For more precise "
                "results, paste the full job description instead."
            )
        elif not jd_skills:
            st.caption(
                "Note: no recognized technical skills were found in the "
                "job description text, so skill matching may be limited."
            )

        st.markdown("---")

        # ==================================================
        # Candidate Information
        # ==================================================

        st.subheader("Candidate Information")

        left, right = st.columns(2)

        with left:
            st.write("**Name:**", candidate.get("name", "Not Available"))
            st.write("**Email:**", candidate.get("email", "Not Available"))
            st.write("**Phone:**", candidate.get("phone", "Not Available"))
            st.write("**Education:**", candidate.get("education", "Not Available"))

        with right:
            st.write("**Experience:**", candidate.get("experience", "Not Available"))
            st.write("**Recommended Role:**", candidate.get("recommended_role", "Not Specified"))
            st.write("**Skills:**")

            if candidate.get("skills"):
                for skill in candidate["skills"]:
                    st.success(skill)
            else:
                st.info("No skills detected.")
                st.markdown("---")

        # ==================================================
        # Skill Gap Analysis
        # ==================================================

        st.subheader("Skill Gap Analysis")
        st.info(candidate["skill_gap_analysis"])

        st.markdown("---")

        # ==================================================
        # Hiring Recommendation
        # ==================================================

        st.subheader("Hiring Recommendation")

        recommendation = candidate["hiring_recommendation"].strip().lower()

        if recommendation == "strong hire":
            st.success("Strong Hire")
        elif recommendation == "hire":
            st.success("Hire")
        elif recommendation == "consider":
            st.warning("Consider")
        elif recommendation == "reject":
            st.error("Reject")
        else:
            st.info(candidate["hiring_recommendation"])

        st.markdown("---")

        # ==================================================
        # Overall Match Score
        # ==================================================

        st.markdown(
            f"""
<div style="text-align:center; padding:20px 0;">
<h4>Overall Match Score</h4>
<h1 style="font-size:64px; margin:0;">{score}%</h1>
</div>
""",
            unsafe_allow_html=True
        )

        st.progress(score / 100)
        st.markdown("---")

    else:
        st.info("Upload a resume and paste the job description.")