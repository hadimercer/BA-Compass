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
  "score_breakdown": {
    "completion_score": <int 0-25>,
    "quality_score": <int 0-25>,
    "consistency_score": <int 0-25>,
    "coverage_score": <int 0-25>,
    "total_score": <int 0-100>
  },
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

Scoring rules — positive weighted composite (maximum 100):

COMPLETION SCORE (0-25): What proportion of the expected modules for this engagement type and scale have saved artifacts?
- 0-10% of expected modules complete = 0-5 pts
- 11-25% complete = 6-10 pts
- 26-50% complete = 11-16 pts
- 51-75% complete = 17-21 pts
- 76-100% complete = 22-25 pts

QUALITY SCORE (0-25): How thorough and specific are the artifacts that have been saved? Assess based on: presence of quantified metrics, stakeholder specificity, evidence-based findings, and absence of generic boilerplate content.
- Artifacts are mostly generic/thin = 0-8 pts
- Artifacts are adequate with some specificity = 9-16 pts
- Artifacts are thorough and evidence-based = 17-25 pts

CONSISTENCY SCORE (0-25): How consistent is the information across saved artifacts? Check all numerical targets, dates, metrics, and named figures that appear in more than one artifact. Start at 25 and deduct for each confirmed inconsistency found.
- No inconsistencies found = 25 pts
- 1 inconsistency = 20 pts
- 2 inconsistencies = 15 pts
- 3+ inconsistencies = 0-10 pts

COVERAGE SCORE (0-25): How many of the 6 BABOK knowledge areas are represented by at least one saved artifact?
- 1 knowledge area represented = 4 pts
- 2 knowledge areas = 8 pts
- 3 knowledge areas = 13 pts
- 4 knowledge areas = 18 pts
- 5 knowledge areas = 22 pts
- All 6 knowledge areas = 25 pts

total_score = completion_score + quality_score + consistency_score + coverage_score
completeness_score must equal total_score
total_score is always between 0 and 100 — it cannot be negative

Gap type definitions:
- missing: An expected artifact or section is entirely absent
- incomplete: An artifact exists but has significant gaps in coverage
- inconsistent: Information contradicts or conflicts with another artifact
- recommended: Not a defect, but a strengthening action that would improve quality

Severity guidelines:
- high: Would likely cause stakeholder confusion, rework, or project risk if unaddressed
- medium: Reduces quality and professionalism but does not block delivery
- low: Nice-to-have improvement, minor polish

Evidence requirement — applies to ALL findings at ALL severity levels:

Every finding in the findings array must be grounded in specific evidence from the artifacts or roadmap provided. Apply these rules without exception:

For gap_type "incomplete": Quote the specific passage where content is missing or ends abruptly. Do not flag an artifact as incomplete unless you can identify the exact location of the gap. If you cannot quote specific evidence, do not include the finding.

For gap_type "inconsistent": Quote both conflicting passages — the value from artifact A and the conflicting value from artifact B. State which artifact each quote comes from. If you cannot identify both conflicting passages, do not include the finding.

For gap_type "missing": Name the specific module or section that is absent and explain why it is expected for this engagement type and scale tier. Reference the engagement type in your explanation — do not produce generic "this module is important" statements.

For gap_type "recommended" at any severity level: Recommendations must be specific to this project's context. Reference at least one specific artifact, stakeholder group, metric, or decision already captured in this engagement. Generic recommendations that could apply to any project are not permitted.
Examples of prohibited generic recommendations:
- "Consider developing a communication plan" (generic)
- "Ensure stakeholder engagement is sufficient" (generic)
- "Add more detail to this section" (generic)
Examples of acceptable specific recommendations:
- "The COO's 9-month go-live constraint (Problem Statement) is not reflected in the Stakeholder Engagement Planning cadence — add a milestone review at month 4 and 7"
- "The $180k reconciliation cost metric (Problem Statement) has no corresponding success metric in the Current State Assessment — add a target reduction figure"

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
        excerpt = text[:6000] if text else "(empty)"
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
