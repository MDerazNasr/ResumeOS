# Section 14: Constraint-Aware Layout Heuristics

## Goal

Turn layout-sensitive rules into product logic instead of leaving them as prompt text only.

## Why This Section Exists

Rules like “keep each bullet to one line” need more than persistence. The product should:

- detect likely violations
- surface them visibly
- bias review toward the affected parts of the resume

## First Slice Boundary

The first pragmatic slice should:

- add rule-driven layout signals to holistic review context
- detect likely one-line bullet violations with conservative heuristics
- bias holistic review generation toward the relevant bullet blocks

## Later Slices

After the first heuristics are in place, improve them with:

- stronger PDF-aware layout extraction
- more rule types
- more explicit per-rule enforcement feedback
