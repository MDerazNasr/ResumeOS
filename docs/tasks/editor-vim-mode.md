# Editor Vim Mode Task Checklist

## Scope

Add a user-facing toggle in the LaTeX editor so the user can switch between standard Monaco editing and Vim keybindings.

## Out of Scope

- persisted user preferences across sessions
- broader theme or light/dark settings
- custom Vim statusline theming beyond a minimal usable display
- multi-editor preference management

## Implementation Checklist

- [x] document the Vim-mode slice
- [x] add Monaco Vim integration to the frontend workspace
- [x] expose a simple standard/Vim toggle in the editor workspace
- [x] keep normal editing behavior unchanged when Vim mode is off
- [x] show minimal Vim status or mode feedback when Vim mode is on
- [x] verify frontend production build passes
- [x] persist the selected editor mode across reloads

## Verification Checklist

- [x] user can toggle between standard and Vim modes
- [x] Monaco remains usable in standard mode
- [x] Vim keybindings are active in Vim mode
- [x] frontend production build passes
- [x] the selected editor mode survives a page reload on the same browser

## Notes

- keep this slice focused on editor behavior only
- do not fold theme preferences into this branch
