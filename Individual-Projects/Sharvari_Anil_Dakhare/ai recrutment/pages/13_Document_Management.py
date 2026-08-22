import os

import streamlit as st
from styles.theme import inject_global_styles
from components.sidebar import render_sidebar_branding, render_theme_toggle, render_nav, render_profile_card
from components.global_chat import render_global_chat
from components.header import page_header
from utils.auth import require_login
from services import database

st.set_page_config(page_title="Document Management | YourTalentPilot", layout="wide")

inject_global_styles()
require_login()
render_sidebar_branding()
render_theme_toggle()
render_nav()
render_profile_card()
page_header("Document Management", "Upload and manage employee documents")

database.init_db()
employees = database.get_all_employees()

if not employees:
    st.info("No employees yet. Onboard a selected candidate on the **Onboarding** page first.")
    st.page_link("pages/11_Onboarding.py", label="Go to Onboarding →")
    render_global_chat()
    st.stop()

DOC_TYPES = [
    "Payslip",
    "Previous Employment Document",
    "Resignation Letter",
    "Offer Letter",
    "ID Proof",
    "Educational Certificate",
    "Other",
]

emp_options = {f"{e['employee_code']} — {e['name']}": e for e in employees}
picked_label = st.selectbox("Select an employee", list(emp_options.keys()))
emp = emp_options[picked_label]

st.write("")

with st.container(border=True):
    st.markdown(f"**Upload a Document for {emp['name']}**")
    col1, col2 = st.columns([1, 2])
    with col1:
        doc_type = st.selectbox("Document Type", DOC_TYPES)
    with col2:
        uploaded = st.file_uploader(
            "File", type=["pdf", "docx", "doc", "jpg", "jpeg", "png"], key=f"doc_upload_{emp['id']}"
        )

    if st.button("Upload Document", type="primary", use_container_width=True):
        if not uploaded:
            st.error("Please choose a file first.")
        else:
            employee_dir = os.path.join(database.DOCUMENTS_DIR, emp["employee_code"])
            os.makedirs(employee_dir, exist_ok=True)
            safe_name = uploaded.name.replace("/", "_").replace("\\", "_")
            filepath = os.path.join(employee_dir, f"{doc_type.replace(' ', '_')}__{safe_name}")
            with open(filepath, "wb") as f:
                f.write(uploaded.getvalue())
            database.add_document(emp["id"], doc_type, uploaded.name, filepath)
            st.success(f"Uploaded **{uploaded.name}** as {doc_type}.")
            st.rerun()

st.write("")
st.markdown(f"**Documents on File — {emp['name']}**")

docs = database.get_documents_for_employee(emp["id"])
if not docs:
    st.info("No documents uploaded for this employee yet.")
else:
    for doc in docs:
        with st.container(border=True):
            cols = st.columns([1.4, 2.4, 1.4, 1, 1])
            cols[0].markdown(f"**{doc['doc_type']}**")
            cols[1].markdown(doc["filename"])
            cols[2].caption(doc["uploaded_at"])

            file_exists = os.path.exists(doc["filepath"])
            with cols[3]:
                if file_exists:
                    with open(doc["filepath"], "rb") as f:
                        st.download_button(
                            "Download", data=f.read(), file_name=doc["filename"],
                            key=f"dl_{doc['id']}", use_container_width=True,
                        )
                else:
                    st.caption("File missing")
            with cols[4]:
                if st.button("Delete", key=f"del_{doc['id']}", use_container_width=True):
                    database.delete_document(doc["id"])
                    st.rerun()

render_global_chat()
