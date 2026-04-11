# Section 9: Hardening

## Goal

Improve developer reliability and production-readiness around the current core product instead of adding new product surface area immediately.

## Scope

- remove known local dev/build warnings where practical
- tighten app-shell runtime verification around auth and theming
- improve docs for stable local startup and recovery steps

## Out of Scope

- new AI product modes
- new editor capabilities
- infrastructure migration away from SQLite

## Acceptance Criteria

- backend tests pass
- frontend production build passes without the known Tailwind content warning
- docs describe the stable local startup workflow
