import streamlit as st
import pandas as pd
import plotly.express as px


def dashboard_page():

    st.title("Dashboard")
    st.caption("Real-time recruitment overview")
    st.markdown("---")

    # =====================================================
    # LOAD DATA
    # =====================================================

    candidates = st.session_state.get(
        "candidates",
        []
    )

    employees = st.session_state.get(
        "employees",
        []
    )

    interviews = st.session_state.get(
        "interviews",
        []
    )

    # =====================================================
    # EMPTY STATE
    # =====================================================

    if not candidates:

        st.info(
            "No candidates available yet.\n\n"
            "Upload and analyze resumes to populate the dashboard."
        )

        return

    # =====================================================
    # DATAFRAME
    # =====================================================

    rows = []

    for candidate in candidates:

        rows.append(

            {

                "Name":
                    candidate.get(
                        "name",
                        "Unknown"
                    ),

                "Email":
                    candidate.get(
                        "email",
                        "Not Available"
                    ),

                "Education":
                    candidate.get(
                        "education",
                        "Not Available"
                    ),

                "Experience":
                    candidate.get(
                        "experience",
                        "Not Available"
                    ),

                "Role":
                    candidate.get(
                        "recommended_role",
                        "Not Assigned"
                    ),

                "Recommendation":
                    candidate.get(
                        "hiring_recommendation",
                        "Consider"
                    ),

                "Score":
                    int(
                        candidate.get(
                            "score",
                            0
                        )
                    ),

                "Status":
                    candidate.get(
                        "status",
                        "Applied"
                    )

            }

        )

    df = pd.DataFrame(rows)

    df = df.sort_values(
        "Score",
        ascending=False,
    ).reset_index(drop=True)

    # =====================================================
    # KPI CALCULATIONS
    # =====================================================

    total_candidates = len(df)

    total_employees = len(employees)

    total_interviews = len(interviews)

    average_match = (
        round(df["Score"].mean())
        if not df.empty
        else 0
    )

    # =====================================================
    # KPI CARDS
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Candidates",
        total_candidates,
    )

    c2.metric(
        "Employees",
        total_employees,
    )

    c3.metric(
        "Interviews",
        total_interviews,
    )

    c4.metric(
        "Average Match",
        f"{average_match}%"
    )

    st.markdown("---")

    # =====================================================
    # CHARTS
    # =====================================================

    st.subheader("Candidates by Role")

    role_df = (
        df["Role"]
        .value_counts()
        .reset_index()
    )

    role_df.columns = [
        "Role",
        "Candidates"
    ]

    role_chart = px.bar(
        role_df,
        x="Role",
        y="Candidates",
        text="Candidates",
    )

    role_chart.update_layout(
        height=350,
        showlegend=False,
        xaxis_title="",
        yaxis_title="Candidates",
    )

    role_chart.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        role_chart,
        use_container_width=True,
    )

    st.markdown("---")

    # =====================================================
    # MATCH SCORE & DEPARTMENT
    # =====================================================

    # -----------------------------------------------------
    # MATCH SCORES
    # -----------------------------------------------------

    st.subheader("AI Match Scores")

    score_chart = px.bar(
        df,
        x="Name",
        y="Score",
        text="Score",
    )

    score_chart.update_layout(
        height=350,
        xaxis_title="Candidate",
        yaxis_title="Match Score (%)",
    )

    score_chart.update_traces(
        texttemplate="%{text}%",
        textposition="outside",
    )

    st.plotly_chart(
        score_chart,
        use_container_width=True,
    )

    st.markdown("---")

    # =====================================================
    # CANDIDATE OVERVIEW
    # =====================================================

    st.subheader("Candidate Overview")

    st.dataframe(

        df,

        use_container_width=True,

        hide_index=True,

    )

    st.markdown("---")

    # =====================================================
    # TOP CANDIDATES
    # =====================================================

    st.subheader("Top Candidates")

    top_candidates = df.head(5)

    for candidate in top_candidates.to_dict("records"):

        with st.container(border=True):

            left, right = st.columns([4, 1])

            with left:

                st.markdown(
                    f"#### {candidate['Name']}"
                )

                st.caption(
                    candidate["Role"]
                )

                st.write(
                    f"**Recommendation:** {candidate['Recommendation']}"
                )

                st.write(
                    f"**Experience:** {candidate['Experience']}"
                )

                st.write(
                    f"**Education:** {candidate['Education']}"
                )

            with right:

                st.metric(

                    "AI Match Score",

                    f"{candidate['Score']}%"

                )

    st.markdown("---")

    # =====================================================
    # DASHBOARD FOOTER
    # =====================================================

    st.caption(
        "AI Recruitment & Talent Management Copilot • Dashboard"
    )