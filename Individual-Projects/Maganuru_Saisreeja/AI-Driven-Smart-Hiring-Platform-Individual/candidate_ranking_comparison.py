import streamlit as st
import pandas as pd


def candidate_ranking_comparison_page():

    st.title("Candidate Ranking & Comparison")
    st.caption("Rank, compare and shortlist uploaded candidates")
    st.markdown("---")

    # ============================================
    # ACTIVE CANDIDATES ONLY
    # ============================================

    candidates = st.session_state.get("candidates", [])

    candidates = [
        candidate
        for candidate in candidates
        if candidate.get("status") != "Hired"
    ]

    if not candidates:

        st.info(
            "No active candidates found. Upload resumes or hire new candidates."
        )
        return

    # ============================================
    # BUILD DATAFRAME
    # ============================================

    rows = []

    for candidate in candidates:

        rows.append(
            {
                "Candidate": candidate.get("name", "Unknown"),
                "Match Score": int(candidate.get("score", 0)),
                "Recommended Role": candidate.get(
                    "recommended_role",
                    "Not Specified",
                ),
                "Hiring Recommendation": candidate.get(
                    "hiring_recommendation",
                    "Consider",
                ),
                "Experience": candidate.get(
                    "experience",
                    "",
                ),
                "Education": candidate.get(
                    "education",
                    "",
                ),
            }
        )

    df = (
        pd.DataFrame(rows)
        .sort_values(
            "Match Score",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    df.insert(
        0,
        "Rank",
        range(1, len(df) + 1),
    )

    # ============================================
    # METRICS
    # ============================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Candidates",
        len(df),
    )

    col2.metric(
        "Strong Hire/Hire",
        len(
            df[
                df["Hiring Recommendation"].isin(
                    ["Strong Hire", "Hire"]
                )
            ]
        ),
    )

    col3.metric(
        "Average Score",
        f"{int(df['Match Score'].mean())}%",
    )

    col4.metric(
        "Top Candidate",
        df.iloc[0]["Candidate"],
    )

    st.markdown("---")

    # ============================================
    # LEADERBOARD
    # ============================================

    st.subheader("Candidate Leaderboard")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # ============================================
    # COMPARE CANDIDATES
    # ============================================

    st.subheader("Compare Candidates")

    names = df["Candidate"].tolist()

    left, right = st.columns(2)

    with left:

        candidate_one = st.selectbox(
            "Candidate 1",
            names,
            key="compare_candidate_1",
        )

    with right:

        candidate_two = st.selectbox(
            "Candidate 2",
            names,
            index=1 if len(names) > 1 else 0,
            key="compare_candidate_2",
        )

    comparison = df[
        df["Candidate"].isin(
            [
                candidate_one,
                candidate_two,
            ]
        )
    ]

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # ============================================
    # TOP RECOMMENDATION
    # ============================================

    st.success(
        f"🏆 **Recommended Candidate:** "
        f"{df.iloc[0]['Candidate']} "
        f"with a Match Score of "
        f"**{df.iloc[0]['Match Score']}%** "
        f"({df.iloc[0]['Hiring Recommendation']})."
    )