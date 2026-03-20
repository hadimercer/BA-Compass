"""Artifact and project package export helpers for BA Compass."""

from __future__ import annotations

from datetime import datetime


def format_artifact_markdown(
    artifact: dict,
    module_name: str,
    knowledge_area: str,
    project: dict,
) -> str:
    """Return a standalone Markdown document for a single artifact."""
    content = artifact.get("content", {})
    text = content.get("text", "") if isinstance(content, dict) else str(content)
    version = artifact.get("version", 1)
    exported_at = datetime.now().strftime("%d %B %Y")

    lines = [
        f"# {module_name}",
        "",
        f"**Project:** {project.get('name', 'Unknown')}  ",
        f"**Engagement Type:** {project.get('engagement_type', '—')}  ",
        f"**Scale Tier:** {project.get('scale_tier', '—')}  ",
        f"**Knowledge Area:** {knowledge_area}  ",
        f"**Artifact Version:** v{version}  ",
        f"**Exported:** {exported_at}  ",
        "",
        "---",
        "",
        text,
    ]
    return "\n".join(lines)


def build_project_package(
    project: dict,
    artifacts: list[dict],
    dimensions: list[dict],
) -> str:
    """
    Return a single Markdown document containing all project artifacts.

    `artifacts` must be a list of dicts, each with:
        module_name, knowledge_area, version, content (JSONB dict with 'text')
    """
    exported_at = datetime.now().strftime("%d %B %Y, %H:%M")
    name = project.get("name", "Unknown Project")
    eng_type = project.get("engagement_type", "—")
    scale = project.get("scale_tier", "—")

    # Cover page
    lines: list[str] = [
        f"# {name}",
        "## Business Analysis Work Package",
        "",
        f"**Engagement Type:** {eng_type}  ",
        f"**Scale Tier:** {scale}  ",
        f"**Total Artifacts:** {len(artifacts)}  ",
        f"**Exported:** {exported_at}  ",
        "",
        "---",
        "",
    ]

    # Dimensions section
    if dimensions:
        lines += [
            "## Engagement Dimensions",
            "",
        ]
        for d in dimensions:
            lines.append(f"- **{d['dimension_name']}:** {d['dimension_value']}")
        lines += ["", "---", ""]

    # Table of contents
    lines += [
        "## Table of Contents",
        "",
    ]
    for i, a in enumerate(artifacts, start=1):
        lines.append(f"{i}. [{a['module_name']}](#{_anchor(a['module_name'])})")
    lines += ["", "---", ""]

    # Each artifact as a section
    for a in artifacts:
        content = a.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content)
        version = a.get("version", 1)
        ka = a.get("knowledge_area", "—")

        lines += [
            f"## {a['module_name']}",
            "",
            f"*Knowledge Area: {ka} · v{version}*",
            "",
            text,
            "",
            "---",
            "",
        ]

    return "\n".join(lines)


def _anchor(text: str) -> str:
    """Convert heading text to a GitHub-flavoured Markdown anchor slug."""
    return text.lower().replace(" ", "-").replace("/", "").replace("&", "")
