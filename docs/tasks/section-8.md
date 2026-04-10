# Section 8 Task Checklist

## Scope

Add persisted UI preferences on top of the new settings foundation, starting with light/dark mode.

## Out of Scope

- major design overhaul
- new auth flows
- additional editor behavior beyond existing Vim mode

## Implementation Checklist

- [x] document the Section 8 UI-preferences boundary
- [x] extend backend settings with theme mode
- [x] apply theme mode at the app shell level
- [x] add a settings-page light/dark toggle
- [x] move the main resume workspace panels onto shared theme variables
- [x] expose the theme switch directly in the authenticated app header
- [x] verify backend tests pass
- [x] verify frontend production build passes

## Verification Checklist

- [x] a signed-in user can switch between light and dark mode
- [x] the selected theme persists across reloads
- [x] the app shell reflects the active theme
- [x] the main resume workspace panels no longer look hardcoded to dark mode
- [x] the user can toggle theme without leaving the main app pages
- [x] backend tests pass
- [x] frontend production build passes
