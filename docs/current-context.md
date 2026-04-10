# ResumeOS Current Context

## Current Milestone

Active milestone:

- Section 8: UI preferences

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

Build on the new settings foundation with the first real app-level preference surface.

That means:

- extend backend settings with theme mode
- apply light/dark mode at the app shell level
- expose a settings-page theme toggle
- move the main resume workspace panels onto shared theme variables
- expose the theme switch directly in the authenticated app header
- move remaining high-traffic auth/list/error surfaces onto shared theme variables

## Definition of Success for the Current Slice

- a signed-in user can switch between light and dark mode
- the theme persists across reloads
- the app shell reflects the active theme consistently
- the main workspace panels reflect the active theme instead of staying visually hardcoded to dark mode
- the theme can be switched directly from the main app pages without opening settings
- major auth/list/error surfaces also reflect the active theme instead of defaulting back to dark styling
- backend tests pass
- frontend production build passes

## Known Risks

- local TeX tooling may differ from the intended production container
- compile subprocesses need timeouts and temp-directory isolation
- PDF serving needs a clean local artifact strategy before later migration to object storage
- the current document-model parser is heuristic and intentionally conservative
- auth changes touch every route through current-user resolution
- cookie/session handling must work cleanly across the local frontend/backend split
- the current UI is still largely hardcoded around the original dark shell, so theme support must centralize colors instead of patching isolated pages
- some lower-traffic surfaces still use inline colors, but the highest-traffic authenticated and auth-entry paths now share the theme variable system
