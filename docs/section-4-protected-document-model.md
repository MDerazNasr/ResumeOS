# Section 4: Protected Document Model

## Purpose

Before ResumeOS can safely generate or validate AI patches, it needs a first-class model of the resume source that distinguishes structural LaTeX from content text.

This slice establishes that boundary.

## Initial Contract

The backend should extract two things from the current working draft:

1. protected regions
2. editable blocks

Protected regions are read-only for future AI patch generation.
Editable blocks are the only safe patch targets.

## Protected Regions in v1

The first heuristic version treats these areas as protected:

- preamble before `\begin{document}`
- `\begin{document}` and `\end{document}`
- section heading lines like `\section*{...}`
- environment boundary lines like `\begin{itemize}` and `\end{itemize}`
- other LaTeX command lines that are not yet explicitly supported as editable leaf text

This biases toward safety over flexibility.

## Editable Blocks in v1

The first heuristic version treats these areas as editable:

- plain text lines inside the document body that do not begin with a LaTeX command
- bullet item text after the `\item` prefix

For each editable block, the model should expose:

- stable block id
- block kind
- label or section context
- extracted text
- source line and column range

## Why This Is Acceptable Now

This is not a full LaTeX parser.

That is fine for this milestone because the goal is:

- establish a server-side safety boundary
- make the boundary visible in the product
- create something patch validation can build on later

The main rule for v1 is simple:

If a region is ambiguous, classify it as protected.

## Next Uses

Once this exists, later AI and patch slices can:

- target editable blocks by id
- reject patches that touch protected ranges
- explain to the user why some parts of the resume are not AI-editable yet

## First Patch-Validation Contract

The first validator should be intentionally strict.

A proposed edit is valid only when:

- it targets one existing editable block by id
- the proposed line range exactly matches that block's extracted range
- the proposed `beforeText` still matches the current draft text for that block

This is narrower than the final system will be, but it is the right starting point because it gives the backend a trustworthy acceptance gate before patch generation exists.

## Mocked Patch Flow Before AI

Before connecting a model, ResumeOS should exercise the future patch workflow with deterministic mocked proposals.

The mocked flow should:

- pick a few editable blocks from the current document model
- build concrete patch proposals against those blocks
- validate each proposal through the same patch-validation gate
- only return proposals that pass validation

This is useful because it proves the architecture end to end:

- document model extraction
- block-targeted proposal generation
- server-side validation
- frontend review surface

without introducing model variability yet.

## First Patch-Apply Contract

The first apply path should stay as strict as the validator.

A patch apply request should include:

- target block id
- exact line range
- exact `beforeText`
- replacement `afterText`

The backend should:

- re-run validation against the current draft
- reject stale or invalid requests
- replace only the targeted editable block text
- persist the updated working draft immediately

This keeps the first apply mechanic easy to reason about and avoids mixing optimistic client-side editing with safety-critical server-side validation.

## Grouped Suggestion Sets Before AI

The next step after single mocked proposals is to group related patches into suggestion sets.

A suggestion set should:

- have its own id, title, and summary rationale
- contain one or more validated patch proposals
- support retry/regenerate at the set level

This matters because the eventual AI UX should feel like reviewing a coherent edit pass, not a pile of unrelated isolated cards.

## Suggestion Review Refinement

After grouped suggestion sets exist, the next refinement is presentation and schema clarity.

The review surface should emphasize:

- patch-like before/after hunks
- operation metadata such as `replace`
- validation status that reads like a review system, not a mock-only scaffold

The point of this step is to make the workflow feel closer to the final product without changing the strict backend safety rules underneath.
