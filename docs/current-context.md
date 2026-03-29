# ResumeOS Current Context

## Current Milestone

Active milestone:

- Section 3: snapshots and recovery

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
- right pane: compile status, logs, and real PDF preview
- dirty-state tracking now follows the last saved draft

## Immediate Next Goal

Add autosave on top of the snapshot foundation so the working draft persists automatically and snapshot creation can use the latest saved state without a manual save step.

## Definition of Success for the Current Slice

- named snapshots can be created from the working draft
- the current working draft remains separate from snapshots
- a prior snapshot can be restored safely
- the snapshot flow is verified with backend tests
- the editor autosaves changes after a short idle delay

## Known Risks

- local TeX tooling may differ from the intended production container
- compile subprocesses need timeouts and temp-directory isolation
- PDF serving needs a clean local artifact strategy before later migration to object storage
