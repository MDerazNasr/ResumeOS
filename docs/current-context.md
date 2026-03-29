# ResumeOS Current Context

## Current Milestone

Active milestone:

- Section 2 wrap-up: Monaco integration and test hardening

## Completed Milestones

- project architecture and production planning documented
- Section 1: resume document core scaffolded and verified
- Section 2A: compile contract and editor workspace scaffolded and verified

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
- left pane: raw LaTeX source editor
- right pane: compile status, logs, and real PDF preview
- dirty-state tracking now follows the last saved draft

## Immediate Next Goal

Close out Section 2 by replacing the temporary textarea editor with Monaco and by adding checked-in verification around the now-working compile flow.

## Definition of Success for the Current Slice

- valid LaTeX compiles successfully
- resulting PDF is served to the frontend
- preview pane renders the latest PDF
- invalid LaTeX returns readable real compile logs
- compile failure does not corrupt the draft
- Monaco replaces the temporary textarea editor

## Known Risks

- local TeX tooling may differ from the intended production container
- compile subprocesses need timeouts and temp-directory isolation
- PDF serving needs a clean local artifact strategy before later migration to object storage
