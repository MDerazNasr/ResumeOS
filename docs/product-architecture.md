# ResumeOS Product Architecture and Production Plan

## Product Definition

ResumeOS is a LaTeX resume editor with AI-assisted editing, review, and tailoring. It should behave more like an IDE than a chatbot. The AI does not directly rewrite the document. It proposes structured patches against editable content, and the user approves or rejects those changes before they are applied.

The product should optimize for:

- safe edits
- explicit user control
- preserved writing style
- reliable LaTeX compilation
- versioned editing history

## Core Product Principle

The most important invariant in the system is:

AI never directly edits the full document.

Instead, it:

1. reads the current resume and relevant context
2. generates structured patch proposals
3. passes those proposals through server-side validation
4. presents them to the user as diffs
5. applies only the user-approved hunks

This is the main difference between ResumeOS and a generic AI writing tool.

## System Architecture

ResumeOS should be split into the following major components.

### Frontend

The frontend should be a Next.js app responsible for:

- Monaco-based LaTeX editor
- PDF preview pane
- AI sidebar for Edit, Review, and Tailor modes
- diff review UI with accept/reject per hunk
- snapshot and version history UI
- auth session handling

### Backend

The backend should be a FastAPI service responsible for:

- auth/session APIs
- resume CRUD
- working draft persistence
- snapshot creation and restore
- AI orchestration
- patch validation
- compile job submission and result handling
- style-memory retrieval
- feedback logging

### Database

PostgreSQL should store:

- users
- resumes
- working drafts
- snapshots
- job applications
- AI suggestion sets
- AI suggestion hunks
- feedback events
- compile runs

### Object Storage

Cloudflare R2 should store:

- raw LaTeX artifacts
- compiled PDFs
- compile logs if needed

### Vector Store

Chroma should be used initially for style-memory retrieval. It should store embeddings for accepted bullets and other approved style examples from a given user.

### Compile Service

LaTeX compilation should run in an isolated TeX Live container. The compile path should be treated as an isolated service boundary even if it starts as a simple backend-invoked worker.

### LLM Provider Layer

The system should talk to a model through a provider abstraction so the rest of the product remains independent of the specific model vendor.

## Core Request Flow

The standard AI editing flow should work like this:

1. user opens a resume snapshot or working draft
2. frontend loads LaTeX source and editable/protected region metadata
3. user triggers Edit, Review, or Tailor
4. backend assembles context from:
   - current resume content
   - editable block metadata
   - protected document boundaries
   - optional job description
   - style-memory retrieval results
5. model returns structured patch proposals
6. backend validates the proposed patches
7. frontend renders patches as IDE-style diffs
8. user accepts or rejects hunks individually
9. accepted hunks are applied to the working draft
10. backend compiles the updated draft
11. PDF preview refreshes on success
12. feedback is logged for each hunk decision

## Document Safety Model

ResumeOS should rely on three layers of safety.

### 1. Protected Structural Regions

These regions should be read-only to the AI:

- preamble
- package imports
- macros
- document scaffolding
- layout definitions

### 2. Editable Content Regions

These regions should be AI-editable:

- summary text
- bullet items
- project descriptions
- experience descriptions
- other leaf-level resume content

### 3. Server-Side Patch Validation

All proposed patches must be validated server-side before the frontend can render or apply them.

Validation should check:

- touched ranges are allowed
- patch format is valid
- protected regions are untouched
- expected original text still matches the current draft

## Patch-First Editing Model

ResumeOS should not ask the model to return a rewritten file. It should return structured patch proposals.

Each patch or hunk should include fields such as:

- `operation_id`
- `target_block_id`
- `start_line`
- `end_line`
- `before_text`
- `after_text`
- `rationale`
- `mode`

The frontend should render these patches like a code review or IDE diff, showing removed and added lines clearly and allowing selective approval.

## Product Modes

All AI modes should use the same patch-based interaction model.

### Edit

Purpose:

- make targeted edits from explicit user instructions

Examples:

- strengthen this bullet
- make this more concise
- improve the technical specificity here

### Review

Purpose:

- critique the resume and propose concrete changes

Output should be structured and actionable, not generic writing advice.

### Tailor

Purpose:

- tailor the resume to a pasted job description

This mode should create a snapshot automatically before generating suggestions so the user can always return to the base version.

## Style Memory

Style memory should preserve user voice without requiring model fine-tuning.

Initial approach:

- embed accepted bullets and selected historical bullet examples
- retrieve top examples per request
- inject them into the prompt as style references

This should help preserve:

- bullet length
- phrasing patterns
- tone
- level of specificity

## Versioning Model

ResumeOS should separate:

- working draft
- named snapshots

The working draft is the live editable state. Snapshots are stable named versions that can be restored or compared later.

Recommended behavior:

- autosave working draft continuously
- allow manual snapshot creation
- create an automatic snapshot before tailoring

## Compile Subsystem

Compilation should be treated as a first-class product capability.

Requirements:

- compile from backend only
- run in isolated TeX container
- collect logs
- surface errors clearly
- preserve previous working state on compile failure

Compile should eventually be asynchronous, even if the earliest version starts with a simpler request-response pattern.

## Initial Data Model

The following core entities should exist early.

### `users`

- auth identity
- profile metadata

### `resumes`

- top-level resume record per user

### `working_drafts`

- current editable state for a resume

### `snapshots`

- named saved versions
- optional linkage to a job application

### `job_applications`

- company
- role
- job description
- linked tailored snapshot

### `ai_suggestion_sets`

- one record per AI request

### `ai_suggestion_hunks`

- individual patch proposals and decisions

### `feedback_events`

- accept
- reject
- retry
- manual edit after apply

### `compile_runs`

- source version
- status
- logs
- output PDF reference

## Engineering Rule: Avoid Slop

Every production section should:

- produce a concrete, usable artifact
- have a narrow scope
- end with clear acceptance criteria
- avoid speculative features

If a section does not produce a real user-visible capability or a necessary hard system boundary, it should be split further or deferred.

## Production Plan

The product should be built in small, concrete sections.

### Section 0: Project Foundation

Goal:

- establish the repo and app boundaries

Build:

- monorepo structure
- frontend scaffold
- backend scaffold
- shared types/package
- env handling
- linting and formatting
- base docs

Deliverable:

- web and api boot locally

Acceptance:

- web app runs
- api responds on `/health`
- shared types import correctly
- README explains local setup

### Section 1: Resume Document Core

Goal:

- make the resume a first-class product object

Build:

- user model
- resume model
- working draft model
- basic auth/session layer
- save and load raw `.tex`

Deliverable:

- user can create, open, and save a resume

Acceptance:

- resume content persists correctly
- user can reopen and recover exact source
- no AI required yet

### Section 2: Editor and Compile Loop

Goal:

- make ResumeOS a usable LaTeX editor

Build:

- Monaco editor
- compile endpoint
- TeX container execution
- compile logs
- PDF preview
- autosave working draft

Deliverable:

- user can edit, compile, and preview the resume

Acceptance:

- source edits appear in Monaco
- compile works end to end
- preview updates on success
- errors are visible on failure
- failed compile does not destroy the draft

### Section 3: Snapshots and Recovery

Goal:

- make resume editing safe

Build:

- named snapshots
- working draft separate from snapshots
- snapshot list
- restore flow
- compare flow

Deliverable:

- user can save versions and recover them safely

Acceptance:

- create snapshot
- restore snapshot
- compare versions
- keep working draft separate

### Section 4: Protected Document Model

Goal:

- enforce document safety before AI integration

Build:

- define protected regions
- define editable regions
- parse enough LaTeX structure to identify editable blocks
- patch-range validator

Deliverable:

- backend knows what AI is allowed to change

Acceptance:

- protected regions are detected consistently
- editable regions are addressable
- invalid patches are rejected server-side

### Section 5: Patch Engine

Goal:

- create the core IDE-style review system

Build:

- patch schema
- mocked patch payloads
- diff UI
- accept/reject per hunk
- apply flow

Deliverable:

- user can review and apply structured changes like in a code editor

Acceptance:

- removed and added lines render correctly
- hunks can be accepted individually
- accepted hunks update the draft
- rejected hunks do nothing

### Section 6: AI Edit Mode

Goal:

- connect a real model to the patch engine

Build:

- provider abstraction
- prompt builder for edit requests
- structured output handling
- validation and retry flow

Deliverable:

- user can request targeted edits and receive reviewable diffs

Acceptance:

- valid edit request yields patch hunks
- invalid model output is rejected safely
- no direct full-document rewrite path exists

### Section 7: Review Mode

Goal:

- generate useful critiques with optional concrete edits

Build:

- review prompting
- issue grouping
- optional patch proposals

Deliverable:

- user receives structured review feedback tied to resume content

Acceptance:

- critiques reference real content
- suggestions are actionable
- patch proposals integrate with the same review UI

### Section 8: Tailor Mode

Goal:

- tailor the resume to a job description without losing the base version

Build:

- JD input
- automatic pre-tailor snapshot
- gap extraction
- grouped patch suggestions

Deliverable:

- user pastes a JD and gets targeted resume changes

Acceptance:

- tailoring snapshot is created automatically
- suggestions map to job requirements
- user can approve selectively

### Section 9: Style Memory

Goal:

- preserve user style through retrieval

Build:

- style example extraction
- embeddings pipeline
- retrieval on AI requests

Deliverable:

- AI suggestions better match the user's prior writing style

Acceptance:

- style examples are retrieved per request
- results meaningfully shape generated suggestions

### Section 10: Feedback and Learning

Goal:

- capture user decisions as product intelligence

Build:

- accept/reject/retry/edit logs
- suggestion outcome tracking
- compile-success-after-apply tracking

Deliverable:

- the system records which AI changes helped

Acceptance:

- each hunk decision is logged
- suggestion outcomes are queryable later

### Section 11: Hardening

Goal:

- make the app robust enough for public usage

Build:

- auth hardening
- rate limiting
- job timeouts
- compile sandboxing
- error handling
- observability
- baseline tests

Deliverable:

- stable public-ready foundation

Acceptance:

- jobs cannot hang indefinitely
- malformed model output is handled safely
- critical flows are covered by basic tests

## Explicit Deferrals

The following should be deferred until the core product is strong:

- custom fine-tuning
- self-hosted inference
- GitHub bullet generation
- collaboration features
- analytics dashboards
- speculative advanced RAG features

## Immediate Next Implementation Scope

The first concrete implementation window should cover:

1. Section 0: Project Foundation
2. Section 1: Resume Document Core
3. Section 2: Editor and Compile Loop
4. Section 3: Snapshots and Recovery
5. Section 4: Protected Document Model

These sections create a real product base before any AI integration begins.

## Next Step After This Document

The next planning artifact should define the actual implementation blueprint for Sections 0 through 5:

- repo folder layout
- backend route map
- database schema
- shared contracts
- first milestone definition
