# Section 14: Constraint-Aware Layout Heuristics

## Goal

Make layout-sensitive constraints visible and actionable in holistic review.

## Scope

- rule-driven holistic-review signals
- one-line bullet heuristic
- likely-violation labels in holistic review context
- holistic-review block prioritization when the rule is active

## Out of Scope

- exact PDF line-wrap measurement
- hard enforcement at patch-apply time
- full rule engine

## Implementation Checklist

- [x] define the Section 14 boundary
- [x] add rule-driven holistic-review signals
- [x] add first one-line bullet heuristic
- [x] surface likely violation labels in the workspace
- [x] bias holistic review generation toward likely violating bullets

## Verification Checklist

- [ ] backend tests pass
- [ ] frontend production build passes
- [ ] holistic-review context exposes rule-driven signals
- [ ] holistic-review generation reflects active one-line bullet rules
