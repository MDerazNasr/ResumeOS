# ResumeOS Current Context

## Current Milestone

Active milestone:

- Section 6: style memory

## Completed Milestones

- project architecture and production planning documented
- Section 1: resume document core scaffolded and verified
- Section 2A: compile contract and editor workspace scaffolded and verified
- Section 2B: real TeX compile execution and PDF preview implemented and verified
- Section 2C: Monaco integration and compile test hardening implemented and verified
- Section 5: patch-set workflow completed and merged into `main`
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

Start Section 6 by adding a narrow style-memory layer on top of the now-stable patch-set workflow.

That means:

- define persisted style examples
- extract them from the current draft and accepted outcomes
- retrieve a bounded style context for generation requests
- thread that context into edit, review, and tailor flows

## Definition of Success for the Current Slice

- style examples are stored in a first-pass local persistence model
- edit, review, and tailor flows can retrieve a bounded style context
- provider inputs visibly include style-memory context
- patch sets now expose the retrieved style examples so the style-memory behavior is inspectable
- accepted patch outcomes now contribute to style memory and are preferred during retrieval
- patch validation and apply behavior remain unchanged
- backend tests pass
- frontend production build passes
- the first version remains deterministic and local, without vector or embedding infrastructure

## Known Risks

- local TeX tooling may differ from the intended production container
- compile subprocesses need timeouts and temp-directory isolation
- PDF serving needs a clean local artifact strategy before later migration to object storage
- the current document-model parser is heuristic and intentionally conservative
- simple style retrieval may need refinement before it feels strong enough for real users
