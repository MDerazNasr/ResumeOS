# Section 8: UI Preferences

## Goal

Add a real app-level preference layer on top of the Section 7 settings foundation, starting with light/dark mode.

## Scope

- persist light/dark mode through backend user settings
- apply the active theme at the app shell level
- expose a theme toggle on the settings page

## Out of Scope

- broad visual redesign
- per-page theme overrides
- new account-management features beyond settings

## Acceptance Criteria

- authenticated users can switch between light and dark mode
- the selected theme persists across reloads
- the app shell uses the selected theme consistently
- backend tests pass
- frontend production build passes
