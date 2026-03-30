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
