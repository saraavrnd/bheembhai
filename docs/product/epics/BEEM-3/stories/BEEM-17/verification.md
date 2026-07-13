# Verification — BEEM-17: Register a local user account

**Verdict:** PASS · **Branch:** `feat/BEEM-16-bootstrap-initial-platform-admin` · **Date:** 2026-07-13

## Suite, lint, coverage
### Commands
- `uv run pytest -vv`
- `uv run ruff check .`

### Test suite output
```text
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.1, asyncio-1.4.0, playwright-0.8.0, base-url-2.1.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 37 items

tests/e2e/test_home_page.py::test_home_page_renders[chromium] PASSED     [  2%]
tests/integration/auth/test_register.py::test_register_endpoint_creates_user_and_returns_user_shape PASSED [  5%]
tests/integration/auth/test_register.py::test_register_endpoint_rejects_invalid_input PASSED [  8%]
tests/integration/main/test_bootstrap_startup.py::test_app_startup_serves_health_without_bootstrapping_admin PASSED [ 11%]
tests/integration/main/test_health.py::test_health_endpoint_returns_ok PASSED [ 13%]
tests/unit/auth/test_service.py::test_bootstrap_creates_first_platform_admin_and_sends_activation_email PASSED [ 16%]
tests/unit/auth/test_service.py::test_bootstrap_is_idempotent_when_admin_already_exists PASSED [ 19%]
tests/unit/auth/test_service.py::test_bootstrap_rolls_back_when_verification_email_delivery_fails PASSED [ 22%]
tests/unit/auth/test_service.py::test_upsert_user_updates_existing_record_without_duplicate PASSED [ 25%]
tests/unit/auth/test_service.py::test_register_user_creates_standard_user_and_sends_verification_email PASSED [ 27%]
tests/unit/auth/test_service.py::test_register_user_rejects_duplicate_email_without_creating_duplicate_user PASSED [ 30%]
tests/unit/auth/test_service.py::test_email_verification_request_and_confirmation_activate_user PASSED [ 33%]
tests/unit/auth/test_service.py::test_password_reset_request_and_confirmation_update_password PASSED [ 36%]
tests/unit/auth/test_service.py::test_invalid_verification_token_is_rejected PASSED [ 38%]
tests/unit/cli/test_admin_handler.py::test_bootstrap_admin_requires_email_and_password PASSED [ 41%]
tests/unit/cli/test_admin_handler.py::test_bootstrap_admin_delegates_to_service PASSED [ 44%]
tests/unit/cli/test_admin_handler.py::test_upsert_user_uses_the_explicit_role PASSED [ 47%]
tests/unit/core/test_settings.py::test_default_settings_use_repo_name PASSED [ 50%]
tests/unit/core/test_settings.py::test_auth_and_email_settings_are_loaded_from_env PASSED [ 52%]
tests/unit/core/test_settings.py::test_email_brevo_legacy_names_are_supported PASSED [ 55%]
tests/unit/main/test_main.py::test_app_factory_registers_versioned_api_routes PASSED [ 58%]
tests/unit/notifications/test_brevo_email.py::test_brevo_email_sender_posts_expected_payload PASSED [ 61%]
tests/unit/notifications/test_brevo_email.py::test_brevo_email_sender_raises_on_http_error PASSED [ 63%]
tests/unit/secure_storage/test_encryption.py::test_envelope_cipher_round_trip PASSED [ 66%]
tests/unit/secure_storage/test_minio_service.py::test_minio_secure_storage_encrypts_before_persisting PASSED [ 69%]
tests/unit/tooling/test_run_ledger.py::test_record_appends_a_jsonl_event_and_generates_run_id PASSED [ 72%]
tests/unit/tooling/test_run_ledger.py::test_latest_finds_the_most_recent_matching_run PASSED [ 75%]
tests/unit/tooling/test_run_ledger.py::test_preview_summarises_changed_files_commits_and_actions PASSED [ 77%]
tests/unit/tooling/test_run_ledger.py::test_hook_appends_a_post_tool_use_event_from_stdin PASSED [ 80%]
tests/unit/web/test_verify_email.py::test_create_app_builds_browser_auth_service_once PASSED [ 83%]
tests/unit/web/test_verify_email.py::test_verify_email_page_mentions_fragment_handshake PASSED [ 86%]
tests/unit/web/test_verify_email.py::test_verify_email_submit_confirms_valid_token PASSED [ 88%]
tests/unit/web/test_verify_email.py::test_verify_email_submit_shows_failure_for_invalid_token PASSED [ 91%]
tests/unit/web/test_verify_email.py::test_reset_password_page_mentions_fragment_handshake PASSED [ 94%]
tests/unit/web/test_verify_email.py::test_reset_password_submit_confirms_new_password PASSED [ 97%]
tests/unit/web/test_verify_email.py::test_reset_password_submit_shows_failure_for_invalid_token PASSED [100%]

=============================== warnings summary ===============================
app/main.py:58: 1 warning
tests/integration/auth/test_register.py: 2 warnings
tests/integration/main/test_bootstrap_startup.py: 1 warning
tests/integration/main/test_health.py: 1 warning
tests/unit/main/test_main.py: 1 warning
tests/unit/web/test_verify_email.py: 7 warnings
  /home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/app/main.py:58: DeprecationWarning:
          on_event is deprecated, use lifespan event handlers instead.

    @app.on_event("startup")

.venv/lib/python3.13/site-packages/fastapi/applications.py:4675: 1 warning
tests/integration/auth/test_register.py: 2 warnings
tests/integration/main/test_bootstrap_startup.py: 1 warning
tests/integration/main/test_health.py: 1 warning
tests/unit/main/test_main.py: 1 warning
tests/unit/web/test_verify_email.py: 7 warnings
  /home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/.venv/lib/python3.13/site-packages/fastapi/applications.py:4675: DeprecationWarning:
          on_event is deprecated, use lifespan event handlers instead.

    return self.router.on_event(event_type)  # ty: ignore[deprecated]

.venv/lib/python3.13/site-packages/fastapi/testclient.py:1
  /home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/.venv/lib/python3.13/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 37 passed, 53 warnings in 1.92s ========================
```
- [x] Full test suite green
- [x] Lint clean
- [x] Coverage gate met (N/A - no dedicated coverage command is defined in the repo tooling)

### Lint output
```text
All checks passed!
```

### Coverage output
```text
N/A - no dedicated coverage command is defined in the repo tooling.
```

## Acceptance-scenario coverage
| Scenario | Test exists & runs | Unhappy path |
|----------|--------------------|--------------|
| New user registration creates an account | yes, [tests/unit/auth/test_service.py](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/tests/unit/auth/test_service.py) `test_register_user_creates_standard_user_and_sends_verification_email`, [tests/integration/auth/test_register.py](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/tests/integration/auth/test_register.py) `test_register_endpoint_creates_user_and_returns_user_shape` | yes |
| Registration sends a verification email | yes, [tests/unit/auth/test_service.py](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/tests/unit/auth/test_service.py) `test_register_user_creates_standard_user_and_sends_verification_email` | no |
| Duplicate email registration is rejected | yes, [tests/unit/auth/test_service.py](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/tests/unit/auth/test_service.py) `test_register_user_rejects_duplicate_email_without_creating_duplicate_user`, `test_register_user_translates_racing_duplicate_into_conflict` | yes |
| Invalid registration input is rejected | yes, [tests/integration/auth/test_register.py](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/tests/integration/auth/test_register.py) `test_register_endpoint_rejects_invalid_input` | yes |
- [x] Every scenario covered by a real, running test
- [x] Unhappy paths present

## Faked-green inspection
- [x] No tests skipped/xfail/disabled/deleted vs the test-plan
- [x] No assertions loosened or removed vs acceptance criteria
- [x] No production special-casing of test inputs
- [x] No swallowed errors hiding unhappy-path behaviour

## Regression & design
- [x] Pre-existing suite still passes
- [x] Code landed in `app/auth/service.py`, `app/auth/router.py`, `app/main.py`, `tests/conftest.py`, `tests/e2e/conftest.py`, `tests/unit/auth/test_service.py`, `tests/integration/auth/test_register.py`, and `tests/unit/core/test_settings.py`; no unplanned architecture change

## If BLOCK — issues to fix
(n/a — PASS)

---
*PASS → next is `pr-create`. BLOCK → fix in the owning step, then re-run `test-verify`.*
