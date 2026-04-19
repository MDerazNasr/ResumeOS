# Section 15: Constraint-Aware Candidate Enforcement

## Goal

Move persistent constraints from prompt guidance into candidate shaping and filtering.

## Why This Section Exists

Rules should not only be stored and displayed. They should affect which candidate edits are allowed to reach review.

The first useful version should:

- avoid leaking rule text into generated output
- filter out candidates that obviously violate active rules
- shape mock candidates so local behavior stays believable

## Later Slices

After first enforcement exists, improve it with:

- richer rule types
- better PDF-aware enforcement
- stronger provider-side compliance checks
