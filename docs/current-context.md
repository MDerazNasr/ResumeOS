# ResumeOS Current Context

## Current Milestone

Active milestone:

- Section 5: patch-set workflow

## Completed Milestones

- project architecture and production planning documented
- Section 1: resume document core scaffolded and verified
- Section 2A: compile contract and editor workspace scaffolded and verified
- Section 2B: real TeX compile execution and PDF preview implemented and verified
- Section 2C: Monaco integration and compile test hardening implemented and verified
- Section 4: protected document model and safe suggestion workflow completed and merged into `main`

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
- the review surface now speaks in terms of patch sets instead of generic suggestions
- the workspace now also includes a first tailoring input for job descriptions
- tailoring now creates a pre-tailor snapshot before suggestions are generated
- dirty-state tracking now follows the last saved draft

## Immediate Next Goal

Start Section 5 by turning the current suggestion workflow into one first-class patch-set system.

That now means:

- finish the remaining route and service naming cleanup around seeded baseline patch sets
- keep validation, apply, retry, and feedback behavior intact under the patch-set naming
- close Section 5 cleanly once the workflow is coherent end to end

## Definition of Success for the Current Slice

- patch sets are represented through one shared contract
- edit, review, and tailor all emit the new patch-set structure explicitly
- patch application and feedback logging still work
- the old mock-suggestion type aliases have been removed from the shared contract surface
- the seeded baseline patch-set endpoint and client naming match the patch-set workflow language
- frontend review UI still renders grouped diff hunks correctly
- backend tests pass
- frontend production build passes

## Known Risks

- local TeX tooling may differ from the intended production container
- compile subprocesses need timeouts and temp-directory isolation
- PDF serving needs a clean local artifact strategy before later migration to object storage
- the current document-model parser is heuristic and intentionally conservative
