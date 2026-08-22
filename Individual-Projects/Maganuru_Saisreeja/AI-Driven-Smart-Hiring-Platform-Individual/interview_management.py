import re
import streamlit as st
import pandas as pd
from utils.ai import ask_ai


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def extract_questions(response: str):
    """
    Extract exactly 5 interview questions from
    the AI response.
    """

    questions = []

    patterns = [
        r"^\d+\.\s*(.*)",
        r"^\d+\)\s*(.*)",
        r"^-\s*(.*)",
        r"^•\s*(.*)"
    ]

    for line in response.splitlines():

        line = line.strip()

        if not line:
            continue

        matched = False

        for pattern in patterns:

            match = re.match(pattern, line)

            if match:

                questions.append(
                    match.group(1).strip()
                )

                matched = True
                break

        if not matched and line.endswith("?"):

            questions.append(line)

    clean = []

    for question in questions:

        if (
            question
            and question not in clean
        ):
            clean.append(question)

    return clean[:5]


def format_recommendation(text: str) -> str:
    """
    Rebuild proper Markdown (section headers + a real bullet list)
    from the AI's hiring recommendation text.

    The raw response often comes back as one run-on line (the model
    doesn't reliably emit newlines, and ai.clean_response() collapses
    blank lines further), which makes st.markdown render everything
    as a single flat paragraph. This reconstructs line breaks around
    the known section headers and bullet markers so it renders as
    headed sections with an actual bullet list.
    """

    if not text:
        return text

    text = text.strip()

    section_headers = [
        "Hiring Recommendation:",
        "Reason:",
        "Strengths:",
        "Areas for Improvement:",
        "Suggested Department:",
        "Suggested Designation:",
    ]

    for header in section_headers:
        text = re.sub(
            rf"\s*{re.escape(header)}\s*",
            f"\n\n**{header}**\n",
            text,
            flags=re.IGNORECASE,
        )

    # Turn "• " (or "- ") bullet markers into their own Markdown
    # list lines, wherever they land in the text.
    text = re.sub(r"\s*[•\-]\s+", "\n- ", text)

    # Collapse accidental triple+ blank lines back down to one.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ==========================================================
# MAIN PAGE
# ==========================================================

def interview_management_page():

    st.title("Interview Management")

    st.caption(
        "AI-powered interview scheduling and hiring."
    )

    st.markdown("---")

    # ======================================================
    # SESSION STATE
    # ======================================================

    if "interviews" not in st.session_state:
        st.session_state.interviews = []

    if "generated_questions" not in st.session_state:
        st.session_state.generated_questions = []

    if "employees" not in st.session_state:
        st.session_state.employees = []

    if "recommendations" not in st.session_state:
        st.session_state.recommendations = {}

    candidates = st.session_state.get(
        "candidates",
        []
    )

    # ======================================================
    # METRICS
    # ======================================================

    total = len(
        st.session_state.interviews
    )

    completed = sum(
        1
        for interview in st.session_state.interviews
        if interview.get("Status") == "Completed"
    )

    upcoming = total - completed

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Scheduled",
        total
    )

    col2.metric(
        "Upcoming",
        upcoming
    )

    col3.metric(
        "Completed",
        completed
    )

    st.markdown("---")

    # ======================================================
    # AI QUESTION GENERATOR
    # ======================================================

    st.subheader(
        "AI Interview Question Generator"
    )

    role = st.selectbox(

        "Job Role",

        [
            "AI Engineer",
            "ML Engineer",
            "Data Scientist",
            "Backend Developer",
            "Frontend Developer",
            "Full Stack Developer",
            "DevOps Engineer",
            "Cloud Engineer",
            "Data Analyst",
            "Python Developer"
        ],

        key="question_role"

    )

    level = st.selectbox(

        "Experience Level",

        [
            "Fresher",
            "1-3 Years",
            "3-5 Years",
            "5+ Years"
        ],

        key="question_level"

    )

    question_type = st.selectbox(

        "Question Type",

        [
            "Technical",
            "Behavioral",
            "HR"
        ],

        key="question_type"

    )

    if st.button(

        "Generate AI Questions",

        use_container_width=True,

        key="generate_questions"

    ):

        prompt = f"""
You are an expert technical interviewer.

Generate EXACTLY FIVE interview questions.

Role:
{role}

Experience:
{level}

Question Type:
{question_type}

Rules:

- Generate only questions.
- No answers.
- No explanations.
- No headings.
- Number them 1 to 5.
"""

        with st.spinner(
            "Generating interview questions..."
        ):

            response = ask_ai(prompt)

        st.session_state.generated_questions = (
            extract_questions(response)
        )

    if st.session_state.generated_questions:

        st.success(
            "Interview Questions Generated"
        )

        st.markdown(
            "### Interview Questions"
        )

        for index, question in enumerate(

            st.session_state.generated_questions,

            start=1

        ):

            with st.container(border=True):

                st.markdown(
                    f"#### Question {index}"
                )

                st.write(question)

    st.markdown("---")

    # ======================================================
    # INTERVIEW SCHEDULING
    # ======================================================

    st.subheader("Interview Scheduling")

    if not candidates:

        st.info(
            "Upload candidates using Resume Matching before scheduling interviews."
        )

    else:

        candidate_names = [
            candidate.get("name", "Unknown Candidate")
            for candidate in candidates
        ]

        col1, col2 = st.columns(2)

        with col1:

            selected_candidate = st.selectbox(
                "Candidate",
                candidate_names,
                key="schedule_candidate",
            )

            interview_date = st.date_input(
                "Interview Date",
                key="schedule_date",
            )

            interview_time = st.time_input(
                "Interview Time",
                key="schedule_time",
            )

        with col2:

            interviewer = st.text_input(
                "Interviewer",
                value="HR Manager",
                key="schedule_interviewer",
            )

            interview_type = st.selectbox(
                "Interview Type",
                [
                    "Technical",
                    "Behavioral",
                    "HR",
                    "Managerial",
                    "Final"
                ],
                key="schedule_type",
            )

            interview_mode = st.radio(
                "Interview Mode",
                [
                    "Online",
                    "Offline"
                ],
                horizontal=True,
                key="schedule_mode",
            )

        recruiter_notes = st.text_area(
            "Recruiter Notes",
            placeholder="Add interview instructions or recruiter comments...",
            height=120,
            key="schedule_notes",
        )

        if st.button(
            "Schedule Interview",
            use_container_width=True,
            key="schedule_button",
        ):

            interview = {

                "Candidate": selected_candidate,

                "Date": str(interview_date),

                "Time": str(interview_time),

                "Interview Type": interview_type,

                "Interviewer": interviewer,

                "Mode": interview_mode,

                "Notes": recruiter_notes,

                "Status": "Scheduled"

            }

            st.session_state.interviews.append(
                interview
            )

            # Update candidate status
            for candidate in candidates:

                if (
                    candidate.get("name")
                    == selected_candidate
                ):

                    candidate["status"] = (
                        "Interview Scheduled"
                    )

                    break

            st.success(
                f"Interview scheduled successfully for {selected_candidate}."
            )

    st.markdown("---")

    # ======================================================
    # INTERVIEW SCHEDULE
    # ======================================================

    st.subheader("Interview Schedule")

    if st.session_state.interviews:

        interview_df = pd.DataFrame(
            st.session_state.interviews
        )

        st.dataframe(
            interview_df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No interviews scheduled yet."
        )

    st.markdown("---")

    # ======================================================
    # AI HIRING RECOMMENDATION
    # ======================================================

    st.subheader("AI Hiring Recommendation")

    if candidates:

        recommendation_candidate = st.selectbox(
            "Candidate",
            [candidate.get("name", "Unknown Candidate") for candidate in candidates],
            key="recommend_candidate",
        )

        # Full candidate record for the selected name, so the AI prompt
        # can be built from real resume/skills/experience data instead
        # of just the candidate's name.
        selected_candidate_data = next(
            (
                candidate
                for candidate in candidates
                if candidate.get("name") == recommendation_candidate
            ),
            {},
        )

        interview_rating = st.slider(
            "Interview Rating",
            min_value=1,
            max_value=5,
            value=4,
            key="recommend_rating",
        )

        recruiter_feedback = st.text_area(
            "Recruiter Feedback",
            height=150,
            placeholder="Write your interview feedback...",
            key="recommend_feedback",
        )

        if st.button(
            "Generate AI Recommendation",
            use_container_width=True,
            key="generate_recommendation",
        ):

            # Pull candidate details defensively, since the exact key
            # names depend on how Resume Matching / Candidate Ranking
            # populated st.session_state.candidates.
            candidate_type = (
                selected_candidate_data.get("candidate_type")
                or selected_candidate_data.get("type")
                or "Not specified"
            )

            experience_years = (
                selected_candidate_data.get("experience_years")
                or selected_candidate_data.get("total_experience")
                or selected_candidate_data.get("experience")
                or "Not specified"
            )

            education = (
                selected_candidate_data.get("education")
                or "Not specified"
            )

            skills = (
                selected_candidate_data.get("skills")
                or selected_candidate_data.get("matched_skills")
                or []
            )
            skills_text = (
                ", ".join(str(skill) for skill in skills)
                if isinstance(skills, list) and skills
                else (str(skills) if skills else "Not specified")
            )

            match_score = (
                selected_candidate_data.get("match_score")
                or selected_candidate_data.get("score")
            )
            match_score_text = (
                f"{match_score}%" if match_score not in (None, "") else "Not specified"
            )

            resume_summary = (
                selected_candidate_data.get("summary")
                or selected_candidate_data.get("resume_summary")
                or "Not specified"
            )

            feedback_text = (
                recruiter_feedback.strip()
                if recruiter_feedback and recruiter_feedback.strip()
                else "Not provided"
            )

            prompt = f"""
You are an experienced HR Recruitment Manager.

Candidate Information:

Candidate Name:
{recommendation_candidate}

Candidate Type:
{candidate_type}

Experience:
{experience_years}

Education:
{education}

Skills:
{skills_text}

Resume Match Score:
{match_score_text}

Resume Summary:
{resume_summary}

Interview Rating:
{interview_rating}/5

Recruiter Feedback:
{feedback_text}

Based on the candidate information and interview details above, provide a professional hiring recommendation.

Return ONLY in the following format.

Hiring Recommendation:
(Strong Hire / Hire / Hold / Reject)

Reason:
- Bullet points

Strengths:
- Bullet points

Areas for Improvement:
- Bullet points

Suggested Department:

Suggested Designation:


"""

            with st.spinner(
                "Generating AI recommendation..."
            ):

                recommendation = ask_ai(prompt)

            st.session_state.recommendations[
                recommendation_candidate
            ] = format_recommendation(recommendation)

        if recommendation_candidate in st.session_state.recommendations:

            st.success("Recommendation Generated")

            with st.container(border=True):

                st.markdown(
                    st.session_state.recommendations[
                        recommendation_candidate
                    ]
                )

    else:

        st.info(
            "Upload candidates first to generate hiring recommendations."
        )

    st.markdown("---")

    # ======================================================
    # HIRE CANDIDATE
    # ======================================================

    if candidates and (
        recommendation_candidate
        in st.session_state.recommendations
    ):

        st.subheader("Hire Candidate")

        col1, col2 = st.columns(2)

        with col1:

            department = st.selectbox(
                "Department",
                [
                    "AI",
                    "Machine Learning",
                    "Data Science",
                    "Backend",
                    "Frontend",
                    "Full Stack",
                    "DevOps",
                    "Cloud",
                    "HR"
                ],
                key="hire_department",
            )

            joining_date = st.date_input(
                "Joining Date",
                key="hire_joining_date",
            )

        with col2:

            designation = st.selectbox(
                "Designation",
                [
                    "AI Engineer",
                    "ML Engineer",
                    "Data Scientist",
                    "Backend Developer",
                    "Frontend Developer",
                    "Full Stack Developer",
                    "DevOps Engineer",
                    "Cloud Engineer",
                    "HR Executive",
                ],
                key="hire_designation",
            )

            employee_id = (
                f"EMP{len(st.session_state.employees)+1:03d}"
            )

            st.text_input(
                "Employee ID",
                value=employee_id,
                disabled=True,
                key="employee_id_preview",
            )

        if st.button(
            "Hire Candidate",
            type="primary",
            use_container_width=True,
            key="hire_candidate_button",
        ):

            already_hired = any(

                employee.get("name")
                == recommendation_candidate

                for employee
                in st.session_state.employees

            )

            if already_hired:

                st.warning(
                    "This candidate has already been hired."
                )

            else:

                employee = {

                    "employee_id": employee_id,

                    "name": recommendation_candidate,

                    "department": department,

                    "designation": designation,

                    "joining_date": str(joining_date),

                    "experience": "0 Years",

                    "performance": "Not Rated",

                    "status": "Active"

                }

                st.session_state.employees.append(
                    employee
                )

                # Update candidate status

                for candidate in candidates:

                    if (
                        candidate.get("name")
                        == recommendation_candidate
                    ):

                        candidate["status"] = "Hired"

                        candidate["department"] = department

                        candidate["designation"] = designation

                        break

                st.success(
                    f"{recommendation_candidate} has been hired successfully."
                )

                st.dataframe(

                    pd.DataFrame(
                        [
                            {
                                "Employee ID": employee_id,
                                "Name": recommendation_candidate,
                                "Department": department,
                                "Designation": designation,
                                "Joining Date": str(joining_date),
                                "Status": "Active",
                            }
                        ]
                    ),

                    use_container_width=True,
                    hide_index=True,

                )

                st.info(
                    "Employee has been added to Talent Management."
                )

    st.markdown("---")

    # ======================================================
    # RECRUITER BEST PRACTICES
    # ======================================================

    with st.expander(
        "Recruiter Best Practices",
        expanded=False,
    ):

        st.markdown(
            """
### Interview Tips

- Review the candidate's resume before the interview.
- Ask role-specific and scenario-based questions.
- Evaluate both technical and communication skills.
- Record structured feedback immediately after the interview.
- Use AI recommendations as decision support, not as the final decision.
"""
        )

    st.markdown("---")

    # ======================================================
    # UPCOMING FEATURES
    # ======================================================

    with st.expander(
        "Upcoming AI Features",
        expanded=False,
    ):

        st.markdown(
            """
🚀 Planned AI Features

- AI Offer Letter Generator
- AI Interview Invitation Email
- AI Rejection Email
- AI Next Round Invitation
- AI Employee Onboarding Email
- AI Interview Summary Generator
"""
        )

    st.markdown("---")

    st.caption(
        "AI Recruitment & Talent Management Copilot • Interview Management"
    )