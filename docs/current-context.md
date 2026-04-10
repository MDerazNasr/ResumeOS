# ResumeOS Current Context

## Current Milestone

Active milestone:

- Section 7: auth and user settings

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

Replace the hardcoded dev-user foundation with real auth/session handling and persisted user settings.

That means:

- add real registration/login/logout
- resolve current user from a session cookie
- add persisted settings
- connect editor preferences to the backend settings model
- add a dedicated auth entry route and protect product routes from anonymous access
- remove the remaining dev-fallback identity from the live auth contract

## Definition of Success for the Current Slice

- a user can register and log in
- existing resume routes resolve the authenticated user correctly
- user settings can be stored and read
- editor mode can persist through backend settings
- backend tests pass
- frontend production build passes
- the editor now reads and writes its mode through `/settings`, with local storage only as a fallback cache
- unauthenticated access to resume/settings routes is now blocked, with the frontend redirecting to `/auth` before protected data loads
- `/me` now returns a real session user or `401`; the frontend treats that as authenticated vs unauthenticated state instead of manufacturing a fallback user

## Known Risks

- local TeX tooling may differ from the intended production container
- compile subprocesses need timeouts and temp-directory isolation
- PDF serving needs a clean local artifact strategy before later migration to object storage
- the current document-model parser is heuristic and intentionally conservative
- auth changes touch every route through current-user resolution
- cookie/session handling must work cleanly across the local frontend/backend split
- auth UX is still minimal and route-focused; there is not yet a dedicated full settings page or richer account management surface
