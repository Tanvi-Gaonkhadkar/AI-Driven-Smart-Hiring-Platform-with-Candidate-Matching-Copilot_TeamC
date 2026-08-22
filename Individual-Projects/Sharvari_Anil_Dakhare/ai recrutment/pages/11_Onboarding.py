import datetime

import streamlit as st
from styles.theme import inject_global_styles
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from components.header import page_header
from utils.auth import require_login
from services import database

st.set_page_config(page_title="Onboarding | YourTalentPilot", layout="wide")

inject_global_styles()
require_login()
render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()
page_header("Onboarding", "Convert selected candidates into employees and move them into Talent Management")

database.init_db()

selected_candidates = [
    c for c in database.get_all_job_candidates()
    if c["status"] == "Selected" and not database.is_candidate_onboarded(c["id"])
]

if not selected_candidates:
    st.info(
        "No candidates awaiting onboarding. Mark a candidate's interview as **Selected** on the "
        "Interview Management page first."
    )
    st.page_link("pages/10_Interview_Scheduling.py", label="Go to Interview Management →")
else:
    st.markdown("**Ready for Onboarding**")
    for c in selected_candidates:
        with st.container(border=True):
            st.markdown(f"**{c['name']}** — {c['job_title']} (`{c['job_code']}`)")
            st.caption(f"Email: {c['email'] or '—'}  ·  ATS Score: {c['ats_score']}")

            with st.form(f"onboard_form_{c['id']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    department = st.text_input("Department", key=f"dept_{c['id']}")
                    designation = st.text_input("Designation", value=c["job_title"], key=f"desig_{c['id']}")
                with col2:
                    joining_date = st.date_input("Joining Date", value=datetime.date.today(), key=f"join_{c['id']}")
                    manager = st.text_input("Manager", key=f"mgr_{c['id']}")
                with col3:
                    performance_rating = st.slider(
                        "Initial Performance Rating", 1.0, 5.0, 3.0, 0.5, key=f"perf_{c['id']}"
                    )
                confirmed = st.form_submit_button("Convert to Employee", type="primary", use_container_width=True)

            if confirmed:
                if not department.strip() or not manager.strip():
                    st.error("Department and Manager are required.")
                else:
                    employee = database.create_employee(
                        candidate_id=c["id"],
                        name=c["name"],
                        email=c["email"],
                        department=department,
                        designation=designation,
                        joining_date=joining_date,
                        manager=manager,
                        performance_rating=performance_rating,
                    )
                    st.success(f"🎉 {c['name']} onboarded as **{employee['employee_code']}**. Now visible in Talent Management.")
                    st.rerun()

render_global_chat()
