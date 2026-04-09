# ResumeOS Implementation Log

## Working Convention

This project should be developed in small, verifiable slices.

For each slice:

1. define scope and acceptance criteria
2. implement the smallest concrete version
3. verify the slice
4. update documentation
5. create a structured commit before moving on

Commit messages should stay section-oriented and descriptive.

Examples:

- `docs: add product architecture and implementation log`
- `feat(section-1): scaffold web and api apps`
- `feat(section-1): add resume and working draft persistence`
- `fix(section-1): update backend dependencies for python 3.14`

## Completed Work

### 2026-04-08: Section 5 Planning

Opened the Section 5 branch from merged `main` after Section 4 was pushed and integrated.

Planned scope:

- formalize one first-class patch-set contract
- adapt edit, review, and tailor flows to emit that contract
- keep validation, apply, retry, and feedback behavior intact

Primary planning files:

- [section-5-patch-set-workflow.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/section-5-patch-set-workflow.md)
- [section-5.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/tasks/section-5.md)

### 2026-04-08: Section 5 First Patch-Set Contract Slice

Started the Section 5 migration by introducing a first-class patch-set contract without rewriting the whole subsystem at once.

Added:

- backend `PatchHunk`, `PatchSet`, and `PatchSetList` DTOs
- backend `edit` route migration onto the new patch-set response model
- frontend review-surface vocabulary shift from “suggestions” to “patch sets”
- frontend state and handler updates so the live editor now works in terms of patch sets

Verified:

- backend test suite passes after the first contract migration
- frontend production build passes after the review-surface rename

### 2026-04-09: Section 5 Patch-Set Contract Migration

Completed the contract migration so the live AI-assisted flows now speak one explicit backend shape.

Added:

- backend `review` and `tailor` route migration onto the shared patch-set response model
- frontend client updates so mock, edit, review, and tailor retrieval now all work against the shared patch-set structure

Verified:

- backend test suite passes after migrating all live generation flows to the patch-set contract
- frontend production build passes with the unified contract in place

### 2026-03-29: Initial Project Docs

Added the first project-level documentation:

- product definition
- system architecture
- document safety model
- patch-first AI editing model
- phased production plan split into concrete sections

Primary file:

- [product-architecture.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/product-architecture.md)

Planning updates should keep landing in the architecture doc as the product brief evolves.

Recent planning additions:

- light/dark mode is now tracked as a later UI preference and polish item
- standard/Vim editor mode is now tracked as part of the editor experience

### 2026-03-29: Section 1 Scaffold

Built the first real project slice for Resume Document Core.

Implemented:

- monorepo-style repo layout with `apps/web`, `apps/api`, and `packages/shared`
- FastAPI backend for local dev auth, resume creation, resume listing, draft loading, and draft saving
- SQLite schema for `users`, `resumes`, and `working_drafts`
- starter LaTeX resume template
- Next.js frontend for:
  - resume list
  - create resume flow
  - raw LaTeX draft editor
  - save draft flow

### 2026-03-29: Section 1 Verification

Verified the backend flow end to end using FastAPI's test client.

Verified behaviors:

- health endpoint responds
- local dev user is returned
- resume list starts empty
- resume creation succeeds
- starter draft is created automatically
- draft save increments version
- stale draft save returns `409`

Also verified:

- frontend production build passes with `next build`

Environment note:

- the original backend dependency pins did not work with the only installed interpreter on this machine, Python 3.14
- backend requirements were updated to versions that install and run correctly under Python 3.14

## Current State

The repo currently contains:

- documentation for product architecture and production plan
- a verified Section 1 backend slice
- a frontend that builds successfully

The next planned milestone is Section 2:

- Monaco editor
- compile endpoint
- LaTeX compile loop
- PDF preview

### 2026-03-29: Section 2 Planning

Section 2 was broken into two controlled sub-slices:

- Sub-slice A: compile contract and workspace
- Sub-slice B: real TeX compile and PDF preview

Primary planning file:

- [section-2-editor-compile.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/section-2-editor-compile.md)

### 2026-03-29: Section 2A Compile Contract and Workspace

Implemented the first concrete compile slice without pretending the real TeX backend was finished.

Added:

- `compile_runs` persistence in the backend schema
- compile request and response DTOs
- `POST /resumes/{resume_id}/compile`
- backend compile contract validation for:
  - missing `\documentclass`
  - missing `\begin{document}`
  - missing `\end{document}`
  - unbalanced braces
- editor workspace layout with:
  - source pane
  - compile panel
  - compile logs
  - preview placeholder for Section 2B

Also fixed:

- draft dirty-state tracking now compares against the last saved draft instead of the initially loaded draft

Verified:

- compile success path returns a `success` result
- invalid source returns an `error` result with logs
- stale compile versions return `409`
- frontend production build passes after the workspace changes

### 2026-03-29: Section 2B Real Compile and PDF Preview

Implemented the real compile loop against the locally installed TeX toolchain.

Added:

- real `latexmk` subprocess execution
- temp-directory compile workflow
- compile timeout boundary
- local PDF artifact persistence
- `GET /resumes/{resume_id}/compile/latest.pdf`
- preview pane wiring to the generated PDF

Verified:

- starter resume compiles successfully
- latest PDF route returns a real PDF artifact
- broken LaTeX returns real compile failure logs
- frontend production build still passes

Open follow-up:

- Monaco is still the main remaining editor upgrade before Section 2 is fully complete

### 2026-03-29: Section 2C Monaco and Compile Tests

Closed out the remaining editor and verification work for Section 2.

Added:

- Monaco-based LaTeX editor component
- backend compile tests checked into the repo
- README command for running backend tests

Verified:

- backend compile success test passes
- backend compile failure test passes
- backend compile conflict test passes
- frontend production build passes with Monaco integrated

Section 2 outcome:

- ResumeOS now has a real LaTeX editing workspace, real compile loop, real PDF preview, and checked-in compile regression tests

### 2026-03-29: Local Run Command Fix

Found a concrete local-dev issue during live reproduction:

- the forwarded host/port command shape I used with `npm run dev:web -- ...` was wrong for this workspace setup

Added:

- `npm run dev:web:local`

This gives a reliable frontend start path on `127.0.0.1:3000` without relying on broken npm argument forwarding.

### 2026-03-29: App Router Error Boundary Hardening

After live reproduction, added explicit Next.js app-router error boundaries:

- `app/error.tsx`
- `app/global-error.tsx`

Reason:

- the browser was showing a missing required error components refresh loop
- explicit error boundaries give the app router the required fallback surface and prevent that failure mode from degrading into a blank page

### 2026-03-29: PDF Preview Header Fix

Found a real preview issue during live usage:

- the compiled PDF route worked, but the browser treated the PDF as a download instead of rendering it inline

Fix:

- changed the PDF file response to use `Content-Disposition: inline`

Verified:

- PDF route now returns `application/pdf`
- content disposition is `inline`

### 2026-03-29: Section 3 Snapshot Foundation

Started the first versioning and recovery slice on the dedicated feature branch.

Added:

- `snapshots` table
- backend snapshot DTOs and routes
- snapshot create/list/restore service layer
- frontend snapshot panel in the editor workspace
- backend snapshot tests

Verified:

- snapshot creation works from the current draft
- snapshot listing returns saved snapshots
- restoring a snapshot updates the working draft correctly
- backend tests pass
- frontend production build passes

### 2026-03-29: Section 3 Autosave

Added autosave behavior on top of the snapshot foundation.

Behavior:

- the working draft saves automatically after a short idle delay while typing
- manual save remains available as a fallback
- snapshot creation waits for the latest persisted draft before saving the snapshot

Verified:

- backend tests still pass
- frontend production build passes

### 2026-04-08: Section 4 First Review Mode

Expanded the protected-document workflow from single-block edit generation into the first multi-block review path.

Added:

- backend review suggestion route for the current resume draft
- provider contract support for multi-block review rewrites
- validation of generated review suggestions through the same exact block gate as edit mode
- backend regression test coverage for review suggestion generation
- frontend `Review Resume` action that loads generated review suggestions into the existing diff-style review surface

Verified:

- backend test suite passes with the new review suggestion flow
- frontend production build passes after wiring review generation into the editor workspace

### 2026-04-08: Section 4 First Tailor Mode

Expanded the same safe suggestion pipeline into the first tailoring flow.

Added:

- backend tailoring suggestion route that accepts a pasted job description
- provider contract support for job-description-guided rewrites across a small set of editable blocks
- validation of tailoring suggestions through the same exact block gate as edit and review mode
- backend regression test coverage for tailoring suggestion generation
- frontend `Tailor Resume` input and action that loads tailoring suggestions into the existing diff-style review surface

Verified:

- backend test suite passes with the new tailoring suggestion flow
- frontend production build passes after wiring tailoring generation into the editor workspace

### 2026-04-08: Section 4 Tailoring Safety Snapshot

Added the first safety behavior for tailoring so users do not lose the base draft while generating JD-focused suggestions.

Added:

- backend automatic snapshot creation before tailoring suggestions are generated
- backend regression coverage that verifies the tailoring flow creates a pre-tailor snapshot
- frontend snapshot panel refresh after tailoring so the new safeguard is visible immediately

Verified:

- backend test suite passes with the automatic snapshot behavior
- frontend production build passes with the snapshot refresh wiring

### 2026-04-08: Section 4 Tailoring Theme Grouping

Improved tailoring output organization so the review surface feels closer to the real product and less like raw per-block scaffolding.

Added:

- backend grouping of tailoring suggestion sets around coarse job-description themes such as backend/API, systems/infrastructure, and ownership/collaboration
- backend regression coverage that verifies theme-based grouping appears when the job description supports it

Verified:

- backend test suite passes with the new tailoring grouping behavior
- frontend production build still passes with the unchanged review surface

### 2026-04-08: Section 4 Suggestion Lifecycle Refinement

Made the suggestion subsystem more explicit and mode-aware instead of treating every suggestion set like the same generic scaffold.

Added:

- explicit suggestion mode metadata across mock, edit, review, and tailor suggestion sets
- backend regression checks for the new mode contract
- frontend mode badges and mode-aware regenerate labels
- frontend empty-state messaging for zero-result and fully dismissed suggestion flows
- frontend regenerate behavior that now actually replays edit, review, and tailor requests instead of only rotating mock sets

Verified:

- backend test suite passes with the mode-aware suggestion contract
- frontend production build passes with the new review surface behavior

### 2026-04-08: Section 4 Feedback Event Logging

Closed the first loop on the suggestion subsystem by persisting user outcomes instead of leaving them only in transient UI state.

Added:

- backend `feedback_events` persistence for suggestion apply and dismiss outcomes
- backend feedback logging route scoped to the current resume
- backend regression test coverage for feedback-event creation
- frontend apply and dismiss logging with suggestion mode, set id, proposal id, and target block id

Verified:

- backend test suite passes with feedback-event logging enabled
- frontend production build passes with the feedback calls wired into the review surface

### 2026-04-08: Section 4 SQLite Connection Hardening

Cleaned up a backend reliability issue that was showing up as a wall of SQLite resource warnings during repeated test runs.

Added:

- explicit database connection closing in the shared SQLite helper so existing service call sites do not leak connections

Verified:

- backend test suite still passes after the helper change
- the prior SQLite resource warning flood no longer appears in the test run
- frontend production build still passes

### 2026-03-29: Section 3 Snapshot Safety Polish

Improved the safety and clarity of destructive snapshot actions.

Added:

- restore confirmation before replacing the working draft
- visible success feedback after snapshot creation
- visible success feedback after snapshot restore

Verified:

- backend tests still pass
- frontend production build passes

### 2026-03-30: Section 3 Minimal Snapshot Compare

Added a lightweight comparison view so snapshots are not just restorable, but inspectable.

Added:

- lazy snapshot detail API for fetching a snapshot's saved source only when requested
- minimal line-based snapshot compare view against the current working draft
- backend regression test for fetching snapshot detail

Why this shape:

- compare is intentionally lightweight for now
- snapshot list payloads stay small because source text is fetched on demand
- the goal was clarity and version history usefulness, not a full IDE diff product yet

Verified:

- backend tests still pass
- frontend production build passes

### 2026-03-30: Section 3 Snapshot Metadata Polish

Closed out the snapshot slice with a small UX cleanup instead of letting the panel accumulate avoidable friction.

Added:

- sensible default snapshot naming (`Snapshot N`)
- automatic reset to the next default name after creating a snapshot
- clearer panel metadata showing saved snapshot count
- a small `Latest` badge on the newest snapshot

Verified:

- backend tests still pass
- frontend production build passes

### 2026-03-30: Section 4 Protected Document Model Foundation

Started the next major feature area by making the resume structure explicit instead of treating the LaTeX source as an undifferentiated text blob.

Added:

- documented protected-vs-editable contract for the first heuristic document model
- backend document-model DTOs
- backend extraction service for protected regions and editable blocks
- `GET /resumes/{resume_id}/document-model`
- backend tests covering protected preamble/scaffold detection and editable summary/bullet extraction
- editor-side document model panel showing the extracted boundary

Why this shape:

- this is a concrete safety foundation for later AI patch validation
- the parser is intentionally conservative and biases ambiguous lines toward protected
- the feature is visible in the product instead of being invisible backend plumbing

Verified:

- backend tests still pass
- frontend production build passes

### 2026-03-30: Section 4 Exact Patch Validation Gate

Built the first real acceptance gate that future AI patch proposals will need to pass.

Added:

- documented v1 patch-validation contract
- backend patch-validation DTOs
- `POST /resumes/{resume_id}/patches/validate`
- strict server-side validation that only accepts edits targeting one current editable block exactly
- backend tests covering valid, stale, and unknown-target cases

Why this shape:

- it creates a trustworthy backend gate before any generated patches exist
- it keeps the first validator easy to reason about
- it forces later patch flows to anchor themselves to the extracted document model instead of raw freeform text edits

Verified:

- backend tests still pass
- frontend production build passes

### 2026-03-30: Preview Layout Restoration

After the Section 4 panels were added, the PDF preview was pushed too far down the right-hand column and stopped feeling like a first-class part of the editor workspace.

Fix:

- restored compile status, preview, and logs ahead of the newer document-model and snapshot panels in the right-hand layout

Verified:

- backend tests still pass
- frontend production build passes

### 2026-03-30: Section 4 Mocked Patch Flow

Added the first end-to-end patch review exercise without introducing a model yet.

Added:

- documented mocked patch proposal contract
- backend DTOs for mocked patch proposals
- `GET /resumes/{resume_id}/patches/mock`
- deterministic backend proposal generation from editable blocks
- backend self-validation of each mocked proposal through the exact patch gate
- backend tests for mocked proposal generation
- minimal frontend review cards for mocked before/after proposals

Why this shape:

- it proves the future AI patch path end to end
- it keeps proposal generation deterministic and easy to debug
- it exercises the real validation boundary instead of bypassing it

Verified:

- backend tests still pass
- frontend production build passes

### 2026-04-08: Section 4 Mock Patch Apply Mechanics

Turned the mocked patch cards from a static review surface into a real working-draft update path.

Added:

- documented first patch-apply contract
- backend patch-apply DTO and route
- strict backend apply logic that re-validates the target block before persisting
- backend tests for valid and stale patch apply cases
- frontend `Apply` and `Dismiss` controls on mocked patch cards

Why this shape:

- it proves that patch review can mutate the working draft safely
- it keeps the source of truth on the backend instead of attempting risky client-side text surgery
- it uses the same strict block-based validation gate as the mocked proposal flow

Verified:

- backend tests still pass
- frontend production build passes

### 2026-04-08: Section 4 Grouped Suggestion Sets

Moved the mocked review flow closer to the eventual AI UX by grouping related patches into coherent suggestion sets.

Added:

- documented grouped suggestion-set contract
- backend grouped suggestion-set DTOs
- grouped mocked suggestion generation instead of a flat patch list
- simple retry/regenerate behavior driven by a deterministic seed
- grouped review UI with set-level retry

Why this shape:

- the eventual AI UX should present coherent edit passes, not unrelated isolated cards
- retry behavior now exists at the set level, which maps better to future model-generated suggestion batches
- the flow is still deterministic and still uses the same strict validation boundary

Verified:

- backend tests still pass
- frontend production build passes

### 2026-04-08: Section 4 Diff-Centric Suggestion Review

Refined the grouped suggestion workflow so it reads more like the final product and less like scaffolding.

Added:

- clearer suggestion metadata such as operation and validation status
- renamed the review surface around suggestions rather than mock patches
- diff-centric hunk presentation with explicit removed and added lines
- preserved apply, dismiss, and regenerate behavior in the refined UI

Why this shape:

- the safety core was already in place, so the leverage here was making the workflow read like a real review system
- this brings the product closer to the eventual AI editing UX without introducing model variability yet

Verified:

- backend tests still pass
- frontend production build passes

### 2026-04-08: Section 4 First Generated Edit Suggestions

Added the first real generation path on top of the existing safety and review system.

Added:

- LLM provider abstraction for block-level edit generation
- default mock provider plus an OpenAI-backed provider path behind configuration
- backend edit suggestion endpoint for one selected editable block
- validation of generated candidates through the same patch gate used elsewhere
- per-block `Suggest Edit` action in the document model panel

Why this shape:

- it introduces real generation at the narrowest safe scope
- it reuses the same review/apply system instead of inventing a second path
- it keeps testing stable by defaulting to a deterministic provider when not configured otherwise

Verified:

- backend tests still pass
- frontend production build passes

### 2026-04-08: User-Directed Edit Prompts

Made the first generated edit flow user-directed instead of relying on one canned instruction.

Added:

- per-block prompt input in the document model panel
- `Suggest Edit` now uses the user-provided instruction for that block
- README guidance for switching from the default mock provider to the OpenAI-backed provider

Why this shape:

- it makes the block-level generation path materially more useful without changing the underlying safety model
- it keeps the UI control close to the specific editable block being targeted

Verified:

- backend tests still pass
- frontend production build passes

## Open Notes

- local dev persistence is SQLite for now
- PostgreSQL is still the intended longer-term primary database
- browser-level local dev serving could not be fully exercised in the sandbox because port binding was restricted
