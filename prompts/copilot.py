"""Prompt templates for the co-pilot module experience."""

from __future__ import annotations

SYSTEM_COPILOT_BASE = """You are an expert Business Analyst co-pilot embedded in BA Compass.
Your role is to guide the user through completing one specific BA module — the one shown in the context below.

Your behaviour:
- Ask exactly one question per response. Never ask two questions in the same message. Prioritise the most important unknown and ask only that.
- Use the project context (dimensions, prior artifacts) to make questions specific — never generic.
- Never invent stakeholder names, system names, business details, or facts not provided by the user.
- All methodology, module structure, and artifact types come from the BABOK-aligned library — do not invent new frameworks.
- When you have gathered sufficient information, you will be asked to generate a draft — wait for that trigger.
- Flag gaps as you notice them (missing stakeholders, vague scope, unaddressed risks) — do this inline, naturally.
- Keep responses conversational but concise. This is a working session, not a lecture.

PQ-01 — NEVER REPEAT PRIOR ARTIFACT CONTENT:
Before asking any question, check whether it has already been answered in the prior artifacts injected into your context. If the answer exists in a prior artifact, do not ask the question. Instead reference the artifact: 'From the [artifact name], I can see that [relevant information]. Building on that — [next question that advances the work rather than repeating it].' Never ask a user to repeat information that appears in any prior artifact.

PQ-03 — CHALLENGE VAGUE OR IMPRECISE INPUTS:
If the user provides a vague or imprecise answer, do not accept it and move on. Challenge it with a specific follow-up. If the user says 'faster', ask 'Faster by how much — do you have a target in days, hours, or percentage improvement?' If the user gives a metric that conflicts with a prior artifact, flag the discrepancy explicitly: 'I notice [prior artifact] established [value] — is [new value] the same target or a different one? I want to make sure the artifact is consistent with prior documents.' Never allow imprecise metrics to be documented without confirmation.

PQ-04 — DIRECTIVE CLOSING — NO PASSIVE LANGUAGE:
When you have gathered sufficient information to produce a complete artifact, do not ask 'is there anything else you would like to add?' Replace this with: 'I have sufficient information to produce a complete [module name]. Click Generate Draft above to generate the formal artifact, or tell me specifically if there is something you want to add first.' Be direct and confident — the user is relying on you to tell them when the work is done.

PQ-05 — COMPLETENESS CHECK BEFORE ACCEPTING SIGN-OFF:
If the user says anything equivalent to 'looks good', 'that covers it', 'we are done', or 'generate the draft' before all required content areas for this module are covered, do not proceed directly to draft. First perform a completeness check against the MODULE BACKGROUND CONTEXT. If anything is missing respond: 'Before we finalise — I want to make sure we have covered everything needed for a complete [module name]. I notice we have not addressed [specific missing area]. [Ask one specific question to fill the gap].' Only accept the sign-off and proceed to draft when all required areas are confirmed.

ENH-02 — EXAMPLES IN EVERY QUESTION:
Every question you ask must include at least two concrete examples relevant to the engagement type and context. Examples must be specific to the domain, not generic. For a process improvement engagement, examples should reference process steps, handoffs, systems, or stakeholder dynamics. For a technology implementation engagement, examples should reference integration points, user roles, or system capabilities. Never ask a bare question without examples. Format: question text followed by 'For example: [example 1], [example 2], or [example 3].'

ENH-04 — COMPLETENESS CHECK BEFORE DRAFT:
Before generating any draft, perform a completeness check against the required content areas for this module as specified in your MODULE BACKGROUND CONTEXT below. If any required content area has not been covered in the conversation, do not proceed to draft. Instead respond: 'Before I draft — I notice we have not covered [specific missing area]. This is important for a complete [module name] because [reason]. [Ask a specific question to gather the missing information].' Only proceed to draft when all required content areas have been addressed. When all areas are covered, respond: 'I have everything needed to produce a complete [module name]. Click Generate Draft to generate the formal artifact, or let me know if you want to add anything first.'
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

MODULE_CONTEXT: dict[str, dict] = {
    # ── Business Analysis Planning & Monitoring ──────────────────────────────
    "BA Approach Definition": {
        "required_sections": [
            "Methodology choice (agile / waterfall / hybrid) with explicit rationale",
            "Formality level and documentation standards",
            "Tooling decisions (repository, collaboration, modelling tools)",
            "Governance expectations and escalation paths",
            "Engagement-specific adaptations from standard BA practice",
        ],
        "must_gather_before_draft": [
            "Why this methodology was chosen over alternatives for this specific engagement",
            "Constraints that influenced the approach (time, budget, stakeholder availability)",
            "Tooling available or mandated by the organisation",
            "Who the BA approach needs to be approved by",
        ],
        "artifact_format": (
            "Structured approach document: sections for Methodology, Formality Level, Tooling, "
            "Governance, and Engagement-Specific Adaptations. Each section includes rationale."
        ),
        "junior_misses": [
            "Rationale for methodology choice — stating 'agile' without explaining why",
            "Escalation paths when BA work is blocked",
            "How the approach will be adapted if engagement scope changes",
        ],
        "common_omissions": [
            "Justification for methodology against engagement characteristics",
            "What happens when stakeholder availability is limited",
            "Governance escalation path",
        ],
    },
    "Stakeholder Engagement Planning": {
        "required_sections": [
            "All stakeholder groups with communication preferences",
            "Engagement frequency and cadence per group",
            "Communication channels per group",
            "Escalation paths for each stakeholder tier",
            "Key milestones requiring stakeholder input or sign-off",
        ],
        "must_gather_before_draft": [
            "Complete stakeholder list (cross-reference Stakeholder Register if available)",
            "Preferred communication method per group",
            "Frequency expectations — some groups may want weekly updates, others only at milestones",
            "Who has authority to escalate when engagement is blocked",
        ],
        "artifact_format": (
            "Engagement plan table: Stakeholder Group | Role | Communication Channel | "
            "Frequency | Key Touchpoints | Escalation Path. Narrative section for overall approach."
        ),
        "junior_misses": [
            "Escalation paths — what happens when a stakeholder is unresponsive",
            "Differentiating engagement intensity by stakeholder influence vs interest",
            "Milestone-driven touchpoints beyond regular cadence",
        ],
        "common_omissions": [
            "Escalation contacts",
            "Different engagement intensities per stakeholder tier",
            "What triggers an unplanned communication",
        ],
    },
    "BA Governance Setup": {
        "required_sections": [
            "Decision-making framework — who decides what",
            "Requirements change control process",
            "Approval authority matrix (who approves at each stage)",
            "Conflict resolution process",
            "Audit trail and version control expectations",
        ],
        "must_gather_before_draft": [
            "Who holds final approval authority for requirements",
            "How change requests will be submitted, assessed, and approved",
            "Who resolves conflicts between stakeholders",
            "What records must be kept and where",
        ],
        "artifact_format": (
            "Governance document: Decision Authority Matrix table, Change Control Process narrative, "
            "Conflict Resolution Protocol, and Records Management section."
        ),
        "junior_misses": [
            "Who holds veto or final approval authority",
            "What the change request process looks like in practice",
            "How conflicts between stakeholders are formally resolved",
        ],
        "common_omissions": [
            "Final approval authority",
            "Practical change request mechanism",
            "Conflict resolution process",
        ],
    },
    "Information Management Planning": {
        "required_sections": [
            "Artifact storage location and structure",
            "Versioning and naming conventions",
            "Access control — who can view and edit each artifact type",
            "Artifact lifecycle — when artifacts are created, updated, and retired",
            "Handoff process at engagement close",
        ],
        "must_gather_before_draft": [
            "Where artifacts will be stored (shared drive, tool, repository)",
            "Naming and versioning conventions to use",
            "Who needs access to which artifact types",
            "Retention and handoff requirements at project end",
        ],
        "artifact_format": (
            "Information management plan with: Storage Structure, Naming Conventions table, "
            "Access Control matrix, Artifact Lifecycle table, and Handoff Protocol."
        ),
        "junior_misses": [
            "Access control — not everyone should edit every artifact",
            "What happens to artifacts after the engagement closes",
            "Naming conventions for versioned artifacts",
        ],
        "common_omissions": [
            "Access control differentiation by artifact type",
            "Post-engagement retention and handoff process",
            "Version numbering conventions",
        ],
    },
    "Performance Metrics Definition": {
        "required_sections": [
            "BA quality metrics (e.g. requirements rework rate, defect-to-requirements traceability)",
            "Engagement effectiveness metrics (stakeholder satisfaction, on-time delivery)",
            "Measurement frequency and method for each metric",
            "Baseline and target for each metric",
            "Owner responsible for tracking each metric",
        ],
        "must_gather_before_draft": [
            "What 'good BA work' looks like on this specific engagement",
            "How quality will be measured — not just what will be measured",
            "Baseline current state for each metric if known",
            "Who will track and report on BA performance",
        ],
        "artifact_format": (
            "Metrics register table: Metric Name | Description | Measurement Method | "
            "Frequency | Baseline | Target | Owner. Narrative section on overall performance approach."
        ),
        "junior_misses": [
            "How each metric will actually be measured — not just naming it",
            "Baseline data to compare against",
            "Owner for each metric",
        ],
        "common_omissions": [
            "Measurement method per metric",
            "Baseline values",
            "Metric ownership",
        ],
    },
    # ── Elicitation & Collaboration ──────────────────────────────────────────
    "Elicitation Planning": {
        "required_sections": [
            "Technique selection per stakeholder group with rationale",
            "Scheduling and logistics for each elicitation activity",
            "Preparation requirements (pre-read materials, access, tools)",
            "Expected outputs from each technique",
            "Risks to elicitation (stakeholder availability, sensitive topics)",
        ],
        "must_gather_before_draft": [
            "Which stakeholder groups are involved",
            "Why each technique was chosen for each group (not just which technique)",
            "Scheduling constraints and logistics requirements",
            "What outputs are needed from each activity",
        ],
        "artifact_format": (
            "Elicitation plan: Technique Selection table (Group | Technique | Rationale | Output | "
            "Schedule), Preparation Checklist, and Risks section."
        ),
        "junior_misses": [
            "Rationale for why each technique suits each stakeholder group",
            "Preparation requirements — what must be ready before each session",
            "Elicitation risks and mitigations",
        ],
        "common_omissions": [
            "Technique rationale per group",
            "Preparation and logistics detail",
            "Elicitation risks",
        ],
    },
    "Stakeholder Interviews": {
        "required_sections": [
            "Interview guide per stakeholder group with 5-6 specific questions",
            "Interview objectives per group",
            "Sensitive areas and navigation approach per group",
            "Logistics (duration, format, recording approach)",
            "Analysis approach for interview outputs",
        ],
        "must_gather_before_draft": [
            "All stakeholder groups requiring individual interviews",
            "Specific objectives for each group's interview",
            "Sensitive or political areas to navigate carefully",
            "5-6 specific questions per group",
        ],
        "artifact_format": (
            "Interview guide document: one section per stakeholder group with Objectives, "
            "Questions (5-6 per group), Sensitive Areas, and Logistics. "
            "Summary analysis template at the end."
        ),
        "junior_misses": [
            "Sensitive or political areas that need careful navigation",
            "Differentiating questions per stakeholder group rather than one generic set",
            "Analysis approach for synthesising interview outputs",
        ],
        "common_omissions": [
            "Sensitive areas per group",
            "Group-specific question sets",
            "Output synthesis approach",
        ],
        "opening_approach": (
            "Structure the conversation around interview guide design per stakeholder group. "
            "For each group ask: what is the objective of this interview, what are five to six "
            "specific questions you would ask, and are there any sensitive areas to navigate carefully. "
            "After covering all primary stakeholder groups, proactively check for missing groups "
            "by referencing the Stakeholder Register artifact if it exists."
        ),
    },
    "Workshops & Focus Groups": {
        "required_sections": [
            "Workshop objectives and desired outputs",
            "Participant list with roles",
            "Agenda with timing",
            "Facilitation techniques (e.g. affinity mapping, dot voting, MoSCoW)",
            "Pre-work requirements",
            "Conflict management approach",
        ],
        "must_gather_before_draft": [
            "What decision or alignment the workshop must achieve",
            "Who must attend versus who is optional",
            "How long and in what format (in-person, virtual, hybrid)",
            "What facilitation technique suits the objective",
        ],
        "artifact_format": (
            "Workshop design document: Objectives, Participant List with roles, "
            "Agenda table (Time | Activity | Owner | Output), Facilitation Techniques, "
            "Pre-Work Requirements, and Conflict Management Protocol."
        ),
        "junior_misses": [
            "Specific facilitation technique choice with rationale",
            "What to do when participants disagree — conflict management",
            "Pre-work that enables productive workshop time",
        ],
        "common_omissions": [
            "Facilitation technique rationale",
            "Conflict management approach",
            "Pre-work requirements",
        ],
    },
    "Observation & Job Shadowing": {
        "required_sections": [
            "Observation objectives and focus areas",
            "Participants and processes to observe",
            "Observation protocol (passive vs active, duration, recording method)",
            "Data capture template",
            "Ethical and confidentiality considerations",
        ],
        "must_gather_before_draft": [
            "Which processes and roles will be observed",
            "What specifically to look for — undocumented workarounds, timing, handoffs",
            "Duration and scheduling",
            "How observations will be recorded and by whom",
        ],
        "artifact_format": (
            "Observation plan with: Objectives, Scope (processes/roles), Protocol, "
            "Data Capture Template, and Ethics/Confidentiality section."
        ),
        "junior_misses": [
            "Ethical and confidentiality considerations — participants have rights",
            "What specific behaviours to look for beyond just watching",
            "How to handle sensitive or restricted information observed",
        ],
        "common_omissions": [
            "Ethical and confidentiality handling",
            "Specific observation focus areas",
            "Data capture template design",
        ],
    },
    "Survey & Questionnaire Design": {
        "required_sections": [
            "Survey objectives and target population",
            "Question types and rationale (Likert, open-ended, multiple choice)",
            "Distribution method and timeline",
            "Response rate target and chase plan",
            "Analysis approach for responses",
        ],
        "must_gather_before_draft": [
            "What specific questions the survey must answer",
            "Who will receive it and how",
            "Expected response rate and what to do if it is insufficient",
            "How qualitative responses will be analysed",
        ],
        "artifact_format": (
            "Survey design document: Objectives, Question Set with type annotations, "
            "Distribution Plan, Response Rate Target, and Analysis Approach."
        ),
        "junior_misses": [
            "Response rate target and chase plan if response is low",
            "Rationale for question type choices",
            "Analysis approach for open-ended responses",
        ],
        "common_omissions": [
            "Response rate target",
            "Chase plan for low response",
            "Qualitative analysis approach",
        ],
    },
    "Document Analysis": {
        "required_sections": [
            "Documents to be reviewed with source and version",
            "Analysis objectives per document type",
            "Key findings structured by theme",
            "Gaps in existing documentation",
            "Reliability assessment of each source",
        ],
        "must_gather_before_draft": [
            "Which documents exist and are available",
            "What information each document is expected to yield",
            "Gaps where documentation is absent or outdated",
            "How reliable and current each source is",
        ],
        "artifact_format": (
            "Document analysis register: Source | Version | Relevance | Key Findings | Gaps. "
            "Narrative synthesis section. Reliability assessment per source."
        ),
        "junior_misses": [
            "Reliability assessment — old or unofficial documents must be flagged",
            "What is notably absent from existing documentation",
            "Cross-referencing contradictions between documents",
        ],
        "common_omissions": [
            "Source reliability assessment",
            "Documentation gaps",
            "Contradictions between sources",
        ],
    },
    "Benchmarking & Market Analysis": {
        "required_sections": [
            "Benchmarking scope — what is being compared and against what",
            "Peer organisations or industry standards used as reference points",
            "Performance data for each benchmark dimension",
            "Gap between current state and benchmark",
            "Implications for solution design",
        ],
        "must_gather_before_draft": [
            "What dimensions are being benchmarked (process time, cost, quality, etc.)",
            "What reference sources are being used (industry reports, competitor data, standards)",
            "Current performance data to compare against benchmarks",
            "What the benchmark analysis implies for the solution",
        ],
        "artifact_format": (
            "Benchmarking report: Scope section, Benchmark Sources table, "
            "Comparison table (Dimension | Current | Benchmark | Gap | Implication), "
            "and Recommendations section."
        ),
        "junior_misses": [
            "Source credibility — not all benchmarks are equally reliable",
            "Implications for solution design, not just the gap data",
            "Accounting for context differences between benchmarked organisations",
        ],
        "common_omissions": [
            "Source credibility assessment",
            "Solution implications from benchmark gaps",
            "Context differences that qualify the benchmark",
        ],
    },
    "Brainstorming Facilitation": {
        "required_sections": [
            "Brainstorming objectives and scope",
            "Facilitation method (silent brainstorm, round-robin, mind mapping)",
            "Participant list and roles",
            "Idea capture and organisation method",
            "Convergence technique to prioritise outputs",
        ],
        "must_gather_before_draft": [
            "What problem or opportunity the brainstorm addresses",
            "Which facilitation method suits the group dynamic",
            "How ideas will be captured and organised during the session",
            "How outputs will be prioritised or converged after the session",
        ],
        "artifact_format": (
            "Brainstorming plan: Objectives, Method with rationale, Participant List, "
            "Session Agenda, Idea Capture Template, and Convergence/Prioritisation approach."
        ),
        "junior_misses": [
            "How ideas will be prioritised after generation — brainstorms need convergence",
            "Managing dominant participants who shut down contribution",
            "Connecting brainstorm outputs back to the problem statement",
        ],
        "common_omissions": [
            "Convergence technique after idea generation",
            "Dominant participant management",
            "Link between outputs and the original problem",
        ],
    },
    "Elicitation Results Documentation": {
        "required_sections": [
            "Summary of elicitation activities completed",
            "Raw outputs organised by theme or stakeholder group",
            "Conflicts or contradictions between stakeholder inputs",
            "Preliminary insights and patterns",
            "Outstanding questions requiring follow-up",
        ],
        "must_gather_before_draft": [
            "All elicitation activities completed for this engagement",
            "Key themes that emerged across activities",
            "Conflicts between stakeholder inputs that need resolution",
            "What remains unanswered after elicitation",
        ],
        "artifact_format": (
            "Elicitation results document: Activities Summary table, Thematic Findings sections, "
            "Conflicts Register, Preliminary Insights, and Outstanding Questions log."
        ),
        "junior_misses": [
            "Documenting conflicts between stakeholder views — not just consensus",
            "Outstanding questions that elicitation did not resolve",
            "Distinguishing stakeholder opinions from confirmed facts",
        ],
        "common_omissions": [
            "Conflicts and contradictions between stakeholder inputs",
            "Outstanding questions register",
            "Opinion vs fact differentiation",
        ],
    },
    # ── Requirements Life Cycle Management ────────────────────────────────────
    "Requirements Traceability Setup": {
        "required_sections": [
            "Traceability framework — which artifacts link to which",
            "Traceability tool or mechanism",
            "ID naming convention for requirements, user stories, and test cases",
            "Roles responsible for maintaining traceability",
            "When traceability is updated during the engagement lifecycle",
        ],
        "must_gather_before_draft": [
            "Which artifact types need to be traced (BRs to FRs, FRs to test cases, etc.)",
            "What tool will be used — spreadsheet, Jira, specialist tool",
            "Who is responsible for maintaining the traceability matrix",
            "When updates are triggered",
        ],
        "artifact_format": (
            "Traceability framework document: Linkage Diagram (which artifacts connect to which), "
            "ID Naming Convention table, Tool Decision, Roles table, and Maintenance Protocol."
        ),
        "junior_misses": [
            "Who is responsible for keeping traceability up to date during the engagement",
            "Tracing in both directions — forward to test cases and backward to objectives",
            "What triggers a traceability update",
        ],
        "common_omissions": [
            "Bidirectional traceability (forward and backward)",
            "Maintenance responsibility and trigger",
            "Tool decision with rationale",
        ],
    },
    "Requirements Prioritization": {
        "required_sections": [
            "Prioritisation method (MoSCoW, Kano, weighted scoring) with rationale",
            "Prioritisation criteria with weights",
            "Prioritised requirements list with priority assignment and rationale",
            "Stakeholders involved in prioritisation decisions",
            "How conflicts in priority between stakeholders are resolved",
        ],
        "must_gather_before_draft": [
            "Which prioritisation method is appropriate and why",
            "The criteria being used to prioritise",
            "Who has authority to make final priority decisions",
            "How conflicting stakeholder priorities are resolved",
        ],
        "artifact_format": (
            "Prioritisation document: Method section with rationale, Criteria table with weights, "
            "Prioritised Requirements table (ID | Requirement | Priority | Rationale), "
            "and Conflict Resolution record."
        ),
        "junior_misses": [
            "Rationale per priority assignment — not just labelling Must Have",
            "How to resolve when two stakeholders assign conflicting priorities",
            "Naming the prioritisation method and explaining why it was chosen",
        ],
        "common_omissions": [
            "Priority rationale per requirement",
            "Conflict resolution between competing stakeholder priorities",
            "Prioritisation method rationale",
        ],
    },
    "Requirements Change Management": {
        "required_sections": [
            "Change request process (submission, assessment, approval, implementation)",
            "Change request form template",
            "Impact assessment criteria",
            "Approval authority by change type/size",
            "Communication process for approved changes",
        ],
        "must_gather_before_draft": [
            "How change requests are submitted",
            "Who assesses impact and how",
            "Approval authority — different levels for minor vs major changes",
            "How approved changes are communicated to the team",
        ],
        "artifact_format": (
            "Change management procedure: Process Flowchart narrative, Change Request Form template, "
            "Impact Assessment Criteria, Approval Authority Matrix, Communication Protocol."
        ),
        "junior_misses": [
            "Different approval levels for minor vs significant scope changes",
            "How changes are communicated to downstream stakeholders",
            "Handling emergency changes outside the normal process",
        ],
        "common_omissions": [
            "Tiered approval authority by change magnitude",
            "Change communication process",
            "Emergency change procedure",
        ],
    },
    "Requirements Baselining": {
        "required_sections": [
            "Baseline scope — which requirements are included in the baseline",
            "Baseline version and date",
            "Sign-off record with names, roles, and dates",
            "What changes require a rebaseline",
            "Where the baseline is stored and access control",
        ],
        "must_gather_before_draft": [
            "Which requirements are ready for baseline",
            "Who must sign off and by when",
            "What will trigger a rebaseline",
            "Storage location and access",
        ],
        "artifact_format": (
            "Baseline record: Scope section, Included Requirements list with IDs, "
            "Version record, Sign-off Table (Name | Role | Date | Signature), "
            "Rebaseline Trigger Criteria, Storage Protocol."
        ),
        "junior_misses": [
            "What specifically triggers a rebaseline — not all changes require one",
            "Sign-off accountability — role, not just name",
            "How out-of-scope requirements are handled that are not in the baseline",
        ],
        "common_omissions": [
            "Rebaseline trigger criteria",
            "Role-specific sign-off accountability",
            "Out-of-baseline requirements handling",
        ],
    },
    "Requirements Sign-off & Approval": {
        "required_sections": [
            "Formal sign-off process and timeline",
            "Approvers list with roles and requirements scope each approver covers",
            "Review period and objection handling process",
            "Signed approval record",
            "What happens if a stakeholder refuses to sign",
        ],
        "must_gather_before_draft": [
            "Who must sign off on which requirements",
            "Review period duration",
            "Escalation process if a stakeholder objects or refuses",
            "Format of the formal approval record",
        ],
        "artifact_format": (
            "Sign-off plan: Approvers table (Name | Role | Requirements Scope | Deadline), "
            "Review Process narrative, Objection Handling Protocol, and Approval Record template."
        ),
        "junior_misses": [
            "What happens when a stakeholder objects or refuses to sign",
            "Scoping which approver covers which requirements",
            "Escalation when sign-off is missed or blocked",
        ],
        "common_omissions": [
            "Objection and refusal handling",
            "Approver scope per stakeholder",
            "Escalation path for missed sign-off",
        ],
    },
    "Traceability Matrix": {
        "required_sections": [
            "Business Objectives to Business Requirements linkage",
            "Business Requirements to Functional Requirements linkage",
            "Functional Requirements to Test Cases linkage",
            "Coverage gaps — FRs without test cases, BRs without FRs",
            "Maintenance status and last updated date",
        ],
        "must_gather_before_draft": [
            "Complete list of Business Objectives, BRs, and FRs to include",
            "Existing test cases or user stories to link",
            "Any known gaps in traceability coverage",
            "How the matrix will be maintained going forward",
        ],
        "artifact_format": (
            "Traceability Matrix table: columns BO-ID | BR-ID | FR-ID | Test Case ID | Status. "
            "Coverage Gap Analysis section. Maintenance Protocol."
        ),
        "junior_misses": [
            "Bidirectional traceability — not just top-down",
            "Coverage gap analysis — highlighting what is not yet covered",
            "Maintenance protocol for keeping the matrix current",
        ],
        "common_omissions": [
            "Backward traceability (test cases back to objectives)",
            "Gap analysis",
            "Maintenance ownership and process",
        ],
    },
    # ── Strategy Analysis ──────────────────────────────────────────────────────
    "Current State Assessment": {
        "required_sections": [
            "Process overview — steps, duration, handoff count",
            "Systems and tools landscape",
            "Stakeholder involvement per team",
            "Pain points with supporting evidence",
            "Impact on end users",
            "Performance gaps with data where available",
        ],
        "must_gather_before_draft": [
            "Current process steps and their durations",
            "All systems and tools in use (including unofficial/shadow tools)",
            "Informal workarounds not documented in official procedures",
            "End user experience — distinct from the process owner perspective",
            "System integration gaps and data flow breaks",
        ],
        "artifact_format": (
            "Structured assessment with: Process Narrative section, Systems Landscape table, "
            "Stakeholder Involvement table, Pain Point Register, End User Impact section, "
            "and Performance Gap table."
        ),
        "junior_misses": [
            "System integration gaps — where data does not flow cleanly between systems",
            "Informal workarounds — what people actually do vs what the procedure says",
            "End user experience data separate from process owner perspective",
        ],
        "common_omissions": [
            "Integration gaps between systems",
            "Undocumented workarounds",
            "End-user perspective distinct from process owner",
        ],
    },
    "Problem Statement Definition": {
        "required_sections": [
            "Trigger origin — what event or evidence prompted this engagement",
            "Quantified impact metrics — cost, time, quality, risk",
            "Pain points with supporting evidence per stakeholder group",
            "Stakeholder landscape with roles and their stake in the problem",
            "Desired future state with measurable targets",
            "Baseline metrics — current performance before any change",
        ],
        "must_gather_before_draft": [
            "What event or evidence triggered this engagement",
            "Current measurable baseline (e.g. current processing time, error rate, cost)",
            "Specific concerns per stakeholder group — not just aggregate pain",
            "Quantified future state targets (e.g. reduce from X to Y by date Z)",
        ],
        "artifact_format": (
            "Structured problem statement: Context → Evidence → Impact → Desired Outcome. "
            "Sections: Background, Current State Evidence, Stakeholder Impact by Group, "
            "Baseline Metrics table, Desired Future State with Measurable Targets."
        ),
        "junior_misses": [
            "Quantified baseline metrics — stating the problem without numbers",
            "Specific stakeholder concerns per group — not just one generic pain point",
            "Measurable future state targets — 'improved' is not a target",
        ],
        "common_omissions": [
            "Baseline metrics",
            "Per-stakeholder concern differentiation",
            "Measurable targets in the desired future state",
        ],
    },
    "Root Cause Analysis": {
        "required_sections": [
            "Named technique applied (5-Whys or fishbone) with explicit labelling",
            "At least two complete root cause chains traced to root level",
            "Coverage of all major pain points from Current State Assessment",
            "Root cause summary connecting causes to the Problem Statement",
            "Implications for solution design",
        ],
        "must_gather_before_draft": [
            "Primary pain point to start the first Why chain",
            "Causal chain for each pain point traced to root level (not stopping at symptoms)",
            "Confirmation that all pain points from current state are covered",
            "Interconnections between root causes if any",
        ],
        "artifact_format": (
            "For 5-Whys: numbered Why chains per pain point, each chain labelled with the pain point. "
            "For fishbone: category branches (People, Process, Technology, Data, Governance) "
            "with cause entries. Root Cause Summary table. Solution Implications section."
        ),
        "junior_misses": [
            "Stopping at symptom level — 'the process is slow' is not a root cause",
            "Covering only one root cause when multiple independent causes exist",
            "Not applying a named technique explicitly",
        ],
        "common_omissions": [
            "Second and third root cause chains",
            "Connection back to all pain points identified in current state",
            "Named technique application",
        ],
        "opening_approach": (
            "Open the conversation by naming the 5-Whys technique and applying it immediately "
            "to the most significant pain point identified in prior artifacts. Say: 'Let's apply "
            "the 5-Whys technique to identify the root cause. Starting with [pain point from "
            "current state assessment] — why does this problem occur?' Chain the whys explicitly "
            "in the conversation. Do not move to a second root cause until the first chain reaches "
            "a root level cause. Do not offer the technique as an option — apply it from the first message."
        ),
    },
    "Business Need Definition": {
        "required_sections": [
            "The business need stated as an outcome, not a solution",
            "Why this need exists now — triggering conditions",
            "Who the primary beneficiaries are",
            "How the need aligns to organisational strategy or objectives",
            "What 'met' looks like — measurable success conditions",
        ],
        "must_gather_before_draft": [
            "The business outcome required — not the solution",
            "Why this is a priority now (trigger, urgency, cost of inaction)",
            "Strategic alignment — which organisational goal this serves",
            "Measurable definition of when the need is satisfied",
        ],
        "artifact_format": (
            "Business need statement: Context, Need Statement (outcome-framed), "
            "Triggering Conditions, Beneficiaries, Strategic Alignment, "
            "and Success Conditions (measurable)."
        ),
        "junior_misses": [
            "Framing the need as a solution rather than an outcome",
            "Strategic alignment — connecting the need to organisational goals",
            "Measurable success conditions for when the need is met",
        ],
        "common_omissions": [
            "Outcome framing (not solution framing)",
            "Strategic alignment",
            "Measurable success conditions",
        ],
    },
    "Future State Design": {
        "required_sections": [
            "Design principles guiding the future state",
            "Future state process narrative",
            "System integrations with specific technical requirements",
            "Stakeholder enablement plan — training and change management per group",
            "KPIs with measurement approach (not just what, but how)",
            "Anticipated challenges with mitigations",
            "SLAs — service level targets for the future state",
        ],
        "must_gather_before_draft": [
            "Design principles the future state must honour",
            "Each integration point with its specific technical requirements",
            "Training needs per stakeholder group",
            "How each KPI will be measured — method, frequency, owner",
            "Change management implications and anticipated resistance",
        ],
        "artifact_format": (
            "Future State Design document: Design Principles, Process Narrative, "
            "Systems/Integrations table (System | Integration Type | Technical Requirement | Owner), "
            "KPI table (KPI | Target | Measurement Method | Frequency | Owner), "
            "Enablement Plan per stakeholder group, Challenges and Mitigations table, SLAs section."
        ),
        "junior_misses": [
            "Specific SLAs — not just 'faster' but 'within 2 business days'",
            "How KPIs will be measured, not just what they are",
            "Training requirements differentiated per stakeholder group",
            "Change management implications",
        ],
        "common_omissions": [
            "SLA targets",
            "KPI measurement methodology",
            "Per-group training requirements",
            "Change management plan",
        ],
    },
    "Gap Analysis": {
        "required_sections": [
            "Current state description per identified gap area",
            "Future state description per identified gap area",
            "Specific delta (what needs to change) per gap",
            "Process ownership gap",
            "Visibility and reporting gap",
            "Cultural or behavioural change gap",
            "Priority or effort indicator per gap",
        ],
        "must_gather_before_draft": [
            "Confirmation of gaps derived from prior artifacts — present these to user for confirmation, do not ask user to identify gaps from scratch",
            "Process ownership situation — is it clear who owns what in the future state",
            "Visibility/reporting gap — can the organisation see what it needs to see",
            "Any cultural or behavioural change required, not just process or system changes",
        ],
        "artifact_format": (
            "Gap Analysis table: Gap Area | Current State | Future State | Delta | Priority. "
            "One row per gap. Summary narrative. Change Implications section."
        ),
        "junior_misses": [
            "Process ownership gap — who owns the new process is often unclear",
            "Visibility gap — can the organisation monitor the future state effectively",
            "Cultural or behavioural gaps — assuming technology alone closes gaps",
        ],
        "common_omissions": [
            "Process ownership gap",
            "Visibility/reporting gap",
            "Cultural and behavioural change gap",
        ],
        "opening_approach": (
            "Open by stating the structured comparison approach. Say: 'We will compare the current "
            "state to the future state for each identified gap area. Let me start with the first "
            "gap — [derive a specific gap from prior artifacts such as the Current State Assessment "
            "and Future State Design].' Work through each gap systematically. Do not ask the user "
            "to identify the gaps — derive them from the prior artifacts and present them for confirmation."
        ),
    },
    "Risk Assessment": {
        "required_sections": [
            "Risk register with ID, description, probability, impact, and severity rating",
            "Risk category (strategic, operational, technical, compliance, people)",
            "Mitigation action per risk",
            "Risk owner per risk",
            "Residual risk after mitigation",
            "Monitoring and review approach",
        ],
        "must_gather_before_draft": [
            "All risk categories relevant to this engagement",
            "Probability and impact assessment for each risk",
            "Mitigation action and who owns it",
            "Residual risk after mitigation — not all risks can be fully mitigated",
        ],
        "artifact_format": (
            "Risk Register table: Risk ID | Category | Description | Probability | Impact | "
            "Severity | Mitigation | Owner | Residual Risk | Status. "
            "Narrative section on risk management approach."
        ),
        "junior_misses": [
            "Residual risk — what risk remains after mitigation",
            "Risk owner — assigning someone accountable for each risk",
            "People and change management risks, not just technical risks",
        ],
        "common_omissions": [
            "Residual risk after mitigation",
            "Risk ownership",
            "People/change management risk category",
        ],
    },
    "Assumption & Constraint Documentation": {
        "required_sections": [
            "Assumptions list — what is being assumed to be true",
            "Validation approach per assumption (how and when it will be confirmed)",
            "Constraints list — boundaries the solution must operate within",
            "Impact if an assumption proves false",
            "Constraint source (regulatory, technical, budgetary, policy)",
        ],
        "must_gather_before_draft": [
            "All assumptions being made — technical, people, process, data",
            "How each assumption will be confirmed or disproved",
            "All constraints — budget, time, technology, regulatory, policy",
            "What happens to the solution if a key assumption is invalidated",
        ],
        "artifact_format": (
            "Two-part document: Assumptions Register (ID | Assumption | Validation Method | "
            "If False Impact | Status) and Constraints Register (ID | Constraint | Category | "
            "Source | Impact on Solution)."
        ),
        "junior_misses": [
            "Validation approach — how and when each assumption will be confirmed",
            "Impact analysis if the assumption is wrong",
            "Distinguishing assumptions (unverified beliefs) from constraints (hard limits)",
        ],
        "common_omissions": [
            "Assumption validation method",
            "Impact if assumption is invalidated",
            "Assumption vs constraint differentiation",
        ],
    },
    "Business Case Development": {
        "required_sections": [
            "Problem statement summary",
            "Solution options considered with pros and cons",
            "Recommended option with rationale",
            "Cost-benefit analysis with NPV or payback period",
            "Risks of the recommended option",
            "Risks of doing nothing",
            "Success criteria",
        ],
        "must_gather_before_draft": [
            "All solution options considered",
            "Cost data for the recommended option",
            "Quantified benefits with timeframes",
            "Risk of inaction — what happens if nothing is done",
        ],
        "artifact_format": (
            "Business case: Executive Summary, Problem Summary, Options Analysis table, "
            "Recommended Option with rationale, Financial Analysis (cost/benefit table, ROI), "
            "Risk Summary, Do-Nothing Analysis, Success Criteria."
        ),
        "junior_misses": [
            "Do-nothing risk — the cost of inaction, not just the cost of the solution",
            "Multiple options with genuine pros and cons — not just one option presented as obvious",
            "Quantified benefits with realistic timeframes",
        ],
        "common_omissions": [
            "Do-nothing risk analysis",
            "Genuine multi-option comparison",
            "Quantified benefit timeframes",
        ],
    },
    "Change Strategy Definition": {
        "required_sections": [
            "Change vision and key messages",
            "Stakeholder impact assessment by group",
            "Change management activities and timeline",
            "Communication plan",
            "Training plan per stakeholder group",
            "Change readiness approach",
            "Success metrics for the change program",
        ],
        "must_gather_before_draft": [
            "Change vision and the key message for each stakeholder group",
            "Resistance hotspots — which groups are most likely to resist",
            "Training needs per group",
            "How change readiness will be measured before go-live",
        ],
        "artifact_format": (
            "Change strategy document: Change Vision, Stakeholder Impact table, "
            "Communication Plan, Training Plan by group, Readiness Assessment Approach, "
            "Change Activity Timeline, and Success Metrics."
        ),
        "junior_misses": [
            "Resistance hotspot identification — not all groups accept change equally",
            "Differentiated training plans per stakeholder group",
            "How change readiness will be assessed before implementation",
        ],
        "common_omissions": [
            "Resistance hotspot identification",
            "Per-group training differentiation",
            "Change readiness assessment approach",
        ],
    },
    # ── Requirements Analysis & Design Definition ─────────────────────────────
    "Stakeholder Requirements Documentation": {
        "required_sections": [
            "Requirements stated in stakeholder language (not system language)",
            "One section per stakeholder group",
            "Conflicting requirements between groups explicitly flagged",
            "Priority or importance indicator per requirement",
            "Traceability to stakeholder group and elicitation source",
        ],
        "must_gather_before_draft": [
            "Requirements from each stakeholder group in their own language",
            "Conflicts between what different groups need",
            "Relative importance of requirements per group",
            "Elicitation source for each requirement",
        ],
        "artifact_format": (
            "Stakeholder requirements document: one section per group with requirements list "
            "(SR-ID | Requirement | Priority | Source). Conflicts section. "
            "Traceability to elicitation activities."
        ),
        "junior_misses": [
            "Keeping requirements in stakeholder language, not translating to system specs prematurely",
            "Explicitly documenting conflicts between groups",
            "Traceability back to which elicitation activity surfaced each requirement",
        ],
        "common_omissions": [
            "Stakeholder language (not system language)",
            "Inter-group conflicts",
            "Elicitation source traceability",
        ],
    },
    "Business Requirements Documentation": {
        "required_sections": [
            "High-level business objectives the solution must satisfy",
            "BR-ID format (BR-01, BR-02...)",
            "Each BR linked to at least one business objective",
            "Rationale for each requirement",
            "In-scope vs out-of-scope delineation",
        ],
        "must_gather_before_draft": [
            "Business objectives this engagement must achieve",
            "High-level business needs (not system functions)",
            "What is explicitly out of scope and why",
        ],
        "artifact_format": (
            "BRD: Objectives section, Business Requirements table (BR-ID | Requirement | "
            "Linked Objective | Priority | Rationale), Scope Boundary section."
        ),
        "junior_misses": [
            "Linking each BR to a specific business objective — not just listing requirements",
            "Rationale per requirement — why does the business need this",
            "Explicit out-of-scope documentation",
        ],
        "common_omissions": [
            "Objective linkage per BR",
            "Rationale per requirement",
            "Out-of-scope documentation",
        ],
    },
    "Functional Requirements Documentation": {
        "required_sections": [
            "FR-ID format (FR-01, FR-02...) for every requirement",
            "Each FR with: ID, description, details paragraph, rationale paragraph",
            "Coverage of automation triggers",
            "Coverage of system integrations",
            "Coverage of ownership designation",
            "Coverage of SLA monitoring requirements",
            "Coverage of dashboard and reporting requirements",
            "Coverage of user-facing features",
        ],
        "must_gather_before_draft": [
            "All functional areas from the Future State Design",
            "SLA monitoring requirements — how the system tracks against SLAs",
            "Escalation authority — who is notified and with what authority when SLAs breach",
            "Notification trigger specifications — what events trigger what notifications",
            "Dashboard requirements — what data must be visible to whom",
        ],
        "artifact_format": (
            "FRD: Requirements table (FR-ID | Description | Details | Rationale | Priority | "
            "Linked BR). Each FR must have a full details paragraph, not just a headline. "
            "Grouped by functional area."
        ),
        "junior_misses": [
            "SLA monitoring as a distinct functional requirement",
            "Escalation authority requirements",
            "Notification trigger specifications",
        ],
        "common_omissions": [
            "SLA monitoring requirement",
            "Escalation path and authority requirements",
            "Notification trigger specifications",
        ],
    },
    "Non-Functional Requirements Documentation": {
        "required_sections": [
            "Performance requirements with quantified thresholds",
            "Security and access control requirements",
            "Usability and accessibility requirements",
            "Scalability and capacity requirements",
            "Compliance and regulatory requirements",
            "Availability and recovery requirements",
            "Rationale paragraph for each NFR",
        ],
        "must_gather_before_draft": [
            "Performance thresholds (response time, throughput, concurrency)",
            "Security requirements specific to this engagement",
            "Compliance obligations — regulatory, industry, or policy",
            "Availability requirements — uptime, maintenance windows, disaster recovery",
        ],
        "artifact_format": (
            "NFR document: one section per category (Performance, Security, Usability, "
            "Scalability, Compliance, Availability). Each NFR has: ID, statement, "
            "quantified threshold, rationale paragraph."
        ),
        "junior_misses": [
            "Quantified thresholds — 'fast' is not an NFR; '< 2 seconds for 95% of requests' is",
            "Rationale paragraphs explaining why each NFR exists",
            "Compliance requirements specific to the domain and jurisdiction",
        ],
        "common_omissions": [
            "Quantified thresholds per NFR",
            "Rationale paragraphs",
            "Domain-specific compliance requirements",
        ],
    },
    "User Story Writing": {
        "required_sections": [
            "User stories in As a [role] / I want [capability] / So that [benefit] format",
            "US-ID format for each story",
            "Acceptance criteria per story (Given/When/Then or bullet criteria)",
            "Story size/complexity estimate or T-shirt sizing",
            "Dependency mapping between stories",
            "Definition of Done applicable to all stories",
        ],
        "must_gather_before_draft": [
            "All user roles/personas that will have stories",
            "Core capabilities needed per role",
            "Acceptance criteria for each story",
            "Dependencies between stories",
        ],
        "artifact_format": (
            "User story backlog: US-ID | Story (As a / I want / So that) | Acceptance Criteria | "
            "Size | Dependencies | Priority. Definition of Done section at the top."
        ),
        "junior_misses": [
            "Acceptance criteria are often too vague — must be testable",
            "Dependency mapping between stories",
            "Definition of Done that applies to all stories in the backlog",
        ],
        "common_omissions": [
            "Testable acceptance criteria",
            "Story dependencies",
            "Definition of Done",
        ],
    },
    "Process Modeling — Current State": {
        "required_sections": [
            "Swimlane structure identifying all roles/teams with their own lane",
            "Process steps per swimlane in sequence",
            "Handoffs between swimlanes with explicit notation",
            "Decision points with branching paths",
            "System touchpoints in each step",
            "Pain points annotated on the diagram",
        ],
        "must_gather_before_draft": [
            "All roles or teams that have their own swimlane",
            "Steps performed by each lane in sequence",
            "All handoff points — where work moves from one lane to another",
            "Decision points and their branching logic",
            "System or tool used in each step",
        ],
        "artifact_format": (
            "Swimlane diagram narrative (text-based): structured by lane with Step ID, "
            "Step Description, Inputs, Outputs, Handoffs, Systems, and Pain Points. "
            "One section per swimlane."
        ),
        "junior_misses": [
            "Handoffs — where work passes between lanes is where most delays occur",
            "Decision points and what happens on each branch",
            "Annotating pain points directly on the process rather than separating them",
        ],
        "common_omissions": [
            "Explicit handoff notation between lanes",
            "Decision point branching",
            "Pain point annotations on the process",
        ],
        "opening_approach": (
            "Structure the entire conversation around swimlane identification from the first question. "
            "Ask: 'Let's build the swimlane structure. Which teams or roles have their own lane in "
            "this process? For example: a Procurement team lane, a Finance Approvals lane, and a "
            "Vendor lane — or something else for your context?' Then systematically gather the steps, "
            "handoffs, decision points, and dependencies for each lane. The artifact output must be "
            "structured by swimlane with explicit handoff notation between lanes."
        ),
    },
    "Process Modeling — Future State": {
        "required_sections": [
            "Swimlane structure for the future state (may differ from current state)",
            "Process steps per swimlane showing the redesigned flow",
            "Handoffs between swimlanes — reduced or restructured vs current state",
            "Automation points explicitly marked",
            "System touchpoints per step",
            "Comparison to current state — what changed and why",
        ],
        "must_gather_before_draft": [
            "Future state swimlane structure — which roles/teams are involved",
            "Steps per lane in the redesigned process",
            "Automation points — steps that will be automated",
            "How handoffs are reduced or improved vs current state",
            "Systems involved in each future state step",
        ],
        "artifact_format": (
            "Swimlane diagram narrative structured by lane: Step ID, Description, "
            "Automation flag (Manual/Automated/Semi-automated), System, Handoffs. "
            "Change Summary section comparing current vs future state by lane."
        ),
        "junior_misses": [
            "Explicitly marking automation points — which steps are automated vs manual",
            "Change summary comparing current to future — makes the value visible",
            "New roles or restructured responsibilities in the future state",
        ],
        "common_omissions": [
            "Automation point annotation",
            "Current-to-future change summary",
            "New or restructured role responsibilities",
        ],
        "opening_approach": (
            "Structure the entire conversation around swimlane identification for the future state. "
            "Ask: 'Let's define the future state swimlane structure. Which teams or roles have their "
            "own lane — and does this differ from the current state? For example: if procurement was "
            "manual before but is now automated, we may no longer need a Procurement Analyst lane.' "
            "Then systematically gather the redesigned steps, automation points, and handoffs for "
            "each lane. The artifact must be structured by swimlane with explicit automation and "
            "handoff notation."
        ),
    },
    "Use Case Development": {
        "required_sections": [
            "Actor identification (primary and secondary actors)",
            "Use case list with UC-ID format",
            "Normal flow for each use case",
            "Alternative flows for each use case",
            "Exception flows for each use case",
            "Pre-conditions and post-conditions per use case",
        ],
        "must_gather_before_draft": [
            "All actors (human and system) interacting with the solution",
            "All use cases — normal, alternative, and exception flows",
            "Pre-conditions (what must be true before the use case starts)",
            "Post-conditions (what the system state is after the use case completes)",
        ],
        "artifact_format": (
            "Use case specification: Actor list, Use Case Index table, then one section per use case: "
            "UC-ID, Name, Actor, Pre-conditions, Normal Flow (numbered steps), "
            "Alternative Flows, Exception Flows, Post-conditions."
        ),
        "junior_misses": [
            "Exception flows — what happens when things go wrong is often omitted",
            "System actors as well as human actors",
            "Pre-conditions — what must already be true for the use case to start",
        ],
        "common_omissions": [
            "Exception flows",
            "System actors",
            "Pre-conditions and post-conditions",
        ],
    },
    "Data Requirements Definition": {
        "required_sections": [
            "Data entities required by the solution",
            "Data sources for each entity",
            "Data transformations required",
            "Data quality requirements (completeness, accuracy, timeliness)",
            "Data governance requirements (ownership, retention, access)",
            "Data migration requirements if applicable",
        ],
        "must_gather_before_draft": [
            "All data the solution needs to function",
            "Where that data comes from and its quality",
            "Transformations needed before data is usable",
            "Data governance obligations — ownership, retention, access control",
        ],
        "artifact_format": (
            "Data requirements document: Data Entity register (Entity | Source | Owner | "
            "Quality Standard | Retention), Transformation Requirements section, "
            "Data Governance section, Migration Requirements section."
        ),
        "junior_misses": [
            "Data quality requirements — not just what data is needed but how clean it must be",
            "Data governance — ownership, retention, and access control",
            "Data migration if legacy data must be moved to the new solution",
        ],
        "common_omissions": [
            "Data quality requirements",
            "Data governance (ownership, retention, access)",
            "Data migration requirements",
        ],
    },
    "Business Rules Documentation": {
        "required_sections": [
            "Business rule register with BR-Rule-ID format",
            "Each rule: condition, action, outcome (If [condition] Then [action])",
            "Rule category (calculation, constraint, classification, inference)",
            "Source of the rule (policy, regulation, operational procedure)",
            "Exceptions and edge cases per rule",
        ],
        "must_gather_before_draft": [
            "All rules governing how the solution must behave",
            "The condition that triggers each rule",
            "Exceptions to each rule",
            "Source authority for each rule (who owns it)",
        ],
        "artifact_format": (
            "Business rules register: Rule ID | Category | Rule Statement (If [condition] Then [action]) | "
            "Exceptions | Source | Owner. Grouped by category."
        ),
        "junior_misses": [
            "Exceptions to rules — every rule has edge cases",
            "Rule source authority — who is responsible for the rule and can change it",
            "Rule categories — calculation rules behave differently from constraint rules",
        ],
        "common_omissions": [
            "Exceptions per rule",
            "Rule source and ownership",
            "Rule category classification",
        ],
    },
    "Acceptance Criteria Definition": {
        "required_sections": [
            "One or more testable criteria per functional requirement",
            "What is measured per criterion",
            "Pass threshold per criterion",
            "Verification method (automated test, manual test, review, demonstration)",
            "Test instance count",
            "Verified By — sign-off owner per criterion",
        ],
        "must_gather_before_draft": [
            "Complete list of functional requirements to map criteria to",
            "Pass/fail threshold for each criterion (specific, not 'works correctly')",
            "How each criterion will be verified — test type and method",
            "Number of test instances required",
            "Who signs off that each criterion is met",
        ],
        "artifact_format": (
            "AC table: FR-ID | Criterion | Measurement | Pass Threshold | Verification Method | "
            "Test Instances | Verified By. One row per criterion. Multiple rows per FR where needed."
        ),
        "junior_misses": [
            "Verification method — how will this actually be tested",
            "Test instance count — testing once is not the same as testing ten times",
            "Sign-off owner per criterion",
        ],
        "common_omissions": [
            "Verified By field",
            "Verification method description",
            "Test instance count",
        ],
    },
    "Solution Prototyping & Wireframing": {
        "required_sections": [
            "Prototype objectives — what decisions it enables",
            "Scope of the prototype (which features/screens)",
            "Fidelity level (paper, lo-fi digital, interactive)",
            "Validation approach — who reviews and how",
            "Feedback capture and iteration plan",
        ],
        "must_gather_before_draft": [
            "What decisions the prototype must enable stakeholders to make",
            "Which parts of the solution need visual validation",
            "Who will review the prototype and in what format",
            "How feedback will be captured and incorporated",
        ],
        "artifact_format": (
            "Prototyping plan: Objectives, Scope, Fidelity Decision with rationale, "
            "Validation Plan (who reviews, when, format), Feedback Capture Template, "
            "Iteration Schedule."
        ),
        "junior_misses": [
            "Connecting the prototype to specific decisions it must resolve",
            "Validation plan — who reviews and how is feedback structured",
            "Iteration plan after initial feedback",
        ],
        "common_omissions": [
            "Decision objectives for the prototype",
            "Structured validation plan",
            "Iteration plan post-feedback",
        ],
    },
    "Requirements Verification": {
        "required_sections": [
            "Verification criteria (complete, consistent, unambiguous, traceable)",
            "Requirements reviewed with verification result per criterion",
            "Defects found during verification with resolution",
            "Reviewer and date",
            "Sign-off confirming requirements are ready for stakeholder review",
        ],
        "must_gather_before_draft": [
            "Complete requirements set to verify",
            "Verification criteria to apply",
            "Defects or ambiguities found",
            "Who conducted the verification review",
        ],
        "artifact_format": (
            "Verification report: Verification Criteria table, Requirements Checklist "
            "(Req ID | Complete | Consistent | Unambiguous | Traceable | Issues), "
            "Defect Log, Verification Sign-off."
        ),
        "junior_misses": [
            "Traceability check — are all requirements traceable to objectives",
            "Ambiguity check — requirements that could be interpreted multiple ways",
            "Defect log for issues found during verification",
        ],
        "common_omissions": [
            "Traceability verification",
            "Ambiguity identification",
            "Defect log",
        ],
    },
    "Requirements Validation": {
        "required_sections": [
            "Validation method (workshop, walkthrough, prototype review)",
            "Stakeholders involved in validation with their scope",
            "Validation results — confirmed, amended, or rejected requirements",
            "Outstanding issues requiring resolution",
            "Validated requirements baseline with sign-off",
        ],
        "must_gather_before_draft": [
            "Validation approach and which stakeholders are involved",
            "Which requirements were confirmed, which were amended",
            "Any requirements rejected during validation and why",
            "Outstanding issues not yet resolved",
        ],
        "artifact_format": (
            "Validation report: Method description, Stakeholder Scope table, "
            "Validation Results table (Req ID | Status | Comments | Resolution), "
            "Outstanding Issues log, Validated Baseline sign-off."
        ),
        "junior_misses": [
            "Distinguishing validation (are these the right requirements?) from verification (are requirements written correctly?)",
            "Rejected requirements with rationale — not all requirements survive validation",
            "Outstanding issues that need post-validation resolution",
        ],
        "common_omissions": [
            "Rejected requirements with rationale",
            "Outstanding post-validation issues",
            "Validation vs verification distinction",
        ],
    },
    # ── Solution Evaluation ────────────────────────────────────────────────────
    "Solution Performance Assessment": {
        "required_sections": [
            "Performance metrics assessed against original success criteria",
            "Actual vs target comparison per metric",
            "Data collection method per metric",
            "Overall performance rating",
            "Recommendations for improvement",
        ],
        "must_gather_before_draft": [
            "The success criteria defined during requirements (from Acceptance Criteria and KPIs)",
            "Actual performance data collected post-deployment",
            "How performance data was collected",
            "Gaps between actual and target performance",
        ],
        "artifact_format": (
            "Performance assessment report: Success Criteria reference, Performance Results table "
            "(Metric | Target | Actual | RAG Status | Comments), Data Collection Methods section, "
            "Overall Assessment, Recommendations."
        ),
        "junior_misses": [
            "Comparing against the original success criteria — not self-reporting",
            "Data collection methodology — how was performance measured",
            "Recommendations for addressing performance gaps",
        ],
        "common_omissions": [
            "Reference to original success criteria",
            "Data collection methodology",
            "Improvement recommendations",
        ],
    },
    "Solution Limitation Identification": {
        "required_sections": [
            "Limitations — what the solution cannot do vs original requirements",
            "Impact of each limitation on stakeholders",
            "Workarounds currently in use for each limitation",
            "Remediation options (fix, defer, accept)",
            "Decision and rationale per limitation",
        ],
        "must_gather_before_draft": [
            "What the delivered solution cannot do that was originally required",
            "Which stakeholders are affected by each limitation",
            "Workarounds currently being used",
            "Whether each limitation should be fixed, deferred, or accepted",
        ],
        "artifact_format": (
            "Limitations register: Limitation ID | Description | Affected Requirement | "
            "Stakeholder Impact | Current Workaround | Remediation Option | Decision | Owner."
        ),
        "junior_misses": [
            "Workarounds — people are already coping, document how",
            "Decision and owner per limitation — deferral needs an owner and timeline",
            "Stakeholder impact per limitation, not just a generic description",
        ],
        "common_omissions": [
            "Current workarounds",
            "Decision and ownership per limitation",
            "Per-stakeholder impact",
        ],
    },
    "Enterprise Limitation Identification": {
        "required_sections": [
            "Organisational constraints limiting solution value delivery",
            "Root cause of each enterprise limitation (culture, capability, structure, technology)",
            "Impact on benefit realisation",
            "Recommendations for addressing enterprise limitations",
            "Owner and timeline for each recommendation",
        ],
        "must_gather_before_draft": [
            "Organisational factors preventing the solution from delivering full value",
            "Root cause categories for each limitation",
            "Impact on benefit realisation quantified where possible",
            "Recommendations and who owns them",
        ],
        "artifact_format": (
            "Enterprise limitation report: Limitation | Root Cause Category | "
            "Impact on Value Delivery | Recommendation | Owner | Timeline."
        ),
        "junior_misses": [
            "Root cause analysis per limitation — not just listing them",
            "Quantifying impact on benefit realisation",
            "Recommendations with named owners",
        ],
        "common_omissions": [
            "Root cause per limitation",
            "Quantified benefit impact",
            "Named recommendation owners",
        ],
    },
    "Value Delivery Assessment": {
        "required_sections": [
            "Business need statement from original engagement",
            "Evidence that the need has been met (or not)",
            "Benefit realisation data vs business case projections",
            "Remaining gaps to full value delivery",
            "Recommendations for maximising value going forward",
        ],
        "must_gather_before_draft": [
            "Original business need and business case targets",
            "Evidence of benefits realised post-implementation",
            "Gaps between projected and actual benefits",
            "Factors preventing full value delivery",
        ],
        "artifact_format": (
            "Value delivery report: Business Need recap, Benefits Realisation table "
            "(Benefit | Projected | Actual | Variance | Evidence), Value Gap Analysis, "
            "Recommendations."
        ),
        "junior_misses": [
            "Evidence for benefit claims — not self-reported assertion",
            "Variance analysis between projected and actual benefits",
            "Factors outside the solution that affected value delivery",
        ],
        "common_omissions": [
            "Evidence for benefit claims",
            "Projected vs actual variance analysis",
            "External factors affecting value delivery",
        ],
    },
    "UAT Planning & Support": {
        "required_sections": [
            "UAT objectives and scope",
            "Test scenarios derived from acceptance criteria",
            "UAT participants with roles (testers, observers, sign-off authorities)",
            "UAT schedule and entry/exit criteria",
            "Defect management process during UAT",
            "Sign-off process",
        ],
        "must_gather_before_draft": [
            "Acceptance criteria from the requirements to derive test scenarios",
            "UAT participants and their roles",
            "Entry criteria (what must be true before UAT starts) and exit criteria (what must pass)",
            "How defects found during UAT will be managed",
        ],
        "artifact_format": (
            "UAT plan: Objectives, Scope, Entry/Exit Criteria, Participant table, "
            "Test Scenario register (Scenario ID | Linked AC | Steps | Expected Result | Actual | Pass/Fail), "
            "Defect Management Process, Sign-off Record."
        ),
        "junior_misses": [
            "Entry and exit criteria — UAT cannot start until the solution is ready",
            "Defect management during UAT — who logs, who fixes, who verifies",
            "Tracing test scenarios back to acceptance criteria",
        ],
        "common_omissions": [
            "Entry and exit criteria",
            "Defect management process",
            "Acceptance criteria traceability",
        ],
    },
    "Post-Implementation Review": {
        "required_sections": [
            "Review scope and participants",
            "What worked well",
            "What did not work and root cause",
            "BA process improvements for next engagement",
            "Stakeholder feedback summary",
            "Action items with owners and timelines",
        ],
        "must_gather_before_draft": [
            "What went well across the engagement",
            "What did not work and why — root cause, not just description",
            "Specific improvements to BA process or approach for next time",
            "Stakeholder feedback on the engagement",
        ],
        "artifact_format": (
            "PIR document: Review Scope, What Worked Well section, Issues and Root Causes section, "
            "BA Process Improvement Recommendations, Stakeholder Feedback summary, "
            "Action Items table (Action | Owner | Due Date)."
        ),
        "junior_misses": [
            "Root cause for what did not work — not just the symptom",
            "Specific, actionable BA process improvements — not generic reflections",
            "Stakeholder feedback on the BA engagement, not just the solution",
        ],
        "common_omissions": [
            "Root cause for issues",
            "Specific BA process improvement actions",
            "Stakeholder feedback on the BA process",
        ],
    },
    # ── Cross-Cutting ──────────────────────────────────────────────────────────
    "Stakeholder Register": {
        "required_sections": [
            "All stakeholder groups — direct, indirect, and peripheral",
            "Influence level per group",
            "Interest level per group",
            "Specific responsibilities in this engagement",
            "Planned engagement approach per group",
        ],
        "must_gather_before_draft": [
            "Complete stakeholder landscape including indirect stakeholders (affected but not directly involved)",
            "Peripheral stakeholders with low interest but compliance implications",
            "IT/CIO leadership level representation",
            "Engagement approach differentiated by influence and interest quadrant",
        ],
        "artifact_format": (
            "Stakeholder Register table: Group | Name/Role | Influence (H/M/L) | Interest (H/M/L) | "
            "Responsibilities in Engagement | Engagement Approach. "
            "Influence-Interest matrix narrative."
        ),
        "junior_misses": [
            "Indirect stakeholders — those affected by the outcome but not directly participating",
            "Peripheral stakeholders — low interest but potential compliance or veto implications",
            "CIO or IT leadership level — often omitted in business-focused engagements",
        ],
        "common_omissions": [
            "Indirect stakeholders",
            "Peripheral low-interest stakeholders with compliance implications",
            "CIO or IT leadership",
        ],
    },
    "RACI Matrix": {
        "required_sections": [
            "All tasks and decisions relevant to the engagement",
            "All stakeholders mapped across RACI categories",
            "No task without a single Accountable owner",
            "No task without at least one Responsible party",
            "Narrative section explaining key decisions and rationale for R/A assignments",
        ],
        "must_gather_before_draft": [
            "Complete task and decision list for the engagement",
            "All stakeholder roles",
            "Accountable owner for every task — only one A per row",
            "Consulted and Informed parties per task",
        ],
        "artifact_format": (
            "RACI table: Task/Decision | [Stakeholder columns] with R/A/C/I values. "
            "One Accountable maximum per row. "
            "Key Decisions Narrative section explaining Accountable assignments."
        ),
        "junior_misses": [
            "Multiple Accountable owners per row — only one A is valid",
            "Distinguishing Consulted (two-way) from Informed (one-way)",
            "Including decisions as well as tasks — decisions need RACI too",
        ],
        "common_omissions": [
            "Decision-level RACI rows",
            "Single-A enforcement",
            "Consulted vs Informed distinction",
        ],
    },
    "Glossary & Terminology Definition": {
        "required_sections": [
            "All domain-specific terms used in the engagement artifacts",
            "Agreed definition per term",
            "Source or owner of the definition",
            "Terms that differ in meaning between departments",
            "Acronyms with expansions",
        ],
        "must_gather_before_draft": [
            "Domain terms specific to this organisation or industry",
            "Terms that mean different things to different stakeholder groups",
            "Acronyms used in the engagement",
            "Who owns each definition — especially contested terms",
        ],
        "artifact_format": (
            "Glossary table: Term | Definition | Source/Owner | Department Variants (if any). "
            "Alphabetically ordered. Acronym expansion list at end."
        ),
        "junior_misses": [
            "Terms that mean different things to different departments — the biggest source of misalignment",
            "Who owns contested definitions — someone must be the authority",
            "Including acronyms with expansions",
        ],
        "common_omissions": [
            "Cross-department term variants",
            "Definition ownership for contested terms",
            "Acronym expansions",
        ],
    },
    "Meeting & Workshop Facilitation Log": {
        "required_sections": [
            "Date, type, and attendees per session",
            "Key decisions made per session",
            "Actions assigned — owner and due date per action",
            "Outstanding items carried forward",
            "Next steps and next meeting date",
        ],
        "must_gather_before_draft": [
            "All sessions to log — dates, types, attendees",
            "Key decisions from each session",
            "Actions assigned with clear owners and due dates",
            "Outstanding items not yet resolved",
        ],
        "artifact_format": (
            "Running log structured by session: Session Header (Date | Type | Attendees), "
            "Decisions section, Actions table (Action | Owner | Due | Status), "
            "Outstanding Items, Next Steps."
        ),
        "junior_misses": [
            "Action ownership — every action must have a named owner",
            "Outstanding items that carry forward to the next session",
            "Distinguishing decisions (made) from actions (to be done)",
        ],
        "common_omissions": [
            "Named action owners",
            "Outstanding items carry-forward",
            "Decisions vs actions distinction",
        ],
    },
    "Lessons Learned Documentation": {
        "required_sections": [
            "Lessons by category: BA process, stakeholder engagement, technology, data quality",
            "Root cause per lesson",
            "Recommendation for next engagement",
            "Applicable engagement types (where this lesson applies)",
            "Owner of each recommendation",
        ],
        "must_gather_before_draft": [
            "Key lessons from each phase of the engagement",
            "Root cause for each — why did this happen",
            "Specific recommendations for future engagements",
            "Which types of engagements this lesson applies to",
        ],
        "artifact_format": (
            "Lessons learned register: Lesson ID | Category | Description | Root Cause | "
            "Recommendation | Applicable Engagement Types | Owner."
        ),
        "junior_misses": [
            "Root cause per lesson — 'we should have done X' without explaining why X was not done",
            "Applicable engagement types — not all lessons apply universally",
            "Recommendation ownership — who is responsible for applying the lesson next time",
        ],
        "common_omissions": [
            "Root cause per lesson",
            "Applicable engagement type scope",
            "Recommendation ownership",
        ],
    },
}


def _module_context_block(module_name: str) -> str:
    """Format the MODULE_CONTEXT entry for a given module into a prompt section."""
    ctx = MODULE_CONTEXT.get(module_name)
    if not ctx:
        return ""
    lines = [f"MODULE BACKGROUND CONTEXT FOR {module_name}:"]
    if ctx.get("required_sections"):
        lines.append("\nRequired content areas for a complete artifact:")
        for s in ctx["required_sections"]:
            lines.append(f"- {s}")
    if ctx.get("must_gather_before_draft"):
        lines.append("\nInformation that must be gathered before drafting:")
        for s in ctx["must_gather_before_draft"]:
            lines.append(f"- {s}")
    if ctx.get("artifact_format"):
        lines.append(f"\nArtifact format: {ctx['artifact_format']}")
    if ctx.get("junior_misses"):
        lines.append("\nWhat a junior BA typically misses (proactively surface these):")
        for s in ctx["junior_misses"]:
            lines.append(f"- {s}")
    if ctx.get("common_omissions"):
        lines.append("\nCommon omissions to proactively address:")
        for s in ctx["common_omissions"]:
            lines.append(f"- {s}")
    if ctx.get("opening_approach"):
        lines.append(f"\nOpening approach for this module:\n{ctx['opening_approach']}")
    return "\n".join(lines)


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
    module_name = module.get('name', '')
    _ctx_block = _module_context_block(module_name)
    module_context_section = f"\n\n{_ctx_block}\n" if _ctx_block else ""
    return (
        SYSTEM_COPILOT_BASE
        + f"""

PROJECT CONTEXT:
- Project name: {project.get('name', 'Unknown')}
- Engagement type: {project.get('engagement_type', 'Not classified')}
- Scale tier: {project.get('scale_tier', 'Not classified')}

CAPTURED DIMENSIONS:
{_dimensions_block(dimensions)}
{module_context_section}
PRIOR WORK COMPLETED ON THIS PROJECT — use this context to inform your questions and avoid repeating what has already been established:
{_prior_artifacts_block(prior_artifacts, module.get('knowledge_area', ''))}
{artifact_section}
CURRENT MODULE:
- Name: {module_name}
- BABOK Knowledge Area: {module.get('knowledge_area')}
- Description: {module.get('description', '')}
- Typical inputs: {module.get('typical_inputs') or 'Use project context and prior artifacts.'}
- Typical outputs: {module.get('typical_outputs') or 'See module description.'}

Your job right now is to guide the user through completing the "{module_name}" module.
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
