# ResumeOS Current Context

## Current Milestone

Active milestone:

- Section 13: constraint and rule system

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
- Section 9: hardening completed and merged into `main`
- Section 10: inline patch review UX completed on a feature branch
- Section 11: chat layer completed on a feature branch
- Section 12: holistic PDF + LaTeX review completed on a feature branch

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
- right pane: AI chat, compile status, real PDF preview, snapshots, document model summary, and suggestion review
- the review surface now speaks in terms of patch sets instead of generic suggestions
- the workspace now also includes a first tailoring input for job descriptions
- tailoring now creates a pre-tailor snapshot before suggestions are generated
- dirty-state tracking now follows the last saved draft

## Immediate Next Goal

Add durable resume rules that the AI must follow across generation modes.

That means:

- persist per-resume rules
- make those rules editable in the workspace
- thread them into edit, review, holistic review, and tailor generation
- surface rule influence inside patch review
- thread constraints into chat grounding and deterministic question handling
- preserve the existing patch-review safety model while expanding user control

## Definition of Success for the Current Slice

- backend tests pass
- frontend production build passes
- the backend exposes persistent resume constraints
- the workspace lets the user edit those constraints
- constraints are threaded into AI generation prompts
- edit generation reflects stored constraints
- patch sets expose applied constraints in the review UI
- chat can explain active rules from stored resume constraints

## Known Risks

- local TeX tooling may differ from the intended production container
- compile subprocesses need timeouts and temp-directory isolation
- PDF serving needs a clean local artifact strategy before later migration to object storage
- the current document-model parser is heuristic and intentionally conservative
- auth changes touch every route through current-user resolution
- cookie/session handling must work cleanly across the local frontend/backend split
- the local Next runtime still behaves less reliably than the production build in this environment, so the docs need to steer people toward the stable workflow explicitly

## Next Planned Branch

After persistent rules are in place, deepen rule-aware review quality.

That next slice should include:

- stronger PDF-aware enforcement for layout-sensitive constraints
- continued improvement of rendered-review quality
- better rule-aware chat and holistic-review explanations
