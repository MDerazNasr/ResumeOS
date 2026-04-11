# Section 7 Task Checklist

## Scope

Add real auth/session handling and persisted user settings so ResumeOS stops depending on a hardcoded dev user.

## Out of Scope

- multiple auth providers beyond the initial sign-in path
- password reset
- email verification
- theme implementation itself
- advanced account management UI

## Implementation Checklist

- [x] document the Section 7 auth/settings boundary
- [x] add the initial backend auth/session model
- [x] add user settings persistence
- [x] replace the dev-user resolver with session-backed current-user resolution
- [x] add auth routes for sign-in/logout and session resolution
- [x] add settings routes for read/update
- [x] connect editor mode persistence to backend settings
- [x] add a minimal frontend auth flow for sign-in/logout
- [x] add a dedicated auth page and enforce session auth on product routes
- [x] remove the temporary dev-user fallback from the live auth contract
- [x] add a minimal authenticated settings page
- [x] add backend tests for auth/session and settings behavior
- [x] verify frontend production build passes

## Verification Checklist

- [x] a user can sign in and resume a session
- [x] existing resume routes resolve the authenticated user correctly
- [x] user settings can be read and updated
- [x] editor mode persists through the backend settings model
- [x] unauthenticated users are redirected to `/auth` before product routes load protected data
- [x] `/me` only returns a real session user or `401`
- [x] authenticated users can reach a settings page and update editor mode there
- [x] backend tests pass
- [x] frontend production build passes

## Notes

- keep the first slice simple and session-cookie based
- do not mix account-recovery work or extra auth providers into this section
- this section should establish a clean product boundary for future preferences like theme switching
