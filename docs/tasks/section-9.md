# Section 9 Task Checklist

## Scope

Harden the current ResumeOS baseline so local development and verification are more predictable.

## Out of Scope

- new feature work
- visual redesign
- auth model changes

## Implementation Checklist

- [x] document the Section 9 hardening boundary
- [x] add a valid Tailwind content config to remove the known warning
- [x] update local dev docs for the current stable workflow
- [x] add a stable auth/app-shell runtime verification script
- [x] verify backend tests pass
- [x] verify frontend production build passes
- [x] verify the live auth/app shell routes through the stable run path

## Verification Checklist

- [x] backend tests pass
- [x] frontend production build passes
- [x] the known Tailwind content warning is gone
- [x] the README reflects the current startup and recovery workflow
- [x] `/health` returns `200`
- [x] `/auth/google/status` returns `200`
- [x] Google auth reports `configured: true` when local OAuth env vars are set
- [x] `/auth` returns `200`
- [x] protected app routes redirect to `/auth` instead of failing at runtime
