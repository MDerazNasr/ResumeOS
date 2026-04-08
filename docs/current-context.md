# ResumeOS Current Context

## Current Milestone

Active milestone:

- Section 4: protected document model

## Completed Milestones

- project architecture and production planning documented
- Section 1: resume document core scaffolded and verified
- Section 2A: compile contract and editor workspace scaffolded and verified
- Section 2B: real TeX compile execution and PDF preview implemented and verified
- Section 2C: Monaco integration and compile test hardening implemented and verified

## Current Constraints

- AI features remain deferred until the editor and compile foundation is solid
- local dev persistence is SQLite for now
- browser port binding is restricted in the current sandbox, so frontend verification relies on production builds
- compile behavior should preserve the existing API contract introduced in Section 2A

## Current Backend Reality

- backend stack: FastAPI
- active compile route: `POST /resumes/{resume_id}/compile`
- compile runs are persisted in `compile_runs`
- current compile implementation uses real `latexmk` execution and stores generated PDF artifacts locally

## Current Frontend Reality

- editor page is a two-pane workspace
- left pane: Monaco-based LaTeX editor
- right pane: compile status, real PDF preview, snapshots, document model summary, and suggestion review
- the workspace now also includes a first tailoring input for job descriptions
- tailoring now creates a pre-tailor snapshot before suggestions are generated
- dirty-state tracking now follows the last saved draft

## Immediate Next Goal

Build the next protected-document slice on top of the new extraction, validation, and first generated suggestion flows.

That likely means:

- tighten editable-block coverage for common resume constructs
- prepare a cleaner patch schema around block IDs and source ranges
- expand from the first real block-level edit, review, and tailoring generation paths into richer suggestion generation modes

## Definition of Success for the Current Slice

- protected regions are extracted from the current working draft
- editable blocks are extracted from the current working draft
- exact block-targeted patch validation is enforced server-side
- the editor shows the model in a visible way
- mocked patch proposals exercise the same validation gate before any AI integration
- mocked patch proposals can be applied directly into the working draft
- mocked patch proposals are grouped into suggestion sets with retry behavior
- suggestion review now reads like a diff workflow instead of a mock card list
- selected editable blocks can now request generated edit suggestions through a provider abstraction
- block-level generated edits are now user-directed instead of using one fixed prompt
- the workspace can now request multi-block review suggestions through the same review/apply flow
- the workspace can now request first-pass tailoring suggestions from a pasted job description through the same review/apply flow
- the snapshot panel now refreshes after tailoring so the pre-tailor snapshot is visible immediately
- tailoring suggestions are now grouped around coarse job-description themes instead of only per-block buckets
- suggestion sets now carry explicit mode metadata and regenerate according to their originating flow
- document-model backend tests pass
- frontend production build passes

## Known Risks

- local TeX tooling may differ from the intended production container
- compile subprocesses need timeouts and temp-directory isolation
- PDF serving needs a clean local artifact strategy before later migration to object storage
- the current document-model parser is heuristic and intentionally conservative
