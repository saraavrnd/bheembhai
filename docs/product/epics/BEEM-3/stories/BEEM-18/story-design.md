# Story Design — BEEM-18: Add browser signup page

**Status:** AWAITING APPROVAL · **Epic:** BEEM-3 · **Date:** 2026-07-13
**Domain:** full-stack

> Thin design note. Review and approve before test-creator writes tests. Change anything;
> I'll realign and re-confirm.

## Target module(s)
- `app/web/router.py` for the browser-facing signup page and form submission handling.
- `app/web/templates/auth/signup.html` for the new signup page template.
- `app/auth/router.py` for the JSON registration endpoint used by the browser flow and API clients.
- `app/auth/service.py` for the shared registration logic, duplicate-email rejection, and verification email trigger.

## Interfaces / endpoints
| Kind | Signature | Request → Response |
|------|-----------|--------------------|
| page | `GET /signup` | visitor request → signup form with email/password fields and submit action |
| page | `POST /signup` | form submission → success state or inline validation / duplicate-email error |
| API | `POST /api/v1/auth/register` | `RegisterRequest` JSON → `201` with `User` on success, `409` on duplicate email |
| service | `AuthService.register_user(email: str, password: str) -> UserMutationResult` | normalized registration inputs → created user + verification email, or duplicate rejection |

## Data-model deltas
None. The existing `User` entity already covers email, password hash, and unverified state.

## Reuse
- Existing `User` repository and verification-email flow in `app/auth/service.py`.
- Existing email delivery adapter in `app/notifications/email.py`.
- Existing auth contract in `docs/api-contracts/beembhai-api.openapi.yaml`.
- Existing browser auth card styling and status-pill patterns in `app/web/templates/auth/verify_email.html`, `app/web/templates/auth/reset_password.html`, and `app/web/static/css/theme.css`.

## Approach
Add a shared registration method to the auth service that normalizes email, rejects duplicate addresses, hashes the password, creates the user, and sends the verification email. Expose that service through the JSON auth register route so the browser page stays thin and does not re-implement registration rules. The browser `/signup` page renders the form, posts the submitted values back to the server, and maps validation or duplicate-email failures into a clear error state while the success state points the visitor to verify their email. Keep the UI consistent with the existing auth pages by reusing the same card layout, status pill, and semantic form structure.

## Test surface
- [x] Unit:
- [x] Integration:
- [ ] E2E:

## Out of scope
Sign in, email verification activation, password reset, MFA, SSO, social login, invite-only provisioning, and admin-only provisioning.

## Architecture impact
None — fits existing architecture.

## Dependencies discovered (feeds epic-sequence)
- Consumes: `BEEM-17` registration behavior and verification-email flow, plus the documented `POST /auth/register` contract.
- Produces: a browser signup entry point that reuses the shared registration flow.
- Effect on sequence: matches the provisional order; `BEEM-17` remains the prerequisite.

## Traceability
**Requirements covered:** FR-005

---
*On approval: next step is `test-creator` (failing tests from these interfaces + the story's
acceptance criteria), then `implement`.*
