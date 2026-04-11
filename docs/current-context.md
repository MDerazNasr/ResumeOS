# ResumeOS Current Context

## Current Milestone

Active milestone:

- Section 9: hardening

## Completed Milestones

- project architecture and production planning documented
- Section 1: resume document core scaffolded and verified
- Section 2A: compile contract and editor workspace scaffolded and verified
- Section 2B: real TeX compile execution and PDF preview implemented and verified
- Section 2C: Monaco integration and compile test hardening implemented and verified
- Section 5: patch-set workflow completed and merged into `main`
- Section 6: style memory completed and merged into `main`
- Section 4: protected document model and safe suggestion workflow completed and merged into `main`
- editor enhancement: Vim mode completed and merged into `main`
- Section 7: auth and settings completed and merged into `main`
- Section 8: UI preferences completed and merged into `main`

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

Close out the current hardening branch and decide whether to merge it before the next major section.

That means:

- keep the stable local startup flow documented
- keep the Tailwind config warning gone
- keep a stable runtime verification path for auth and app-shell routes
- keep that runtime verification aligned with the current Google-backed auth flow

## Definition of Success for the Current Slice

- backend tests pass
- frontend production build passes
- the known Tailwind build warning is gone
- the local startup workflow in the README matches how the project is actually being run now
- the stable runtime verification script passes against the live API and frontend
- the runtime verification script reflects the current Google-backed auth behavior

## Known Risks

- local TeX tooling may differ from the intended production container
- compile subprocesses need timeouts and temp-directory isolation
- PDF serving needs a clean local artifact strategy before later migration to object storage
- the current document-model parser is heuristic and intentionally conservative
- auth changes touch every route through current-user resolution
- cookie/session handling must work cleanly across the local frontend/backend split
- the local Next runtime still behaves less reliably than the production build in this environment, so the docs need to steer people toward the stable workflow explicitly
