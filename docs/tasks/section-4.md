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
- [x] document the mocked patch proposal contract
- [x] add backend DTOs for patch proposals and suggestion sets
- [x] add backend mocked patch proposal endpoint that validates its own proposals
- [x] add backend tests for mocked patch proposal generation
- [x] expose mocked patch proposals in a minimal review surface
- [x] document the first patch-apply contract
- [x] add backend patch-apply DTOs and route
- [x] add backend apply logic for exact validated block replacements
- [x] add backend tests for valid and invalid patch apply cases
- [x] add minimal apply and dismiss mechanics to the mocked patch review UI
- [x] document grouped suggestion-set contract
- [x] add backend DTOs for grouped suggestion sets
- [x] return grouped mocked suggestions instead of a flat patch list
- [x] add retry/regenerate behavior for mocked suggestion sets
- [x] update the review UI to operate on grouped suggestion sets
- [x] document the suggestion-schema refinement for the review UI
- [x] add clearer patch metadata for suggestion review
- [x] replace the mock review panel with a diff-centric suggestion review surface
- [x] keep apply/dismiss/retry behavior working in the new review surface
- [x] add LLM provider abstraction for block-level edit generation
- [x] add backend block-level edit suggestion endpoint
- [x] validate generated suggestions through the same patch gate
- [x] add backend tests for generated edit suggestions
- [x] expose a per-block "Suggest Edit" action in the editor UI
- [x] add backend multi-block review suggestion endpoint
- [x] generate review suggestions across a small set of editable blocks
- [x] validate review suggestions through the same patch gate
- [x] add backend tests for review suggestion generation
- [x] expose a "Review Resume" action that loads review suggestions into the same review surface
- [x] add backend first tailoring suggestion endpoint
- [x] generate tailoring suggestions across a small set of editable blocks using a job description input
- [x] validate tailoring suggestions through the same patch gate
- [x] add backend tests for tailoring suggestion generation
- [x] expose a "Tailor Resume" action that loads tailoring suggestions into the same review surface
- [x] auto-create a snapshot before tailoring suggestions are generated
- [x] refresh the snapshot panel after tailoring so the pre-tailor snapshot is visible immediately
- [x] group tailoring suggestion sets by coarse job-description themes instead of only by block
- [x] add explicit mode metadata to suggestion sets
- [x] make regenerate behavior mode-aware for edit, review, and tailor flows
- [x] improve empty-state messaging when a suggestion request returns nothing valid or everything is dismissed

## Verification Checklist

- [x] preamble and document scaffolding are marked protected
- [x] summary/body paragraphs are surfaced as editable blocks
- [x] bullet items are surfaced as editable blocks
- [x] backend document-model tests pass
- [x] frontend production build passes
- [x] a valid exact block-targeted edit is accepted
- [x] a stale or mismatched edit is rejected
- [x] an unknown block target is rejected
- [x] mocked proposals target only validated editable blocks
- [x] mocked proposals are visible in the editor UI
- [x] a valid mocked proposal can be applied into the working draft
- [x] an invalid or stale proposal is rejected by the backend
- [x] mocked suggestions are grouped into coherent sets
- [x] a suggestion set can be retried/regenerated
- [x] suggestion review feels diff-centric rather than card-centric
- [x] a selected editable block can request generated edit suggestions
- [x] generated edit suggestions appear in the same review/apply flow
- [x] multi-block review suggestions appear in the same review/apply flow
- [x] tailoring suggestions appear in the same review/apply flow
- [x] tailoring creates a pre-tailor snapshot automatically
- [x] tailoring suggestion sets are grouped by job-description themes or gaps
- [x] suggestion review exposes explicit suggestion mode metadata
- [x] retry/regenerate behavior respects the originating suggestion mode

## Notes

- this is a heuristic v1, not a full parser
- the point of this slice is to establish enforceable safety boundaries before AI patch generation exists
- if a line is ambiguous, bias toward protected rather than editable
- the first validator should be intentionally strict; loosen it later only if there is a clear product need
