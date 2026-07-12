# Test Plan — BEEM-16: Bootstrap initial platform admin

**Epic:** BEEM-3 · **Date:** 2026-07-11 · **Runners:** pytest (unit + integration)

## Scenario → test mapping
Every Gherkin scenario must map to at least one test.

| # | Acceptance scenario | Layer | Test file::test name | Type |
|---|---------------------|-------|----------------------|------|
| 1 | Bootstrap creates the first admin user | unit | `tests/unit/auth/test_service.py::test_bootstrap_creates_first_platform_admin_and_sends_activation_email` | happy |
| 2 | Bootstrapped admin can sign in | dependency | `docs/product/epics/BEEM-3/_epic/stories.md` / BEEM-14 auth story | covered elsewhere |
| 3 | Bootstrap is idempotent | unit | `tests/unit/auth/test_service.py::test_bootstrap_is_idempotent_when_admin_already_exists` | happy |
| 4 | Bootstrap rolls back when email delivery fails | unit | `tests/unit/auth/test_service.py::test_bootstrap_rolls_back_when_verification_email_delivery_fails` | unhappy |
| 5 | Bootstrap CLI requires explicit credentials | unit | `tests/unit/cli/test_admin_handler.py::test_bootstrap_admin_requires_email_and_password` | unhappy |
| 6 | Bootstrap CLI delegates into the auth service | unit | `tests/unit/cli/test_admin_handler.py::test_bootstrap_admin_delegates_to_service` | happy |

## Coverage check
- [x] Every bootstrap-specific acceptance scenario has at least one test.
- [x] The sign-in outcome is covered by the shared auth story (`BEEM-14`).
- [x] Unhappy paths covered (invalid input, boundary, permissions where relevant).
- [x] Tests target the interfaces from the approved story-design note.

## Red-phase verification
```
3 failed, 3 passed

Failures are the intended red:
- `app.cli.admin_handler` does not yet enforce explicit bootstrap credentials.
- `app.auth.service` does not yet keep the bootstrap flow transaction-safe on email failure.
- `app.auth.repository` does not yet support session-scoped persistence helpers.
```

## Traceability
**Requirements covered:** FR-005

---
*Next: `implement` makes these tests pass without weakening them.*
