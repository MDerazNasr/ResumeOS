# Section 5: Patch-Set Workflow

## Purpose

Section 4 proved that ResumeOS can safely generate, validate, review, and apply AI-assisted edits.

Section 5 should make that system feel like a first-class editing workflow instead of a growing pile of suggestion-specific contracts.

## Problem

Right now the system works, but the naming and contracts still reflect the order it was built in:

- mocked patches
- generated edit suggestions
- review suggestions
- tailor suggestions

Those flows all reuse the same safety architecture, but they do not yet present themselves as one coherent patch-set system.

## Section 5 Goal

Define and adopt one shared patch-set contract that all AI editing modes emit.

That contract should represent:

- one patch set
- its mode (`edit`, `review`, `tailor`)
- its rationale and grouping metadata
- one or more validated patch hunks

This should sit above the existing strict validation and apply rules, not replace them.

## Desired Shape

The user should experience:

- one patch-review system
- one grouped patch-set vocabulary
- one apply/reject loop
- consistent feedback logging

The user should not need to care whether a patch set came from:

- block edit
- review
- tailoring
- future style-memory retrieval

## Non-Goals

Section 5 is not about:

- richer model quality
- new retrieval systems
- fine-tuning
- broader UX polish like theming

Those can come later.

## Success Criteria

Section 5 is successful when:

- backend patch sets have one shared contract
- edit, review, and tailor all emit that contract
- the review surface uses the same vocabulary and behaviors for every mode
- apply, dismiss, retry, and feedback still work
- no safety guarantees are weakened

## First Migration Slice

The first concrete Section 5 migration should stay narrow:

- define first-class `PatchHunk` and `PatchSet` DTOs
- migrate the `edit` flow to emit that contract explicitly
- move the frontend review surface vocabulary to patch-set terminology
- keep `review` and `tailor` source-compatible while they wait for the next migration slice

This gives the system a real new contract without attempting a risky all-at-once rename.

## Why This Matters

Section 4 made the system safe.

Section 5 should make it coherent.

That is the step that turns the current AI workflow from “impressive prototype” into “real product subsystem.”
