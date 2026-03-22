"""Prompt templates for gap analysis and traceability."""

from __future__ import annotations

import json

SYSTEM_GAP_ANALYSIS = """You are a senior Business Analyst reviewing a junior BA's work package.
Your job is to identify gaps, weaknesses, and inconsistencies across their completed artifacts
and flag what is missing relative to the engagement type and scale.

Be specific and constructive — every finding must reference the exact artifact or module it concerns.
Do not invent gaps. Only flag issues that are genuinely missing or unclear based on the content provided.

Respond ONLY with valid JSON in this exact structure:
{
  "overall_assessment": "2-3 sentence summary of the engagement's completeness and quality.",
  "completeness_score": <integer 0-100>,
  "findings": [
    {
      "severity": "high" | "medium" | "low",
      "gap_type": "missing" | "incomplete" | "inconsistent" | "recommended",
      "module_reference": "<module name or 'Cross-artifact'>",
      "finding": "<specific description of the issue>",
      "recommendation": "<concrete action to address it>"
    }
  ]
}

Gap type definitions:
- missing: An expected artifact or section is entirely absent
- incomplete: An artifact exists but has significant gaps in coverage
- inconsistent: Information contradicts or conflicts with another artifact
- recommended: Not a defect, but a strengthening action that would improve quality

Severity guidelines:
- high: Would likely cause stakeholder confusion, rework, or project risk if unaddressed
- medium: Reduces quality and professionalism but does not block delivery
- low: Nice-to-have improvement, minor polish

Evidence requirement for "incomplete" findings:
When flagging any artifact as incomplete, truncated, or missing content, you must quote
the specific passage from the artifact that supports your finding. Do not flag an artifact
as incomplete unless you can identify and quote the exact location where content is missing
or ends abruptly. If you cannot quote specific evidence, do not include the finding.

Cross-artifact consistency check:
Perform a cross-artifact consistency check on all numerical targets, dates, metrics, and
named figures. For each metric that appears in more than one artifact, verify the value
is stated consistently. Flag any case where the same metric is stated differently across
artifacts as gap_type "inconsistent" and module_reference "Cross-artifact".
Examples to check: duration targets (days, weeks, hours), handoff counts, satisfaction
score targets, timeline dates, budget figures, headcount constraints.
Quote both passages when flagging — the consistent value and the conflicting value.
"""


def build_gap_analysis_messages(
    project: dict,
    dimensions: list[dict],
    roadmap_items: list[dict],
    artifacts: list[dict],
) -> list[dict]:
    """Build the messages array for a gap analysis call."""

    # Dimensions summary
    dim_lines = [f"- {d['dimension_name']}: {d['dimension_value']}" for d in dimensions] or ["None captured."]

    # Roadmap status summary
    roadmap_lines = []
    for item in roadmap_items:
        roadmap_lines.append(f"- [{item['status'].upper()}] {item['module_name']} ({item['knowledge_area']})")

    # Artifact content summaries
    artifact_lines = []
    for a in artifacts:
        content = a.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content)
        excerpt = text[:1200].replace("\n", " ") if text else "(empty)"
        artifact_lines.append(
            f"\n### {a['module_name']} (v{a['version']})\n{excerpt}"
        )

    user_message = f"""PROJECT: {project.get('name')}
ENGAGEMENT TYPE: {project.get('engagement_type')}
SCALE TIER: {project.get('scale_tier')}

CAPTURED DIMENSIONS:
{chr(10).join(dim_lines)}

ROADMAP STATUS ({len(roadmap_items)} modules):
{chr(10).join(roadmap_lines)}

COMPLETED ARTIFACTS:
{''.join(artifact_lines) if artifact_lines else 'No artifacts saved yet.'}

Please review this engagement package and return your gap analysis JSON."""

    return [
        {"role": "system", "content": SYSTEM_GAP_ANALYSIS},
        {"role": "user", "content": user_message},
    ]


def parse_gap_response(response_text: str) -> dict:
    """Parse the gap analysis JSON response with fallback."""
    import re

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

    return {
        "overall_assessment": "Could not parse the analysis response. Please try again.",
        "completeness_score": 0,
        "findings": [],
    }
