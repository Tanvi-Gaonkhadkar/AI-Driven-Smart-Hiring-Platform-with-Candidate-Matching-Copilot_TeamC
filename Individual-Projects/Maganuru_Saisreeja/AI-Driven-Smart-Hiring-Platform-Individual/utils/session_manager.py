import streamlit as st


def initialize_session():

    defaults = {
        "candidates": [],
        "job_description": "",
        "employees": [],
        "emails": [],
        "interviews": []
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value