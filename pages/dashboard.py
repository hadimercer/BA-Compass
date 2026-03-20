"""Protected dashboard for viewing and creating BA Compass projects."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from components.auth import require_auth
from components.db import run_query
from components.ui import inject_css, render_page_header, render_sidebar


st.set_page_config(page_title="BA Compass", layout="wide", initial_sidebar_state="expanded")

current_user = require_auth()

inject_css()
render_sidebar("dashboard")


def _greeting_for_utc_hour(hour: int) -> str:
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


def _badge_class(status: str | None) -> str:
    normalized = (status or "default").strip().lower().replace("_", "-")
    allowed = {"active", "complete", "in-progress", "skipped", "not-started"}
    return normalized if normalized in allowed else "default"


def _format_timestamp(value: object) -> str:
    if isinstance(value, datetime):
        return value.strftime("%b %d, %Y %H:%M UTC")
    return "Unknown"


render_page_header(
    f"{_greeting_for_utc_hour(datetime.utcnow().hour)}, {current_user['email']}",
    "Your BA Compass workspace keeps every engagement, classification, and roadmap in one place.",
)

project_error = ""
project_rows: list[dict[str, object]] = []

try:
    project_rows = run_query(
        """
        SELECT project_id, name, description, engagement_type, scale_tier, status, updated_at
        FROM projects
        WHERE user_id = %s
        ORDER BY updated_at DESC
        """,
        (current_user["user_id"],),
        fetch=True,
    ) or []
except RuntimeError as exc:
    project_error = str(exc)

with st.expander("New Project", expanded=False):
    st.markdown(
        "<p class='muted-copy'>Create a project shell, then continue into the intake stub to classify it later.</p>",
        unsafe_allow_html=True,
    )
    with st.form("new_project_form", clear_on_submit=True):
        project_name = st.text_input("Project Name", placeholder="Customer onboarding redesign")
        project_description = st.text_area(
            "Brief Description",
            placeholder="Optional context for what this project is trying to accomplish.",
            height=120,
        )
        create_project = st.form_submit_button("Create Project", use_container_width=True)

    if create_project:
        if not project_name.strip():
            st.error("Project Name is required.")
        else:
            try:
                inserted_rows = run_query(
                    """
                    INSERT INTO projects (user_id, name, description)
                    VALUES (%s, %s, %s)
                    RETURNING project_id
                    """,
                    (
                        current_user["user_id"],
                        project_name.strip(),
                        project_description.strip() or None,
                    ),
                    fetch=True,
                ) or []
            except RuntimeError as exc:
                st.error(str(exc))
            else:
                st.session_state["active_project_id"] = inserted_rows[0]["project_id"]
                st.switch_page("pages/project_intake.py")
                st.stop()

if project_error:
    st.error(project_error)
elif not project_rows:
    st.markdown(
        """
        <div class="empty-state">
            <h2>Your workspace is empty</h2>
            <p>
                BA Compass helps you create a project shell, capture project context, and organize
                the right business analysis work through a guided roadmap. Start with a new project
                to begin the portfolio flow.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    column_count = 3 if len(project_rows) > 2 else max(1, len(project_rows))
    columns = st.columns(column_count)

    for index, project in enumerate(project_rows):
        with columns[index % column_count]:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <h3>{project['name']}</h3>
                    <div class="card-meta"><strong>Engagement:</strong> {project.get('engagement_type') or 'Not yet classified'}</div>
                    <div class="card-meta"><strong>Scale Tier:</strong> {project.get('scale_tier') or 'Not sized yet'}</div>
                    <div class="status-badge {_badge_class(project.get('status'))}">{(project.get('status') or 'Active').replace('_', ' ').title()}</div>
                    <div class="card-meta"><strong>Last updated:</strong> {_format_timestamp(project.get('updated_at'))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Open Roadmap", key=f"open_project_{project['project_id']}", use_container_width=True):
                st.session_state["active_project_id"] = project["project_id"]
                st.switch_page("pages/roadmap.py")
                st.stop()
