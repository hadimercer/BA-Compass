"""
All 55 BABOK-aligned modules for BA Compass.
Source: F2_Product_Definition_v1.0.docx, Section 7.
typical_inputs and typical_outputs are not defined in the source document — NULL in DB.
"""

MODULES = [
    # ─── Business Analysis Planning & Monitoring ───────────────────────────────
    {
        "name": "BA Approach Definition",
        "knowledge_area": "Business Analysis Planning & Monitoring",
        "description": (
            "Define how BA work will be conducted on this engagement — formality level, "
            "methodology (agile, waterfall, hybrid), tools, and governance expectations."
        ),
    },
    {
        "name": "Stakeholder Engagement Planning",
        "knowledge_area": "Business Analysis Planning & Monitoring",
        "description": (
            "Plan how and when each stakeholder will be engaged — communication preferences, "
            "frequency, channels, and escalation paths."
        ),
    },
    {
        "name": "BA Governance Setup",
        "knowledge_area": "Business Analysis Planning & Monitoring",
        "description": (
            "Define how decisions are made, how changes to requirements are controlled, "
            "and who holds approval authority."
        ),
    },
    {
        "name": "Information Management Planning",
        "knowledge_area": "Business Analysis Planning & Monitoring",
        "description": (
            "Define how artifacts are stored, versioned, shared, and retired "
            "across the engagement lifecycle."
        ),
    },
    {
        "name": "Performance Metrics Definition",
        "knowledge_area": "Business Analysis Planning & Monitoring",
        "description": (
            "Define how the quality and effectiveness of BA work will be measured "
            "on this specific engagement."
        ),
    },

    # ─── Elicitation & Collaboration ──────────────────────────────────────────
    {
        "name": "Elicitation Planning",
        "knowledge_area": "Elicitation & Collaboration",
        "description": (
            "Select the elicitation techniques most appropriate for this engagement type "
            "and stakeholder group before beginning information gathering."
        ),
    },
    {
        "name": "Stakeholder Interviews",
        "knowledge_area": "Elicitation & Collaboration",
        "description": (
            "Structured one-on-one or small-group sessions to extract stakeholder needs, "
            "pain points, expectations, and constraints."
        ),
    },
    {
        "name": "Workshops & Focus Groups",
        "knowledge_area": "Elicitation & Collaboration",
        "description": (
            "Facilitated group sessions designed to surface requirements, resolve conflicts, "
            "or build alignment across multiple stakeholders."
        ),
    },
    {
        "name": "Observation & Job Shadowing",
        "knowledge_area": "Elicitation & Collaboration",
        "description": (
            "Direct observation of current-state processes to capture undocumented workflows "
            "and real-world deviations from documented procedures."
        ),
    },
    {
        "name": "Survey & Questionnaire Design",
        "knowledge_area": "Elicitation & Collaboration",
        "description": (
            "Structured data collection instruments for gathering input from larger "
            "stakeholder groups efficiently."
        ),
    },
    {
        "name": "Document Analysis",
        "knowledge_area": "Elicitation & Collaboration",
        "description": (
            "Systematic review of existing documentation, reports, policies, and systems "
            "to extract requirements and understand current state."
        ),
    },
    {
        "name": "Benchmarking & Market Analysis",
        "knowledge_area": "Elicitation & Collaboration",
        "description": (
            "External reference points — industry standards, competitor approaches, "
            "regulatory benchmarks — to inform requirements and solution design."
        ),
    },
    {
        "name": "Brainstorming Facilitation",
        "knowledge_area": "Elicitation & Collaboration",
        "description": (
            "Structured ideation sessions with stakeholders to generate solution options, "
            "identify risks, or explore problem dimensions."
        ),
    },
    {
        "name": "Elicitation Results Documentation",
        "knowledge_area": "Elicitation & Collaboration",
        "description": (
            "Capture, organize, and summarize the raw outputs of elicitation activities "
            "before moving to analysis and requirements structuring."
        ),
    },

    # ─── Requirements Life Cycle Management ───────────────────────────────────
    {
        "name": "Requirements Traceability Setup",
        "knowledge_area": "Requirements Life Cycle Management",
        "description": (
            "Define the traceability framework — how requirements will be linked to business "
            "objectives, user stories, test cases, and delivered features."
        ),
    },
    {
        "name": "Requirements Prioritization",
        "knowledge_area": "Requirements Life Cycle Management",
        "description": (
            "Rank requirements by business value, urgency, dependency, and implementation "
            "feasibility using a structured prioritization method."
        ),
    },
    {
        "name": "Requirements Change Management",
        "knowledge_area": "Requirements Life Cycle Management",
        "description": (
            "Define and operate the process for handling changes to requirements after "
            "they have been baselined and approved."
        ),
    },
    {
        "name": "Requirements Baselining",
        "knowledge_area": "Requirements Life Cycle Management",
        "description": (
            "Formally lock a version of requirements as the agreed-upon foundation "
            "for design, development, and testing."
        ),
    },
    {
        "name": "Requirements Sign-off & Approval",
        "knowledge_area": "Requirements Life Cycle Management",
        "description": (
            "Facilitate formal stakeholder review and documented approval of requirements "
            "before handoff."
        ),
    },
    {
        "name": "Traceability Matrix",
        "knowledge_area": "Requirements Life Cycle Management",
        "description": (
            "Produce and maintain the live linkage document connecting requirements to "
            "user stories, test cases, and business objectives."
        ),
    },

    # ─── Strategy Analysis ─────────────────────────────────────────────────────
    {
        "name": "Current State Assessment",
        "knowledge_area": "Strategy Analysis",
        "description": (
            "Document and analyze the existing situation — processes, systems, data flows, "
            "pain points, and performance gaps."
        ),
    },
    {
        "name": "Problem Statement Definition",
        "knowledge_area": "Strategy Analysis",
        "description": (
            "Formally articulate the core problem being solved, grounded in evidence "
            "from elicitation and current state analysis."
        ),
    },
    {
        "name": "Root Cause Analysis",
        "knowledge_area": "Strategy Analysis",
        "description": (
            "Identify the underlying causes of the problem rather than surface symptoms, "
            "using structured techniques such as 5-Whys or fishbone diagrams."
        ),
    },
    {
        "name": "Business Need Definition",
        "knowledge_area": "Strategy Analysis",
        "description": (
            "Articulate what the business actually needs as an outcome — distinct from "
            "any specific solution or technology."
        ),
    },
    {
        "name": "Future State Design",
        "knowledge_area": "Strategy Analysis",
        "description": (
            "Define the desired end state after the solution is implemented — processes, "
            "systems, roles, and performance expectations."
        ),
    },
    {
        "name": "Gap Analysis",
        "knowledge_area": "Strategy Analysis",
        "description": (
            "Structured comparison of current state versus future state, identifying "
            "exactly what needs to change and what the change effort entails."
        ),
    },
    {
        "name": "Risk Assessment",
        "knowledge_area": "Strategy Analysis",
        "description": (
            "Identify, assess, and document risks to the solution, the engagement process, "
            "or the change program."
        ),
    },
    {
        "name": "Assumption & Constraint Documentation",
        "knowledge_area": "Strategy Analysis",
        "description": (
            "Capture what is being assumed as true and what boundaries or limitations exist "
            "that the solution must operate within."
        ),
    },
    {
        "name": "Business Case Development",
        "knowledge_area": "Strategy Analysis",
        "description": (
            "Articulate the full justification for the proposed solution — costs, benefits, "
            "risks, alternatives, and expected ROI."
        ),
    },
    {
        "name": "Change Strategy Definition",
        "knowledge_area": "Strategy Analysis",
        "description": (
            "Define the approach for transitioning the organization from current state to "
            "future state, including change management considerations."
        ),
    },

    # ─── Requirements Analysis & Design Definition ────────────────────────────
    {
        "name": "Stakeholder Requirements Documentation",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Document what each stakeholder group needs from the solution in their own terms, "
            "before translation into formal requirements."
        ),
    },
    {
        "name": "Business Requirements Documentation",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Document the high-level business objectives the solution must satisfy — "
            "the 'what' at the business level, not the system level."
        ),
    },
    {
        "name": "Functional Requirements Documentation",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Document in detail what the system, process, or solution must do — "
            "specific behaviors, functions, and capabilities required."
        ),
    },
    {
        "name": "Non-Functional Requirements Documentation",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Document performance, security, usability, scalability, and compliance "
            "requirements that constrain how the solution must operate."
        ),
    },
    {
        "name": "User Story Writing",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Express requirements in agile format — as user stories with acceptance criteria "
            "— suitable for iterative development teams."
        ),
    },
    {
        "name": "Process Modeling — Current State",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Create visual representations of how processes work today using standard "
            "notation (swimlane diagrams, BPMN, or equivalent)."
        ),
    },
    {
        "name": "Process Modeling — Future State",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Create visual representations of how processes will work after "
            "the solution is implemented."
        ),
    },
    {
        "name": "Use Case Development",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Document actor-system interaction scenarios for system-related engagements, "
            "covering both normal and exception flows."
        ),
    },
    {
        "name": "Data Requirements Definition",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Define what data the solution requires — sources, formats, transformations, "
            "storage, and governance requirements."
        ),
    },
    {
        "name": "Business Rules Documentation",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Document the logic, conditions, and constraints that govern how the solution "
            "must behave under various circumstances."
        ),
    },
    {
        "name": "Acceptance Criteria Definition",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Define the specific, testable conditions that must be met for each requirement "
            "to be considered successfully delivered."
        ),
    },
    {
        "name": "Solution Prototyping & Wireframing",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Produce low-fidelity representations of the solution for stakeholder validation "
            "before detailed design or development begins."
        ),
    },
    {
        "name": "Requirements Verification",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Internal quality check confirming that requirements are complete, consistent, "
            "unambiguous, and traceable before stakeholder review."
        ),
    },
    {
        "name": "Requirements Validation",
        "knowledge_area": "Requirements Analysis & Design Definition",
        "description": (
            "Stakeholder-facing confirmation that documented requirements accurately reflect "
            "actual business needs and intended outcomes."
        ),
    },

    # ─── Solution Evaluation ──────────────────────────────────────────────────
    {
        "name": "Solution Performance Assessment",
        "knowledge_area": "Solution Evaluation",
        "description": (
            "Measure whether the implemented solution meets the success criteria defined "
            "during requirements — post-deployment evaluation."
        ),
    },
    {
        "name": "Solution Limitation Identification",
        "knowledge_area": "Solution Evaluation",
        "description": (
            "Document what the delivered solution cannot do or where it falls short of "
            "the original requirements, for stakeholder awareness."
        ),
    },
    {
        "name": "Enterprise Limitation Identification",
        "knowledge_area": "Solution Evaluation",
        "description": (
            "Document organizational or environmental constraints that are limiting the "
            "solution's ability to deliver full expected value."
        ),
    },
    {
        "name": "Value Delivery Assessment",
        "knowledge_area": "Solution Evaluation",
        "description": (
            "Evaluate whether the business need has been met post-implementation — "
            "has the problem actually been solved?"
        ),
    },
    {
        "name": "UAT Planning & Support",
        "knowledge_area": "Solution Evaluation",
        "description": (
            "Define user acceptance test scenarios and support stakeholders through "
            "the formal acceptance testing process."
        ),
    },
    {
        "name": "Post-Implementation Review",
        "knowledge_area": "Solution Evaluation",
        "description": (
            "Conduct a structured retrospective on the engagement — what worked, "
            "what did not, what would be done differently next time."
        ),
    },

    # ─── Cross-Cutting ────────────────────────────────────────────────────────
    {
        "name": "Stakeholder Register",
        "knowledge_area": "Cross-Cutting",
        "description": (
            "Master reference document listing all stakeholders with their roles, "
            "influence level, interest level, and planned engagement approach."
        ),
    },
    {
        "name": "RACI Matrix",
        "knowledge_area": "Cross-Cutting",
        "description": (
            "Responsibility assignment matrix mapping tasks and decisions to stakeholders "
            "across the Responsible / Accountable / Consulted / Informed framework."
        ),
    },
    {
        "name": "Glossary & Terminology Definition",
        "knowledge_area": "Cross-Cutting",
        "description": (
            "Shared language document capturing key terms and their agreed definitions "
            "to prevent ambiguity across the engagement."
        ),
    },
    {
        "name": "Meeting & Workshop Facilitation Log",
        "knowledge_area": "Cross-Cutting",
        "description": (
            "Running record of key decisions made, actions assigned, and attendees present "
            "across all formal sessions."
        ),
    },
    {
        "name": "Lessons Learned Documentation",
        "knowledge_area": "Cross-Cutting",
        "description": (
            "Structured capture of insights, surprises, and recommendations from this "
            "engagement for the benefit of future BA work."
        ),
    },
]
