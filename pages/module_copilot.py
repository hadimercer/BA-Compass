"""Co-pilot module experience — guided BA artifact production."""

from __future__ import annotations

import streamlit as st

from components.ai import call_openai, truncate_conversation
from components.auth import require_auth
from components.db import (
    get_completed_artifacts_summary,
    get_conversation_history,
    get_latest_artifact,
    run_query,
    save_artifact,
    save_message,
)
from components.ui import inject_css, render_sidebar
from prompts.copilot import (
    build_copilot_system,
    build_draft_system,
    opening_message,
)


st.set_page_config(page_title="BA Compass", layout="wide", initial_sidebar_state="expanded")

current_user = require_auth()
inject_css()
render_sidebar("module_copilot")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_project(project_id: str) -> dict | None:
    rows = run_query(
        "SELECT project_id, name, engagement_type, scale_tier FROM projects WHERE project_id = %s AND user_id = %s LIMIT 1",
        (project_id, current_user["user_id"]),
        fetch=True,
    )
    return dict(rows[0]) if rows else None


def _load_module(module_id: str) -> dict | None:
    rows = run_query(
        "SELECT module_id, name, knowledge_area, description, typical_inputs, typical_outputs FROM modules WHERE module_id = %s LIMIT 1",
        (module_id,),
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


def _set_roadmap_status(roadmap_item_id: str, status: str) -> None:
    run_query(
        "UPDATE project_roadmap_items SET status = %s WHERE roadmap_item_id = %s",
        (status, roadmap_item_id),
        fetch=False,
    )


def _render_message(role: str, content: str) -> None:
    css_class = "chat-bubble-user" if role == "user" else "chat-bubble-ai"
    st.markdown(
        f'<div class="{css_class}"><div>{content}</div></div>',
        unsafe_allow_html=True,
    )


# ── Resolve context ───────────────────────────────────────────────────────────

project_id = st.query_params.get("project_id") or st.session_state.get("active_project_id")
module_id = st.query_params.get("module_id") or st.session_state.get("active_module_id")
roadmap_item_id = st.query_params.get("roadmap_item_id") or st.session_state.get("active_roadmap_item_id")

if not project_id or not module_id:
    st.error("No module selected. Return to the roadmap and enter a module.")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/dashboard.py")
    st.stop()

project_id = str(project_id)
module_id = str(module_id)
st.query_params["project_id"] = project_id
st.query_params["module_id"] = module_id
st.session_state["active_project_id"] = project_id
st.session_state["active_module_id"] = module_id

project = _load_project(project_id)
module = _load_module(module_id)

if not project or not module:
    st.error("Project or module not found.")
    st.stop()

dimensions = _load_dimensions(project_id)
prior_artifacts = get_completed_artifacts_summary(project_id, module_id)
existing_artifact = get_latest_artifact(project_id, module_id)

# ── Mark roadmap item in-progress on entry ────────────────────────────────────

if roadmap_item_id:
    roadmap_item_id = str(roadmap_item_id)
    st.query_params["roadmap_item_id"] = roadmap_item_id
    rows = run_query(
        "SELECT status FROM project_roadmap_items WHERE roadmap_item_id = %s LIMIT 1",
        (roadmap_item_id,),
        fetch=True,
    )
    if rows and rows[0]["status"] == "not_started":
        _set_roadmap_status(roadmap_item_id, "in_progress")

# ── Session state for this module session ─────────────────────────────────────

session_key = f"copilot_{project_id}_{module_id}"
draft_key = f"draft_{project_id}_{module_id}"

if session_key not in st.session_state:
    # Load persisted conversation from DB
    db_history = get_conversation_history(project_id, module_id)
    st.session_state[session_key] = [
        {"role": r["role"], "content": r["content"]} for r in db_history
    ]

if draft_key not in st.session_state:
    # Pre-populate draft from existing artifact if present
    if existing_artifact:
        content = existing_artifact.get("content", {})
        st.session_state[draft_key] = content.get("text", "") if isinstance(content, dict) else str(content)
    else:
        st.session_state[draft_key] = ""

messages: list[dict] = st.session_state[session_key]

# ── Page layout ───────────────────────────────────────────────────────────────

# Back button + header row
nav_col, title_col = st.columns([1, 5])
with nav_col:
    if st.button("← Roadmap", use_container_width=True):
        st.switch_page("pages/roadmap.py")
        st.stop()
with title_col:
    st.markdown(
        f"""
        <div style="padding:0.6rem 0 0.3rem;">
            <span style="font-size:0.72rem;color:#4A9FD4;letter-spacing:0.07em;
                         text-transform:uppercase;">{module['knowledge_area']}</span>
            <div style="font-size:1.55rem;font-weight:700;color:#F0F4F8;line-height:1.25;">
                {module['name']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Module context expander
with st.expander("Module guide", expanded=not bool(messages)):
    st.markdown(
        f"<p style='color:#8B9CBD;font-size:0.9rem;line-height:1.65;margin:0'>{module.get('description','')}</p>",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# Main two-column layout
chat_col, panel_col = st.columns([5, 2])

with panel_col:
    # Existing artifact panel
    if existing_artifact:
        content = existing_artifact.get("content", {})
        artifact_text = content.get("text", "") if isinstance(content, dict) else str(content)
        ver = existing_artifact.get("version", 1)
        st.markdown(
            f"""
            <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);
                        border-radius:14px;padding:0.9rem 1rem;margin-bottom:0.75rem;">
                <div style="font-size:0.7rem;color:#6EE7B7;letter-spacing:0.06em;
                             text-transform:uppercase;margin-bottom:0.3rem;">Saved Artifact v{ver}</div>
                <div style="font-size:0.82rem;color:#F0F4F8;line-height:1.5;
                             max-height:140px;overflow:hidden;">{artifact_text[:300]}{'…' if len(artifact_text)>300 else ''}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Project context pill
    st.markdown(
        f"""
        <div style="font-size:0.75rem;color:#8B9CBD;margin-bottom:0.4rem;">Project context</div>
        <div style="font-size:0.8rem;color:#F0F4F8;background:rgba(30,37,56,0.9);
                    border:1px solid rgba(45,53,80,0.9);border-radius:12px;
                    padding:0.7rem 0.85rem;line-height:1.6;">
            <strong>{project.get('engagement_type','—')}</strong><br>
            {project.get('scale_tier','—')} scale<br>
            {len(dimensions)} dimension{'s' if len(dimensions)!=1 else ''} captured<br>
            {len(prior_artifacts)} prior artifact{'s' if len(prior_artifacts)!=1 else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

with chat_col:
    # Render conversation
    if not messages:
        st.markdown(
            f"""
            <div style="background:rgba(30,37,56,0.88);border:1px solid rgba(45,53,80,0.9);
                        border-radius:14px 14px 14px 4px;padding:0.75rem 1rem;
                        color:#F0F4F8;font-size:0.92rem;line-height:1.6;margin-bottom:0.75rem;">
                {opening_message(module['name'])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    for msg in messages:
        _render_message(msg["role"], msg["content"])

    # Draft area — shown when draft exists
    if st.session_state[draft_key]:
        st.markdown(
            "<div style='margin-top:0.75rem;font-size:0.75rem;color:#4A9FD4;"
            "letter-spacing:0.06em;text-transform:uppercase;margin-bottom:0.3rem;'>"
            "Draft Artifact</div>",
            unsafe_allow_html=True,
        )
        edited_draft = st.text_area(
            "Edit draft before saving",
            value=st.session_state[draft_key],
            height=320,
            key=f"draft_editor_{module_id}",
            label_visibility="collapsed",
        )
        save_col, mark_col = st.columns([2, 1])
        with save_col:
            if st.button("Save Artifact", use_container_width=True):
                with st.spinner("Saving..."):
                    result = save_artifact(project_id, module_id, module["name"], edited_draft)
                    if roadmap_item_id:
                        _set_roadmap_status(roadmap_item_id, "complete")
                st.session_state[draft_key] = edited_draft
                ver = result.get("version", "?")
                st.success(f"Artifact saved (v{ver}). Module marked complete.")
                st.rerun()
        with mark_col:
            if st.button("Clear Draft", use_container_width=True):
                st.session_state[draft_key] = ""
                st.rerun()

    # Input form
    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

    with st.form(f"copilot_form_{module_id}", clear_on_submit=True):
        user_input = st.text_area(
            "Message",
            placeholder="Answer the question above, or add context...",
            height=100,
            label_visibility="collapsed",
        )
        form_col1, form_col2 = st.columns([3, 1])
        with form_col1:
            send = st.form_submit_button("Send", use_container_width=True)
        with form_col2:
            gen_draft = st.form_submit_button("Generate Draft", use_container_width=True)

    # ── Handle send ──────────────────────────────────────────────────────────
    if send and user_input.strip():
        user_text = user_input.strip()
        save_message(project_id, module_id, "user", user_text)
        messages.append({"role": "user", "content": user_text})

        system_prompt = build_copilot_system(module, project, dimensions, prior_artifacts)
        ai_messages = truncate_conversation(
            [{"role": m["role"], "content": m["content"]} for m in messages],
            system_prompt,
            max_turns=12,
        )

        with st.spinner(""):
            try:
                response = call_openai(ai_messages, temperature=0.4)
            except RuntimeError as exc:
                st.error(str(exc))
                st.stop()

        save_message(project_id, module_id, "assistant", response)
        messages.append({"role": "assistant", "content": response})
        st.session_state[session_key] = messages
        st.rerun()

    # ── Handle generate draft ─────────────────────────────────────────────────
    if gen_draft:
        if user_input.strip():
            # Include any last input before generating
            user_text = user_input.strip()
            save_message(project_id, module_id, "user", user_text)
            messages.append({"role": "user", "content": user_text})
            st.session_state[session_key] = messages

        if len(messages) < 2:
            st.warning("Have a short conversation first so I have enough context to draft from.")
        else:
            system_prompt = build_draft_system(module, project, dimensions)
            ai_messages = truncate_conversation(
                [{"role": m["role"], "content": m["content"]} for m in messages],
                system_prompt,
                max_turns=14,
            )
            ai_messages.append({
                "role": "user",
                "content": (
                    f"Based on everything discussed, please generate a complete draft of the "
                    f'"{module["name"]}" artifact now.'
                ),
            })

            with st.spinner("Generating draft..."):
                try:
                    draft_text = call_openai(ai_messages, temperature=0.3)
                except RuntimeError as exc:
                    st.error(str(exc))
                    st.stop()

            st.session_state[draft_key] = draft_text
            st.rerun()
