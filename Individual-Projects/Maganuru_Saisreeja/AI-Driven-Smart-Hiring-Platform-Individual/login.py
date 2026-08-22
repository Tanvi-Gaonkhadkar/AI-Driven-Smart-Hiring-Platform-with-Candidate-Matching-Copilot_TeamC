import streamlit as st


# Demo credentials — replace with real auth (DB / API) as needed
VALID_EMAIL = "admin@copilot.ai"
VALID_PASSWORD = "admin123"


def _inject_css():
    st.markdown(
        """
        <style>
        /* ---------- Global page cleanup ---------- */
        #MainMenu, header, footer {visibility: hidden;}
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
            max-width: 100% !important;
        }
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stHeader"] {
            background: #ffffff !important;
            color-scheme: light !important;
        }

        /* ---------- Left branding panel ---------- */
        .login-left {
            position: relative;
            overflow: hidden;
            height: 100vh;
            background: linear-gradient(160deg, #eef3ff 0%, #f7f9ff 55%, #ffffff 100%) !important;
            padding: 4rem 3rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            color-scheme: light;
        }
        .login-left::before {
            content: "";
            position: absolute;
            top: -120px;
            left: -120px;
            width: 320px;
            height: 320px;
            border-radius: 50%;
            background: rgba(59, 106, 255, 0.10);
        }
        .login-left::after {
            content: "";
            position: absolute;
            bottom: -160px;
            left: -80px;
            width: 380px;
            height: 380px;
            border-radius: 50%;
            background: rgba(59, 106, 255, 0.08);
        }
        .dots-grid {
            position: absolute;
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
        }
        .dots-grid span {
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: #c7d3f7;
            display: block;
        }
        .dots-top-right { top: 60px; right: 60px; }
        .dots-bottom-left { bottom: 60px; left: 60px; }

        .login-icon-box {
            width: 72px;
            height: 72px;
            border-radius: 18px;
            background: linear-gradient(135deg, #3b6aff, #2f56e0);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 34px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 24px rgba(59, 106, 255, 0.35);
            position: relative;
            z-index: 1;
        }
        .login-title {
            font-size: 2.6rem;
            font-weight: 800;
            color: #10204d;
            line-height: 1.15;
            margin-bottom: 1.2rem;
            position: relative;
            z-index: 1;
        }
        .login-underline {
            width: 64px;
            height: 4px;
            background: #3b6aff;
            border-radius: 4px;
            margin-bottom: 1.6rem;
            position: relative;
            z-index: 1;
        }
        .login-subtitle {
            font-size: 1.05rem;
            color: #6b7690;
            max-width: 420px;
            line-height: 1.55;
            position: relative;
            z-index: 1;
        }

        /* ---------- Right form panel ----------
           Streamlit doesn't let raw <div> tags from separate st.markdown()
           calls wrap widgets rendered in between, so we style the actual
           generated column containers instead. */
        div[data-testid="stHorizontalBlock"] {
            align-items: stretch;
        }
        div[data-testid="column"]:nth-of-type(1) {
            padding: 0 !important;
            background: #f7f9ff !important;
        }
        div[data-testid="column"]:nth-of-type(2) {
            background: #ffffff !important;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem 0 !important;
        }
        div[data-testid="column"]:nth-of-type(2) > div {
            width: 100%;
            max-width: 400px;
            margin: 0 auto;
        }
        .login-card {
            width: 100%;
        }
        .login-avatar {
            width: 76px;
            height: 76px;
            border-radius: 50%;
            background: #e8effe;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.2rem auto;
            font-size: 32px;
            color: #3b6aff;
        }
        .login-welcome {
            text-align: center;
            font-size: 1.8rem;
            font-weight: 800;
            color: #10204d;
            margin-bottom: 0.35rem;
        }
        .login-signin-text {
            text-align: center;
            color: #8892a6;
            margin-bottom: 1.8rem;
            font-size: 0.95rem;
        }

        /* Streamlit input styling */
        div[data-testid="stTextInput"] label,
        div[data-testid="stTextInput"] label p {
            font-weight: 600;
            color: #10204d !important;
            font-size: 0.9rem;
        }
        div[data-testid="stTextInput"] input {
            border-radius: 10px !important;
            border: 1.5px solid #e3e7f1 !important;
            padding: 0.65rem 0.9rem !important;
            background: #fbfcff !important;
            color: #10204d !important;
        }
        div[data-testid="stTextInput"] input::placeholder {
            color: #9aa3b8 !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #3b6aff !important;
            box-shadow: 0 0 0 2px rgba(59, 106, 255, 0.15) !important;
        }
        div[data-testid="stTextInput"] > div {
            background: transparent !important;
        }
        div[data-testid="stTextInputRootElement"] {
            background: #fbfcff !important;
            border-color: #e3e7f1 !important;
        }

        div[data-testid="stCheckbox"] label p {
            color: #4a5268 !important;
            font-size: 0.9rem;
        }

        div[data-testid="stFormSubmitButton"] {
            width: 100%;
        }
        div[data-testid="stFormSubmitButton"] button,
        button[data-testid^="stBaseButton-primary"],
        button[data-testid^="stBaseButton-secondary"] {
            width: 100% !important;
            background: linear-gradient(135deg, #4b7bff, #3b63ff);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.7rem 0;
            font-weight: 700;
            font-size: 1rem;
            margin-top: 0.6rem;
            box-shadow: 0 10px 20px rgba(59, 106, 255, 0.3);
        }
        div[data-testid="stFormSubmitButton"] button:hover,
        button[data-testid^="stBaseButton-primary"]:hover,
        button[data-testid^="stBaseButton-secondary"]:hover {
            background: linear-gradient(135deg, #3b63ff, #2c50e0);
            color: white;
        }
        div[data-testid="stFormSubmitButton"] button p,
        button[data-testid^="stBaseButton-primary"] p,
        button[data-testid^="stBaseButton-secondary"] p {
            color: white;
            font-weight: 700;
        }

        /* Password show/hide toggle icon — force light styling regardless of app theme */
        button[aria-label="Show password"],
        button[aria-label="Hide password"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: #8892a6 !important;
        }
        button[aria-label="Show password"] svg,
        button[aria-label="Hide password"] svg,
        button[aria-label="Show password"] svg path,
        button[aria-label="Hide password"] svg path {
            fill: #8892a6 !important;
            color: #8892a6 !important;
        }
        button[aria-label="Show password"]:hover,
        button[aria-label="Hide password"]:hover {
            background: rgba(59, 106, 255, 0.08) !important;
        }

        .forgot-link {
            text-align: right;
            margin-top: 0.6rem;
        }
        .forgot-link a {
            color: #3b6aff;
            font-size: 0.9rem;
            text-decoration: none;
            font-weight: 500;
        }
        .forgot-link a:hover { text-decoration: underline; }

        .login-footer {
            text-align: center;
            color: #a3aabd;
            font-size: 0.8rem;
            margin-top: 2rem;
            border-top: 1px solid #eef0f5;
            padding-top: 1.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _dots(css_class: str, rows: int = 4, cols: int = 5):
    spans = "".join("<span></span>" for _ in range(rows * cols))
    return f'<div class="dots-grid {css_class}">{spans}</div>'


def login_page():
    _inject_css()

    left, right = st.columns([1, 1], gap="small")

    with left:
        st.markdown(
            f"""
            <div class="login-left">
                {_dots("dots-top-right")}
                {_dots("dots-bottom-left")}
                <div class="login-icon-box">👥</div>
                <div class="login-title">AI Recruitment &amp;<br>Talent Management Copilot</div>
                <div class="login-underline"></div>
                <div class="login-subtitle">
                    Empowering HR teams to hire the right talent faster with
                    AI-driven insights and automation.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="login-card">
                <div class="login-avatar">👤</div>
                <div class="login-welcome">Welcome back!</div>
                <div class="login-signin-text">Sign in to continue to your account.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("📧  Email Address", placeholder="admin@copilot.ai")
            password = st.text_input("🔒  Password", placeholder="Enter password", type="password")
            remember_me = st.checkbox("Remember Me")

            submitted = st.form_submit_button("Login", type="primary", width="stretch")

            if submitted:
                if email == VALID_EMAIL and password == VALID_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.remember_me = remember_me
                    st.rerun()
                elif not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    st.error("Invalid email or password.")

        st.markdown(
            """
            <div class="forgot-link"><a href="#">Forgot Password?</a></div>
            <div class="login-footer">© 2026 AI Recruitment &amp; Talent Management Copilot<br>All rights reserved.</div>
            """,
            unsafe_allow_html=True,
        )