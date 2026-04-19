# Section 15: Constraint-Aware Candidate Enforcement

## Goal

Filter and shape generated candidates using active resume constraints.

## Scope

- candidate violation detection for a small set of rules
- one-line bullet shaping for mock generation
- filtering invalid candidates before they reach patch review

## Out of Scope

- exact PDF-based enforcement
- apply-time hard rejection
- comprehensive natural-language rule parsing

## Implementation Checklist

- [x] define the Section 15 boundary
- [x] add candidate-violation evaluation helpers
- [x] filter candidates against active constraints
- [x] stop leaking constraints literally into mock outputs
- [x] add regression coverage for one-line bullet enforcement

## Verification Checklist

- [ ] backend tests pass
- [ ] frontend production build passes
- [ ] constraint text does not appear verbatim in generated candidate text
- [ ] one-line bullet constraints keep candidates under the current heuristic threshold
