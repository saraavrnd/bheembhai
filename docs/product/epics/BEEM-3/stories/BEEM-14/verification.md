# Verification — BEEM-14: Sign in, verify email, and reset password

**Verdict:** PASS · **Branch:** `feat/BEEM-14-sign-in-verify-reset-password` · **Date:** 2026-07-13

## Suite, lint, coverage
### Commands
- `uv run pytest -q`
- `uv run ruff check app tests`

### Test suite output
```text
55 passed, 65 warnings in 43.08s
```

### Lint output
```text
All checks passed!
```

### Coverage output
Not run. The repository does not define a dedicated coverage gate for this story.

## Acceptance-scenario coverage
| Scenario | Test exists & runs | Unhappy path |
|----------|--------------------|--------------|
| Unverified user cannot sign in | yes, `tests/unit/auth/test_service.py::test_authenticate_user_rejects_unverified_users`, `tests/unit/web/test_login.py::test_login_submit_shows_unverified_account_error`, `tests/integration/auth/test_auth_login.py::test_login_endpoint_rejects_unverified_user` | yes |
| Verified user can sign in | yes, `tests/unit/auth/test_service.py::test_authenticate_user_returns_verified_user_for_valid_credentials`, `tests/unit/web/test_login.py::test_login_submit_sets_session_cookie_and_success_state`, `tests/integration/auth/test_auth_login.py::test_login_endpoint_sets_session_and_me_returns_current_user`, `tests/e2e/test_login_page.py::test_login_page_signs_verified_user_in` | yes |
| Verification link activates the account | yes, `tests/unit/web/test_verify_email.py::test_verify_email_submit_confirms_valid_token`, `tests/integration/auth/test_auth_login.py::test_login_endpoint_sets_session_and_me_returns_current_user` | yes |
| Password reset link is issued | yes, `tests/unit/auth/test_service.py::test_password_reset_request_and_confirmation_update_password`, `tests/integration/auth/test_auth_login.py::test_password_reset_flow_updates_password_and_rejects_old_password` | yes |
| Password reset sets a new password | yes, `tests/unit/auth/test_service.py::test_password_reset_request_and_confirmation_update_password`, `tests/integration/auth/test_auth_login.py::test_password_reset_flow_updates_password_and_rejects_old_password` | yes |
| Invalid or expired reset link is rejected | yes, `tests/unit/web/test_verify_email.py::test_reset_password_submit_shows_failure_for_invalid_token` | yes |
- [x] Every scenario covered by a real, running test
- [x] Unhappy paths present

## Faked-green inspection
- [x] No tests skipped/xfail/disabled/deleted vs the test-plan
- [x] No assertions loosened or removed vs acceptance criteria
- [x] No production special-casing of test inputs
- [x] No swallowed errors hiding unhappy-path behaviour

## Regression & design
- [x] Pre-existing suite still passes
- [x] Code stayed within the approved auth/web/session seams from the story design

## Notes
- The compose-based integration stack was updated to rebuild the API image during test startup so the deployed-stack checks always exercise the current branch.

## If BLOCK — issues to fix
(n/a — PASS)

---
*PASS → next is `code-review`. BLOCK → fix in the owning step, then re-run `test-verify`.*
