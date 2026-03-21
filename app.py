"""BA Compass — single-entry-point router."""

from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="BA Compass", layout="wide", initial_sidebar_state="expanded")

from components.auth import get_current_user
from components.db import get_last_active_project
from components.ui import inject_css, render_sidebar

# Bootstrap — only runs on first load / refresh
if "page" not in st.session_state:
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
