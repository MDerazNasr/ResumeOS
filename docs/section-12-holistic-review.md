# Section 12: Holistic PDF + LaTeX Review

## Goal

Extend ResumeOS so AI review can reason over both the current LaTeX source and the latest compiled PDF artifact.

## Why This Section Exists

The product vision is not only patch-safe text rewriting. The AI also needs a whole-resume view:

- visual flow
- density and spacing
- structure across sections
- presentation constraints like one-line bullets

The current system knows the source and the editable blocks, but it does not yet treat the compiled artifact as first-class review context.

## First Slice Boundary

Start by building the holistic-review context boundary rather than pretending the model is already visually aware.

That first slice should:

- expose the latest compile artifact state
- expose current source-level structure that matters to review
- make that context visible in the editor
- keep all edits flowing back through validated patch sets

## Later Slices

After the boundary exists, add:

- provider prompts that explicitly use holistic review context
- rendered-review reasoning against the compiled PDF artifact
- user constraints such as bullet-length and density rules
- PDF-aware patch generation that still respects protected/editable boundaries
