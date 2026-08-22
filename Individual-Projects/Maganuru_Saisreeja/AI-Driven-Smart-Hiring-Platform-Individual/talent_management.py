import streamlit as st
import pandas as pd
import plotly.express as px
import re
from utils.ai import ask_ai


def format_talent_insight(text: str) -> str:
    """
    Rebuild proper Markdown from the AI talent-insight response.

    The raw response often comes back as one run-on line (the model
    doesn't reliably emit newlines), which breaks two things:
    1. Bullet points under Strengths / Areas for Improvement / etc.
       run together in a single paragraph instead of a real list.
    2. Section headings were previously mapped to a mix of "##" and
       "###", which render at different sizes. Every heading here
       maps to the same level so they're all the same size.
    """

    if not text:
        return text

    text = text.strip()

    section_headers = [
        "Performance Rating:",
        "Career Readiness Score:",
        "Strengths:",
        "Areas for Improvement:",
        "Training Recommendations:",
        "Career Growth Plan:",
        "Promotion Readiness:",
        "Manager Summary:",
    ]

    for header in section_headers:
        heading_text = header.rstrip(":")
        text = re.sub(
            rf"\s*{re.escape(header)}\s*",
            f"\n\n#### {heading_text}\n",
            text,
            flags=re.IGNORECASE,
        )

    # Turn "• " (or "- ") bullet markers into their own Markdown
    # list lines, wherever they land in the run-on text.
    text = re.sub(r"\s*[•\-]\s+", "\n- ", text)

    # Collapse accidental triple+ blank lines back down to one.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_section_text(raw_text: str, header: str, all_headers: list) -> str:
    """
    Return only the text that follows `header` up to the next known
    section header (or end of string).

    Without this, keyword/number extraction scans the ENTIRE AI
    response, so a word like "excellent" mentioned in passing inside
    the Manager Summary (e.g. "shows excellent potential") can
    override the real Performance Rating of "Average", and the first
    "%" found anywhere can be picked up instead of the one under
    Career Readiness Score.
    """

    other_headers = [h for h in all_headers if h != header]

    pattern = (
        re.escape(header)
        + r"\s*(.*?)(?="
        + "|".join(re.escape(h) for h in other_headers)
        + r"|$)"
    )

    match = re.search(pattern, raw_text, flags=re.IGNORECASE | re.DOTALL)

    return match.group(1).strip() if match else ""


def talent_management_page():

    st.title("Talent Management")
    st.caption("AI-powered employee performance and career insights.")
    st.markdown("---")

    # ==================================================
    # LOAD EMPLOYEES
    # ==================================================

    employees = st.session_state.get(
        "employees",
        []
    )

    if not employees:

        st.info(
            "No employee data available.\n\n"
            "Hire candidates from the Interview Management module "
            "to populate Talent Management."
        )

        return

    # ==================================================
    # DATAFRAME
    # ==================================================

    df = pd.DataFrame(employees)

    defaults = {

        "name": "Unknown Employee",

        "department": "Not Assigned",

        "experience": "Not Available",

        "performance": "Pending AI Evaluation",

    }

    for column, value in defaults.items():

        if column not in df.columns:

            df[column] = value

        else:

            df[column] = df[column].fillna(value)

    # Career Readiness

    if "career_readiness" not in df.columns:

        df["career_readiness"] = None

    # ==================================================
    # KPI CALCULATIONS
    # ==================================================

    total_employees = len(df)

    total_departments = df["department"].nunique()

    analyzed = sum(

        1

        for emp in employees

        if emp.get("career_readiness") is not None

    )

    average_readiness = 0

    valid_scores = [

        emp.get("career_readiness")

        for emp in employees

        if pd.notna(emp.get("career_readiness"))
        and isinstance(emp.get("career_readiness"), (int, float))

    ]

    if valid_scores:

        average_readiness = round(

            sum(valid_scores)

            / len(valid_scores)

        )

    # ==================================================
    # KPI CARDS
    # ==================================================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(

        "Employees",

        total_employees,

    )

    c2.metric(

        "Departments",

        total_departments,

    )

    c3.metric(

        "AI Analyzed",

        analyzed,

    )

    c4.metric(

        "Average Readiness",

        f"{average_readiness}%"

        if analyzed

        else "N/A",

    )

    st.markdown("---")

    # ==================================================
    # EMPLOYEE ANALYTICS
    # ==================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------
    # DEPARTMENT DISTRIBUTION
    # --------------------------------------------------

    with col1:

        st.subheader("Department Distribution")

        department_df = (

            df["department"]

            .fillna("Not Assigned")

            .replace("", "Not Assigned")

            .value_counts()

            .reset_index()

        )

        department_df.columns = [

            "Department",

            "Employees"

        ]

        department_chart = px.pie(

            department_df,

            names="Department",

            values="Employees",

            hole=0.45,

        )

        department_chart.update_layout(

            height=360,

            legend_title="Department",

            margin=dict(

                l=20,

                r=20,

                t=40,

                b=20

            )

        )

        st.plotly_chart(

            department_chart,

            use_container_width=True,

        )

    # --------------------------------------------------
    # EXPERIENCE DISTRIBUTION
    # --------------------------------------------------

    with col2:

        st.subheader("Experience Distribution")

        experience_df = (

            df["experience"]

            .fillna("Not Available")

            .replace("", "Not Available")

            .value_counts()

            .reset_index()

        )

        experience_df.columns = [

            "Experience",

            "Employees"

        ]

        experience_chart = px.bar(

            experience_df,

            x="Experience",

            y="Employees",

            text="Employees",

        )

        experience_chart.update_layout(

            height=360,

            xaxis_title="Experience",

            yaxis_title="Employees",

            showlegend=False,

            margin=dict(

                l=20,

                r=20,

                t=40,

                b=20

            )

        )

        experience_chart.update_traces(

            textposition="outside"

        )

        st.plotly_chart(

            experience_chart,

            use_container_width=True,

        )

    st.markdown("---")

    # ==================================================
    # CAREER READINESS OVERVIEW
    # ==================================================

    readiness_data = []

    for emp in st.session_state.get("employees", []):

        readiness = emp.get("career_readiness")

        if pd.notna(readiness) and isinstance(readiness, (int, float)):

            readiness_data.append(

                {

                    "Employee": emp.get(

                        "name",

                        "Unknown"

                    ),

                    "Career Readiness": readiness,

                }

            )

    if readiness_data:

        st.subheader("Career Readiness Overview")

        readiness_df = pd.DataFrame(

            readiness_data

        )

        readiness_chart = px.bar(

            readiness_df.sort_values(

                "Career Readiness",

                ascending=False,

            ),

            x="Employee",

            y="Career Readiness",

            text="Career Readiness",

        )

        readiness_chart.update_layout(

            height=380,

            xaxis_title="Employee",

            yaxis_title="Career Readiness (%)",

            showlegend=False,

            margin=dict(

                l=20,

                r=20,

                t=40,

                b=20,

            )

        )

        readiness_chart.update_traces(

            texttemplate="%{text}%",

            textposition="outside",

        )

        st.plotly_chart(

            readiness_chart,

            use_container_width=True,

        )

    else:

        st.info(

            "Career Readiness scores will appear after generating AI Talent Insights."

        )

    st.markdown("---")

    # ==================================================
    # EMPLOYEE DIRECTORY
    # ==================================================

    st.subheader("Employee Directory")

    display_df = df.copy()

    display_df.rename(

        columns={

            "name": "Employee",

            "department": "Department",

            "experience": "Experience",

            "performance": "Performance",

        },

        inplace=True,

    )

    # Performance

    display_df["Performance"] = (

        display_df["Performance"]

        .fillna("Pending AI Evaluation")

        .replace("", "Pending AI Evaluation")

    )

    # Career Readiness

    display_df["Career Readiness"] = (

        display_df["career_readiness"]

        .apply(

            lambda x:

            f"{int(x)}%"

            if pd.notna(x) and isinstance(x, (int, float))

            else "Pending AI Analysis"

        )

    )

    st.dataframe(

        display_df[

            [

                "Employee",

                "Department",

                "Experience",

                "Performance",

                "Career Readiness",

            ]

        ],

        use_container_width=True,

        hide_index=True,

    )

    st.markdown("---")

    # ==================================================
    # EMPLOYEE PROFILE
    # ==================================================

    st.subheader("Employee Profile")

    employee_name = st.selectbox(
        "Select Employee",
        df["name"].tolist(),
        key="employee_profile",
    )

    employee = next(

        (

            emp

            for emp in st.session_state["employees"]

            if emp.get("name") == employee_name

        ),

        None,

    )

    st.info(
        f"""
### {employee_name}

**Department:** {employee.get('department','Not Assigned')}

**Experience:** {employee.get('experience','Not Available')}

**Current Performance:** {employee.get('performance','Pending AI Evaluation')}
"""
    )

    st.markdown("---")

    # ==================================================
    # AI TALENT INSIGHTS
    # ==================================================

    st.subheader("AI Talent Insights")

    if st.button(
        "Generate AI Talent Insights",
        use_container_width=True,
    ):

        prompt = f"""
You are an experienced HR Talent Management Specialist.

Analyze the following employee profile.

Employee Name:
{employee_name}

Department:
{employee.get('department', 'Not Assigned')}

Experience:
{employee.get('experience', 'Not Available')}

Current Performance:
{employee.get('performance', 'Pending AI Evaluation')}

Evaluate the employee based on experience, role, skills, growth potential and overall career readiness.

Return ONLY in the following format.

Do NOT use markdown.
Do NOT add introductions.
Do NOT add conclusions.
Do NOT use numbering.
Do NOT change the headings.

Performance Rating:
(Choose EXACTLY one)
Excellent
Good
Average
Needs Improvement

Career Readiness Score:
(Provide ONLY one percentage)

Strengths:
(Write exactly 3 bullet points.)

Areas for Improvement:
(Write exactly 3 bullet points.)

Training Recommendations:
(Write exactly 3 bullet points.)

Career Growth Plan:
(Write exactly 3 bullet points.)

Promotion Readiness:
(Write one professional sentence.)

Manager Summary:
(Write 3-4 professional sentences summarizing the employee's performance and future growth.)

Guidelines:
- Do NOT leave any section blank.
- Do NOT write N/A.
- Do NOT skip any heading.
- Use concise and professional HR language.
- Return ONLY the requested format.
"""

        with st.spinner("Generating AI Talent Insights..."):

            result = ask_ai(prompt)

        # ==============================================
        # DISPLAY AI RESULT
        # ==============================================

        st.markdown("---")

        st.subheader("AI Assessment")

        formatted = format_talent_insight(result)

        with st.container(border=True):
            st.markdown(formatted)

        # ==============================================
        # SECTION-SCOPED TEXT (so extraction below only
        # looks at each field's own section, not the
        # whole response)
        # ==============================================

        all_section_headers = [
            "Performance Rating:",
            "Career Readiness Score:",
            "Strengths:",
            "Areas for Improvement:",
            "Training Recommendations:",
            "Career Growth Plan:",
            "Promotion Readiness:",
            "Manager Summary:",
        ]

        performance_section = extract_section_text(
            result, "Performance Rating:", all_section_headers
        )

        readiness_section = extract_section_text(
            result, "Career Readiness Score:", all_section_headers
        )

        # Fallback to the full response only if the model didn't
        # produce the expected heading at all.
        if not performance_section:
            performance_section = result

        if not readiness_section:
            readiness_section = result

        # ==============================================
        # PERFORMANCE EXTRACTION
        # ==============================================

        performance = "Pending AI Evaluation"

        ratings = [

            "Excellent",

            "Good",

            "Average",

            "Needs Improvement"

        ]

        for rating in ratings:

            if rating.lower() in performance_section.lower():

                performance = rating

                break

        # ==============================================
        # CAREER READINESS EXTRACTION
        # ==============================================

        readiness = None

        match = re.search(

            r"(\d{1,3})\s*%",

            readiness_section,

        )

        if match:

            readiness = max(

                0,

                min(

                    100,

                    int(match.group(1))

                )

            )

        # ==============================================
        # SAVE RESULTS
        # ==============================================

        if employee:

            employee["performance"] = performance

            if readiness is not None:

                employee["career_readiness"] = readiness

        # ==============================================
        # EVALUATION SUMMARY
        # ==============================================

        st.markdown("---")

        st.subheader("Employee Evaluation")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(

                "Performance Rating",

                performance,

            )

        with col2:

            st.metric(

                "Career Readiness",

                f"{readiness}%"

                if readiness is not None

                else "Pending",

            )

        if readiness is not None:

            st.progress(readiness)

        st.success(
            "AI Talent Insights generated successfully."
        )

    else:

        st.info(
            "Select an employee and click **Generate AI Talent Insights**."
        )

    st.markdown("---")

    st.caption(
        "AI Recruitment & Talent Management Copilot • Talent Management"
    )