import streamlit as st
from database.database import get_user
import extra_streamlit_components as stx
from datetime import datetime, timedelta
import json

st.set_page_config(
    page_title="AI-Driven Hiring Copilot",
    page_icon="🤖",
    layout="wide"
)
st.markdown(
    """
    <style>
        /* Hide Streamlit sidebar/navigation on Login page */
        [data-testid="stSidebar"] {
            display: none;
        }

        /* Remove the left margin created by the sidebar */
        [data-testid="stAppViewContainer"] {
            margin-left: 0;
        }

        /* Hide the sidebar collapse button */
        [data-testid="stSidebarCollapsedControl"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# SESSION STATE
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "name" not in st.session_state:
    st.session_state.name = None

if "role" not in st.session_state:
    st.session_state.role = None


# -----------------------------
# PERSISTENT LOGIN COOKIE
# -----------------------------
cookie_manager = stx.CookieManager()

login_cookie = cookie_manager.get("artm_user")

if login_cookie and not st.session_state.logged_in:

    try:
        saved_user = json.loads(login_cookie)

        st.session_state.logged_in = True
        st.session_state.user = saved_user["email"]
        st.session_state.name = saved_user["name"]
        st.session_state.role = saved_user["role"]

    except Exception:
        st.session_state.logged_in = False

# -----------------------------
# IF ALREADY LOGGED IN
# -----------------------------
if st.session_state.logged_in:
    st.switch_page("pages/1_Dashboard.py")

# -----------------------------
# LANDING PAGE
# -----------------------------
st.markdown(
"""
<h1 style='text-align:center;'>
🤖 Al-Driven Smart Hiring Platform with Candidate Matching Copilot
</h1>

<h4 style='text-align:center;color:gray;'>
AI-Powered Intelligent Hiring Platform
</h4>
""",
unsafe_allow_html=True
)

st.write("")

c1, c2, c3 = st.columns(3)

with c1:
    st.success("📄 Resume Analyzer")

with c2:
    st.success("👥 Candidate Screening")

with c3:
    st.success("🎤 Interview Copilot")

c4, c5, c6 = st.columns(3)

with c4:
    st.success("📊 Hiring Analytics")

with c5:
    st.success("🤖 AI Assistant")

with c6:
    st.success("⭐ AI Recommendations")

st.write("")
st.divider()

left, center, right = st.columns([1, 2, 1])

with center:

    st.subheader("🔐 Login")

    role = st.selectbox(
        "Login As",
        ["Recruiter", "HR"]
    )

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login", use_container_width=True):

        user = get_user(email, password)

        if user:

            db_role = user[4]      # role column

            if db_role == role:

                st.session_state.logged_in = True
                st.session_state.user = user[2]
                st.session_state.name = user[1]
                st.session_state.role = db_role

                # Keep user logged in
                

                cookie_manager.set(
                    "artm_user",
                    json.dumps({
                        "email": user[2],
                        "name": user[1],
                        "role": db_role
                    }),
                    expires_at=datetime.now() + timedelta(hours=24)
                )

                st.switch_page("pages/1_Dashboard.py")

            else:
                st.error("Selected role does not match your account.")

        else:
            st.error("Invalid Email or Password") 
st.divider()

st.caption(
    "© 2026 AI Recruitment & Talent Acquisition Copilot | Infosys Springboard Virtual Internship 7.0"
)