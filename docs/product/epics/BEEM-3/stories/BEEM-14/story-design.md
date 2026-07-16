# Story Design — BEEM-14: Sign in, verify email, and reset password

**Status:** AWAITING APPROVAL · **Epic:** BEEM-3 · **Date:** 2026-07-13
**Domain:** full-stack

> Thin design note. Review and approve before test-creator writes tests. Change anything;
> I'll realign and re-confirm.

## Target module(s)
- `app/auth/router.py` for login, logout, email verification, password-reset, and `me` API routes.
- `app/auth/service.py` for credential validation plus the shared verification and password-reset flows.
- `app/auth/repository.py` for user lookup and password-hash persistence against Postgres.
- `app/auth/tokens.py` for the stateless verification and reset token format already used by email links.
- `app/web/router.py` for the browser sign-in page and the existing verify/reset page wiring.
- `app/web/templates/auth/login.html` for the new browser sign-in page.
- `app/web/templates/auth/verify_email.html` and `app/web/templates/auth/reset_password.html` for the existing browser recovery pages.
- `app/main.py` only if a small session-cookie wiring change is required to expose the authenticated session.

## Interfaces / endpoints
| Kind | Signature | Request → Response |
|------|-----------|--------------------|
| API | `POST /api/v1/auth/login` | `{ email, password }` → `200 SessionResponse` and an authenticated `bb_session` cookie on success |
| API | `POST /api/v1/auth/logout` | signed-in request → `204` and cleared session cookie |
| API | `POST /api/v1/auth/email/verify` | `{ token }` → `204` on success, `400/401` on invalid or expired token |
| API | `POST /api/v1/auth/password-reset/request` | `{ email }` → `204` after a reset email is queued when eligible |
| API | `POST /api/v1/auth/password-reset/confirm` | `{ token, newPassword }` → `204` when the password is updated |
| API | `GET /api/v1/me` | authenticated request → `200 MeResponse` with the current user |
| page | `GET /login` | visitor request → browser sign-in form |
| page | `POST /login` | browser form submission → success state or inline validation / credential / verification error |
| page | `GET /verify-email` / `POST /verify-email` | email-link landing page → account activation or invalid-link state |
| page | `GET /reset-password` / `POST /reset-password` | email-link landing page → password update or invalid-link state |
| service | `AuthService.authenticate_user(email: str, password: str) -> UserRecord` | normalized login inputs → verified user on success, error on invalid credentials or unverified account |

## Data-model deltas
None. The durable source of truth remains the Postgres `users` table; this story reads and updates the existing `email`, `password_hash`, and `email_verified_at` fields. The authenticated browser session can be represented by the HTTP session cookie without introducing a new persisted entity in this story.

## Reuse
- Existing `SqlAlchemyUserRepository` lookup and update helpers.
- Existing `AuthTokenService` token parsing and issuance for verification and reset links.
- Existing `AuthService.request_email_verification(...)`, `confirm_email_verification(...)`, `request_password_reset(...)`, and `confirm_password_reset(...)` methods.
- Existing browser auth-card styling in `app/web/static/css/theme.css`.
- Existing recovery page fragment-handshake patterns in `app/web/templates/auth/verify_email.html` and `app/web/templates/auth/reset_password.html`.
- Existing auth contract shapes in `docs/api-contracts/beembhai-api.openapi.yaml`.

## Approach
Add a shared login method in the auth service that normalizes the email, looks up the user from Postgres, verifies the Argon2 password hash, and rejects unverified accounts before the router sets any authenticated session state. Expose that through the JSON login route and the browser `/login` page so both clients use the same credential checks. Reuse the existing token service and repository-backed account state for the email-verification and password-reset routes, which keeps verification and recovery aligned with the current `users` table instead of introducing a parallel local shim. The browser pages stay thin: sign-in submits credentials, verification and reset keep their token-from-fragment behavior, and each success state clearly points the user back to a signed-in session or the next recovery step.

## Test surface
- [x] Unit: login success/failure, unverified-account rejection, and existing verification/reset service behavior.
- [x] Integration: API login/logout, email verification, password-reset request/confirm, and `me` session behavior.
- [x] E2E: browser sign-in page render plus a successful sign-in or recovery path.

## Out of scope
MFA, SSO, social login, invite-only provisioning, project-role management, and any server-side session revocation model beyond the MVP cookie/session seam.

## Architecture impact
None. This fits the current modular-monolith auth boundary and uses the existing Postgres-backed user record as the system of record.

## Dependencies discovered (feeds epic-sequence)
- Consumes: `BEEM-17` registration, the existing verification-email plumbing, and the `users` table state that marks an account verified or unverified.
- Produces: the authenticated session and recovery flows that `BEEM-16` and later admin/project stories rely on.
- Effect on sequence: remains after `BEEM-17` and before the admin-dependent stories that require a real sign-in path.

## Traceability
**Requirements covered:** FR-005

---
*On approval: next step is `test-creator` (failing tests from these interfaces + the story's
acceptance criteria), then `implement`.*
