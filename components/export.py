"""Artifact and project package export helpers for BA Compass."""

from __future__ import annotations

from datetime import datetime

# Human-readable labels for raw database field values
_ENGAGEMENT_TYPE_LABELS: dict[str, str] = {
    "Process Improvement": "Process Improvement",
    "New System / Technology Implementation": "New System / Technology Implementation",
    "Data & Reporting": "Data & Reporting",
    "Regulatory & Compliance": "Regulatory & Compliance",
    "Organizational Change": "Organizational Change",
    "New Product / Service Development": "New Product / Service Development",
    "Vendor Selection & Procurement": "Vendor Selection & Procurement",
    "Strategic Initiative": "Strategic Initiative",
}

_SCALE_TIER_LABELS: dict[str, str] = {
    "Request": "Request — focused, single-outcome engagement",
    "Engagement": "Engagement — structured multi-stakeholder analysis",
    "Initiative": "Initiative — full lifecycle BA engagement",
}

DIMENSION_LABELS: dict[str, str] = {
    "engagement_type": "Engagement Type",
    "scale_tier": "Scale Tier",
    "trigger_origin": "Trigger / Origin",
    "solution_clarity": "Solution Clarity",
    "stakeholder_complexity": "Stakeholder Complexity",
    "timeline_constraint": "Timeline Constraint",
    "regulatory_driver": "Regulatory Driver",
}


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
    roadmap_total: int = 0,
    roadmap_complete: int = 0,
    ba_name: str | None = None,
) -> str:
    """
    Return a single Markdown document containing all project artifacts.

    `artifacts` must be a list of dicts, each with:
        module_name, knowledge_area, version, content (JSONB dict with 'text')
    """
    exported_at = datetime.now().strftime("%d %B %Y, %H:%M")
    name = project.get("name", "Unknown Project")
    description = project.get("description", "") or ""
    eng_type = project.get("engagement_type", "—")
    scale = project.get("scale_tier", "—")

    # Human-readable engagement labels
    eng_label = _ENGAGEMENT_TYPE_LABELS.get(eng_type, eng_type)
    scale_label = _SCALE_TIER_LABELS.get(scale, scale)

    # Completion percentage
    if roadmap_total > 0:
        completion_pct = round((roadmap_complete / roadmap_total) * 100)
        completion_str = f"{roadmap_complete}/{roadmap_total} modules complete ({completion_pct}%)"
    else:
        completion_str = f"{len(artifacts)} artifacts saved"

    # Knowledge areas covered
    ka_set = sorted({a.get("knowledge_area", "—") for a in artifacts})
    ka_str = ", ".join(ka_set) if ka_set else "—"

    # Cover page
    lines: list[str] = [
        f"# {name}",
        "## Business Analysis Work Package",
        "",
    ]
    if description:
        lines += [description, ""]
    if ba_name:
        lines.append(f"**Prepared by:** {ba_name}  ")
    lines += [
        f"**Engagement Type:** {eng_label}  ",
        f"**Scale Tier:** {scale_label}  ",
        f"**Completion:** {completion_str}  ",
        f"**Knowledge Areas:** {ka_str}  ",
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
            # Use human-readable label if available, else title-case the raw name
            raw_name = d["dimension_name"]
            label = DIMENSION_LABELS.get(raw_name, raw_name.replace("_", " ").title())
            lines.append(f"- **{label}:** {d['dimension_value']}")
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


def generate_pdf(
    project: dict,
    artifacts: list[dict],
    dimensions: list[dict],
    roadmap_total: int = 0,
    roadmap_complete: int = 0,
    ba_name: str | None = None,
    problem_statement_text: str | None = None,
) -> bytes:
    """Generate a professional PDF work package using reportlab.

    Returns the PDF as bytes, ready for st.download_button().
    """
    from io import BytesIO

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    buffer = BytesIO()
    exported_at = datetime.now().strftime("%d %B %Y")
    name = project.get("name", "Unknown Project")
    description = project.get("description", "") or ""
    eng_type = project.get("engagement_type", "—")
    scale = project.get("scale_tier", "—")
    eng_label = _ENGAGEMENT_TYPE_LABELS.get(eng_type, eng_type)
    scale_label = _SCALE_TIER_LABELS.get(scale, scale)

    if roadmap_total > 0:
        completion_pct = round((roadmap_complete / roadmap_total) * 100)
        completion_str = f"{roadmap_complete}/{roadmap_total} modules complete ({completion_pct}%)"
    else:
        completion_str = f"{len(artifacts)} artifacts saved"

    ka_set = sorted({a.get("knowledge_area", "—") for a in artifacts})
    ka_str = ", ".join(ka_set) if ka_set else "—"

    # ── Define styles ────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()

    # Colour palette
    DARK_BG = colors.HexColor("#0E1117")
    TEAL = colors.HexColor("#4DB6AC")
    LIGHT_TEXT = colors.HexColor("#F1F5F9")
    MUTED = colors.HexColor("#94A3B8")
    BLUE = colors.HexColor("#3B82F6")
    HR_COLOR = colors.HexColor("#2D3748")

    cover_title = ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        textColor=LIGHT_TEXT,
        spaceAfter=8,
    )
    cover_sub = ParagraphStyle(
        "CoverSub",
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=TEAL,
        spaceAfter=24,
    )
    meta_label = ParagraphStyle(
        "MetaLabel",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=MUTED,
        spaceAfter=2,
    )
    meta_value = ParagraphStyle(
        "MetaValue",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=LIGHT_TEXT,
        spaceAfter=8,
    )
    summary_style = ParagraphStyle(
        "Summary",
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=LIGHT_TEXT,
        spaceAfter=12,
    )
    toc_item = ParagraphStyle(
        "TocItem",
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=LIGHT_TEXT,
        leftIndent=12,
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=TEAL,
        spaceBefore=8,
        spaceAfter=4,
    )
    section_meta = ParagraphStyle(
        "SectionMeta",
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=12,
        textColor=MUTED,
        spaceAfter=10,
    )
    body_style = ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=LIGHT_TEXT,
        spaceAfter=6,
    )

    # ── Page template with footer ────────────────────────────────────────────
    def _on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(2 * cm, 1.2 * cm, name)
        canvas.drawRightString(
            A4[0] - 2 * cm, 1.2 * cm,
            f"Page {doc.page}  ·  {exported_at}",
        )
        canvas.restoreState()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    story = []

    # ── Cover page ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(name, cover_title))
    story.append(Paragraph("Business Analysis Work Package", cover_sub))
    story.append(HRFlowable(width="100%", thickness=1, color=TEAL))
    story.append(Spacer(1, 0.5 * cm))

    # Engagement summary (from Problem Statement artifact or project description)
    summary_text = ""
    if problem_statement_text:
        summary_text = problem_statement_text[:500].replace("\n", " ").strip()
    elif description:
        summary_text = description[:500].strip()
    if summary_text:
        story.append(Paragraph(summary_text, summary_style))
        story.append(Spacer(1, 0.4 * cm))

    # Metadata table
    meta_data = [
        ["Engagement Type", eng_label],
        ["Scale Tier", scale_label],
        ["Completion", completion_str],
        ["Knowledge Areas", ka_str],
        ["Total Artifacts", str(len(artifacts))],
        ["Exported", exported_at],
    ]
    if ba_name:
        meta_data.insert(0, ["Prepared by", ba_name])

    for label, value in meta_data:
        story.append(Paragraph(label.upper(), meta_label))
        story.append(Paragraph(value, meta_value))

    if dimensions:
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("ENGAGEMENT DIMENSIONS", meta_label))
        for d in dimensions:
            raw_name = d["dimension_name"]
            label = DIMENSION_LABELS.get(raw_name, raw_name.replace("_", " ").title())
            story.append(Paragraph(f"{label}: {d['dimension_value']}", meta_value))

    story.append(PageBreak())

    # ── Table of contents ────────────────────────────────────────────────────
    story.append(Paragraph("Table of Contents", section_heading))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HR_COLOR))
    story.append(Spacer(1, 0.3 * cm))
    for i, a in enumerate(artifacts, start=1):
        ka = a.get("knowledge_area", "—")
        ver = a.get("version", 1)
        story.append(Paragraph(f"{i}.  {a['module_name']}   <font color='#94A3B8' size='9'>{ka} · v{ver}</font>", toc_item))
    story.append(PageBreak())

    # ── Artifact sections ────────────────────────────────────────────────────
    for a in artifacts:
        content = a.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content)
        version = a.get("version", 1)
        ka = a.get("knowledge_area", "—")

        story.append(Paragraph(a["module_name"], section_heading))
        story.append(Paragraph(f"Knowledge Area: {ka}  ·  Version {version}", section_meta))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HR_COLOR))
        story.append(Spacer(1, 0.2 * cm))

        # Split text into paragraphs and render each
        for para_text in text.split("\n\n"):
            para_text = para_text.strip()
            if not para_text:
                continue
            # Replace single newlines with spaces for paragraph flow
            para_text = para_text.replace("\n", " ")
            story.append(Paragraph(para_text, body_style))

        story.append(PageBreak())

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return buffer.getvalue()


def _anchor(text: str) -> str:
    """Convert heading text to a GitHub-flavoured Markdown anchor slug."""
    return text.lower().replace(" ", "-").replace("/", "").replace("&", "")
