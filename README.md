# BA Compass — Business Analysis Co-Pilot

**Portfolio Project F2 | Hadi Mercer | BA Portfolio 2026**

A Streamlit application that guides a business analyst through an end-to-end engagement workflow — from an AI intake conversation that classifies the work, through a BABOK-structured module roadmap, to a co-pilot that produces versioned artifacts via guided conversation with GPT-4o, a gap analysis engine that scores completeness, and a full Markdown export of the engagement package.

> BA Compass is built as a realistic fictional portfolio product. The engagement types, scale tiers, and roadmap template library reflect genuine BABOK v3 knowledge areas and are designed to demonstrate how AI can be embedded into an analyst's working method rather than replacing it.

---

## Live Demo

> **Deployment in progress** — the Streamlit Community Cloud deployment is configured and ready for the public URL to be linked here.

**Demo credentials:** Email `demo@bacompass.app` · Password `bacompass2026`

**Engagement types supported:**
- Process Improvement · New System / Technology Implementation · Data & Reporting
- Regulatory & Compliance · Organizational Change · New Product / Service Development
- Vendor Selection & Procurement · Strategic Initiative

**Scale tiers:** Request · Engagement · Initiative

---

## Screenshots

Screenshots will be added after the final smoke test and public deployment publish.

| Screen | Purpose |
|---|---|
| Dashboard | Project workspace — card grid with engagement type, scale tier, and status badges |
| Project Intake | AI classification conversation — describes engagement, confirms classification, generates roadmap |
| Roadmap | BABOK-grouped module grid with progress bar, status badges, and per-module entry |
| Module Co-Pilot | Chat interface with GPT-4o — guided conversation, draft generation, artifact save with versioning |
| Gap Analysis | AI completeness score + prioritised findings cards grouped by severity |
| Traceability Matrix | Module-by-module coverage view showing roadmap status and saved artifact version |
| Export | Individual artifact preview + download, or full engagement package as a single Markdown document |

---

## What This Project Demonstrates

| Capability | Evidence |
|---|---|
| End-to-end business analysis to working product | FRD, schema, roadmap template library, working Streamlit app |
| AI workflow design | Structured intake conversation with JSON-mode classification, co-pilot conversation with draft generation, gap analysis scoring — three distinct AI interaction patterns in one product |
| BABOK v3 methodology implementation | Roadmap templates aligned to knowledge areas, module descriptions sourced from BABOK practice standards |
| Engagement classification engine | 8 engagement types × 3 scale tiers = 24 addressable template combinations with 4 captured context dimensions |
| Artifact lifecycle management | Versioned artifact storage, conversation history persistence, draft edit-before-save workflow |
| Gap analysis and traceability | AI-scored completeness against project dimensions, traceability matrix linking modules to saved artifacts |
| Multi-page Streamlit architecture | Session-based auth, cross-page state via query params and session state, URL-bookmarkable project context |
| Deployment readiness | Streamlit Cloud secrets, per-request DB connections, Neon PostgreSQL, cold-start documented |

---

## The Business Problem

Business analysis work is inconsistently structured. A BA starting a new engagement faces the same set of questions every time — what kind of work is this, what does good look like for this type of engagement, which BABOK knowledge areas apply — and typically answers them from memory or by adapting a template that does not quite fit. The result is engagement packages that are technically complete but analytically uneven: strong in the analyst's preferred areas, thin in the ones they find harder.

The second problem is that AI tools are currently used for one-off generation — paste a prompt, get a document, move on. There is no structure for iterative elicitation, no version control for generated content, and no mechanism for the tool to assess what has been done and what is missing.

BA Compass addresses both problems by treating the engagement as a structured object. The intake conversation classifies the work into an engagement type and scale tier, then instantiates the appropriate BABOK-aligned roadmap. Each module in the roadmap is worked through a co-pilot conversation that elicits the right information before generating a draft. The artifact is saved with version history. At any point the analyst can run a gap analysis that reads all saved artifacts and tells them what is incomplete, inconsistent, or missing — before the engagement is handed over.

---

## BA Process

### Problem discovery

The starting point was not "build a chatbot for BAs." It was observing that the failure mode in most analyst engagements is not a lack of skill — it is a lack of structure applied consistently across different engagement types. A process improvement engagement needs different things from a system implementation. A small-scoped request needs different depth than a multi-phase initiative. The design question was: can a classification system combined with a template library make the right structure available at the right time, without requiring the analyst to make all those choices from scratch?

### Personas

Two personas shaped the requirements:

**The BA Practitioner** is working on multiple concurrent engagements at different stages. They need a workspace where each project has a defined state — classified, roadmapped, partially complete — rather than a folder of documents in various stages of draft. Their core frustration is spending time on structure instead of substance.

**The Portfolio Reviewer** is assessing the analyst's work at the end of the engagement. They need to see that the work was approached methodically — that the engagement type was identified correctly, that the right knowledge areas were addressed, that gaps were identified and not left unchecked. Their core frustration is BA output that is technically correct but impossible to assess for completeness.

### Scope decisions

The most significant scoping decision was the choice to use a template-based roadmap rather than a fully dynamic AI-generated one. The rationale: a template library grounded in BABOK v3 produces predictable, assessable roadmaps. A fully generated roadmap is harder to audit and introduces variability that would undermine the gap analysis step. The AI is used for elicitation and generation within modules, and for gap analysis across the package — not for determining what the roadmap should contain.

A second decision was to make the classification step conversational rather than a form. The intake prompt requires the AI to gather four context dimensions — engagement type, scale tier, trigger origin, and solution clarity — before committing to a classification. This is deliberate: forcing the analyst to describe the work in their own words before seeing a label produces better-classified engagements than a dropdown form.

Authentication is single-user per account. Role-based collaboration and team sharing were deferred. The analytical architecture supports it — every record carries a user ID — but the value of collaboration features depends on the core analytical workflow being correct first.

### Design decisions

The two-column layout on the Module Co-Pilot page was the most important UX decision. The conversation (left) and the artifact panel with project context (right) are kept visible simultaneously. This prevents the analyst from losing track of what has already been established mid-conversation — a common failure mode in long generative conversations.

Artifact versioning was built in from the start rather than treating save as overwrite. An analyst who generates a draft, edits it, and saves it needs to be able to see what changed. The traceability matrix shows the current version of each artifact; the underlying table retains the history.

---

## Technology Decision

BA Compass follows the established portfolio stack — Python, Streamlit, PostgreSQL, Plotly, psycopg2-binary — with one deviation worth noting.

**Neon instead of Supabase PostgreSQL:** this project uses Neon's serverless PostgreSQL rather than Supabase's free-tier instance. Neon's connection string is passed as a single `neon_db_url` secret, which simplifies the credential surface. The pooler behaviour on Streamlit Cloud is equivalent. Future projects will return to Supabase for consistency with the portfolio standard; this was an early implementation decision that predated the locked stack.

**OpenAI GPT-4o for the co-pilot and analysis layers:** three separate interaction patterns are used — a structured JSON-mode intake classifier, an open-ended elicitation conversation with conversation truncation, and a single-shot gap analysis call that reads the full artifact payload. Temperature is tuned per pattern: 0.2 for classification and gap analysis (precision), 0.3–0.4 for conversational responses and draft generation (creativity within structure).

**Custom session auth instead of Supabase Auth:** session tokens are managed in PostgreSQL rather than through the Supabase auth service, since Supabase Auth was not available with the Neon database. The auth pattern is bcrypt-hashed passwords with a `user_sessions` table. A production implementation would replace this with a managed auth provider.

---

## Architecture

```
User describes engagement (free text or pasted brief)
        |
        v
pages/project_intake.py
  - Structured AI conversation (prompts/intake_classification.py)
  - Extracts 4 dimensions: engagement_type, scale_tier, trigger_origin, solution_clarity
  - JSON-mode classification via GPT-4o (temperature 0.2)
  - Classification recommendation card with override option
        |
        v
components/db.py → generate_roadmap_from_template()
  - Lookup: roadmap_templates WHERE engagement_type + scale_tier
  - Instantiate: project_roadmap_items with sequence order
  - 8 engagement types × 3 scale tiers → up to 24 template combinations
        |
        v
pages/roadmap.py
  - BABOK knowledge area groupings
  - Module status grid (not_started / in_progress / complete / skipped)
  - Overall progress bar
  - Per-module entry → module_copilot
        |
        v
pages/module_copilot.py
  - Conversation load from DB (persisted across sessions)
  - GPT-4o elicitation conversation (temperature 0.4, max 12 turns)
  - "Generate Draft" → draft mode (temperature 0.3)
  - Edit-before-save draft area
  - Artifact saved with version increment
  - Roadmap item marked complete on save
        |
        v
pages/gap_analysis.py
  - Tab 1: AI gap analysis
      - Reads all saved artifacts + project dimensions
      - Single-shot GPT-4o analysis (temperature 0.2)
      - Completeness score /100 + findings grouped by severity
      - Finding types: missing / incomplete / inconsistent / recommended
  - Tab 2: Traceability matrix
      - Module × artifact coverage view
      - Orphaned artifact detection
        |
        v
pages/export.py
  - Tab 1: Individual artifact (.md preview + download)
  - Tab 2: Full package (cover page + TOC + all artifacts as one .md file)
        |
        v
PostgreSQL / Neon
  - users                     (auth and session management)
  - user_sessions             (session tokens)
  - projects                  (core project entity)
  - project_dimensions        (4 captured context dimensions per project)
  - modules                   (BABOK-aligned module library)
  - roadmap_templates         (engagement_type + scale_tier → module sequence)
  - project_roadmap_items     (live roadmap instances per project)
  - conversation_history      (persisted co-pilot turns per project + module)
  - artifacts                 (versioned artifact store per project + module)
        |
        v
Streamlit + OpenAI GPT-4o → Streamlit Community Cloud
```

---

## Repository Structure

```
BA-Compass/
├── app.py                          # Entry point — session check, route to login or dashboard
├── pages/
│   ├── login.py                    # Login page with session handling
│   ├── register.py                 # New account registration
│   ├── dashboard.py                # Project workspace — card grid, new project form
│   ├── project_intake.py           # AI classification conversation + roadmap generation
│   ├── roadmap.py                  # BABOK-grouped module grid with progress tracking
│   ├── module_copilot.py           # Co-pilot chat — elicitation, draft generation, artifact save
│   ├── gap_analysis.py             # AI gap analysis + traceability matrix
│   └── export.py                   # Individual artifact and full package export
├── components/
│   ├── ai.py                       # OpenAI client wrapper, truncation helper
│   ├── auth.py                     # Session auth — require_auth(), logout_user()
│   ├── db.py                       # DB connection, run_query(), roadmap template generator, artifact helpers
│   ├── export.py                   # Markdown formatters for individual artifacts and full packages
│   └── ui.py                       # inject_css(), render_page_header(), render_sidebar()
├── prompts/
│   ├── intake_classification.py    # Intake system prompt, engagement types, scale tiers, response parser
│   ├── copilot.py                  # Module co-pilot system prompt, draft system prompt, opening message
│   └── gap_analysis.py             # Gap analysis system prompt and response parser
├── .streamlit/
│   └── config.toml                 # Dark theme
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## Page Descriptions

**Dashboard**
The project workspace. Displays all projects belonging to the authenticated user as cards showing engagement type, scale tier, status badge, and last-updated timestamp. A collapsed "New Project" form creates a project shell and routes directly to intake. Empty state guides first-time users through the workflow. Each card has an "Open Roadmap" button for projects that have already been classified.

**Project Intake**
The entry point for classifying a new engagement. The analyst describes their work in free text — a brief, an email, or an informal explanation. GPT-4o conducts a focused conversation to establish four context dimensions before committing to a classification: engagement type, scale tier, trigger origin, and solution clarity. Once sufficient signal is gathered, a classification recommendation card is presented with an override option. Accepting the recommendation generates the project roadmap from the matching template and navigates to the roadmap page. Reclassification is available at any time.

**Roadmap**
The project home base after classification. Modules are displayed in a three-column grid grouped by BABOK knowledge area, each showing its current status badge (Not Started / In Progress / Complete / Skipped). Four metric tiles at the top show total, complete, in-progress, and remaining module counts. A progress bar shows overall completion percentage. Each module has an "Enter Module" button routing to the co-pilot, a one-click complete toggle, and a skip toggle for modules that do not apply.

**Module Co-Pilot**
The primary analytical workspace. The left column contains the conversation thread and input form. The right column shows the existing saved artifact (if any) and project context dimensions. When the conversation has sufficient depth, "Generate Draft" produces a complete artifact draft that appears in an editable text area below the conversation. The analyst can edit the draft before saving. Saving increments the artifact version and marks the roadmap item complete. The module guide expander shows the BABOK description, typical inputs, and typical outputs to orient the analyst at the start of each module.

**Gap Analysis**
Two-tab analysis surface available once artifacts have been saved. The Gap Analysis tab sends all saved artifacts and project dimensions to GPT-4o, which returns a completeness score out of 100 and a list of findings grouped by severity (high / medium / low) and type (missing / incomplete / inconsistent / recommended). Each finding includes a module reference, a plain-language description of the gap, and a concrete recommendation. The Traceability Matrix tab displays every module in the roadmap with its status and saved artifact version, grouped by knowledge area. Orphaned artifacts — saved for modules no longer in the roadmap — are flagged separately.

**Export**
Two-tab export surface. The "Export Individual Artifact" tab presents a selectbox of all saved artifacts, a formatted preview, and a Markdown download button named with the project name, module name, and version. The "Export Full Package" tab assembles all saved artifacts into a single Markdown document with a generated cover page, project metadata, captured dimensions, and a table of contents, downloadable as one file for handover or portfolio inclusion.

---

## Setup Instructions

### Prerequisites

- Python 3.9 or later
- A Neon (or Supabase) PostgreSQL database with the BA Compass schema applied
- An OpenAI API key
- Git

### 1. Clone the repository

```powershell
git clone https://github.com/hadimercer/BA-Compass.git
cd BA-Compass
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

For local development, create a `.streamlit/secrets.toml` file:

```toml
neon_db_url = "postgresql://user:password@host/dbname?sslmode=require"
OPENAI_API_KEY = "sk-..."
```

### 4. Apply the database schema

Open the SQL editor in your database provider and run `docs/artifacts/ba_compass_schema.sql` to create all tables.

### 5. Run locally

```powershell
streamlit run app.py
```

Expected behaviour on first launch: the registration page is accessible immediately. Create an account, log in, and create a project to begin the intake flow.

### 6. Deploy to Streamlit Community Cloud

1. Push the repository to GitHub. Confirm `.env` and `CLAUDE.md` are in `.gitignore`.
2. Connect the repository at [share.streamlit.io](https://share.streamlit.io). Point to `app.py` on branch `main`.
3. Add secrets under **Advanced settings → Secrets**:

```toml
neon_db_url = "postgresql://user:password@host/dbname?sslmode=require"
OPENAI_API_KEY = "sk-..."
```

4. Click **Deploy**. First load takes up to 30 seconds on the free tier while the container initialises.

---

## Portfolio Artifacts

| Artifact | File | Traces To |
|---|---|---|
| Functional Requirements Document | `docs/artifacts/BA_Compass_FRD_001.docx` | All FR IDs in coverage table below |
| Data Dictionary | `docs/artifacts/BA_Compass_Data_Dictionary.md` | All database tables |
| Architecture Diagram | `docs/artifacts/ba_compass_architecture.html` | System boundaries and data flow |
| UML / Sequence Diagram | `docs/artifacts/ba_compass_uml.html` | Intake → roadmap → co-pilot lifecycle |
| Live Application | Streamlit Community Cloud — URL TBA | All functional requirements |
| Source Code | [github.com/hadimercer/BA-Compass](https://github.com/hadimercer/BA-Compass) | All FR IDs |

---

## Functional Requirements Coverage

| FR ID | Area | Requirement Summary | Status |
|---|---|---|---|
| FR-01 | Auth | Email and password registration | ✅ Implemented |
| FR-02 | Auth | Login, session token, logout | ✅ Implemented |
| FR-03 | Auth | Protected route guard on all pages | ✅ Implemented |
| FR-04 | Projects | Create project shell with name and description | ✅ Implemented |
| FR-05 | Projects | Project card grid with engagement type, scale tier, status | ✅ Implemented |
| FR-06 | Intake | Structured AI intake conversation to classify engagement | ✅ Implemented |
| FR-07 | Intake | Extract four context dimensions before classifying | ✅ Implemented |
| FR-08 | Intake | Classification recommendation card with confidence explanation | ✅ Implemented |
| FR-09 | Intake | Override classification with manual selectbox | ✅ Implemented |
| FR-10 | Intake | Reclassification — reset and restart intake conversation | ✅ Implemented |
| FR-11 | Roadmap | Generate roadmap from engagement type + scale tier template | ✅ Implemented |
| FR-12 | Roadmap | Display modules grouped by BABOK knowledge area | ✅ Implemented |
| FR-13 | Roadmap | Module status tracking — not started / in progress / complete / skipped | ✅ Implemented |
| FR-14 | Roadmap | Overall progress bar and metric tiles | ✅ Implemented |
| FR-15 | Roadmap | One-click complete and skip toggles per module | ✅ Implemented |
| FR-16 | Co-Pilot | Persistent conversation history per project and module | ✅ Implemented |
| FR-17 | Co-Pilot | Module guide with BABOK description, inputs, and outputs | ✅ Implemented |
| FR-18 | Co-Pilot | Project context panel showing classification and prior artifacts | ✅ Implemented |
| FR-19 | Co-Pilot | Generate Draft button producing a complete artifact draft | ✅ Implemented |
| FR-20 | Co-Pilot | Edit-before-save draft area | ✅ Implemented |
| FR-21 | Co-Pilot | Versioned artifact save with roadmap item auto-complete | ✅ Implemented |
| FR-22 | Co-Pilot | Conversation truncation to manage token limits | ✅ Implemented |
| FR-23 | Gap Analysis | AI completeness score against project dimensions and artifacts | ✅ Implemented |
| FR-24 | Gap Analysis | Findings grouped by severity and gap type | ✅ Implemented |
| FR-25 | Gap Analysis | Re-run analysis on demand | ✅ Implemented |
| FR-26 | Traceability | Module-by-module coverage view with artifact version | ✅ Implemented |
| FR-27 | Traceability | Orphaned artifact detection | ✅ Implemented |
| FR-28 | Export | Individual artifact preview and Markdown download | ✅ Implemented |
| FR-29 | Export | Full engagement package as single Markdown document with cover page and TOC | ✅ Implemented |

---

## Continuous Improvement Roadmap

| Phase | Enhancement | Rationale |
|---|---|---|
| **Phase 1 — Polish** | Artifact diff view (v1 vs v2 side-by-side) | Analysts who iterate through multiple drafts need to see what changed without opening both files |
| **Phase 1 — Polish** | Module notes and annotations alongside the artifact | Not all relevant context ends up in the artifact text; a scratchpad per module captures the thinking |
| **Phase 1 — Polish** | PDF export of the full engagement package | Markdown is machine-readable; PDF is what gets sent to stakeholders and stored in project repositories |
| **Phase 2 — Intelligence** | Adaptive roadmap suggestions based on gap analysis results | If the gap analysis identifies a missing stakeholder register, the system should suggest adding that module |
| **Phase 2 — Intelligence** | Cross-engagement pattern detection | An analyst who has run 10 process improvement engagements can benefit from patterns identified across their prior work |
| **Phase 2 — Intelligence** | Structured artifact validation against BABOK quality criteria | Beyond completeness scoring, validate that specific fields are present and correctly formed per the standard |
| **Phase 3 — Scale** | Team workspaces with role-based access | The data model already carries user IDs; the remaining work is row-level filtering and an invite flow |
| **Phase 3 — Scale** | Engagement template editor | Allow practitioners to extend or modify the roadmap template library without code changes |
| **Phase 3 — Scale** | Integration with Confluence or SharePoint for artifact publish | Close the last handover step — publish directly from the export page to the team's documentation platform |

---

## Portfolio Context

BA Compass is **Flagship Project 2 (F2)** — the most technically complex project in the portfolio and the one that most directly demonstrates AI-assisted business analysis practice.

| # | Project | Label | Status | Connection |
|---|---|---|---|---|
| **F2** | **BA Compass — Business Analysis Co-Pilot** | Flagship 2 | **This project** | Demonstrates AI-assisted methodology across all other portfolio engagement types |
| F1 | Operational Process Intelligence Platform | Flagship 1 | Planned | — |
| S1 | Cadence — HR Process Automation Hub | Small 1 | ✅ Live | Process Improvement and New System engagement types modelled in BA Compass |
| S2 | TechNova — Compensation & Market Benchmarking Dashboard | Small 2 | ✅ Live | Data & Reporting engagement type modelled in BA Compass |
| S3 | Meridian — Portfolio Health Dashboard | Small 3 | ✅ Live | New Product / Service Development engagement type modelled in BA Compass |
| S4 | Lens — Sentiment & Text Analytics Tool | Small 4 | In development | — |

**Cross-portfolio note:** BA Compass is the only project in the portfolio that could have been used to plan and document all other projects. The engagement types and BABOK knowledge area modules were designed with the actual analytical work of S1, S2, and S3 in mind — the problems those projects solved are exactly the kinds of engagements a BA using this tool would classify and roadmap.

---

## Contact

**Hadi Mercer**
LinkedIn: [linkedin.com/in/hadimercer](https://linkedin.com/in/hadimercer)
GitHub: [github.com/hadimercer](https://github.com/hadimercer)
