# Section 12: Holistic Review

## Goal

Build the first real PDF plus LaTeX review boundary for AI-assisted resume critique.

## Scope

- backend holistic-review context endpoint
- latest compile artifact metadata
- source-level structure summary
- visible workspace panel for that context
- compile-triggered refresh of the context

## Out of Scope

- direct PDF parsing
- vision-model review
- PDF-aware patch generation
- user rule enforcement

## Implementation Checklist

- [x] define the Section 12 architecture boundary
- [x] add a holistic-review context DTO
- [x] add a backend route for latest holistic-review context
- [x] include latest compile artifact state in that context
- [x] surface the context in the editor workspace
- [x] refresh the context after compile
- [x] use the context inside model-backed review generation
- [x] add a dedicated holistic-review action in the workspace
- [x] incorporate first rendered-PDF review signals

## Verification Checklist

- [ ] backend tests pass
- [ ] frontend production build passes
- [ ] holistic-review context route works before compile
- [ ] holistic-review context route reports the latest PDF after compile
- [ ] workspace panel renders current holistic-review context
- [ ] holistic-review action returns validated patch sets through the existing review workflow
- [ ] holistic-review context exposes first rendered-review signals from the compiled artifact
