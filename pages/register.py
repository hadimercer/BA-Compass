"""Public registration page for new BA Compass users."""

from __future__ import annotations

import streamlit as st

from components.auth import create_user, get_current_user, login_user
from components.ui import inject_css


st.set_page_config(page_title="BA Compass", layout="wide", initial_sidebar_state="expanded")

if st.session_state.get("pending_redirect"):
    st.session_state["pending_redirect"] = False
    if st.session_state.get("session_token"):
        st.query_params["token"] = st.session_state["session_token"]
    st.switch_page("pages/dashboard.py")
    st.stop()

inject_css()

auth_state_error = ""
try:
    existing_user = get_current_user()
except RuntimeError as exc:
    existing_user = None
    auth_state_error = str(exc)

if existing_user:
    st.switch_page("pages/dashboard.py")
    st.stop()

st.markdown("<div class='auth-shell'>", unsafe_allow_html=True)
left_col, center_col, right_col = st.columns([1, 1.2, 1])

with center_col:
    st.markdown(
        """
        <div class="auth-kicker">Create Your Workspace</div>
        <div class="auth-title">Start building with BA Compass</div>
        <p class="auth-subtitle">
            Create a secure account to manage project intake, keep your roadmap organized,
            and demonstrate BA craft through a polished portfolio app.
        </p>
        """,
        unsafe_allow_html=True,
    )

    error_message = auth_state_error
    with st.form("register_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Re-enter your password",
        )
        submitted = st.form_submit_button("Register", use_container_width=True)

    if submitted:
        if not email.strip() or not password or not confirm_password:
            error_message = "Complete every field before creating your account."
        elif "@" not in email:
            error_message = "Enter a valid email address."
        elif password != confirm_password:
            error_message = "Your passwords do not match."
        else:
            try:
                create_user(email, password)
                user = login_user(email, password)
            except ValueError as exc:
                error_message = str(exc)
            except RuntimeError as exc:
                error_message = str(exc)
            else:
                if user is None:
                    error_message = "Your account was created, but we couldn't sign you in automatically."
                else:
                    st.session_state["session_token"] = user["session_token"]
                    st.session_state["pending_redirect"] = True
                    st.rerun()

    if error_message:
        st.error(error_message)

    st.markdown(
        "<p class='auth-link-copy'>Already have an account?</p>",
        unsafe_allow_html=True,
    )
    st.page_link("pages/login.py", label="Login")

st.markdown("</div>", unsafe_allow_html=True)
