"""Gap analysis and traceability matrix for a BA Compass project."""

from __future__ import annotations

import streamlit as st

from components.ai import call_openai
from components.db import run_query
from components.ui import render_page_header
from prompts.gap_analysis import build_gap_analysis_messages, parse_gap_response


def render(current_user: dict) -> None:

    # ── Data loaders ──────────────────────────────────────────────────────────

    def _load_project(project_id: str) -> dict | None:
        rows = run_query(
            "SELECT project_id, name, engagement_type, scale_tier FROM projects WHERE project_id = %s AND user_id = %s LIMIT 1",
            (project_id, current_user["user_id"]),
            fetch=True,
        )
        return dict(rows[0]) if rows else None

    def _load_dimensions(project_id: str) -> list[dict]:
        rows = run_query(
            "SELECT dimension_name, dimension_value FROM project_dimensions WHERE project_id = %s",
            (project_id,),
            fetch=True,
        )
        return [dict(r) for r in rows]

    def _load_roadmap_with_modules(project_id: str) -> list[dict]:
        rows = run_query(
            """
            SELECT pri.roadmap_item_id, pri.status, pri.sequence_order,
                   m.name AS module_name, m.knowledge_area, m.module_id
            FROM project_roadmap_items pri
            JOIN modules m ON m.module_id = pri.module_id
            WHERE pri.project_id = %s
            ORDER BY pri.sequence_order
            """,
            (project_id,),
            fetch=True,
        )
        return [dict(r) for r in rows]

    def _load_all_artifacts(project_id: str) -> list[dict]:
        """Return latest version of each module's artifact for this project."""
        rows = run_query(
            """
            SELECT DISTINCT ON (a.module_id)
                a.artifact_id, a.module_id, a.artifact_type,
                a.content, a.version, a.created_at,
                m.name AS module_name, m.knowledge_area
            FROM artifacts a
            JOIN modules m ON m.module_id = a.module_id
            WHERE a.project_id = %s
            ORDER BY a.module_id, a.version DESC
            """,
            (project_id,),
            fetch=True,
        )
        return [dict(r) for r in rows]

    # ── Resolve project ───────────────────────────────────────────────────────

    project_id = st.session_state.get("active_project_id")
    if not project_id:
        st.error("No project selected. Return to the dashboard.")
        if st.button("Go to Dashboard"):
            st.session_state["page"] = "dashboard"
            st.rerun()
        return

    project_id = str(project_id)

    project = _load_project(project_id)
    if not project:
        st.error("Project not found.")
        return

    render_page_header(
        project["name"],
        "Gap analysis and requirements traceability",
    )

    # ── Tabs ──────────────────────────────────────────────────────────────────

    tab_gap, tab_trace = st.tabs(["Gap Analysis", "Traceability Matrix"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — GAP ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════

    with tab_gap:
        gap_key = f"gap_result_{project_id}"
        dimensions = _load_dimensions(project_id)
        roadmap_items = _load_roadmap_with_modules(project_id)
        artifacts = _load_all_artifacts(project_id)

        complete_count = sum(1 for r in roadmap_items if r["status"] == "complete")
        artifact_count = len(artifacts)

        # Status summary
        st.markdown(
            f"""
            <div style="display:flex;gap:1rem;margin-bottom:1.2rem;flex-wrap:wrap;">
              <div style="background:rgba(30,37,56,0.9);border:1px solid rgba(45,53,80,0.9);
                          border-radius:12px;padding:0.7rem 1.1rem;flex:1;min-width:120px;text-align:center;">
                <div style="font-size:1.5rem;font-weight:700;color:#F0F4F8;">{len(roadmap_items)}</div>
                <div style="font-size:0.75rem;color:#8B9CBD;">Modules in roadmap</div>
              </div>
              <div style="background:rgba(30,37,56,0.9);border:1px solid rgba(45,53,80,0.9);
                          border-radius:12px;padding:0.7rem 1.1rem;flex:1;min-width:120px;text-align:center;">
                <div style="font-size:1.5rem;font-weight:700;color:#A7F3D0;">{complete_count}</div>
                <div style="font-size:0.75rem;color:#8B9CBD;">Modules complete</div>
              </div>
              <div style="background:rgba(30,37,56,0.9);border:1px solid rgba(45,53,80,0.9);
                          border-radius:12px;padding:0.7rem 1.1rem;flex:1;min-width:120px;text-align:center;">
                <div style="font-size:1.5rem;font-weight:700;color:#B9DEFF;">{artifact_count}</div>
                <div style="font-size:0.75rem;color:#8B9CBD;">Artifacts saved</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if artifact_count == 0:
            st.info("Complete at least one module and save an artifact before running gap analysis.")
        else:
            run_col, _ = st.columns([1, 2])
            with run_col:
                run_btn = st.button("Run Gap Analysis", use_container_width=True)

            if run_btn:
                messages = build_gap_analysis_messages(project, dimensions, roadmap_items, artifacts)
                with st.spinner("Analysing your engagement package — this may take 15-20 seconds..."):
                    try:
                        raw = call_openai(messages, temperature=0.2)
                        result = parse_gap_response(raw)
                    except RuntimeError as exc:
                        st.error(str(exc))
                        return
                st.session_state[gap_key] = result
                st.rerun()

            result = st.session_state.get(gap_key)

            if result:
                findings = result.get("findings", [])
                score = result.get("completeness_score", 0)
                assessment = result.get("overall_assessment", "")

                # Overall assessment card
                score_color = "#10B981" if score >= 70 else "#F59E0B" if score >= 40 else "#EF4444"
                st.markdown(
                    f"""
                    <div style="background:rgba(26,31,46,0.95);border:1px solid rgba(45,53,80,0.9);
                                border-radius:16px;padding:1.2rem 1.4rem;margin-bottom:1.2rem;">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;">
                            <div style="flex:1;">
                                <div style="font-size:0.72rem;color:#4A9FD4;letter-spacing:0.07em;
                                             text-transform:uppercase;margin-bottom:0.5rem;">Overall Assessment</div>
                                <div style="font-size:0.92rem;color:#F0F4F8;line-height:1.65;">{assessment}</div>
                            </div>
                            <div style="text-align:center;min-width:72px;">
                                <div style="font-size:2rem;font-weight:700;color:{score_color};">{score}</div>
                                <div style="font-size:0.7rem;color:#8B9CBD;">/ 100</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if not findings:
                    st.success("No significant gaps found. Your engagement package looks complete.")
                else:
                    # Group by severity
                    severity_order = ["high", "medium", "low"]
                    severity_cfg = {
                        "high":   {"label": "High Priority",   "color": "#EF4444", "bg": "rgba(239,68,68,0.08)",   "border": "rgba(239,68,68,0.3)"},
                        "medium": {"label": "Medium Priority",  "color": "#F59E0B", "bg": "rgba(245,158,11,0.08)",  "border": "rgba(245,158,11,0.3)"},
                        "low":    {"label": "Low Priority",     "color": "#8B9CBD", "bg": "rgba(139,156,189,0.08)", "border": "rgba(139,156,189,0.25)"},
                    }
                    gap_type_labels = {
                        "missing": "Missing",
                        "incomplete": "Incomplete",
                        "inconsistent": "Inconsistent",
                        "recommended": "Recommended",
                    }

                    grouped: dict[str, list] = {s: [] for s in severity_order}
                    for f in findings:
                        sev = f.get("severity", "low")
                        grouped.setdefault(sev, []).append(f)

                    for sev in severity_order:
                        group = grouped.get(sev, [])
                        if not group:
                            continue
                        cfg = severity_cfg[sev]
                        st.markdown(
                            f"<div style='font-size:0.78rem;font-weight:700;color:{cfg['color']};"
                            f"letter-spacing:0.06em;text-transform:uppercase;"
                            f"margin:1rem 0 0.6rem;'>{cfg['label']} ({len(group)})</div>",
                            unsafe_allow_html=True,
                        )
                        for f in group:
                            gap_type = gap_type_labels.get(f.get("gap_type", ""), f.get("gap_type", ""))
                            module_ref = f.get("module_reference", "")
                            finding = f.get("finding", "")
                            recommendation = f.get("recommendation", "")
                            st.markdown(
                                f"""
                                <div style="background:{cfg['bg']};border:1px solid {cfg['border']};
                                            border-radius:14px;padding:0.9rem 1.1rem;margin-bottom:0.6rem;">
                                    <div style="display:flex;justify-content:space-between;
                                                 align-items:center;margin-bottom:0.45rem;">
                                        <span style="font-size:0.82rem;font-weight:600;color:{cfg['color']};">
                                            {module_ref}
                                        </span>
                                        <span style="font-size:0.7rem;color:#8B9CBD;
                                                      background:rgba(139,156,189,0.12);
                                                      border:1px solid rgba(139,156,189,0.2);
                                                      border-radius:999px;padding:0.1rem 0.5rem;">
                                            {gap_type}
                                        </span>
                                    </div>
                                    <div style="font-size:0.88rem;color:#F0F4F8;
                                                 margin-bottom:0.45rem;line-height:1.55;">{finding}</div>
                                    <div style="font-size:0.82rem;color:#8B9CBD;line-height:1.5;">
                                        <strong style="color:rgba(240,244,248,0.7);">Recommendation:</strong> {recommendation}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)
                if st.button("Re-run Analysis", use_container_width=False):
                    st.session_state.pop(gap_key, None)
                    st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — TRACEABILITY MATRIX
    # ══════════════════════════════════════════════════════════════════════════

    with tab_trace:
        roadmap_items = _load_roadmap_with_modules(project_id)
        artifacts = _load_all_artifacts(project_id)

        # Build lookup: module_id → artifact
        artifact_by_module: dict[str, dict] = {str(a["module_id"]): a for a in artifacts}

        # Build lookup: module_id → roadmap status
        status_by_module: dict[str, str] = {str(r["module_id"]): r["status"] for r in roadmap_items}

        # Identify orphan artifacts (saved but module no longer in roadmap)
        roadmap_module_ids = {str(r["module_id"]) for r in roadmap_items}
        orphans = [a for a in artifacts if str(a["module_id"]) not in roadmap_module_ids]

        if not roadmap_items:
            st.info("No roadmap found for this project.")
        else:
            status_icon = {
                "not_started": "○",
                "in_progress": "◑",
                "complete": "●",
                "skipped": "—",
            }
            status_color = {
                "not_started": "#8B9CBD",
                "in_progress": "#4A9FD4",
                "complete": "#10B981",
                "skipped": "#F59E0B",
            }

            # Group roadmap items by knowledge area
            from collections import defaultdict
            grouped_trace: dict[str, list] = defaultdict(list)
            ka_order: list[str] = []
            for item in roadmap_items:
                ka = item["knowledge_area"]
                if ka not in ka_order:
                    ka_order.append(ka)
                grouped_trace[ka].append(item)

            for ka in ka_order:
                st.markdown(
                    f"<div class='ka-header'>{ka}</div>",
                    unsafe_allow_html=True,
                )
                for item in grouped_trace[ka]:
                    mid = str(item["module_id"])
                    status = item["status"]
                    artifact = artifact_by_module.get(mid)
                    icon = status_icon.get(status, "○")
                    color = status_color.get(status, "#8B9CBD")

                    artifact_cell = (
                        f"<span style='color:#A7F3D0;'>v{artifact['version']} saved</span>"
                        if artifact
                        else "<span style='color:#8B9CBD;'>—</span>"
                    )

                    st.markdown(
                        f"""
                        <div style="display:flex;align-items:center;gap:0.75rem;
                                    padding:0.5rem 0.6rem;border-radius:10px;
                                    margin-bottom:0.25rem;background:rgba(30,37,56,0.6);
                                    border:1px solid rgba(45,53,80,0.6);">
                            <span style="font-size:1rem;color:{color};min-width:1.1rem;">{icon}</span>
                            <span style="flex:1;font-size:0.88rem;color:#F0F4F8;">{item['module_name']}</span>
                            <span style="font-size:0.8rem;">{artifact_cell}</span>
                            <span style="font-size:0.75rem;color:{color};min-width:80px;text-align:right;">
                                {status.replace('_',' ').title()}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Coverage summary
            with_artifact = sum(1 for r in roadmap_items if str(r["module_id"]) in artifact_by_module)
            total = len(roadmap_items)
            st.markdown(
                f"""
                <div style="margin-top:1rem;padding:0.75rem 1rem;background:rgba(26,31,46,0.9);
                            border:1px solid rgba(45,53,80,0.8);border-radius:12px;
                            font-size:0.85rem;color:#8B9CBD;">
                    {with_artifact} of {total} modules have saved artifacts
                    &nbsp;·&nbsp;
                    {sum(1 for r in roadmap_items if r['status']=='complete')} complete
                    &nbsp;·&nbsp;
                    {sum(1 for r in roadmap_items if r['status']=='in_progress')} in progress
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Orphan artifacts
            if orphans:
                st.markdown(
                    "<div style='margin-top:1.2rem;font-size:0.78rem;font-weight:700;"
                    "color:#F59E0B;letter-spacing:0.06em;text-transform:uppercase;"
                    "margin-bottom:0.5rem;'>Orphaned Artifacts</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    "<div style='font-size:0.82rem;color:#8B9CBD;margin-bottom:0.6rem;'>"
                    "These artifacts were saved for modules no longer in the roadmap.</div>",
                    unsafe_allow_html=True,
                )
                for a in orphans:
                    st.markdown(
                        f"""
                        <div style="padding:0.5rem 0.75rem;border-radius:10px;margin-bottom:0.25rem;
                                    background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.25);
                                    font-size:0.85rem;color:#FCD34D;">
                            {a['module_name']} — v{a['version']}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
