"""Roadmap navigator — the home base for an active BA Compass project."""

from __future__ import annotations

import streamlit as st

from components.db import run_query
from components.ui import render_page_header


def render(current_user: dict) -> None:

    # ── Transparent row-button overlay CSS ───────────────────────────────────
    st.markdown("""<style>
    /* Row entry overlay — -108px = row height (72px) + observed column-internal gap (36px) */
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="stColumn"]:first-child div[data-testid="stButton"] button,
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="column"]:first-child div[data-testid="stButton"] button {
        height:72px !important; margin-top:-108px !important; background:transparent !important;
        border:none !important; color:transparent !important; border-radius:10px !important;
        box-shadow:none !important;
    }
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="stColumn"]:first-child div[data-testid="stButton"] button:hover,
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="column"]:first-child div[data-testid="stButton"] button:hover {
        background:rgba(74,159,212,0.06) !important; cursor:pointer;
    }
    /* ··· popover — col_menu starts at same Y as the row card, no offset needed */
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="stColumn"]:last-child button,
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="column"]:last-child button {
        height:72px !important; margin-top:0 !important; background:transparent !important;
        border:none !important; box-shadow:none !important; border-radius:10px !important;
        color:rgba(139,156,189,0.55) !important; font-size:1rem !important;
        letter-spacing:0.05em !important;
    }
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="stColumn"]:last-child button:hover,
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="column"]:last-child button:hover {
        background:rgba(74,159,212,0.06) !important;
        color:rgba(139,156,189,0.9) !important; cursor:pointer;
    }
    /* Inter-row spacing */
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"] {
        margin-bottom: 0.35rem;
    }
    </style>""", unsafe_allow_html=True)

    # ── Helpers ───────────────────────────────────────────────────────────────

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

    def _progress_bar_html(pct: int) -> str:
        return (
            f"<div class='progress-track'>"
            f"<div class='progress-fill' style='width:{pct}%;'></div>"
            f"</div>"
        )

    # ── Resolve active project ────────────────────────────────────────────────

    project_id = st.session_state.get("active_project_id")
    if not project_id:
        # Try restoring from query params on refresh
        qp = st.query_params.get("project_id")
        if qp:
            project_id = str(qp)
            st.session_state["active_project_id"] = project_id

    if not project_id:
        st.error("No project selected. Return to the dashboard and open a project.")
        if st.button("Go to Dashboard"):
            st.session_state["page"] = "dashboard"
            st.rerun()
        return

    project_id = str(project_id)

    project = _load_project(project_id)
    if not project:
        st.error("Project not found.")
        return

    # Keep project name in session state for sidebar display
    if not st.session_state.get("active_project_name"):
        st.session_state["active_project_name"] = project["name"]

    # Redirect to intake if not yet classified
    if not project.get("engagement_type"):
        st.info("This project has not been classified yet.")
        if st.button("Start Intake"):
            st.session_state["page"] = "intake"
            st.rerun()
        return

    roadmap = _load_roadmap(project_id)

    if not roadmap:
        st.warning("No roadmap found for this project.")
        if st.button("Go to Intake to generate roadmap"):
            st.session_state["page"] = "intake"
            st.rerun()
        return

    # ── Artifact lookup ───────────────────────────────────────────────────────

    raw_arts = run_query(
        """SELECT DISTINCT ON (a.module_id) a.module_id, a.version, m.name AS module_name
           FROM artifacts a JOIN modules m ON m.module_id = a.module_id
           WHERE a.project_id = %s ORDER BY a.module_id, a.version DESC""",
        (project_id,), fetch=True,
    ) or []
    artifact_by_module = {str(a["module_id"]): a for a in raw_arts}

    # ── Progress stats ────────────────────────────────────────────────────────

    total = len(roadmap)
    complete_count = sum(1 for m in roadmap if m["status"] == "complete")
    in_progress_count = sum(1 for m in roadmap if m["status"] == "in_progress")
    skipped_count = sum(1 for m in roadmap if m["status"] == "skipped")
    done_count = complete_count + skipped_count
    pct = round(done_count / total * 100) if total else 0

    # ── Project header ────────────────────────────────────────────────────────

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

    # ── Module rows (sorted by sequence_order) ───────────────────────────────

    for item in roadmap:
        item_id = str(item["roadmap_item_id"])
        module_id = str(item["module_id"])
        name = item["name"]
        status = item["status"]
        seq = item["sequence_order"]

        dot_color = {
            "not_started": "#6B7280",
            "in_progress": "#4A9FD4",
            "complete": "#10B981",
            "skipped": "rgba(139,156,189,0.35)",
        }.get(status, "#6B7280")

        row_bg = "rgba(16,185,129,0.05)" if status == "complete" else "rgba(30,37,56,0.6)"
        left_border = "3px solid #10B981" if status == "complete" else "1px solid rgba(45,53,80,0.6)"

        artifact_sub = ""
        if status == "complete":
            art = artifact_by_module.get(module_id)
            if art:
                artifact_sub = (
                    f"<div style='font-size:0.72rem;color:#6EE7B7;margin-top:0.1rem;'>"
                    f"Artifact v{art['version']}: {art['module_name']}"
                    f"</div>"
                )

        col_enter, col_menu = st.columns([11, 1])
        with col_enter:
            # Card rendered first, button second — button overlays card via margin-top:-72px
            st.markdown(f"""
            <div style="display:flex;align-items:center;padding:0.65rem 1rem;border-radius:10px;
                border-left:{left_border};border-top:1px solid rgba(45,53,80,0.6);
                border-right:1px solid rgba(45,53,80,0.6);border-bottom:1px solid rgba(45,53,80,0.6);
                background:{row_bg};height:72px;pointer-events:none;">
              <span style="font-size:0.7rem;color:#8B9CBD;min-width:1.4rem;margin-right:0.6rem;">{seq}</span>
              <span style="width:10px;height:10px;border-radius:50%;background:{dot_color};
                           flex-shrink:0;margin-right:0.75rem;display:inline-block;"></span>
              <div style="flex:1;min-width:0;">
                <div style="font-weight:600;font-size:0.9rem;color:#F0F4F8;white-space:nowrap;
                            overflow:hidden;text-overflow:ellipsis;">{name}</div>
                <div style="font-size:0.72rem;color:#8B9CBD;">{item['knowledge_area']}</div>
                {artifact_sub}
              </div>
            </div>""", unsafe_allow_html=True)
            if st.button(" ", key=f"enter_{item_id}", use_container_width=True):
                st.session_state["active_module_id"] = module_id
                st.session_state["active_roadmap_item_id"] = item_id
                st.session_state["page"] = "module"
                st.rerun()
        with col_menu:
            with st.popover("···"):
                if status in ("not_started", "in_progress"):
                    if st.button("Mark Complete", key=f"mc_{item_id}", use_container_width=True):
                        _update_status(item_id, "complete")
                        st.rerun()
                    if st.button("Mark Skipped", key=f"ms_{item_id}", use_container_width=True):
                        _update_status(item_id, "skipped")
                        st.rerun()
                elif status == "complete":
                    if st.button("Reopen & Revise", key=f"rr_{item_id}", use_container_width=True):
                        _update_status(item_id, "in_progress")
                        st.rerun()
                    if st.button("Mark Skipped", key=f"ms_{item_id}", use_container_width=True):
                        _update_status(item_id, "skipped")
                        st.rerun()
                elif status == "skipped":
                    if st.button("Reopen", key=f"ro_{item_id}", use_container_width=True):
                        _update_status(item_id, "not_started")
                        st.rerun()
