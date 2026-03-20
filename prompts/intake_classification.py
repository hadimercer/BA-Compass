"""Prompt templates and response parsing for the project intake classification flow."""

from __future__ import annotations

import json
import re

ENGAGEMENT_TYPES = [
    "Process Improvement",
    "New System / Technology Implementation",
    "Data & Reporting",
    "Regulatory & Compliance",
    "Organizational Change",
    "New Product / Service Development",
    "Vendor Selection & Procurement",
    "Strategic Initiative",
]

SCALE_TIERS = ["Request", "Engagement", "Initiative"]

SYSTEM_INTAKE = f"""You are an expert Business Analyst conducting a structured project intake.
Your goal is to classify the user's engagement into one Engagement Type and one Scale Tier,
then generate a roadmap. You do this through a focused conversation.

ENGAGEMENT TYPES (choose exactly one):
{chr(10).join(f'- {t}' for t in ENGAGEMENT_TYPES)}

SCALE TIERS (choose exactly one):
- Request: Small, bounded, 1-2 stakeholders, hours to days. Example: document requirements for a new report.
- Engagement: Mid-size, a few stakeholders, days to weeks. Example: departmental process improvement.
- Initiative: Multi-phase, multiple stakeholders, weeks to months. Example: enterprise system implementation.

MUST-KNOW DIMENSIONS — extract these before classifying:
1. Engagement Type (what kind of work)
2. Scale Tier (size and complexity)
3. Trigger/Origin (what caused this work to start)
4. Solution Clarity (how defined the solution already is)

RULES:
- Do NOT commit to a classification until you have sufficient signal for all 4 Must-Know dimensions.
- If you need more information, ask at most 2 focused, non-repetitive questions per turn.
- Once you have sufficient signal, present your classification — do not ask more questions.
- Never invent stakeholder names, business details, or facts not provided by the user.
- Always respond in valid JSON using the schema below.

RESPONSE SCHEMA:
{{
  "status": "need_more_info" | "classification_ready",
  "follow_up_questions": ["..."],
  "message": "...",
  "engagement_type": "...",
  "scale_tier": "...",
  "explanation": "...",
  "captured_dimensions": {{
    "trigger_origin": "...",
    "solution_clarity": "...",
    "stakeholder_landscape": "...",
    "timeline_urgency": "..."
  }}
}}

Rules per status:
- "need_more_info": include follow_up_questions (max 2) and a conversational message. Omit engagement_type, scale_tier, explanation.
- "classification_ready": include engagement_type, scale_tier, explanation. Set follow_up_questions to [].
- captured_dimensions: populate whatever you have so far; use null for unknown fields.
- message: always present — conversational text shown to the user above any questions or classification.
"""


def build_intake_messages(
    project_name: str,
    project_description: str,
    conversation_history: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Build the messages array for an intake classification turn."""
    context = f'Project name: "{project_name}"'
    if project_description:
        context += f'\nInitial description: "{project_description}"'

    system = SYSTEM_INTAKE + f"\n\nCONTEXT:\n{context}"
    messages = [{"role": "system", "content": system}]
    messages.extend(conversation_history)
    return messages


def parse_intake_response(response_text: str) -> dict:
    """Parse the JSON response from the intake AI call.

    Returns a dict with at minimum a 'status' key.
    Falls back gracefully if JSON is malformed.
    """
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code fences
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

    # Normalise: ensure required keys exist
    if "status" not in data:
        data["status"] = "need_more_info"
    if "message" not in data:
        data["message"] = response_text  # surface raw text as fallback
    if "follow_up_questions" not in data:
        data["follow_up_questions"] = []
    if "captured_dimensions" not in data:
        data["captured_dimensions"] = {}

    # Validate engagement_type and scale_tier if present
    if data.get("engagement_type") and data["engagement_type"] not in ENGAGEMENT_TYPES:
        data["status"] = "need_more_info"
    if data.get("scale_tier") and data["scale_tier"] not in SCALE_TIERS:
        data["status"] = "need_more_info"

    return data
