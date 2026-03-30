# Section 4 Task Checklist

## Scope

Introduce a protected document model so ResumeOS can distinguish between safe AI-editable content and protected LaTeX structure.

## Out of Scope

- real AI patch generation
- patch application UI
- full LaTeX AST parsing
- perfect support for every resume template shape

## Implementation Checklist

- [x] document the protected vs editable region contract
- [x] add backend DTOs for protected regions and editable blocks
- [x] add backend document-model extraction service from the current working draft
- [x] add a route to fetch the current document model for a resume
- [x] add backend tests for the first extraction heuristics
- [x] expose the extracted model in the editor workspace
- [x] document the first patch-validation contract
- [x] add backend patch-validation DTOs
- [x] add backend validation that only allows exact editable-block targets
- [x] add a route to validate a proposed patch target against the current draft
- [x] add backend tests for valid and invalid patch validation cases

## Verification Checklist

- [x] preamble and document scaffolding are marked protected
- [x] summary/body paragraphs are surfaced as editable blocks
- [x] bullet items are surfaced as editable blocks
- [x] backend document-model tests pass
- [x] frontend production build passes
- [x] a valid exact block-targeted edit is accepted
- [x] a stale or mismatched edit is rejected
- [x] an unknown block target is rejected

## Notes

- this is a heuristic v1, not a full parser
- the point of this slice is to establish enforceable safety boundaries before AI patch generation exists
- if a line is ambiguous, bias toward protected rather than editable
- the first validator should be intentionally strict; loosen it later only if there is a clear product need
