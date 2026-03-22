"""Artifact and project package export page."""

from __future__ import annotations

import streamlit as st

from components.db import get_last_active_project, run_query
from components.export import build_project_package, format_artifact_markdown, generate_pdf


def render(current_user: dict) -> None:

    def _load_project(project_id: str) -> dict | None:
        rows = run_query(
            "SELECT project_id, name, description, engagement_type, scale_tier FROM projects WHERE project_id = %s AND user_id = %s LIMIT 1",
            (project_id, current_user["user_id"]),
            fetch=True,
        )
        return dict(rows[0]) if rows else None

    def _load_roadmap_counts(project_id: str) -> dict:
        """Return total modules and complete count for the project."""
        rows = run_query(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'complete' THEN 1 ELSE 0 END) AS complete_count
            FROM project_roadmap_items
            WHERE project_id = %s
            """,
            (project_id,),
            fetch=True,
        )
        if rows:
            total = int(rows[0]["total"] or 0)
            complete = int(rows[0]["complete_count"] or 0)
            return {"total": total, "complete": complete}
        return {"total": 0, "complete": 0}

    def _load_dimensions(project_id: str) -> list[dict]:
        rows = run_query(
            "SELECT dimension_name, dimension_value FROM project_dimensions WHERE project_id = %s",
            (project_id,),
            fetch=True,
        )
        return [dict(r) for r in rows]

    def _load_artifacts(project_id: str) -> list[dict]:
        """Return latest version of each artifact for this project, ordered by roadmap sequence."""
        rows = run_query(
            """
            SELECT DISTINCT ON (a.module_id)
                a.artifact_id,
                a.content,
                a.version,
                m.name AS module_name,
                m.knowledge_area,
                COALESCE(pri.sequence_order, 999) AS sequence_order
            FROM artifacts a
            JOIN modules m ON m.module_id = a.module_id
            LEFT JOIN project_roadmap_items pri
                ON pri.module_id = a.module_id AND pri.project_id = a.project_id
            WHERE a.project_id = %s
            ORDER BY a.module_id, a.version DESC
            """,
            (project_id,),
            fetch=True,
        )
        # ENH-11: sort by roadmap sequence_order; orphan artifacts (no roadmap item) go last
        result = [dict(r) for r in rows]
        result.sort(key=lambda x: x.get("sequence_order", 999))
        return result

    # ── Resolve project ───────────────────────────────────────────────────────

    project_id = st.session_state.get("active_project_id")
    # BUG-06: rehydrate from DB if session state was cleared by a refresh
    if not project_id:
        recovered = get_last_active_project(current_user["user_id"])
        if recovered:
            project_id = recovered
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

    artifacts = _load_artifacts(project_id)
    dimensions = _load_dimensions(project_id)
    roadmap_counts = _load_roadmap_counts(project_id)

    # ── Page header ───────────────────────────────────────────────────────────

    st.markdown(
        f"""
        <div style="padding:1.1rem 0 0.5rem;">
            <span style="font-size:0.72rem;color:#60A5FA;letter-spacing:0.07em;
                         text-transform:uppercase;">Export</span>
            <div style="font-size:1.55rem;font-weight:700;color:#F1F5F9;line-height:1.25;">
                {project['name']}
            </div>
            <div style="font-size:0.85rem;color:#94A3B8;margin-top:0.2rem;">
                {project['engagement_type']} · {project['scale_tier']} scale ·
                {len(artifacts)} artifact{'s' if len(artifacts) != 1 else ''} saved
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

    if not artifacts:
        st.info("No artifacts saved yet. Complete modules in the Co-Pilot to generate exportable content.")
        if st.button("← Back to Roadmap"):
            st.session_state["page"] = "roadmap"
            st.rerun()
        return

    # ── Two sections ─────────────────────────────────────────────────────────

    tab_individual, tab_package = st.tabs(["Export Individual Artifact", "Export Full Package"])

    # ── Tab 1: Individual artifact ────────────────────────────────────────────

    with tab_individual:
        st.markdown(
            "<p style='color:#94A3B8;font-size:0.88rem;margin:0.5rem 0 1rem;'>"
            "Select a completed artifact to preview and download as Markdown."
            "</p>",
            unsafe_allow_html=True,
        )

        artifact_options = {
            f"{a['module_name']} (v{a['version']})": a for a in artifacts
        }
        selected_label = st.selectbox(
            "Select artifact",
            options=list(artifact_options.keys()),
            label_visibility="collapsed",
        )

        selected = artifact_options[selected_label]
        md_text = format_artifact_markdown(
            artifact=selected,
            module_name=selected["module_name"],
            knowledge_area=selected["knowledge_area"],
            project=project,
        )

        # Preview
        with st.expander("Preview", expanded=True):
            st.markdown(
                f"""
                <div style="background:rgba(25,33,54,0.95);border:1px solid rgba(255,255,255,0.14);
                            border-radius:10px;padding:1.2rem 1.4rem;
                            font-size:0.82rem;color:#F1F5F9;line-height:1.65;
                            white-space:pre-wrap;max-height:360px;overflow-y:auto;">
{md_text[:2000]}{'...' if len(md_text) > 2000 else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )

        file_name = (
            f"{project['name'].replace(' ', '_')}_{selected['module_name'].replace(' ', '_')}_v{selected['version']}.md"
        )
        st.download_button(
            label="Download Artifact (.md)",
            data=md_text.encode("utf-8"),
            file_name=file_name,
            mime="text/markdown",
            use_container_width=True,
        )

    # ── Tab 2: Full package ────────────────────────────────────────────────────

    with tab_package:
        st.markdown(
            "<p style='color:#94A3B8;font-size:0.88rem;margin:0.5rem 0 1rem;'>"
            "Download all saved artifacts as a single Markdown document with a cover page and table of contents."
            "</p>",
            unsafe_allow_html=True,
        )

        # Summary tiles
        ka_count = len({a["knowledge_area"] for a in artifacts})
        c1, c2, c3 = st.columns(3)
        for col, label, value in [
            (c1, "Artifacts", str(len(artifacts))),
            (c2, "Knowledge Areas", str(ka_count)),
            (c3, "Dimensions", str(len(dimensions))),
        ]:
            with col:
                st.markdown(
                    f"""
                    <div style="background:rgba(25,33,54,0.90);border:1px solid rgba(255,255,255,0.14);
                                border-radius:10px;padding:0.9rem 1rem;text-align:center;">
                        <div style="font-size:1.6rem;font-weight:700;color:#60A5FA;">{value}</div>
                        <div style="font-size:0.75rem;color:#94A3B8;margin-top:0.2rem;">{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

        # Artifact list in package
        st.markdown(
            "<div style='font-size:0.78rem;color:#94A3B8;margin-bottom:0.5rem;'>"
            "Included artifacts:</div>",
            unsafe_allow_html=True,
        )
        for a in artifacts:
            st.markdown(
                f"<div style='font-size:0.82rem;color:#F1F5F9;padding:0.2rem 0;'>"
                f"· {a['module_name']} "
                f"<span style='color:#94A3B8;'>({a['knowledge_area']} · v{a['version']})</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

        # Find Problem Statement artifact for PDF cover summary
        problem_stmt_text = None
        for a in artifacts:
            if "Problem Statement" in a.get("module_name", ""):
                content = a.get("content", {})
                problem_stmt_text = content.get("text", "") if isinstance(content, dict) else str(content)
                break

        ba_name = current_user.get("email", "")

        package_md = build_project_package(
            project=project,
            artifacts=artifacts,
            dimensions=dimensions,
            roadmap_total=roadmap_counts["total"],
            roadmap_complete=roadmap_counts["complete"],
            ba_name=ba_name,
        )
        safe_name = project["name"].replace(" ", "_")

        # ENH-09: PDF as primary, Markdown as secondary
        with st.spinner("Preparing export..."):
            pdf_bytes = generate_pdf(
                project=project,
                artifacts=artifacts,
                dimensions=dimensions,
                roadmap_total=roadmap_counts["total"],
                roadmap_complete=roadmap_counts["complete"],
                ba_name=ba_name,
                problem_statement_text=problem_stmt_text,
            )

        dl_col1, dl_col2 = st.columns([3, 2])
        with dl_col1:
            st.download_button(
                label="Download Full Package (PDF)",
                data=pdf_bytes,
                file_name=f"{safe_name}_BA_Package.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with dl_col2:
            st.download_button(
                label="Download as Markdown (for developers)",
                data=package_md.encode("utf-8"),
                file_name=f"{safe_name}_BA_Package.md",
                mime="text/markdown",
                use_container_width=True,
            )
