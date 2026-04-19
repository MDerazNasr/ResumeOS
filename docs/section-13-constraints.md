# Section 13: Constraint and Rule System

## Goal

Add durable, user-editable resume rules that the AI should follow across edit, review, holistic review, and tailor flows.

## Why This Section Exists

The product vision includes instructions like:

- keep each bullet to one line
- prefer concise bullets
- avoid first-person voice

Those should not live only in one-off prompts. They need to be stored, visible, and applied consistently.

## First Slice Boundary

The first useful version should:

- persist rules per resume
- make them editable in the workspace
- thread them into AI generation prompts
- keep the patch workflow unchanged

## Later Slices

After persistent rules exist, the next improvements should include:

- richer rule types and validation
- stronger PDF-aware enforcement for layout-sensitive rules
- clearer UI around which patch sets were shaped by which rules
