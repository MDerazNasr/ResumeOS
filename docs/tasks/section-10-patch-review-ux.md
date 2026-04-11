# Section 10: Patch Review UX

## Goal

Make AI edits feel like reviewing code changes instead of reading generic suggestion cards.

## Scope

- stronger red/green diff rendering
- approve all and reject all actions
- next/previous hunk navigation
- clearer per-hunk review state
- keep the existing validated patch-set backend contract

## Out of Scope

- new model providers
- new suggestion-generation modes
- full conversational chat
- PDF-aware review logic

## Implementation Checklist

- [x] document the Section 10 review-UX boundary
- [x] upgrade the patch review panel to a stronger diff-centric presentation
- [x] add batch actions for approve all and reject all
- [x] add next/previous hunk navigation
- [x] verify backend tests pass
- [x] verify frontend production build passes

## Verification Checklist

- [x] backend tests pass
- [x] frontend production build passes
- [x] additions and removals are more visually distinct
- [x] users can move through hunks intentionally
- [x] users can approve or reject all visible hunks from the current patch sets
