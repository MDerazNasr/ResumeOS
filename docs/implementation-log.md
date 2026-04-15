# ResumeOS Implementation Log

## Working Convention

This project should be developed in small, verifiable slices.

For each slice:

1. define scope and acceptance criteria
2. implement the smallest concrete version
3. verify the slice
4. update documentation
5. create a structured commit before moving on

Commit messages should stay section-oriented and descriptive.

Examples:

- `docs: add product architecture and implementation log`
- `feat(section-1): scaffold web and api apps`
- `feat(section-1): add resume and working draft persistence`
- `fix(section-1): update backend dependencies for python 3.14`

## Completed Work

### 2026-04-12: Section 11 Chat Layer Planning

Opened a new branch for the first conversational AI slice after the inline editor review workflow was in place.

Planned scope:

- add a persistent per-resume chat thread
- ground assistant replies in the current draft and style-memory context
- let chat responses produce patch sets through the existing validated review path
- avoid direct document mutation from chat

Why this shape:

- the safe patch-review foundation already exists, so chat should plug into it rather than invent a second editing path
- the first slice should make chat visible and persistent before adding richer conversational behaviors

### 2026-04-12: Section 11 Chat Layer Implementation

Implemented the first real conversational layer on top of the safe patch workflow.

Added:

- persistent per-resume chat threads and stored user/assistant messages
- chat routes for fetching a thread and sending new messages
- an `AI Chat` sidebar in the editor workspace
- chat intent routing across question, edit, review, and tailor requests
- per-turn linkage showing whether an assistant reply generated patch sets
- recent-message grounding so follow-up replies can see short conversation history
- provider-backed assistant replies so chat can use the same provider abstraction as patch generation

Why this shape:

- the product needs real back-and-forth interaction, but document mutation still has to flow through validated patch application
- grounding replies in recent turns is the minimum needed to make the chat feel conversational instead of transactional
- threading chat through the provider interface keeps the architecture consistent when switching from mock to OpenAI-backed behavior

Verified:

- backend test suite passes after chat persistence, routing, and provider integration
- frontend production build passes after the chat sidebar and editor integration

### 2026-04-15: Section 11 Follow-Up Intent Handling

Extended the chat layer so short follow-up prompts behave more like a conversation instead of resetting to question mode.

Added:

- follow-up-aware intent resolution that can inherit the last actionable user intent
- first-pass reuse of the previous tailor request when a follow-up is clearly continuing that tailoring thread
- chat response metadata indicating whether the resolved intent came from the current message or recent history
- UI badges showing when a reply was treated as a follow-up
- backend regression coverage for inherited review intent

Why this shape:

- users should not need to restate “review this resume” or re-paste the whole JD on every follow-up
- inheriting only clear, short follow-up turns keeps the behavior useful without making intent routing opaque
- exposing follow-up resolution in the UI makes the conversational state auditable instead of implicit

Verified:

- backend test suite passes after follow-up intent handling was added
- frontend production build still passes after the chat metadata and badge updates

### 2026-04-15: Section 11 Response Formatting

Improved how chat responses read and render so different AI actions do not feel like the same generic assistant message.

Added:

- mode-specific provider phrasing for question, review, edit, and tailor replies
- assistant-card headings that distinguish context answers from patch-generating replies
- follow-up support for continuing a prior tailoring request with a short second prompt
- backend regression coverage for follow-up tailoring behavior

Why this shape:

- conversational UX was still too uniform even after the chat layer became provider-backed
- users need to understand quickly whether a reply answered a question or loaded edits to review
- tailoring follow-ups are a common case and should not require re-pasting the whole job description every time

Verified:

- backend test suite passes after mode-specific response formatting and tailor follow-up handling
- frontend production build still passes after the chat card presentation updates

### 2026-04-15: Section 11 Chat Streaming

Added the first incremental chat rendering path so the assistant no longer appears only after the whole response is ready.

Added:

- a streaming chat endpoint that emits `start`, `delta`, and `complete` events
- client-side NDJSON parsing for streamed chat events
- optimistic user/assistant message insertion in the chat sidebar
- incremental assistant text rendering while the request is in flight
- backend regression coverage for the stream endpoint

Why this shape:

- the chat UI felt transactional because the assistant only appeared after the full response was computed
- transport-level streaming improves the product feel immediately without forcing a risky provider-level rewrite
- the final `complete` event still reuses the validated chat response shape, so the patch workflow remains consistent

Verified:

- backend test suite passes after adding the stream endpoint and event test
- frontend production build still passes after the streaming client and optimistic sidebar updates

### 2026-04-12: Section 10 Inline Editor Review

Moved the patch-review workflow into Monaco so the AI editing loop behaves more like an IDE.

Added:

- inline Monaco hunk highlighting tied to the active patch set state
- an inline review widget for the active hunk with previous/next, accept/reject, and approve-all/reject-all controls
- keyboard shortcuts for current-hunk and batch review actions
- tighter editor-native styling so the review flow reads more like a code editor than a detached form

Why this shape:

- the backend patch workflow was already safe enough; the gap was product ergonomics
- review should happen where the source is, not only in a sidebar
- moving the active hunk state into the editor container made Monaco and the review panel share one coherent review state

Verified:

- backend test suite passes after the inline-review integration
- frontend production build passes after the Monaco decoration and widget work

### 2026-04-12: Section 10 Patch Visibility Fix

Closed a real usability gap in the patch-review workflow.

What changed:

- moved the patch-review area to the top of the editor sidebar so generated edits are visible immediately
- added top-level activity and error banners so failed tailor/edit actions are not hidden in the footer
- auto-scrolls the workspace to the patch-review area after edit, review, and tailor generation

Why:

- generation was already wired and passing tests, but the UI made successful results easy to miss
- the fix needed to improve visibility and navigation, not change the suggestion backend

Verified:

- backend test suite passes after the review-visibility update
- frontend production build passes after the layout and status-message changes

### 2026-04-09: Section 6 Planning

Opened the Section 6 branch from merged `main` after Section 5 was pushed and integrated.

Planned scope:

- add a first-pass style-memory layer
- persist local style examples from the draft and accepted outcomes
- retrieve a bounded style context for generation requests
- thread that context into edit, review, and tailor without changing the patch workflow

Primary planning files:

- [section-6-style-memory.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/section-6-style-memory.md)
- [section-6.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/tasks/section-6.md)

### 2026-04-09: Section 6 First Style-Memory Slice

Implemented the first local style-memory layer without introducing vector infrastructure.

Added:

- `style_examples` persistence in the local schema
- a backend style-memory service that refreshes draft-derived style examples and retrieves a bounded relevant subset
- style-context threading into edit, review, and tailor provider prompts
- backend tests covering style-example persistence and retrieval

Verified:

- backend test suite passes after the style-memory integration
- frontend production build still passes after the backend-only change

### 2026-04-09: Section 6 Style-Memory Inspection Slice

Exposed the retrieved style-memory examples through the patch-set contract so the personalization layer is visible instead of hidden in backend prompts.

Added:

- `styleExamples` on patch sets in the shared backend/frontend contract
- edit, review, and tailor patch-set population with the retrieved style examples that informed generation
- review-panel rendering of the retrieved style examples for each patch set
- regression assertions that generated patch sets include bounded style-memory examples

Verified:

- backend test suite still passes after exposing style-memory metadata
- frontend production build still passes with the new review-panel rendering

### 2026-04-09: Section 6 Accepted Outcome Style Memory

Extended style memory so the system learns not only from the current draft but also from text the user actually approved through patch application.

Added:

- accepted style-example persistence at patch-apply time
- retrieval ranking that prefers accepted examples over plain draft-derived examples
- regression tests confirming accepted outcomes are stored and preferred during retrieval

Verified:

- backend test suite passes after accepted-style-example persistence was added
- frontend production build still passes after the backend-only retrieval upgrade

### 2026-04-09: Section 6 Retrieval Quality Upgrade

Improved local style-memory retrieval so it is less repetitive and more useful without needing embeddings yet.

Added:

- retrieval ranking that considers freshness alongside source-type and overlap score
- greedy result selection that prefers label diversity before returning duplicate examples from the same area
- regression coverage confirming varied examples are selected when strong alternatives exist

Verified:

- backend test suite passes after the retrieval-quality upgrade
- frontend production build still passes after the backend-only ranking change

### 2026-04-09: Editor Vim Mode Planning

Opened a dedicated editor-enhancement branch after Section 6 merged into `main`.

Planned scope:

- add Monaco Vim integration
- expose a standard/Vim toggle in the editor workspace
- keep the slice focused on editor behavior only

Primary planning file:

- [editor-vim-mode.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/tasks/editor-vim-mode.md)

### 2026-04-09: Editor Vim Mode Implementation

Implemented the first editor-preference enhancement after Section 6 closed.

Added:

- `monaco-vim` integration in the LaTeX editor component
- a standard/Vim mode toggle in the editor workspace header
- a small mode/status readout under Monaco so the active Vim state is visible

Verified:

- frontend production build passes with Vim integration enabled
- backend regression suite still passes after the editor-only change

### 2026-04-09: Editor Vim Mode Persistence

Added a small follow-up so the editor preference survives reloads instead of resetting to Standard on every page load.

Added:

- local browser persistence for the selected editor mode
- startup restoration of the saved mode with Standard as the safe fallback

Verified:

- frontend production build still passes after persistence was added
- backend regression suite still passes after the editor-state change

### 2026-04-09: Section 7 Planning

Opened the next core product branch after the Vim-mode enhancement merged into `main`.

Planned scope:

- replace the hardcoded dev-user with real auth/session handling
- add persisted user settings
- move editor mode persistence onto the user settings model

Primary planning files:

- [section-7-auth-settings.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/section-7-auth-settings.md)
- [section-7.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/tasks/section-7.md)

### 2026-04-09: Section 7 Backend Auth and Settings Foundation

Implemented the first real auth/settings backend slice while preserving the current demo workflow.

Added:

- session-cookie auth primitives with register, login, logout, and current-user resolution
- `user_settings` persistence and settings read/update routes
- password hashing and session-token hashing using standard-library primitives
- backend tests for auth/session and settings round trips

Verified:

- backend test suite passes after the auth/settings foundation was added
- frontend production build still passes after the backend contract expansion

### 2026-04-10: Section 7 Editor Settings Integration

Connected the existing editor-mode preference to the new backend settings model without forcing a full login UI yet.

Added:

- frontend settings API client methods for reading and updating `/settings`
- editor-mode hydration from backend settings with local storage retained as a fallback cache
- editor-mode writes now update backend settings as the primary persistence path
- test isolation fixes for the new auth/settings backend suite

Verified:

- backend test suite passes after the editor/settings integration
- frontend production build still passes after the settings client changes

### 2026-04-10: Section 7 Minimal Frontend Auth Flow

Added the first frontend surface for the new auth/session foundation without removing the dev fallback yet.

Added:

- visible session/fallback state via `authSource` on the current user contract
- a minimal auth panel on the resumes page for register, login, and logout
- UI copy that makes the temporary dev-fallback mode explicit instead of invisible

Verified:

- backend test suite still passes after the current-user contract expansion
- frontend production build still passes with the new auth panel

### 2026-04-10: Section 7 Auth Route Protection

Moved ResumeOS from a soft auth boundary to a real product gate while preserving `/me` as a lightweight session-status probe.

Added:

- backend `require_authenticated_user` enforcement for resume and settings routes
- a dedicated `/auth` page for login/register instead of relying on inline fallback alone
- frontend redirects from protected app routes to `/auth` before protected API calls fire
- backend assertions that anonymous access to `/resumes` and `/settings` now returns `401`

Verified:

- backend test suite passes after tightening route protection
- frontend production build passes with the new `/auth` route and redirects

### 2026-04-10: Section 7 Remove Dev Fallback Identity

Finished the auth boundary by removing the hardcoded dev-fallback user from the live contract.

Added:

- `/me` now behaves like a real session endpoint and returns `401` when no session exists
- frontend `getCurrentUser()` now treats `401` as unauthenticated state instead of a fake user
- the auth page now renders directly from that unauthenticated state, while protected routes redirect before loading product data
- backend tests now create authenticated clients explicitly instead of leaning on a seeded fallback identity

Verified:

- backend test suite passes after converting protected-route tests to real authenticated clients
- frontend production build passes after removing `authSource` and the dev-fallback flow

### 2026-04-10: Section 7 Google Auth Replacement

Replaced the initial local email/password auth flow with Google OAuth while preserving the existing session-cookie and settings model.

Added:

- backend Google auth status, start, and callback routes
- Google profile upsert into the existing `users` table using `google_sub`
- frontend auth page update to a single Google sign-in action
- backend test helper migration from register/login to mocked Google callback flows

Verified:

- backend test suite passes with the Google auth replacement
- frontend production build passes after removing the register/login UI

### 2026-04-11: AI Roadmap Clarification

Reframed the architecture plan so it matches the intended product more closely instead of stopping at the current patch-generation foundation.

Added to the plan:

- a dedicated patch-review UX slice for IDE-style diff review with approve/reject-all and hunk navigation
- a conversational AI chat layer that can discuss the resume and emit patch sets
- a holistic PDF + LaTeX review layer so the model can reason about rendered structure and layout
- a persistent constraint/rule system for requirements like one-line bullets or concise phrasing
- UI preference notes that light mode should be the default and the editor theme should follow the app theme

### 2026-04-11: Section 9 Google-Auth Runtime Verification

Updated the hardening/runtime verification layer so it matches the current Google-backed auth model instead of the earlier generic auth assumptions.

Added:

- runtime verification coverage for `/auth/google/status`
- an assertion that Google auth reports `configured: true` when local OAuth env vars are present
- README cleanup so the documented local API default matches `127.0.0.1`

Verified:

- backend test suite passes after the Google auth runtime verification update
- frontend production build passes
- `bash scripts/verify_runtime.sh` passes against the live local API and frontend

### 2026-04-11: Section 10 Planning

Opened the next branch from merged `main` after Section 9 was integrated.

Planned scope:

- turn patch-set review into a stronger red/green diff workflow
- add approve-all and reject-all actions
- add next/previous hunk navigation
- keep the existing safe patch-set contract and backend validation unchanged

Primary planning file:

- [section-10-patch-review-ux.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/tasks/section-10-patch-review-ux.md)

### 2026-04-11: Section 10 Diff Review UX

Upgraded the patch review surface so it behaves more like reviewing code changes instead of scanning generic patch cards.

Added:

- stronger red/green diff styling with line-by-line presentation
- next/previous hunk navigation
- approve-all and reject-all actions for visible hunks
- clearer active-hunk focus styling in the review panel

Verified:

- backend test suite passes after the UI-only review upgrade
- frontend production build passes with the new review workflow

### 2026-04-12: Section 10 Review Flow Progression

Refined the review flow so working through hunks feels more intentional instead of leaving navigation state ambiguous after actions.

Added:

- active-hunk auto-advance after approve/reject
- per-set visible-hunk counts
- clearer completion messaging after approve-all or reject-all

Verified:

- backend test suite still passes after the review-flow refinement
- frontend production build still passes with the updated progression logic

### 2026-04-10: Section 9 Planning

Opened the next branch from merged `main` after Section 8 was integrated.

Planned scope:

- remove the known Tailwind build warning
- document the stable local startup and recovery workflow
- tighten confidence around the current auth/theme app shell baseline

Primary planning files:

- [section-9-hardening.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/section-9-hardening.md)
- [section-9.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/tasks/section-9.md)

### 2026-04-10: Section 9 Stable Verification Hardening

Closed the first hardening slice around local build reliability and baseline verification without changing product behavior.

Added:

- a root `tailwind.config.js` with explicit web content globs so the known Tailwind content warning is gone
- README guidance for the current stable local verification workflow using `uvicorn`, a workspace build, and `next start`
- clearer recovery guidance for clearing `apps/web/.next` and rebuilding when local frontend state gets corrupted

Verified:

- backend test suite passes with `python -m unittest discover -s tests`
- frontend production build passes cleanly with `npm --workspace @resumeos/web run build`
- the known Tailwind content warning no longer appears during the production build

### 2026-04-10: Section 9 Runtime Verification Hardening

Added a small explicit runtime check for the auth/app shell so the most common local regressions are caught by one repeatable command.

Added:

- a root `scripts/verify_runtime.sh` script
- a root `verify:runtime` npm command
- README documentation for the stable runtime verification step after starting the API and web servers

Verified:

- `/health` returns `200`
- `/auth` returns `200`
- protected routes like `/app/resumes`, `/app/settings`, and an editor route redirect to `/auth` instead of failing at runtime when unauthenticated

### 2026-04-10: Section 8 Planning

Opened the next branch from merged `main` after Section 7 was integrated.

Planned scope:

- extend the persisted settings model with light/dark theme mode
- apply the active theme at the app shell level
- expose a settings-page theme toggle

Primary planning files:

- [section-8-ui-preferences.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/section-8-ui-preferences.md)
- [section-8.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/tasks/section-8.md)

### 2026-04-10: Section 8 Theme Preferences

Added the first real app-level preference surface on top of the Section 7 settings model.

Added:

- backend `themeMode` persistence in user settings
- app-shell theme application in the root layout
- local theme hydration so the selected mode survives reloads cleanly
- settings-page light/dark toggle alongside the existing editor-mode controls

Verified:

- backend test suite passes after extending the settings contract
- frontend production build passes with the global theme shell and settings toggle

### 2026-04-10: Section 8 Workspace Theme Variable Pass

Moved the most important editor-adjacent panels away from fixed dark colors so light mode is usable beyond the app shell.

Added:

- shared theme variables for borders, surfaces, badges, accents, and diff backgrounds
- document model panel theme-variable adoption
- patch-set review panel theme-variable adoption
- snapshot panel theme-variable adoption

Verified:

- backend test suite still passes after the frontend theme-variable pass
- frontend production build still passes with the updated workspace surfaces

### 2026-04-10: Section 8 App-Header Theme Switch

Exposed the theme control in the authenticated app shell so users no longer need to visit settings just to switch modes.

Added:

- reusable `ThemeToggle` switch component
- `/app` layout header with app identity, settings link, and theme switch
- shared authenticated app chrome across resumes, editor, and settings pages

Verified:

- backend test suite still passes after introducing the shared app layout
- frontend production build still passes with the visible header switch

### 2026-04-10: Section 8 Secondary Surface Theme Pass

Extended the theme variable system into the remaining high-traffic non-workspace surfaces so light mode feels more coherent.

Added:

- auth panel theme-variable adoption
- create-resume form and resume-list theme-variable adoption
- editor shell/status card variable adoption
- error and global-error surface variable adoption

Verified:

- backend test suite still passes after the broader frontend theme pass
- frontend production build still passes with the updated secondary surfaces

### 2026-04-10: Section 7 Minimal Settings Page

Added the first dedicated authenticated settings surface on top of the existing backend settings model.

Added:

- `/app/settings` page for signed-in users
- a settings panel for editor-mode changes and sign-out
- a direct settings link from the signed-in account panel on the resumes page

Verified:

- backend test suite still passes with the new settings surface in place
- frontend production build passes with the new route and client settings panel

### 2026-04-08: Section 5 Planning

Opened the Section 5 branch from merged `main` after Section 4 was pushed and integrated.

Planned scope:

- formalize one first-class patch-set contract
- adapt edit, review, and tailor flows to emit that contract
- keep validation, apply, retry, and feedback behavior intact

Primary planning files:

- [section-5-patch-set-workflow.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/section-5-patch-set-workflow.md)
- [section-5.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/tasks/section-5.md)

### 2026-04-08: Section 5 First Patch-Set Contract Slice

Started the Section 5 migration by introducing a first-class patch-set contract without rewriting the whole subsystem at once.

Added:

- backend `PatchHunk`, `PatchSet`, and `PatchSetList` DTOs
- backend `edit` route migration onto the new patch-set response model
- frontend review-surface vocabulary shift from “suggestions” to “patch sets”
- frontend state and handler updates so the live editor now works in terms of patch sets

Verified:

- backend test suite passes after the first contract migration
- frontend production build passes after the review-surface rename

### 2026-04-09: Section 5 Patch-Set Contract Migration

Completed the contract migration so the live AI-assisted flows now speak one explicit backend shape.

Added:

- backend `review` and `tailor` route migration onto the shared patch-set response model
- frontend client updates so mock, edit, review, and tailor retrieval now all work against the shared patch-set structure

Verified:

- backend test suite passes after migrating all live generation flows to the patch-set contract
- frontend production build passes with the unified contract in place

### 2026-04-09: Section 5 Patch-Set Naming Cleanup

Finished the contract cleanup by removing the leftover old mock-type aliases from the shared patch-set surface.

Added:

- backend mock patch source now emits the shared patch-set types directly
- frontend client and editor helpers now refer to patch sets explicitly instead of carrying old mock-type aliases forward

Verified:

- backend test suite still passes after the naming cleanup
- frontend production build still passes after the client/editor rename

### 2026-04-09: Section 5 Seeded Patch-Set Route Cleanup

Finished the remaining naming cleanup at the route and client layer so the baseline patch-set retrieval path matches the Section 5 vocabulary.

Added:

- backend seeded patch-set route rename from `/patches/mock` to `/patch-sets/seeded`
- backend service rename so the seeded baseline source reads like patch-set infrastructure rather than a leftover mock helper
- frontend client and editor-state rename from `getMockPatchSets` and `mockPatchSeed` to seeded patch-set terminology
- backend test updates so patch-apply and seeded baseline coverage target the renamed route

Verified:

- backend test suite still passes after the route and helper rename
- frontend production build still passes after the client/editor cleanup

### 2026-04-09: Section 5 Review UI Naming Cleanup

Finished the last low-risk frontend naming cleanup so the review surface and editor state match the patch-set workflow terminology introduced in Section 5.

Added:

- review panel component rename from `SuggestionReviewPanel` to `PatchSetReviewPanel`
- editor state rename from suggestion-oriented names to patch-set-oriented names for empty-state and retry context tracking
- Section 5 task/context updates so the recorded milestone matches the implementation

Verified:

- backend test suite still passes after the UI/internal rename
- frontend production build still passes after the component rename

### 2026-03-29: Initial Project Docs

Added the first project-level documentation:

- product definition
- system architecture
- document safety model
- patch-first AI editing model
- phased production plan split into concrete sections

Primary file:

- [product-architecture.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/product-architecture.md)

Planning updates should keep landing in the architecture doc as the product brief evolves.

Recent planning additions:

- light/dark mode is now tracked as a later UI preference and polish item
- standard/Vim editor mode is now tracked as part of the editor experience

### 2026-03-29: Section 1 Scaffold

Built the first real project slice for Resume Document Core.

Implemented:

- monorepo-style repo layout with `apps/web`, `apps/api`, and `packages/shared`
- FastAPI backend for local dev auth, resume creation, resume listing, draft loading, and draft saving
- SQLite schema for `users`, `resumes`, and `working_drafts`
- starter LaTeX resume template
- Next.js frontend for:
  - resume list
  - create resume flow
  - raw LaTeX draft editor
  - save draft flow

### 2026-03-29: Section 1 Verification

Verified the backend flow end to end using FastAPI's test client.

Verified behaviors:

- health endpoint responds
- local dev user is returned
- resume list starts empty
- resume creation succeeds
- starter draft is created automatically
- draft save increments version
- stale draft save returns `409`

Also verified:

- frontend production build passes with `next build`

Environment note:

- the original backend dependency pins did not work with the only installed interpreter on this machine, Python 3.14
- backend requirements were updated to versions that install and run correctly under Python 3.14

## Current State

The repo currently contains:

- documentation for product architecture and production plan
- a verified Section 1 backend slice
- a frontend that builds successfully

The next planned milestone is Section 2:

- Monaco editor
- compile endpoint
- LaTeX compile loop
- PDF preview

### 2026-03-29: Section 2 Planning

Section 2 was broken into two controlled sub-slices:

- Sub-slice A: compile contract and workspace
- Sub-slice B: real TeX compile and PDF preview

Primary planning file:

- [section-2-editor-compile.md](/Users/mderaznasr/Documents/GitHub/ResumeOS/docs/section-2-editor-compile.md)

### 2026-03-29: Section 2A Compile Contract and Workspace

Implemented the first concrete compile slice without pretending the real TeX backend was finished.

Added:

- `compile_runs` persistence in the backend schema
- compile request and response DTOs
- `POST /resumes/{resume_id}/compile`
- backend compile contract validation for:
  - missing `\documentclass`
  - missing `\begin{document}`
  - missing `\end{document}`
  - unbalanced braces
- editor workspace layout with:
  - source pane
  - compile panel
  - compile logs
  - preview placeholder for Section 2B

Also fixed:

- draft dirty-state tracking now compares against the last saved draft instead of the initially loaded draft

Verified:

- compile success path returns a `success` result
- invalid source returns an `error` result with logs
- stale compile versions return `409`
- frontend production build passes after the workspace changes

### 2026-03-29: Section 2B Real Compile and PDF Preview

Implemented the real compile loop against the locally installed TeX toolchain.

Added:

- real `latexmk` subprocess execution
- temp-directory compile workflow
- compile timeout boundary
- local PDF artifact persistence
- `GET /resumes/{resume_id}/compile/latest.pdf`
- preview pane wiring to the generated PDF

Verified:

- starter resume compiles successfully
- latest PDF route returns a real PDF artifact
- broken LaTeX returns real compile failure logs
- frontend production build still passes

Open follow-up:

- Monaco is still the main remaining editor upgrade before Section 2 is fully complete

### 2026-03-29: Section 2C Monaco and Compile Tests

Closed out the remaining editor and verification work for Section 2.

Added:

- Monaco-based LaTeX editor component
- backend compile tests checked into the repo
- README command for running backend tests

Verified:

- backend compile success test passes
- backend compile failure test passes
- backend compile conflict test passes
- frontend production build passes with Monaco integrated

Section 2 outcome:

- ResumeOS now has a real LaTeX editing workspace, real compile loop, real PDF preview, and checked-in compile regression tests

### 2026-03-29: Local Run Command Fix

Found a concrete local-dev issue during live reproduction:

- the forwarded host/port command shape I used with `npm run dev:web -- ...` was wrong for this workspace setup

Added:

- `npm run dev:web:local`

This gives a reliable frontend start path on `127.0.0.1:3000` without relying on broken npm argument forwarding.

### 2026-03-29: App Router Error Boundary Hardening

After live reproduction, added explicit Next.js app-router error boundaries:

- `app/error.tsx`
- `app/global-error.tsx`

Reason:

- the browser was showing a missing required error components refresh loop
- explicit error boundaries give the app router the required fallback surface and prevent that failure mode from degrading into a blank page

### 2026-03-29: PDF Preview Header Fix

Found a real preview issue during live usage:

- the compiled PDF route worked, but the browser treated the PDF as a download instead of rendering it inline

Fix:

- changed the PDF file response to use `Content-Disposition: inline`

Verified:

- PDF route now returns `application/pdf`
- content disposition is `inline`

### 2026-03-29: Section 3 Snapshot Foundation

Started the first versioning and recovery slice on the dedicated feature branch.

Added:

- `snapshots` table
- backend snapshot DTOs and routes
- snapshot create/list/restore service layer
- frontend snapshot panel in the editor workspace
- backend snapshot tests

Verified:

- snapshot creation works from the current draft
- snapshot listing returns saved snapshots
- restoring a snapshot updates the working draft correctly
- backend tests pass
- frontend production build passes

### 2026-03-29: Section 3 Autosave

Added autosave behavior on top of the snapshot foundation.

Behavior:

- the working draft saves automatically after a short idle delay while typing
- manual save remains available as a fallback
- snapshot creation waits for the latest persisted draft before saving the snapshot

Verified:

- backend tests still pass
- frontend production build passes

### 2026-04-08: Section 4 First Review Mode

Expanded the protected-document workflow from single-block edit generation into the first multi-block review path.

Added:

- backend review suggestion route for the current resume draft
- provider contract support for multi-block review rewrites
- validation of generated review suggestions through the same exact block gate as edit mode
- backend regression test coverage for review suggestion generation
- frontend `Review Resume` action that loads generated review suggestions into the existing diff-style review surface

Verified:

- backend test suite passes with the new review suggestion flow
- frontend production build passes after wiring review generation into the editor workspace

### 2026-04-08: Section 4 First Tailor Mode

Expanded the same safe suggestion pipeline into the first tailoring flow.

Added:

- backend tailoring suggestion route that accepts a pasted job description
- provider contract support for job-description-guided rewrites across a small set of editable blocks
- validation of tailoring suggestions through the same exact block gate as edit and review mode
- backend regression test coverage for tailoring suggestion generation
- frontend `Tailor Resume` input and action that loads tailoring suggestions into the existing diff-style review surface

Verified:

- backend test suite passes with the new tailoring suggestion flow
- frontend production build passes after wiring tailoring generation into the editor workspace

### 2026-04-08: Section 4 Tailoring Safety Snapshot

Added the first safety behavior for tailoring so users do not lose the base draft while generating JD-focused suggestions.

Added:

- backend automatic snapshot creation before tailoring suggestions are generated
- backend regression coverage that verifies the tailoring flow creates a pre-tailor snapshot
- frontend snapshot panel refresh after tailoring so the new safeguard is visible immediately

Verified:

- backend test suite passes with the automatic snapshot behavior
- frontend production build passes with the snapshot refresh wiring

### 2026-04-08: Section 4 Tailoring Theme Grouping

Improved tailoring output organization so the review surface feels closer to the real product and less like raw per-block scaffolding.

Added:

- backend grouping of tailoring suggestion sets around coarse job-description themes such as backend/API, systems/infrastructure, and ownership/collaboration
- backend regression coverage that verifies theme-based grouping appears when the job description supports it

Verified:

- backend test suite passes with the new tailoring grouping behavior
- frontend production build still passes with the unchanged review surface

### 2026-04-08: Section 4 Suggestion Lifecycle Refinement

Made the suggestion subsystem more explicit and mode-aware instead of treating every suggestion set like the same generic scaffold.

Added:

- explicit suggestion mode metadata across mock, edit, review, and tailor suggestion sets
- backend regression checks for the new mode contract
- frontend mode badges and mode-aware regenerate labels
- frontend empty-state messaging for zero-result and fully dismissed suggestion flows
- frontend regenerate behavior that now actually replays edit, review, and tailor requests instead of only rotating mock sets

Verified:

- backend test suite passes with the mode-aware suggestion contract
- frontend production build passes with the new review surface behavior

### 2026-04-08: Section 4 Feedback Event Logging

Closed the first loop on the suggestion subsystem by persisting user outcomes instead of leaving them only in transient UI state.

Added:

- backend `feedback_events` persistence for suggestion apply and dismiss outcomes
- backend feedback logging route scoped to the current resume
- backend regression test coverage for feedback-event creation
- frontend apply and dismiss logging with suggestion mode, set id, proposal id, and target block id

Verified:

- backend test suite passes with feedback-event logging enabled
- frontend production build passes with the feedback calls wired into the review surface

### 2026-04-08: Section 4 SQLite Connection Hardening

Cleaned up a backend reliability issue that was showing up as a wall of SQLite resource warnings during repeated test runs.

Added:

- explicit database connection closing in the shared SQLite helper so existing service call sites do not leak connections

Verified:

- backend test suite still passes after the helper change
- the prior SQLite resource warning flood no longer appears in the test run
- frontend production build still passes

### 2026-03-29: Section 3 Snapshot Safety Polish

Improved the safety and clarity of destructive snapshot actions.

Added:

- restore confirmation before replacing the working draft
- visible success feedback after snapshot creation
- visible success feedback after snapshot restore

Verified:

- backend tests still pass
- frontend production build passes

### 2026-03-30: Section 3 Minimal Snapshot Compare

Added a lightweight comparison view so snapshots are not just restorable, but inspectable.

Added:

- lazy snapshot detail API for fetching a snapshot's saved source only when requested
- minimal line-based snapshot compare view against the current working draft
- backend regression test for fetching snapshot detail

Why this shape:

- compare is intentionally lightweight for now
- snapshot list payloads stay small because source text is fetched on demand
- the goal was clarity and version history usefulness, not a full IDE diff product yet

Verified:

- backend tests still pass
- frontend production build passes

### 2026-03-30: Section 3 Snapshot Metadata Polish

Closed out the snapshot slice with a small UX cleanup instead of letting the panel accumulate avoidable friction.

Added:

- sensible default snapshot naming (`Snapshot N`)
- automatic reset to the next default name after creating a snapshot
- clearer panel metadata showing saved snapshot count
- a small `Latest` badge on the newest snapshot

Verified:

- backend tests still pass
- frontend production build passes

### 2026-03-30: Section 4 Protected Document Model Foundation

Started the next major feature area by making the resume structure explicit instead of treating the LaTeX source as an undifferentiated text blob.

Added:

- documented protected-vs-editable contract for the first heuristic document model
- backend document-model DTOs
- backend extraction service for protected regions and editable blocks
- `GET /resumes/{resume_id}/document-model`
- backend tests covering protected preamble/scaffold detection and editable summary/bullet extraction
- editor-side document model panel showing the extracted boundary

Why this shape:

- this is a concrete safety foundation for later AI patch validation
- the parser is intentionally conservative and biases ambiguous lines toward protected
- the feature is visible in the product instead of being invisible backend plumbing

Verified:

- backend tests still pass
- frontend production build passes

### 2026-03-30: Section 4 Exact Patch Validation Gate

Built the first real acceptance gate that future AI patch proposals will need to pass.

Added:

- documented v1 patch-validation contract
- backend patch-validation DTOs
- `POST /resumes/{resume_id}/patches/validate`
- strict server-side validation that only accepts edits targeting one current editable block exactly
- backend tests covering valid, stale, and unknown-target cases

Why this shape:

- it creates a trustworthy backend gate before any generated patches exist
- it keeps the first validator easy to reason about
- it forces later patch flows to anchor themselves to the extracted document model instead of raw freeform text edits

Verified:

- backend tests still pass
- frontend production build passes

### 2026-03-30: Preview Layout Restoration

After the Section 4 panels were added, the PDF preview was pushed too far down the right-hand column and stopped feeling like a first-class part of the editor workspace.

Fix:

- restored compile status, preview, and logs ahead of the newer document-model and snapshot panels in the right-hand layout

Verified:

- backend tests still pass
- frontend production build passes

### 2026-03-30: Section 4 Mocked Patch Flow

Added the first end-to-end patch review exercise without introducing a model yet.

Added:

- documented mocked patch proposal contract
- backend DTOs for mocked patch proposals
- `GET /resumes/{resume_id}/patches/mock`
- deterministic backend proposal generation from editable blocks
- backend self-validation of each mocked proposal through the exact patch gate
- backend tests for mocked proposal generation
- minimal frontend review cards for mocked before/after proposals

Why this shape:

- it proves the future AI patch path end to end
- it keeps proposal generation deterministic and easy to debug
- it exercises the real validation boundary instead of bypassing it

Verified:

- backend tests still pass
- frontend production build passes

### 2026-04-08: Section 4 Mock Patch Apply Mechanics

Turned the mocked patch cards from a static review surface into a real working-draft update path.

Added:

- documented first patch-apply contract
- backend patch-apply DTO and route
- strict backend apply logic that re-validates the target block before persisting
- backend tests for valid and stale patch apply cases
- frontend `Apply` and `Dismiss` controls on mocked patch cards

Why this shape:

- it proves that patch review can mutate the working draft safely
- it keeps the source of truth on the backend instead of attempting risky client-side text surgery
- it uses the same strict block-based validation gate as the mocked proposal flow

Verified:

- backend tests still pass
- frontend production build passes

### 2026-04-08: Section 4 Grouped Suggestion Sets

Moved the mocked review flow closer to the eventual AI UX by grouping related patches into coherent suggestion sets.

Added:

- documented grouped suggestion-set contract
- backend grouped suggestion-set DTOs
- grouped mocked suggestion generation instead of a flat patch list
- simple retry/regenerate behavior driven by a deterministic seed
- grouped review UI with set-level retry

Why this shape:

- the eventual AI UX should present coherent edit passes, not unrelated isolated cards
- retry behavior now exists at the set level, which maps better to future model-generated suggestion batches
- the flow is still deterministic and still uses the same strict validation boundary

Verified:

- backend tests still pass
- frontend production build passes

### 2026-04-08: Section 4 Diff-Centric Suggestion Review

Refined the grouped suggestion workflow so it reads more like the final product and less like scaffolding.

Added:

- clearer suggestion metadata such as operation and validation status
- renamed the review surface around suggestions rather than mock patches
- diff-centric hunk presentation with explicit removed and added lines
- preserved apply, dismiss, and regenerate behavior in the refined UI

Why this shape:

- the safety core was already in place, so the leverage here was making the workflow read like a real review system
- this brings the product closer to the eventual AI editing UX without introducing model variability yet

Verified:

- backend tests still pass
- frontend production build passes

### 2026-04-08: Section 4 First Generated Edit Suggestions

Added the first real generation path on top of the existing safety and review system.

Added:

- LLM provider abstraction for block-level edit generation
- default mock provider plus an OpenAI-backed provider path behind configuration
- backend edit suggestion endpoint for one selected editable block
- validation of generated candidates through the same patch gate used elsewhere
- per-block `Suggest Edit` action in the document model panel

Why this shape:

- it introduces real generation at the narrowest safe scope
- it reuses the same review/apply system instead of inventing a second path
- it keeps testing stable by defaulting to a deterministic provider when not configured otherwise

Verified:

- backend tests still pass
- frontend production build passes

### 2026-04-08: User-Directed Edit Prompts

Made the first generated edit flow user-directed instead of relying on one canned instruction.

Added:

- per-block prompt input in the document model panel
- `Suggest Edit` now uses the user-provided instruction for that block
- README guidance for switching from the default mock provider to the OpenAI-backed provider

Why this shape:

- it makes the block-level generation path materially more useful without changing the underlying safety model
- it keeps the UI control close to the specific editable block being targeted

Verified:

- backend tests still pass
- frontend production build passes

## Open Notes

- local dev persistence is SQLite for now
- PostgreSQL is still the intended longer-term primary database
- browser-level local dev serving could not be fully exercised in the sandbox because port binding was restricted
