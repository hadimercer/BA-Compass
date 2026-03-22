"""Prompt templates for the co-pilot module experience."""

from __future__ import annotations

SYSTEM_COPILOT_BASE = """You are an expert Business Analyst co-pilot embedded in BA Compass.
Your role is to guide the user through completing one specific BA module — the one shown in the context below.

Your behaviour:
- Ask 1-2 focused questions per turn. Do not dump a long list of questions at once.
- Use the project context (dimensions, prior artifacts) to make questions specific — never generic.
- Never invent stakeholder names, system names, business details, or facts not provided by the user.
- All methodology, module structure, and artifact types come from the BABOK-aligned library — do not invent new frameworks.
- When you have gathered sufficient information, you will be asked to generate a draft — wait for that trigger.
- Flag gaps as you notice them (missing stakeholders, vague scope, unaddressed risks) — do this inline, naturally.
- Keep responses conversational but concise. This is a working session, not a lecture.
"""

SYSTEM_DRAFT_GENERATION = """You are an expert Business Analyst generating a structured artifact draft.
Using only the information provided in the conversation history and project context, produce a complete,
professional draft of the specified artifact.

Rules:
- Use only facts provided by the user. Do not invent names, numbers, systems, or decisions.
- Structure the output clearly with headings and sections appropriate to the artifact type.
- Write in professional BA register — clear, precise, unambiguous.
- At the end, add a brief "Gaps & Recommendations" section flagging anything that should be strengthened before final delivery.
- Do not include meta-commentary about what you did — just produce the artifact.
"""

_APPROX_CHARS_PER_TOKEN = 4
_MAX_ARTIFACT_CHARS = 6000 * _APPROX_CHARS_PER_TOKEN  # ≈ 24 000 chars


def _dimensions_block(dimensions: list[dict]) -> str:
    if not dimensions:
        return "No dimensions captured yet."
    lines = []
    for d in dimensions:
        lines.append(f"- {d['dimension_name']}: {d['dimension_value']}")
    return "\n".join(lines)


def _prior_artifacts_block(
    artifacts: list[dict],
    current_module_knowledge_area: str = "",
) -> str:
    """Inject prior artifact text with token-aware truncation.

    If total chars ≤ _MAX_ARTIFACT_CHARS: include all artifacts in full.
    Otherwise: preserve full text for the 3 most recently saved artifacts and the 1
    artifact most thematically related (matching knowledge_area of the current module).
    All others are truncated to a 300-char excerpt labelled '[key findings only]'.

    Expects artifacts ordered oldest-first (as returned by get_all_project_artifacts).
    """
    if not artifacts:
        return "None yet."

    total_chars = sum(len(a["text"]) for a in artifacts)
    if total_chars <= _MAX_ARTIFACT_CHARS:
        lines = []
        for a in artifacts:
            lines.append(f"\n### {a['module_name']} (v{a['version']})\n{a['text']}")
        return "\n".join(lines)

    # Protected set: 3 most recent (tail of sorted-oldest-first list)
    most_recent_indices = set(range(max(0, len(artifacts) - 3), len(artifacts)))

    # Most thematically related: first knowledge_area match; fallback to most recent
    thematic_index: int | None = None
    for i, a in enumerate(artifacts):
        if a.get("knowledge_area", "") == current_module_knowledge_area:
            thematic_index = i
            break
    if thematic_index is None and artifacts:
        thematic_index = len(artifacts) - 1
    protected = most_recent_indices | {thematic_index}

    lines = []
    for i, a in enumerate(artifacts):
        if i in protected:
            lines.append(f"\n### {a['module_name']} (v{a['version']})\n{a['text']}")
        else:
            excerpt = a["text"][:300].rstrip() + "…" if len(a["text"]) > 300 else a["text"]
            lines.append(
                f"\n### {a['module_name']} (v{a['version']}) [key findings only]\n{excerpt}"
            )
    return "\n".join(lines)


def build_copilot_system(
    module: dict,
    project: dict,
    dimensions: list[dict],
    prior_artifacts: list[dict],
    current_artifact_text: str | None = None,
) -> str:
    """Build the full system prompt for a co-pilot session.

    current_artifact_text: when set (Reopen & Revise mode), injects the existing saved
    artifact under a dedicated section so the co-pilot uses it as the revision baseline.
    """
    artifact_section = ""
    if current_artifact_text:
        artifact_section = f"""

CURRENT SAVED VERSION OF THIS ARTIFACT — the user wants to revise and improve it, use this as the baseline:
{current_artifact_text}
"""
    return (
        SYSTEM_COPILOT_BASE
        + f"""

PROJECT CONTEXT:
- Project name: {project.get('name', 'Unknown')}
- Engagement type: {project.get('engagement_type', 'Not classified')}
- Scale tier: {project.get('scale_tier', 'Not classified')}

CAPTURED DIMENSIONS:
{_dimensions_block(dimensions)}

PRIOR WORK COMPLETED ON THIS PROJECT — use this context to inform your questions and avoid repeating what has already been established:
{_prior_artifacts_block(prior_artifacts, module.get('knowledge_area', ''))}
{artifact_section}
CURRENT MODULE:
- Name: {module.get('name')}
- BABOK Knowledge Area: {module.get('knowledge_area')}
- Description: {module.get('description', '')}
- Typical inputs: {module.get('typical_inputs') or 'Use project context and prior artifacts.'}
- Typical outputs: {module.get('typical_outputs') or 'See module description.'}

Your job right now is to guide the user through completing the "{module.get('name')}" module.
Begin by asking the most important opening question to get started.
"""
    )


def build_draft_system(
    module: dict,
    project: dict,
    dimensions: list[dict],
) -> str:
    """Build the system prompt for artifact draft generation."""
    return (
        SYSTEM_DRAFT_GENERATION
        + f"""

PROJECT CONTEXT:
- Project name: {project.get('name', 'Unknown')}
- Engagement type: {project.get('engagement_type', 'Not classified')}
- Scale tier: {project.get('scale_tier', 'Not classified')}

CAPTURED DIMENSIONS:
{_dimensions_block(dimensions)}

ARTIFACT TO GENERATE: {module.get('name')}
BABOK Knowledge Area: {module.get('knowledge_area')}
"""
    )


def opening_message(module_name: str) -> str:
    """Return a brief UI message shown before the AI responds on first entry."""
    return (
        f"I'm ready to help you complete **{module_name}**. "
        "I'll ask you a few questions to gather what I need, then help you produce a draft artifact. "
        "Let's start — tell me about this engagement in your own words, or answer my first question below."
    )
