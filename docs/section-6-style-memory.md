# Section 6: Style Memory

## Goal

Add the first real personalization layer so generated patch sets preserve the user's existing resume voice instead of acting like a generic rewriting system.

## Why This Section Exists

ResumeOS already has:

- safe document modeling
- strict patch validation
- patch-set review and apply
- edit, review, and tailor generation flows

What it does not yet have is durable style awareness. Right now, generated patch sets can be structurally safe while still sounding generic.

Style memory is the next important product differentiator because it moves the system from:

- safe AI editing

to:

- safe AI editing that sounds like the user

## Scope

Section 6 should introduce a narrow, practical style-memory system.

Initial scope:

- extract candidate style examples from the user's current draft and accepted patch outcomes
- persist those examples in a simple local style-memory store
- score or retrieve the most relevant examples for a generation request
- inject those examples into the provider input for `edit`, `review`, and `tailor`
- keep the rest of the patch-set workflow unchanged

## Out of Scope

- vector database infrastructure
- external embedding services
- fine-tuning or preference optimization
- multi-user style analytics
- aggressive retrieval tuning

The first version should be simple and deterministic enough to verify locally.

## Initial Architecture Boundary

Section 6 should add a new backend layer:

- `style_memory`

That layer should own:

- style example extraction
- style example persistence
- style example retrieval
- shaping a compact style context for the provider layer

The LLM provider layer should consume style context, not implement retrieval itself.

## First Slice

The first implementation slice should be intentionally narrow:

1. define a persisted `style_examples` table
2. seed style examples from the current draft's editable bullet and paragraph text
3. add a retrieval helper that returns the top few examples for a target block or mode
4. thread those retrieved examples into the existing generated edit/review/tailor flows

This gives us a concrete end-to-end personalization pass without introducing vector infrastructure yet.

## Definition of Success

Section 6 is successful when:

- style examples are persisted per resume or user
- generation flows can retrieve relevant style examples
- provider inputs clearly include a compact style context
- the patch-set workflow still validates and applies normally
- backend tests and frontend build still pass

## Risks

- retrieval may be too noisy if we index too much content too early
- simplistic similarity may overfit to recent text rather than good text
- style context can bloat prompts if we do not cap it aggressively

The first version should optimize for small, understandable behavior rather than retrieval sophistication.
