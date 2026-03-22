"""Co-pilot module experience — guided BA artifact production."""

from __future__ import annotations

import re

import streamlit as st

from components.ai import call_openai, truncate_conversation
from components.db import (
    get_all_project_artifacts,
    get_artifact_by_id,
    get_artifact_versions,
    get_conversation_history,
    get_last_active_project,
    get_latest_artifact,
    get_opening_question,
    run_query,
    save_artifact,
    save_message,
    trigger_opening_question_regen,
)
from prompts.copilot import (
    build_copilot_system,
    build_draft_system,
)


def _fix_list_spacing(text: str) -> str:
    """Collapse double newlines within numbered list blocks and fix split number-text."""
    # 1. Join number and its text when they appear on separate lines: "1.\n text" → "1. text"
    text = re.sub(r'(\d+\.)\n(\s*\S)', r'\1 \2', text)
    # 2. Remove blank lines between consecutive numbered items (e.g. \n\n2.)
    text = re.sub(r'\n\n(\d+\.)', r'\n\1', text)
    # 3. Remove blank lines between a numbered item and its indented continuation
    text = re.sub(r'(\d+\.[^\n]+)\n\n(\s{2,}\S)', r'\1\n\2', text)
    return text


def render(current_user: dict) -> None:

    # ── Helpers ───────────────────────────────────────────────────────────────

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
        if role == "system":
            st.markdown(
                f'<div style="text-align:center;font-size:0.78rem;color:rgba(110,231,183,0.75);'
                f'margin:0.4rem 0;padding:0.25rem 0.5rem;">{content}</div>',
                unsafe_allow_html=True,
            )
            return
        css_class = "chat-bubble-user" if role == "user" else "chat-bubble-ai"
        st.markdown(
            f'<div class="{css_class}"><div>{content}</div></div>',
            unsafe_allow_html=True,
        )

    def _is_draft_ready(msgs: list[dict]) -> bool:
        """Return True when conditions are met for draft generation.

        True when:
        - A draft was already generated this session (draft_generated_key set)
        - An artifact was previously saved (existing_artifact is not None)
        - An assistant message contains both the readiness phrase AND 'Generate Draft'
        """
        if st.session_state.get(draft_generated_key):
            return True
        if existing_artifact is not None:
            return True
        for msg in msgs:
            if msg.get("role") != "assistant":
                continue
            content = msg.get("content", "")
            if (
                (
                    "I have everything needed to produce" in content
                    or "I have sufficient information to produce" in content
                )
                and "Generate Draft" in content
            ):
                return True
        return False

    # ── Resolve context ───────────────────────────────────────────────────────

    project_id = st.session_state.get("active_project_id")

    # BUG-06: rehydrate from DB if session state was cleared by a refresh
    if not project_id:
        recovered = get_last_active_project(current_user["user_id"])
        if recovered:
            project_id = recovered
            st.session_state["active_project_id"] = project_id

    module_id = st.session_state.get("active_module_id")
    roadmap_item_id = st.session_state.get("active_roadmap_item_id")

    if not project_id or not module_id:
        st.error("No module selected. Return to the roadmap and enter a module.")
        if st.button("Go to Dashboard"):
            st.session_state["page"] = "dashboard"
            st.rerun()
        return

    project_id = str(project_id)
    module_id = str(module_id)

    project = _load_project(project_id)
    module = _load_module(module_id)

    if not project or not module:
        st.error("Project or module not found.")
        return

    dimensions = _load_dimensions(project_id)
    prior_artifacts = get_all_project_artifacts(project_id, module_id)  # BUG-01
    existing_artifact = get_latest_artifact(project_id, module_id)

    # ── Session state keys ────────────────────────────────────────────────────

    session_key = f"copilot_{project_id}_{module_id}"
    draft_key = f"draft_{project_id}_{module_id}"
    draft_generated_key = f"draft_generated_{project_id}_{module_id}"  # BUG-05
    is_revising_key = f"is_revising_{project_id}_{module_id}"           # BUG-04

    # ── BUG-04: Consume one-shot revise flag set by roadmap Reopen & Revise ──

    revise_mode = st.session_state.pop(f"revise_mode_{module_id}", False)
    if revise_mode:
        # Force conversation and draft to reload from DB / existing artifact
        st.session_state.pop(session_key, None)
        st.session_state.pop(draft_key, None)
        st.session_state[is_revising_key] = True
        st.session_state[draft_generated_key] = True  # BUG-05: show buttons immediately

    # ── Mark roadmap item in-progress on entry ────────────────────────────────

    if roadmap_item_id:
        roadmap_item_id = str(roadmap_item_id)
        rows = run_query(
            "SELECT status FROM project_roadmap_items WHERE roadmap_item_id = %s LIMIT 1",
            (roadmap_item_id,),
            fetch=True,
        )
        if rows and rows[0]["status"] == "not_started":
            _set_roadmap_status(roadmap_item_id, "in_progress")

    # ── Resolve current artifact text for revise mode ─────────────────────────

    _current_artifact_text: str | None = None
    if st.session_state.get(is_revising_key) and existing_artifact:
        _art = existing_artifact.get("content", {})
        _current_artifact_text = _art.get("text", "") if isinstance(_art, dict) else str(_art)

    # ── Conversation history ──────────────────────────────────────────────────

    if session_key not in st.session_state:
        db_history = get_conversation_history(project_id, module_id)
        loaded = [{"role": r["role"], "content": r["content"]} for r in db_history]

        if not loaded:
            # ENH-05: use pre-generated context-aware opening question if available
            stored_question = get_opening_question(project_id, module_id)
            if stored_question:
                save_message(project_id, module_id, "assistant", stored_question)
                loaded = [{"role": "assistant", "content": stored_question}]
            else:
                with st.spinner("Starting module..."):
                    sys_prompt = build_copilot_system(
                        module, project, dimensions, prior_artifacts,
                        current_artifact_text=_current_artifact_text,
                    )
                    try:
                        first_q = call_openai(
                            [{"role": "system", "content": sys_prompt},
                             {"role": "user", "content": f"Start the {module['name']} module. Ask your opening question now. Be concise."}],
                            temperature=0.3,
                        )
                        first_q = _fix_list_spacing(first_q)
                        save_message(project_id, module_id, "assistant", first_q)
                        loaded = [{"role": "assistant", "content": first_q}]
                    except RuntimeError:
                        loaded = []

        st.session_state[session_key] = loaded

    if draft_key not in st.session_state:
        if existing_artifact:
            content = existing_artifact.get("content", {})
            st.session_state[draft_key] = content.get("text", "") if isinstance(content, dict) else str(content)
        else:
            st.session_state[draft_key] = ""

    messages: list[dict] = st.session_state[session_key]

    # ── Page layout ───────────────────────────────────────────────────────────

    # CSS reset — undo roadmap's absolute-positioning overlay and restore normal button style
    st.markdown("""<style>
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="stColumn"]:first-child div[data-testid="stVerticalBlock"],
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="column"]:first-child div[data-testid="stVerticalBlock"] {
        position: static !important; gap: 1rem !important;
    }
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="stColumn"]:first-child
        div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stButton"]),
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="column"]:first-child
        div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stButton"]) {
        position: static !important; height: auto !important;
    }
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="stColumn"]:first-child div[data-testid="stButton"] button,
    section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]
        div[data-testid="column"]:first-child div[data-testid="stButton"] button {
        height:auto !important; width:auto !important; margin-top:0 !important;
        background:rgba(255,255,255,0.04) !important;
        border:1px solid rgba(255,255,255,0.14) !important;
        color:#F1F5F9 !important;
        border-radius:0.5rem !important; box-shadow:none !important;
    }
    section[data-testid="stMain"] > div {
        padding-bottom: 140px !important;
    }
    </style>""", unsafe_allow_html=True)

    # Slim header
    col_back, col_title = st.columns([1, 7])
    with col_back:
        st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
        if st.button("← Roadmap", use_container_width=True):
            st.session_state["page"] = "roadmap"
            st.rerun()
    with col_title:
        st.markdown(f"""
        <div style="padding:0.4rem 0 0.2rem;">
          <span style="font-size:0.7rem;color:#60A5FA;letter-spacing:0.07em;
                       text-transform:uppercase;">{module['knowledge_area']}</span>
          <div style="font-size:1.3rem;font-weight:700;color:#F1F5F9;line-height:1.2;">{module['name']}</div>
          <div style="font-size:0.82rem;color:#94A3B8;">{(module.get('description',''))[:120]}</div>
        </div>""", unsafe_allow_html=True)

    # ── Artifact dialog ───────────────────────────────────────────────────────

    if existing_artifact:
        _art_content = existing_artifact.get("content", {})
        _art_text = _art_content.get("text", "") if isinstance(_art_content, dict) else str(_art_content)
        _art_ver = existing_artifact.get("version", 1)
        _all_versions = get_artifact_versions(project_id, module_id)
        _dialog_title = (
            f"{module['name']} — {len(_all_versions)} version{'s' if len(_all_versions) != 1 else ''}"
            if len(_all_versions) > 1
            else f"{module['name']} — v{_art_ver}"
        )

        @st.dialog(_dialog_title, width="large")
        def _show_artifact_dialog():
            st.markdown("""<style>
            div[data-testid="stDialog"] div[data-testid="stButton"] button {
                width: 120px !important;
                float: right !important;
            }
            </style>""", unsafe_allow_html=True)
            # ENH-06: version selector when multiple versions exist
            if len(_all_versions) > 1:
                ver_labels = [f"v{v['version']}" for v in _all_versions]
                selected_label = st.selectbox(
                    "Version",
                    options=ver_labels,
                    index=0,
                    key="artifact_version_selector",
                )
                selected_idx = ver_labels.index(selected_label)
                selected_row = _all_versions[selected_idx]
                art_row = get_artifact_by_id(str(selected_row["artifact_id"]))
                if art_row:
                    content = art_row.get("content", {})
                    display_text = content.get("text", "") if isinstance(content, dict) else str(content)
                else:
                    display_text = _art_text
            else:
                display_text = _art_text
            st.markdown(display_text)
            if st.button("Close"):
                st.rerun()

    # Collapsible context + artifact panel
    has_artifact = existing_artifact is not None
    with st.expander("Project Context & Artifacts", expanded=not has_artifact):
        col_ctx, col_art = st.columns(2)
        with col_ctx:
            st.markdown(f"""
            <div style="background:rgba(9,13,22,0.95);border:1px solid rgba(255,255,255,0.10);
                 border-radius:10px;padding:0.8rem 1rem;">
              <div style="font-size:0.7rem;color:#94A3B8;text-transform:uppercase;
                           letter-spacing:0.06em;margin-bottom:0.5rem;">Project Context</div>
              <div style="font-size:0.85rem;color:#F1F5F9;line-height:1.65;">
                <strong>{project.get('engagement_type','—')}</strong><br>
                {project.get('scale_tier','—')} scale<br>
                {len(dimensions)} dimension{'s' if len(dimensions)!=1 else ''} captured<br>
                {len(prior_artifacts)} prior artifact{'s' if len(prior_artifacts)!=1 else ''}
              </div>
            </div>""", unsafe_allow_html=True)
        with col_art:
            if has_artifact:
                # CSS for transparent overlay button on the artifact box
                st.markdown("""<style>
                div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"]
                    div[data-testid="stColumn"]:last-child div[data-testid="stButton"] button,
                div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"]
                    div[data-testid="column"]:last-child div[data-testid="stButton"] button {
                    height:78px !important; margin-top:-78px !important;
                    background:transparent !important; border:none !important;
                    box-shadow:none !important; color:transparent !important;
                    border-radius:10px !important; cursor:pointer !important;
                }
                </style>""", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.25);
                     border-radius:10px;padding:0.75rem 1rem;height:78px;
                     display:flex;flex-direction:column;justify-content:center;
                     box-shadow:0 0 12px rgba(34,197,94,0.06);">
                  <div style="font-size:0.7rem;color:#86EFAC;text-transform:uppercase;
                               letter-spacing:0.06em;margin-bottom:0.2rem;">
                    {module['name']} · v{_art_ver}</div>
                  <div style="font-size:0.85rem;color:#F1F5F9;font-weight:600;line-height:1.3;">
                    {project.get('engagement_type', '—')}</div>
                  <div style="font-size:0.72rem;color:#86EFAC;margin-top:0.2rem;opacity:0.7;">
                    Click to view full artifact ↗</div>
                </div>""", unsafe_allow_html=True)
                if st.button(" ", key="view_artifact_btn", use_container_width=True):
                    _show_artifact_dialog()
            else:
                st.markdown("""
                <div style="background:rgba(17,24,39,0.50);border:1px dashed rgba(255,255,255,0.10);
                     border-radius:10px;padding:0.8rem 1rem;text-align:center;">
                  <div style="font-size:0.82rem;color:#94A3B8;">No saved artifacts yet</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

    # Full-width chat area
    for msg in messages:
        if msg.get("is_saved_placeholder") or (
            msg.get("role") == "system" and "saved successfully" in msg.get("content", "")
        ):
            st.success(msg["content"])
        else:
            _render_message(msg["role"], msg["content"])

    # ── Draft area — BUG-05: shown whenever a draft exists (not gated on existing_artifact) ──
    if st.session_state[draft_key]:
        st.markdown(
            "<div style='margin-top:0.75rem;font-size:0.75rem;color:#60A5FA;"
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
                    # BUG-04: clear revise mode after successful save
                    st.session_state.pop(is_revising_key, None)
                    st.session_state.pop(draft_generated_key, None)  # BUG-05: reset flag
                st.session_state.pop(draft_key, None)
                ver = result.get("version", "?")
                # BUG-07: toast with icon and ✅ prefix
                st.toast(f"✅ Artifact saved — {module['name']} v{ver}", icon="✅")
                # BUG-08: persist system confirmation message in chat
                system_msg = f"✅ {module['name']} v{ver} saved successfully."
                save_message(project_id, module_id, "system", system_msg)
                messages.append({"role": "system", "content": system_msg, "is_saved_placeholder": True})
                st.session_state[session_key] = messages
                # ENH-05: trigger background opening question regeneration for remaining modules
                import threading
                _db_url = st.secrets["neon_db_url"]
                threading.Thread(
                    target=trigger_opening_question_regen,
                    args=(project_id, _db_url),
                    daemon=True,
                ).start()
                st.rerun()
        with mark_col:
            if st.button("Clear Draft", use_container_width=True):
                st.session_state[draft_key] = ""
                st.rerun()

    # Input area — st.chat_input() is Streamlit's native pinned bottom widget
    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

    draft_ready = _is_draft_ready(messages)
    gen_draft = st.button(
        "Generate Draft",
        disabled=not draft_ready,
        use_container_width=True,
        key=f"gen_draft_{module_id}",
    )
    if not draft_ready:
        st.caption("Complete the conversation above — Generate Draft unlocks when the co-pilot confirms it has enough information.")

    user_input = st.chat_input("Answer the question above, or add context...")

    # ── Handle send ───────────────────────────────────────────────────────────
    if user_input:
        user_text = user_input.strip()
        save_message(project_id, module_id, "user", user_text)
        messages.append({"role": "user", "content": user_text})

        system_prompt = build_copilot_system(
            module, project, dimensions, prior_artifacts,
            current_artifact_text=_current_artifact_text,
        )
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
                return

        # ENH-14: suppress inline drafts — if AI produces long prose before Generate Draft
        # has been clicked, truncate at a natural break and redirect to the button
        if not st.session_state.get(draft_generated_key) and len(response.split()) > 300:
            paragraphs = response.split("\n\n")
            truncated = []
            word_count = 0
            for para in paragraphs:
                word_count += len(para.split())
                truncated.append(para)
                if word_count >= 200:
                    break
            response = "\n\n".join(truncated)
            response += "\n\n*[Click Generate Draft above to produce the full formatted artifact]*"

        response = _fix_list_spacing(response)
        save_message(project_id, module_id, "assistant", response)
        messages.append({"role": "assistant", "content": response})
        st.session_state[session_key] = messages
        st.rerun()

    # ── Handle generate draft ─────────────────────────────────────────────────
    if gen_draft:
        if not draft_ready:
            st.warning("Continue the conversation until the co-pilot confirms it has enough information to generate the draft.")
            st.stop()

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
                    return

            draft_text = _fix_list_spacing(draft_text)
            st.session_state[draft_key] = draft_text
            st.session_state[draft_generated_key] = True  # BUG-05: flag draft as generated
            st.rerun()
