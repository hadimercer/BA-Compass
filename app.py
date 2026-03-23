"""BA Compass — single-entry-point router."""

from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="BA Compass", layout="wide", initial_sidebar_state="expanded")

from components.auth import get_current_user
from components.db import get_last_active_project
from components.ui import inject_css, render_sidebar

# Bootstrap — only runs on first load / refresh
if "page" not in st.session_state:
    # Rehydrate session token from query params before checking session state.
    # This restores the session after a browser refresh without requiring re-login.
    if not st.session_state.get("session_token"):
        from components.auth import _get_query_param_token, _get_user_by_token, _remove_query_param_token
        query_token = _get_query_param_token()
        if query_token:
            restored_user = _get_user_by_token(query_token)
            if restored_user is not None:
                st.session_state["session_token"] = query_token
            else:
                _remove_query_param_token()

    user = get_current_user()
    if user:
        st.session_state["_user"] = user
        st.session_state["page"] = "dashboard"
        if "active_project_id" not in st.session_state:
            pid = st.query_params.get("project_id")
            if not pid:
                try:
                    pid = get_last_active_project(user["user_id"])
                except RuntimeError:
                    pid = None
            if pid:
                st.session_state["active_project_id"] = str(pid)
        # Write token back to URL so the next refresh can rehydrate the session.
        if st.session_state.get("session_token"):
            st.query_params["token"] = st.session_state["session_token"]
    else:
        st.session_state["page"] = "login"

page = st.session_state.get("page", "login")
current_user = st.session_state.get("_user")

# CSS and sidebar — once, here, never inside render functions
if page in ("login", "register"):
    inject_css(hide_sidebar=True)
else:
    inject_css()
    if current_user:
        render_sidebar(page)

# Router
if page == "login":
    from pages.login import render; render()
elif page == "register":
    from pages.register import render; render()
elif page == "dashboard":
    from pages.dashboard import render; render(current_user)
elif page == "intake":
    from pages.project_intake import render; render(current_user)
elif page == "roadmap":
    from pages.roadmap import render; render(current_user)
elif page == "module":
    from pages.module_copilot import render; render(current_user)
elif page == "gap_analysis":
    from pages.gap_analysis import render; render(current_user)
elif page == "export":
    from pages.export import render; render(current_user)
else:
    st.session_state["page"] = "login"
    st.rerun()
