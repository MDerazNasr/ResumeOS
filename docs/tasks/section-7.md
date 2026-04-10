# Section 7 Task Checklist

## Scope

Add real auth/session handling and persisted user settings so ResumeOS stops depending on a hardcoded dev user.

## Out of Scope

- OAuth
- password reset
- email verification
- theme implementation itself
- advanced account management UI

## Implementation Checklist

- [x] document the Section 7 auth/settings boundary
- [ ] add the initial backend auth/session model
- [ ] add user settings persistence
- [ ] replace the dev-user resolver with session-backed current-user resolution
- [ ] add auth routes for register/login/logout
- [ ] add settings routes for read/update
- [ ] connect editor mode persistence to backend settings
- [ ] add backend tests for auth/session and settings behavior
- [ ] verify frontend production build passes

## Verification Checklist

- [ ] a user can register and log in
- [ ] existing resume routes resolve the authenticated user correctly
- [ ] user settings can be read and updated
- [ ] editor mode persists through the backend settings model
- [ ] backend tests pass
- [ ] frontend production build passes

## Notes

- keep the first slice simple and session-cookie based
- do not mix OAuth or account-recovery work into this section
- this section should establish a clean product boundary for future preferences like theme switching
