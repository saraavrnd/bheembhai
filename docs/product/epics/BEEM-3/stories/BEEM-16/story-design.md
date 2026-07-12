# Story Design — BEEM-16: Bootstrap initial platform admin

**Status:** UPDATED · **Epic:** BEEM-3 · **Date:** 2026-07-11
**Domain:** backend

> Thin design note. Review and approve before test-creator writes tests. Change anything; I'll
> realign and re-confirm.

## Target module(s)
- `app/cli/admin_handler.py` for the explicit bootstrap command.
- `app/auth/service.py` for the bootstrap orchestration and user lifecycle logic.
- `app/auth/repository.py` for the Postgres-backed user persistence and transaction scope.
- `app/notifications/email.py` for the activation email delivery boundary.
- `app/core/settings.py` for runtime configuration used by the auth and email services.

## Interfaces / endpoints
| Kind | Signature | Request → Response |
|------|-----------|--------------------|
| CLI | `beembhai-admin bootstrap-admin --email <email> --password <password>` | explicit bootstrap credentials → seeded admin or idempotent skip |
| service | `AuthService.bootstrap_platform_admin(email: str, password: str) -> UserMutationResult` | bootstrap inputs + persistence/email adapters → created admin, skip, or error with rollback |
| repository | `SqlAlchemyUserRepository.session_scope()` and session-scoped create/update helpers | transactional persistence boundary → commit only after the email send succeeds |

No new public API endpoint is required for this story.

## Data-model deltas
None. The existing `User.platform_role` field already supports a platform-admin value, and the password remains stored as a hash.

## Reuse
- Existing `User` identity model and auth flow contract in `docs/api-contracts/beembhai-api.openapi.yaml`.
- Existing `Settings` loader in `app/core/settings.py`.
- Existing email verification token flow in `app/auth/tokens.py`.
- Existing email delivery adapter shape in `app/notifications/email.py`.

## Approach
Run bootstrap as a thin CLI wrapper over the shared auth service. The command accepts explicit bootstrap credentials instead of reading them from environment variables. The auth service uses the Postgres-backed repository to check for an existing platform admin and create the first one only if none exists. The user row is created inside a transaction, a verification token is generated, and the activation email is sent before the commit. If email delivery fails, the transaction is rolled back so a retry can safely bootstrap again. If the admin already exists, bootstrap is idempotent and returns a skip result even when a different email/password is supplied later.

## Test surface
- [x] Unit: bootstrap service behavior, idempotency, and rollback on email failure.
- [x] Unit: CLI argument enforcement and delegation into the auth service.
- [ ] Integration: Postgres-backed bootstrap persistence and retry behavior.
- [ ] E2E: browser verification flow for the activation link is owned by the shared auth story, not this bootstrap story.

## Out of scope
Creating non-admin users, password reset, project creation, workflow-policy assignment, and project-role management. The browser-facing email verification page is part of the shared auth story, not the bootstrap story.

## Architecture impact
None — fits existing architecture.

## Dependencies discovered (feeds epic-sequence)
- Consumes: explicit CLI bootstrap credentials, Postgres-backed auth persistence, the shared email delivery boundary, and the shared auth sign-in/verification flow from `BEEM-14`.
- Produces: the first platform admin account, which `BEEM-12`, `BEEM-13`, and `BEEM-15` consume.
- Effect on sequence: changes provisional order by making `BEEM-16` the prerequisite story for the admin-dependent access stories.

## Bootstrap rule
- The first successful bootstrap creates exactly one platform admin account.
- Relaunching the bootstrap command with a different email or password must not create an additional admin user once one already exists.
- The configured bootstrap credentials are only used when no seeded admin exists yet.
- If email delivery fails before commit, no admin row is left behind and the bootstrap can be retried safely.
- Bootstrap credentials are passed explicitly to the CLI; they are not loaded from `BEEMBHAI_BOOTSTRAP_ADMIN_*` environment variables.

## Traceability
**Requirements covered:** FR-005

---
*On approval: next step is `test-creator` (failing tests from these interfaces + the story's acceptance criteria), then `implement`.*
