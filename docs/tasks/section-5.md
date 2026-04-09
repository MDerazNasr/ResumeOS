# Section 5 Task Checklist

## Scope

Turn the current suggestion workflow into a first-class patch-set editing system instead of a collection of suggestion-specific DTOs and UI behaviors.

## Out of Scope

- new model vendors or fine-tuning work
- style-memory retrieval
- advanced collaboration or multiplayer features
- full document-wide AI rewrites

## Implementation Checklist

- [x] document the Section 5 patch-set contract
- [x] define first-class patch-set DTOs distinct from the current mock suggestion naming
- [x] add backend adapters so edit, review, and tailor flows all emit the same patch-set structure
- [x] preserve the current validation and apply gates under the new patch-set contract
- [x] update the frontend review surface to speak in terms of patch sets rather than mixed suggestion terminology
- [x] keep mode metadata, retry behavior, and feedback logging working after the contract rename
- [x] add backend tests for the new patch-set contract
- [x] verify the frontend still supports edit, review, and tailor flows through the new patch-set model
- [x] remove the leftover mock-suggestion type naming from the shared frontend/backend contracts
- [x] rename the seeded baseline patch-set route and client helpers to match the patch-set vocabulary
- [x] rename the remaining editor review panel and patch-set state internals to match the patch-set workflow language

## Verification Checklist

- [x] patch sets are returned through one shared contract for edit, review, and tailor
- [x] the edit flow returns the new patch-set contract explicitly
- [x] review and tailor also return the new patch-set contract explicitly
- [x] validated patch application still works through the new contract
- [x] feedback logging still records apply and dismiss outcomes
- [x] review UI still renders grouped diff hunks correctly
- [x] backend tests pass
- [x] frontend production build passes

## Notes

- Section 5 should make the system feel more productized, not more speculative
- this is a contract and workflow cleanup section, not a feature explosion section
- if a change does not make the patch workflow more coherent, it probably belongs later
