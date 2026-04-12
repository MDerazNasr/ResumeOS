# Section 10: Patch Review UX

## Goal

Make AI edits feel like reviewing code changes instead of reading generic suggestion cards.

## Scope

- stronger red/green diff rendering
- approve all and reject all actions
- next/previous hunk navigation
- clearer per-hunk review state
- Monaco-inline hunk highlighting and review actions
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
- [x] make hunk progression clearer after approve/reject actions
- [x] surface generated patch sets and errors high enough in the workspace that users can actually see them
- [x] move the active review flow into Monaco with inline accept/reject controls
- [x] add inline previous/next and approve-all/reject-all actions
- [x] expose inline keyboard shortcuts in the editor review widget

## Verification Checklist

- [x] backend tests pass
- [x] frontend production build passes
- [x] additions and removals are more visually distinct
- [x] users can move through hunks intentionally
- [x] users can approve or reject all visible hunks from the current patch sets
- [x] the active hunk advances predictably after review actions
- [x] generated edits, review results, and tailoring failures are visible without hunting through the footer
- [x] users can review the active hunk directly inside Monaco instead of relying on the sidebar alone
