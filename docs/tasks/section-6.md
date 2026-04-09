# Section 6 Task Checklist

## Scope

Add a first-pass style-memory layer that makes generated patch sets reflect the user's existing resume voice more consistently.

## Out of Scope

- external vector stores
- embedding APIs
- model fine-tuning
- large-scale retrieval tuning
- advanced ranking experimentation

## Implementation Checklist

- [x] document the Section 6 style-memory boundary
- [x] define the initial style-example persistence model
- [x] extract style examples from the current draft and accepted outcomes
- [x] add a style-memory retrieval helper for generation requests
- [x] thread retrieved style context into edit, review, and tailor generation flows
- [x] add backend tests for style-example persistence and retrieval
- [x] verify frontend build still passes after backend integration
- [x] expose retrieved style examples through the patch-set contract for inspection
- [x] persist accepted patch outcomes as style-memory examples and prefer them during retrieval
- [x] improve local retrieval quality with recency and label-level variety rules

## Verification Checklist

- [x] style examples can be stored for a resume or user
- [x] generation flows retrieve a bounded set of style examples
- [x] provider inputs include style-context data
- [x] patch validation and apply behavior remain unchanged
- [x] backend tests pass
- [x] frontend production build passes
- [x] patch-review UI can show which style examples informed a patch set
- [x] accepted patch outcomes are incorporated into style-memory retrieval
- [x] local retrieval avoids overly repetitive examples when stronger variety exists

## Notes

- keep the first version deterministic and inspectable
- prefer a simple local ranking heuristic before introducing embeddings
- this section should improve generated output quality without expanding the patch workflow surface area
