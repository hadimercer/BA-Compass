"""Roadmap navigator — the home base for an active BA Compass project."""

from __future__ import annotations

from collections import defaultdict

import streamlit as st

from components.auth import require_auth
from components.db import run_query
from components.ui import inject_css, render_page_header, render_sidebar


st.set_page_config(page_title="BA Compass", layout="wide", initial_sidebar_state="expanded")

current_user = require_auth()
inject_css()
render_sidebar("roadmap")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_project(project_id: str) -> dict | None:
    rows = run_query(
        """
        SELECT project_id, name, description, engagement_type, scale_tier, status
        FROM projects
        WHERE project_id = %s AND user_id = %s
        LIMIT 1
        """,
        (project_id, current_user["user_id"]),
        fetch=True,
    )
    return dict(rows[0]) if rows else None


def _load_roadmap(project_id: str) -> list[dict]:
    rows = run_query(
        """
        SELECT
            pri.roadmap_item_id,
            pri.module_id,
            pri.sequence_order,
            pri.status,
            m.name,
            m.knowledge_area,
            m.description
        FROM project_roadmap_items pri
        JOIN modules m ON m.module_id = pri.module_id
        WHERE pri.project_id = %s
        ORDER BY pri.sequence_order
        """,
        (project_id,),
        fetch=True,
    )
    return [dict(r) for r in rows]


def _update_status(roadmap_item_id: str, new_status: str) -> None:
    run_query(
        "UPDATE project_roadmap_items SET status = %s WHERE roadmap_item_id = %s",
        (new_status, roadmap_item_id),
        fetch=False,
    )


def _status_badge(status: str) -> str:
    labels = {
        "not_started": "Not Started",
        "in_progress": "In Progress",
        "complete": "Complete",
        "skipped": "Skipped",
    }
    css_map = {
        "not_started": "m-badge-not-started",
        "in_progress":  "m-badge-in-progress",
        "complete":     "m-badge-complete",
        "skipped":      "m-badge-skipped",
    }
    label = labels.get(status, status.replace("_", " ").title())
    css = css_map.get(status, "m-badge-not-started")
    return f"<span class='m-badge {css}'>{label}</span>"


def _progress_bar_html(pct: int) -> str:
    return (
        f"<div class='progress-track'>"
        f"<div class='progress-fill' style='width:{pct}%;'></div>"
        f"</div>"
    )


# ── Resolve active project ────────────────────────────────────────────────────

project_id = st.query_params.get("project_id") or st.session_state.get("active_project_id")
if not project_id:
    st.error("No project selected. Return to the dashboard and open a project.")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/dashboard.py")
    st.stop()

project_id = str(project_id)
st.query_params["project_id"] = project_id
st.session_state["active_project_id"] = project_id

project = _load_project(project_id)
if not project:
    st.error("Project not found.")
    st.stop()

# Redirect to intake if not yet classified
if not project.get("engagement_type"):
    st.info("This project has not been classified yet.")
    if st.button("Start Intake"):
        st.switch_page("pages/project_intake.py")
    st.stop()

roadmap = _load_roadmap(project_id)

if not roadmap:
    st.warning("No roadmap found for this project.")
    if st.button("Go to Intake to generate roadmap"):
        st.switch_page("pages/project_intake.py")
    st.stop()

# ── Progress stats ────────────────────────────────────────────────────────────

total = len(roadmap)
complete_count = sum(1 for m in roadmap if m["status"] == "complete")
in_progress_count = sum(1 for m in roadmap if m["status"] == "in_progress")
skipped_count = sum(1 for m in roadmap if m["status"] == "skipped")
done_count = complete_count + skipped_count
pct = round(done_count / total * 100) if total else 0

# ── Project header ────────────────────────────────────────────────────────────

render_page_header(
    project["name"],
    f"{project['engagement_type']}  ·  {project['scale_tier']} scale",
)

stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
with stats_col1:
    st.metric("Total Modules", total)
with stats_col2:
    st.metric("Complete", complete_count)
with stats_col3:
    st.metric("In Progress", in_progress_count)
with stats_col4:
    st.metric("Remaining", total - done_count - in_progress_count)

st.markdown(
    f"<div style='margin-bottom:0.2rem;font-size:0.82rem;color:var(--text-secondary);'>"
    f"Overall progress — {pct}%</div>"
    + _progress_bar_html(pct)
    + "<div style='margin-bottom:1.4rem;'></div>",
    unsafe_allow_html=True,
)

# ── Module grid grouped by knowledge area ─────────────────────────────────────

# Group modules by knowledge area preserving sequence order
grouped: dict[str, list[dict]] = defaultdict(list)
ka_order: list[str] = []
for item in roadmap:
    ka = item["knowledge_area"]
    if ka not in ka_order:
        ka_order.append(ka)
    grouped[ka].append(item)

for ka in ka_order:
    st.markdown(f"<div class='ka-header'>{ka}</div>", unsafe_allow_html=True)

    items = grouped[ka]
    # 3-column grid
    cols = st.columns(3)

    for idx, item in enumerate(items):
        item_id = str(item["roadmap_item_id"])
        module_id = str(item["module_id"])
        name = item["name"]
        desc = item.get("description") or ""
        status = item["status"]

        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="module-card">
                    {_status_badge(status)}
                    <div class="module-card-name">{name}</div>
                    <div class="module-card-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Action buttons
            btn_cols = st.columns([2, 1, 1])

            with btn_cols[0]:
                if st.button("Enter Module", key=f"enter_{item_id}", use_container_width=True):
                    st.session_state["active_module_id"] = module_id
                    st.session_state["active_roadmap_item_id"] = item_id
                    st.query_params["module_id"] = module_id
                    st.query_params["roadmap_item_id"] = item_id
                    st.switch_page("pages/module_copilot.py")
                    st.stop()

            with btn_cols[1]:
                if status != "complete":
                    if st.button("✓", key=f"complete_{item_id}", use_container_width=True, help="Mark Complete"):
                        _update_status(item_id, "complete")
                        st.rerun()
                else:
                    if st.button("↩", key=f"reopen_{item_id}", use_container_width=True, help="Reopen"):
                        _update_status(item_id, "not_started")
                        st.rerun()

            with btn_cols[2]:
                if status != "skipped":
                    if st.button("–", key=f"skip_{item_id}", use_container_width=True, help="Mark Skipped"):
                        _update_status(item_id, "skipped")
                        st.rerun()
