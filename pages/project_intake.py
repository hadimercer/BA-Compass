"""Project intake and AI classification page for BA Compass."""

from __future__ import annotations

import streamlit as st

from components.ai import call_openai
from components.db import generate_roadmap_from_template, run_query
from components.ui import render_page_header
from prompts.intake_classification import (
    ENGAGEMENT_TYPES,
    SCALE_TIERS,
    build_intake_messages,
    parse_intake_response,
)


def render(current_user: dict) -> None:

    def _load_project(project_id: str) -> dict | None:
        rows = run_query(
            "SELECT project_id, name, description, engagement_type, scale_tier FROM projects WHERE project_id = %s AND user_id = %s LIMIT 1",
            (project_id, current_user["user_id"]),
            fetch=True,
        )
        return dict(rows[0]) if rows else None

    def _save_dimension(project_id: str, name: str, value: str | None) -> None:
        if not value:
            return
        existing = run_query(
            "SELECT dimension_id FROM project_dimensions WHERE project_id = %s AND dimension_name = %s LIMIT 1",
            (project_id, name),
            fetch=True,
        )
        if existing:
            run_query(
                "UPDATE project_dimensions SET dimension_value = %s WHERE project_id = %s AND dimension_name = %s",
                (value, project_id, name),
                fetch=False,
            )
        else:
            run_query(
                "INSERT INTO project_dimensions (project_id, dimension_name, dimension_value) VALUES (%s, %s, %s)",
                (project_id, name, value),
                fetch=False,
            )

    def _confirm_classification(project_id: str, engagement_type: str, scale_tier: str, dimensions: dict) -> None:
        run_query(
            "UPDATE projects SET engagement_type = %s, scale_tier = %s WHERE project_id = %s",
            (engagement_type, scale_tier, project_id),
            fetch=False,
        )
        dimension_map = {
            "engagement_type": engagement_type,
            "scale_tier": scale_tier,
            "trigger_origin": dimensions.get("trigger_origin"),
            "solution_clarity": dimensions.get("solution_clarity"),
            "stakeholder_landscape": dimensions.get("stakeholder_landscape"),
            "timeline_urgency": dimensions.get("timeline_urgency"),
        }
        for name, value in dimension_map.items():
            _save_dimension(project_id, name, value)

    # ── Resolve active project ────────────────────────────────────────────────

    project_id = st.session_state.get("active_project_id")
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

    render_page_header(
        project["name"],
        "Describe your engagement below. The co-pilot will classify it and generate your roadmap.",
    )

    # ── Already classified — show status and option to proceed ───────────────

    if project.get("engagement_type") and project.get("scale_tier"):
        st.markdown(
            f"""
            <div style="background:rgba(16,185,129,0.10);border:1px solid rgba(16,185,129,0.30);
                        border-radius:16px;padding:1.2rem 1.4rem;margin-bottom:1.2rem;">
                <div style="font-size:0.78rem;color:#6EE7B7;letter-spacing:0.06em;
                            text-transform:uppercase;margin-bottom:0.4rem;">Classification Confirmed</div>
                <div style="font-size:1.15rem;font-weight:700;color:#F0F4F8;">
                    {project['engagement_type']} &nbsp;·&nbsp; {project['scale_tier']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("View Roadmap", use_container_width=True):
                st.session_state["page"] = "roadmap"
                st.rerun()
        with col_b:
            if st.button("Reclassify", use_container_width=True):
                st.session_state["intake_messages"] = []
                st.session_state.pop("intake_classification", None)
                run_query(
                    "UPDATE projects SET engagement_type = NULL, scale_tier = NULL WHERE project_id = %s",
                    (project_id,),
                    fetch=False,
                )
                st.rerun()
        return

    # ── Intake conversation ───────────────────────────────────────────────────

    if "intake_messages" not in st.session_state:
        st.session_state["intake_messages"] = []

    if "intake_classification" not in st.session_state:
        st.session_state["intake_classification"] = None

    # Render conversation history
    for msg in st.session_state["intake_messages"]:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div style="display:flex;justify-content:flex-end;margin-bottom:0.75rem;">
                  <div style="background:rgba(46,117,182,0.22);border:1px solid rgba(74,159,212,0.3);
                              border-radius:14px 14px 4px 14px;padding:0.7rem 1rem;
                              max-width:78%;color:#F0F4F8;font-size:0.93rem;line-height:1.55;">
                    {msg['content']}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div style="display:flex;justify-content:flex-start;margin-bottom:0.75rem;">
                  <div style="background:rgba(30,37,56,0.88);border:1px solid rgba(45,53,80,0.9);
                              border-radius:14px 14px 14px 4px;padding:0.7rem 1rem;
                              max-width:78%;color:#F0F4F8;font-size:0.93rem;line-height:1.55;">
                    {msg['content']}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Classification result card ────────────────────────────────────────────

    classification = st.session_state.get("intake_classification")

    if classification and classification.get("status") == "classification_ready":
        eng = classification.get("engagement_type", "")
        tier = classification.get("scale_tier", "")
        explanation = classification.get("explanation", "")

        st.markdown(
            f"""
            <div style="background:rgba(26,31,46,0.95);border:1px solid rgba(74,159,212,0.35);
                        border-radius:18px;padding:1.4rem 1.5rem;margin:1rem 0 1.2rem;">
                <div style="font-size:0.75rem;color:#4A9FD4;letter-spacing:0.07em;
                            text-transform:uppercase;margin-bottom:0.7rem;">Classification Recommendation</div>
                <div style="font-size:1.3rem;font-weight:700;color:#F0F4F8;margin-bottom:0.35rem;">
                    {eng}
                </div>
                <div style="font-size:0.95rem;color:#8B9CBD;margin-bottom:0.9rem;">
                    Scale: <strong style="color:#F0F4F8;">{tier}</strong>
                </div>
                <div style="font-size:0.88rem;color:rgba(240,244,248,0.78);line-height:1.6;">
                    {explanation}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Accept & Generate Roadmap", use_container_width=True):
                with st.spinner("Generating your roadmap..."):
                    _confirm_classification(
                        project_id, eng, tier,
                        classification.get("captured_dimensions", {}),
                    )
                    count = generate_roadmap_from_template(project_id, eng, tier)
                if count == 0:
                    st.error("No matching roadmap template found. Try reclassifying.")
                else:
                    st.session_state["intake_messages"] = []
                    st.session_state["intake_classification"] = None
                    st.session_state["page"] = "roadmap"
                    st.rerun()

        with col2:
            with st.expander("Override Classification"):
                override_type = st.selectbox(
                    "Engagement Type", ENGAGEMENT_TYPES, key="override_type"
                )
                override_tier = st.selectbox(
                    "Scale Tier", SCALE_TIERS, key="override_tier"
                )
                if st.button("Confirm Override & Generate Roadmap", use_container_width=True):
                    with st.spinner("Generating your roadmap..."):
                        _confirm_classification(
                            project_id, override_type, override_tier,
                            classification.get("captured_dimensions", {}),
                        )
                        count = generate_roadmap_from_template(project_id, override_type, override_tier)
                    if count == 0:
                        st.error("No matching roadmap template found.")
                    else:
                        st.session_state["intake_messages"] = []
                        st.session_state["intake_classification"] = None
                        st.session_state["page"] = "roadmap"
                        st.rerun()

    else:
        # ── Input area ────────────────────────────────────────────────────────
        placeholder = (
            "Describe your engagement — paste an email, a brief, or just explain it in your own words. "
            "What are you working on and what prompted it?"
            if not st.session_state["intake_messages"]
            else "Continue the conversation..."
        )

        with st.form("intake_form", clear_on_submit=True):
            user_input = st.text_area(
                "Your message",
                placeholder=placeholder,
                height=130,
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Send", use_container_width=True)

        if submitted and user_input.strip():
            st.session_state["intake_messages"].append(
                {"role": "user", "content": user_input.strip()}
            )

            with st.spinner("Analysing your engagement..."):
                messages = build_intake_messages(
                    project["name"],
                    project.get("description") or "",
                    st.session_state["intake_messages"][:-1],  # history before this turn
                )
                # Append current user message
                messages.append({"role": "user", "content": user_input.strip()})

                try:
                    raw = call_openai(messages, temperature=0.2, json_mode=True)
                    parsed = parse_intake_response(raw)
                except RuntimeError as exc:
                    st.error(str(exc))
                    return

            # Build assistant message text for display
            display_parts = []
            if parsed.get("message"):
                display_parts.append(parsed["message"])
            if parsed.get("follow_up_questions"):
                for i, q in enumerate(parsed["follow_up_questions"], 1):
                    display_parts.append(f"{i}. {q}")
            assistant_text = "\n\n".join(display_parts) if display_parts else "Let me know if you have anything to add."

            st.session_state["intake_messages"].append(
                {"role": "assistant", "content": assistant_text}
            )

            if parsed.get("status") == "classification_ready":
                st.session_state["intake_classification"] = parsed

            st.rerun()
