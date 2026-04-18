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
- [ ] use the context inside model-backed review generation
- [ ] incorporate rendered-PDF review signals

## Verification Checklist

- [ ] backend tests pass
- [ ] frontend production build passes
- [ ] holistic-review context route works before compile
- [ ] holistic-review context route reports the latest PDF after compile
- [ ] workspace panel renders current holistic-review context
