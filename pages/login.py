"""Public login page for BA Compass users."""

from __future__ import annotations

import streamlit as st

from components.auth import get_current_user, login_user


def render() -> None:
    auth_state_error = ""
    try:
        existing_user = get_current_user()
    except RuntimeError as exc:
        existing_user = None
        auth_state_error = str(exc)

    if existing_user:
        st.session_state["_user"] = existing_user
        st.session_state["page"] = "dashboard"
        st.rerun()
        return

    st.markdown("<div class='auth-shell'>", unsafe_allow_html=True)
    left_col, center_col, right_col = st.columns([1, 1.2, 1])

    with center_col:
        error_message = auth_state_error
        with st.form("login_form", clear_on_submit=False):
            st.markdown(
                """
                <div class="auth-kicker">Phase 1 Access</div>
                <div class="auth-title">Welcome back to BA Compass</div>
                <p class="auth-subtitle">
                    Sign in to resume your business analysis workspace, review project progress,
                    and launch the next engagement.
                </p>
                """,
                unsafe_allow_html=True,
            )
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if not email.strip() or not password:
                error_message = "Enter both your email and password to continue."
            else:
                try:
                    user = login_user(email, password)
                except RuntimeError as exc:
                    error_message = str(exc)
                else:
                    if user is None:
                        error_message = "We couldn't sign you in with those credentials."
                    else:
                        st.session_state["session_token"] = user["session_token"]
                        st.session_state["_user"] = user
                        st.session_state["page"] = "dashboard"
                        st.rerun()
                        return

        if error_message:
            st.error(error_message)

        st.markdown(
            "<p class='auth-link-copy'>Don't have an account yet?</p>",
            unsafe_allow_html=True,
        )
        if st.button("Register", key="goto_register"):
            st.session_state["page"] = "register"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
