"""
Recruiter / HR authentication.

Module 1 of the new HR workflow: only a logged-in recruiter can use the
system. Accounts live in the `recruiters` SQLite table (services/database.py).
Passwords are never stored in plain text - see _hash_password() below.

Usage - every page (including app.py) calls this as its very first
Streamlit action after st.set_page_config():

    from utils.auth import require_login
    require_login()

If nobody is logged in yet, this renders a full-page Login / Sign Up form
and calls st.stop(), so nothing else on the page executes. Once logged in,
st.session_state["auth_user"] holds the recruiter's id/username/full_name/
role for the rest of the session, and require_login() returns immediately
on every subsequent page.

A default account (username "admin", password "admin123") is seeded the
first time the app runs against an empty database, so there's always a way
in without a separate signup step. Recruiters can also self-register from
the Sign Up tab.
"""

import hashlib
import secrets

import streamlit as st

from services import database


def _hash_password(password: str, salt: str = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${digest.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, _ = stored_hash.split("$", 1)
    except ValueError:
        return False
    return secrets.compare_digest(_hash_password(password, salt), stored_hash)


def _seed_default_admin():
    if not database.any_recruiters_exist():
        database.create_recruiter(
            username="admin",
            password_hash=_hash_password("admin123"),
            full_name="Admin Recruiter",
            email="admin@yourtalentpilot.local",
            role="Admin",
        )


def current_user() -> dict:
    """Returns the logged-in recruiter's session record, or None."""
    return st.session_state.get("auth_user")


def logout():
    st.session_state.pop("auth_user", None)
    st.rerun()


def _do_login(username: str, password: str) -> bool:
    record = database.get_recruiter_by_username(username)
    if not record or not _verify_password(password, record["password_hash"]):
        return False
    st.session_state["auth_user"] = {
        "id": record["id"],
        "username": record["username"],
        "full_name": record["full_name"],
        "role": record["role"],
    }
    return True


def _render_login_page():
    st.markdown(
        "<div style='max-width:420px; margin: 60px auto 0 auto; text-align:center;'>"
        "<div style='font-size:44px;'>🧭</div>"
        "<div style='font-size:28px; font-weight:800; margin-top:6px;'>YourTalentPilot</div>"
        "<div style='opacity:0.7; margin-bottom:24px;'>Recruiter / HR sign-in required</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    center = st.columns([1, 1.4, 1])[1]
    with center:
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

        with login_tab:
            with st.form("login_form"):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                submitted = st.form_submit_button("Log In", use_container_width=True)
            if submitted:
                if _do_login(username, password):
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            st.caption("First time here? Default account — username `admin`, password `admin123`.")

        with signup_tab:
            with st.form("signup_form"):
                full_name = st.text_input("Full Name", key="signup_name")
                new_username = st.text_input("Choose a Username", key="signup_username")
                new_email = st.text_input("Work Email", key="signup_email")
                new_password = st.text_input("Choose a Password", type="password", key="signup_password")
                confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
                signed_up = st.form_submit_button("Create Account", use_container_width=True)
            if signed_up:
                if not full_name.strip() or not new_username.strip() or not new_password:
                    st.error("Full name, username, and password are all required.")
                elif new_password != confirm_password:
                    st.error("Passwords don't match.")
                elif database.get_recruiter_by_username(new_username):
                    st.error("That username is already taken.")
                else:
                    database.create_recruiter(
                        username=new_username,
                        password_hash=_hash_password(new_password),
                        full_name=full_name,
                        email=new_email,
                        role="Recruiter",
                    )
                    st.success("Account created — you can log in now from the Login tab.")


def require_login():
    """
    Call this as the first thing on every page, right after
    st.set_page_config() + inject_global_styles(). Blocks the rest of the
    page from rendering until a recruiter is logged in.
    """
    database.init_db()
    _seed_default_admin()

    if current_user():
        return

    _render_login_page()
    st.stop()
