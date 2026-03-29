# Section 2 Blueprint: Editor and Compile Loop

## Goal

Section 2 turns ResumeOS into a usable LaTeX editing product.

The user should be able to:

1. open a resume
2. edit LaTeX in a proper editor workspace
3. trigger a compile from the backend
4. see either:
   - a successful compile result and preview artifact reference
   - readable compile errors

This section does not include AI.

## Scope

### In Scope

- editor workspace with source pane and result pane
- compile request and response contracts
- backend compile run tracking
- manual compile trigger
- compile status and logs in the UI
- preview panel structure

### Out of Scope

- AI chat
- patch engine
- diff review
- snapshots UI
- job tailoring
- style memory

## Delivery Strategy

Section 2 should be built in two sub-slices.

### Sub-slice A: Compile Contract and Workspace

Deliver:

- editor page upgraded into a workspace layout
- compile request/response schema
- compile run persistence
- backend compile endpoint with a safe placeholder implementation
- frontend compile panel that renders status and logs

Acceptance:

- user can click Compile
- backend records a compile run
- UI renders compile status and logs
- compile flow is wired end to end

### Sub-slice B: Real TeX Compile and PDF Preview

Deliver:

- actual LaTeX compilation from backend
- generated PDF artifact handling
- preview pane rendering
- success and failure handling against real TeX output

Acceptance:

- successful `.tex` source produces a previewable PDF
- bad source produces readable failure logs
- compile failure does not corrupt the draft

## Backend Changes

### New Table

`compile_runs`

- `id`
- `resume_id`
- `draft_version`
- `status`
- `log_text`
- `pdf_path`
- `created_at`

### New Routes

`POST /resumes/{resume_id}/compile`

Request:

```json
{
  "sourceTex": "\\documentclass{article}\n...",
  "draftVersion": 2
}
```

Success response shape:

```json
{
  "status": "success",
  "draftVersion": 2,
  "logs": [],
  "pdfUrl": null,
  "compiledAt": "2026-03-29T21:00:00Z"
}
```

Failure response shape:

```json
{
  "status": "error",
  "draftVersion": 2,
  "logs": [
    {
      "level": "error",
      "message": "Missing \\begin{document}",
      "line": null
    }
  ],
  "pdfUrl": null,
  "compiledAt": "2026-03-29T21:00:00Z"
}
```

## Frontend Changes

The editor page should become a two-pane workspace:

- left pane: source editor
- right pane: compile result panel

The result panel should show:

- compile button
- compile status
- logs
- preview placeholder until real PDF rendering lands

## Risks

The main risk in this section is getting stuck on TeX infrastructure too early.

The rule for Section 2 is:

- wire the compile loop first
- make the UI and backend contracts concrete
- plug in the real compiler after the loop exists

## Definition of Done for Sub-slice A

Sub-slice A is complete when:

- compile run schema exists
- compile endpoint exists
- editor page can trigger compile
- compile results render in the workspace
- compile runs persist in the backend

