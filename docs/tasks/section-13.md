# Section 13: Constraint and Rule System

## Goal

Persist resume-level rules and apply them across AI generation flows.

## Scope

- backend persistence for resume constraints
- workspace panel for viewing and editing rules
- prompt wiring for edit, review, holistic review, and tailor
- minimal regression coverage

## Out of Scope

- advanced structured rule types
- automatic rule validation against rendered PDF
- per-rule accept/reject analytics

## Implementation Checklist

- [x] define the Section 13 boundary
- [x] add backend persistence for resume constraints
- [x] add get/update routes for constraints
- [x] thread constraints into AI generation prompts
- [x] add a workspace panel for editing constraints
- [x] expose rule influence more explicitly inside patch review

## Verification Checklist

- [x] backend tests pass
- [x] frontend production build passes
- [x] constraints can be created and read back
- [x] constraints apply to edit generation
- [x] constraints are visible in the editor workspace
- [x] patch sets show which constraints influenced generation
