# Story Design — BEEM-17: Register a local user account

**Status:** AWAITING APPROVAL · **Epic:** BEEM-3 · **Date:** 2026-07-12
**Domain:** backend

> Thin design note. Review and approve before test-creator writes tests. Change anything;
> I'll realign and re-confirm.

## Target module(s)
- `app/auth/router.py` for the `/auth/register` HTTP route.
- `app/auth/service.py` for registration orchestration, duplicate detection, and verification-email delivery.
- `app/auth/repository.py` for user lookup and transactional persistence.
- `app/notifications/email.py` for the existing email delivery boundary.
- `docs/api-contracts/beembhai-api.openapi.yaml` as the contract the route should satisfy.

## Interfaces / endpoints
| Kind | Signature | Request → Response |
|------|-----------|--------------------|
| API | `POST /api/v1/auth/register` | `RegisterRequest { email, password }` → `201 User`; `409 Conflict` when the email already exists |
| service | `AuthService.register_user(email: str, password: str) -> UserMutationResult` | normalized email + password → created standard user, verification email sent, or duplicate-email rejection |
| repository | `SqlAlchemyUserRepository.find_by_email_in_session(session, email)` / `create_user_in_session(session, *, email, password_hash, platform_role, email_verified_at)` | duplicate check + persisted `users` row |

## Data-model deltas
None. The existing `app.auth.repository.User` table already stores the needed state:
`email`, `password_hash`, `platform_role`, and `email_verified_at`.

## Reuse
- Existing `SqlAlchemyUserRepository` persistence and `UserRecord` model.
- Existing `AuthTokenService.create_email_verification_token(...)`.
- Existing `EmailSender` / `BrevoEmailSender` abstraction and verification-email template logic in `AuthService`.
- Existing API contract schemas: `RegisterRequest` and `User`.
- Existing `PasswordHasher` wiring from `build_auth_service(...)`.

## Approach
Add a dedicated `register_user` service method that normalizes the email, looks up any existing user in the same transactional session, and rejects duplicates before creating a new standard user row. The new row should be persisted with `email_verified_at=None`, then the service should generate a verification token and send the activation email before the transaction commits so a delivery failure rolls back the user creation. Add the `/auth/register` route in `app/auth/router.py` to validate the request payload, call the service, and serialize the created `UserRecord` to the API contract shape (`platformRole=STANDARD`, `emailVerifiedAt=null`).

## Test surface
- [x] Unit: duplicate-email rejection, user creation, and verification-email delivery in `AuthService`.
- [x] Integration: `POST /api/v1/auth/register` persists a real row in `users` and returns `201`.
- [ ] E2E: not needed; this story is backend-only and the browser verification page is covered by `BEEM-14`.

## Out of scope
Email verification activation, sign in, password reset, MFA, SSO, social login, invite-only or admin-only provisioning models, and bootstrap admin creation.

## Architecture impact
None — fits existing architecture.

## Dependencies discovered (feeds epic-sequence)
- Consumes: the existing email delivery boundary from the integrations epic.
- Produces: a standard, unverified `users` row that `BEEM-14` consumes for email verification, sign-in, and password reset.
- Effect on sequence: matches the provisional order; this story is the prerequisite for `BEEM-14` and remains wave 1.

## Traceability
**Requirements covered:** FR-005

---
*On approval: next step is `test-creator` (failing tests from these interfaces + the story's acceptance criteria), then `implement`.*
