# Section 7: Auth and User Settings

## Goal

Replace the local dev-user stub with a real user/session foundation and add a proper home for per-user preferences.

## Why This Section Exists

ResumeOS now has enough real product behavior that the hardcoded dev user is no longer an acceptable base.

Current risks:

- every resume is effectively owned by the same local user
- preferences such as editor mode only live in the browser
- future features like theme switching and job-application ownership need a durable user boundary

This section turns the app from a single-user prototype into a multi-user product foundation.

## Scope

Initial scope:

- real user registration and login
- cookie-backed session handling
- backend user resolution from session state instead of the dev stub
- a persisted user settings model
- editor mode preference stored on the user as well as the browser

## Out of Scope

- OAuth providers
- password reset flows
- email verification
- RBAC or organization features
- advanced security hardening beyond the core session boundary

## Initial Architecture Boundary

Section 7 should add two backend areas:

- `auth`
- `settings`

The `auth` layer should own:

- registration
- login
- logout
- session cookie lifecycle
- current-user resolution

The `settings` layer should own:

- persisted per-user preferences
- preference read/update APIs

The editor should consume settings through the app layer rather than directly talking to browser-only storage forever.

## First Slice

The first implementation slice should stay narrow:

1. add `password_hash` support to users
2. add a `user_settings` table
3. implement register, login, logout, and `GET /me` from a real cookie-backed session
4. add `GET /settings` and `PATCH /settings`
5. wire editor mode persistence to use backend settings with local storage only as a temporary fallback

## Definition of Success

Section 7 is successful when:

- a user can register and log in
- API routes resolve the current user from a real session
- settings can be stored and read per user
- editor mode can persist through the backend user settings model
- backend tests and frontend build still pass

## Risks

- auth changes touch nearly every existing route through current-user resolution
- session cookies need to work cleanly with the current local frontend/backend split
- we should avoid half-finishing auth and breaking the current demo workflow

The first version should optimize for a correct session boundary, not auth feature breadth.
