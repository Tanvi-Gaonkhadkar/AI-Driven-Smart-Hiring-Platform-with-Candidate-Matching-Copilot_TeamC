import datetime

import streamlit as st
from styles.theme import inject_global_styles
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from components.header import page_header
from components.tables import styled_table
from utils.auth import require_login
from services import database, ai_service
import pandas as pd

st.set_page_config(page_title="Talent Management | YourTalentPilot", layout="wide")

inject_global_styles()
require_login()
render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()
page_header("Talent Management", "Manage employees after they join — profile, performance, and reviews")

database.init_db()
employees = database.get_all_employees()

if not employees:
    st.info("No employees yet. Onboard a selected candidate on the **Onboarding** page first.")
    st.page_link("pages/11_Onboarding.py", label="Go to Onboarding →")
    render_global_chat()
    st.stop()

st.markdown("**Employee Roster**")
df = pd.DataFrame([{
    "Employee ID": e["employee_code"],
    "Name": e["name"],
    "Department": e["department"],
    "Designation": e["designation"],
    "Joining Date": e["joining_date"],
    "Performance Rating": e["performance_rating"],
    "Manager": e["manager"],
} for e in employees])
styled_table(df)

st.write("")
st.markdown("**Employee Profile & Performance Review**")

emp_options = {f"{e['employee_code']} — {e['name']}": e for e in employees}
picked_label = st.selectbox("Select an employee", list(emp_options.keys()))
emp = emp_options[picked_label]

profile_col, review_col = st.columns([1, 1.4])

with profile_col:
    with st.container(border=True):
        st.markdown(f"### {emp['name']}")
        st.caption(f"{emp['designation']} · {emp['department']}")
        st.markdown(f"**Employee ID:** {emp['employee_code']}")
        st.markdown(f"**Manager:** {emp['manager']}")
        st.markdown(f"**Joining Date:** {emp['joining_date']}")
        st.markdown(f"**Email:** {emp['email'] or '—'}")

        with st.form(f"edit_employee_{emp['id']}"):
            st.markdown("**Edit Details**")
            new_department = st.text_input("Department", value=emp["department"])
            new_designation = st.text_input("Designation", value=emp["designation"])
            new_manager = st.text_input("Manager", value=emp["manager"])
            new_rating = st.slider("Performance Rating", 1.0, 5.0, float(emp["performance_rating"]), 0.5)
            save_clicked = st.form_submit_button("Save Changes", use_container_width=True)
        if save_clicked:
            database.update_employee(
                emp["id"], department=new_department, designation=new_designation,
                manager=new_manager, performance_rating=new_rating,
            )
            st.success("Updated.")
            st.rerun()

        st.page_link("pages/13_Document_Management.py", label="📁 Manage Documents →")

with review_col:
    with st.container(border=True):
        st.markdown("**AI Performance Review Assistant**")
        if not ai_service.is_configured():
            st.warning("Add a Gemini API key (or set AI_PROVIDER=ollama) in `.env` to enable AI reviews.")
        else:
            if st.button("Generate Performance Review", type="primary", use_container_width=True):
                # Pull skills from the employee's original candidate record if one exists
                skills = "Not specified"
                if emp["candidate_id"]:
                    candidate = database.get_job_candidate(emp["candidate_id"])
                    if candidate and candidate["matched_skills"]:
                        skills = candidate["matched_skills"].replace(",", ", ")

                try:
                    joined = datetime.date.fromisoformat(str(emp["joining_date"]))
                    experience_years = round((datetime.date.today() - joined).days / 365, 1)
                except Exception:
                    experience_years = 0

                with st.spinner("Generating performance review..."):
                    review = ai_service.generate_performance_review({
                        "name": emp["name"],
                        "role": emp["designation"],
                        "department": emp["department"],
                        "experience": experience_years,
                        "performance_rating": emp["performance_rating"],
                        "stage": "Active Employee",
                        "skills": skills,
                    })
                st.session_state[f"review_{emp['id']}"] = review

            review = st.session_state.get(f"review_{emp['id']}")
            if review:
                st.markdown("**Summary**")
                st.write(review.get("summary", ""))

                st.markdown("**Strengths**")
                for s in review.get("strengths", []):
                    st.markdown(f"- {s}")

                st.markdown("**Improvement Areas**")
                for a in review.get("improvement_areas", []):
                    st.markdown(f"- {a}")

                st.markdown("**Training Recommendations**")
                for t in review.get("training_recommendations", []):
                    st.markdown(f"- **{t.get('area', '')}:** {t.get('recommendation', '')}")

                st.markdown("**Career Growth**")
                st.write(review.get("career_growth", ""))

                st.markdown("**Manager Comment (ready to paste)**")
                st.text_area("Manager Comment", value=review.get("manager_comment", ""), height=140, label_visibility="collapsed")

render_global_chat()
