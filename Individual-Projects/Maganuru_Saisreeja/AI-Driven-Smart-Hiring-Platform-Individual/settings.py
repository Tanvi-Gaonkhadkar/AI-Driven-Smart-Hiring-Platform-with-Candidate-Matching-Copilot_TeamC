import streamlit as st


def settings_page():

    st.title("Settings")

    st.caption(
        "Manage application preferences and recruiter settings."
    )

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(
        [
            "General",
            "Notifications",
            "About"
        ]
    )

    # ======================================
    # GENERAL
    # ======================================

    with tab1:

        st.subheader("Recruiter Profile")

        col1, col2 = st.columns(2)

        with col1:

            st.text_input(
                "Full Name",
                value="HR Recruiter"
            )

            st.text_input(
                "Email",
                value="recruiter@company.com"
            )

        with col2:

            st.text_input(
                "Company",
                value="ABC Technologies"
            )

            st.selectbox(
                "Department",
                [
                    "Human Resources",
                    "Engineering",
                    "Operations",
                    "Management"
                ]
            )

        st.markdown("---")

        st.subheader("Application")

        st.toggle(
            "Compact View",
            value=False
        )

        st.toggle(
            "Enable Notifications",
            value=True
        )

        st.toggle(
            "Enable AI Suggestions",
            value=True
        )

        st.button(
            "Save Settings",
            use_container_width=True
        )

    # ======================================
    # NOTIFICATIONS
    # ======================================

    with tab2:

        st.subheader("Notification Preferences")

        st.checkbox(
            "Interview Notifications",
            value=True
        )

        st.checkbox(
            "Candidate Updates",
            value=True
        )

        st.checkbox(
            "Offer Letter Alerts",
            value=True
        )

        st.checkbox(
            "Weekly Recruitment Summary",
            value=True
        )

        st.button(
            "Save Notification Preferences",
            use_container_width=True
        )

    # ======================================
    # ABOUT
    # ======================================

    with tab3:

        st.subheader("AI Recruitment & Talent Management Copilot")

        st.info(
            """
A frontend prototype built using **Python** and **Streamlit**.

### Features

- Dashboard
- Job Description Analyzer AI
- Resume Matching
- AI HR Assistant
- Candidate Ranking & Comparison
- Interview Management
- Talent Management
- AI Email Generator
- Settings

This application is designed for future integration with AI models and backend services.
"""
        )

        st.markdown("---")

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Version",
                "2.0"
            )

            st.metric(
                "Modules",
                "9"
            )

        with c2:

            st.metric(
                "Framework",
                "Streamlit"
            )

            st.metric(
                "Status",
                "Frontend Prototype"
            )

        st.success(
            "All settings are stored locally in this frontend prototype."
        )