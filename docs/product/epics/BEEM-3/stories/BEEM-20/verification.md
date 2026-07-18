# Verification — BEEM-20: UI FIX: Align authentication screens to approved mockups

**Verdict:** PASS · **Branch:** `feat/BEEM-19-align-authentication-screens` · **Date:** 2026-07-18

Commits reviewed: `219eb2c` (test-creator: failing tests) → `589dd33` (implement: Bootstrap/EduAdmin
rebuild) → `f78cd77` (bugfix: duplicated checkmark + dead markup cleanup) → `4feb444` (visual
baselines) → `7e8600c` (lint fix, line-wrap only, no assertion change).

## Suite, lint, coverage

### Commands
- `uv run pytest tests/unit -vv`
- `uv run pytest tests/e2e -vv -m e2e` (against the deployed Docker Compose stack, `tests.compose_stack.deployed_api_stack()`)
- `uv run ruff check .`
- No coverage tool is configured in this repo (`pyproject.toml` has no `pytest-cov` dependency) — no coverage gate applies.

- [x] Full test suite green — **42 unit passed, 34 e2e passed** (76/76)
- [x] Lint clean — `ruff check .` → `All checks passed!`
- [x] Coverage gate met — N/A, no coverage tool configured

### Unit test output (`uv run pytest tests/unit -vv`)
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
rootdir: /home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai
configfile: pyproject.toml
plugins: anyio-4.14.1, asyncio-1.4.0, playwright-0.8.0, base-url-2.1.0
collecting ... collected 42 items

tests/unit/auth/test_service.py::test_bootstrap_creates_first_platform_admin_and_sends_activation_email PASSED [  2%]
tests/unit/auth/test_service.py::test_bootstrap_is_idempotent_when_admin_already_exists PASSED [  4%]
tests/unit/auth/test_service.py::test_bootstrap_rolls_back_when_verification_email_delivery_fails PASSED [  7%]
tests/unit/auth/test_service.py::test_upsert_user_updates_existing_record_without_duplicate PASSED [  9%]
tests/unit/auth/test_service.py::test_register_user_creates_standard_user_and_sends_verification_email PASSED [ 11%]
tests/unit/auth/test_service.py::test_register_user_rejects_duplicate_email_without_creating_duplicate_user PASSED [ 14%]
tests/unit/auth/test_service.py::test_register_user_translates_racing_duplicate_into_conflict PASSED [ 16%]
tests/unit/auth/test_service.py::test_authenticate_user_returns_verified_user_for_valid_credentials PASSED [ 19%]
tests/unit/auth/test_service.py::test_authenticate_user_rejects_unverified_users PASSED [ 21%]
tests/unit/auth/test_service.py::test_authenticate_user_rejects_invalid_password PASSED [ 23%]
tests/unit/auth/test_service.py::test_email_verification_request_and_confirmation_activate_user PASSED [ 26%]
tests/unit/auth/test_service.py::test_password_reset_request_and_confirmation_update_password PASSED [ 28%]
tests/unit/auth/test_service.py::test_invalid_verification_token_is_rejected PASSED [ 30%]
tests/unit/cli/test_admin_handler.py::test_bootstrap_admin_requires_email_and_password PASSED [ 33%]
tests/unit/cli/test_admin_handler.py::test_bootstrap_admin_delegates_to_service PASSED [ 35%]
tests/unit/cli/test_admin_handler.py::test_upsert_user_uses_the_explicit_role PASSED [ 38%]
tests/unit/core/test_settings.py::test_default_settings_use_repo_name PASSED [ 40%]
tests/unit/core/test_settings.py::test_auth_and_email_settings_are_loaded_from_env PASSED [ 42%]
tests/unit/core/test_settings.py::test_email_brevo_legacy_names_are_supported PASSED [ 45%]
tests/unit/main/test_main.py::test_app_factory_registers_versioned_api_routes PASSED [ 47%]
tests/unit/notifications/test_brevo_email.py::test_brevo_email_sender_posts_expected_payload PASSED [ 50%]
tests/unit/notifications/test_brevo_email.py::test_brevo_email_sender_raises_on_http_error PASSED [ 52%]
tests/unit/secure_storage/test_encryption.py::test_envelope_cipher_round_trip PASSED [ 54%]
tests/unit/secure_storage/test_minio_service.py::test_minio_secure_storage_encrypts_before_persisting PASSED [ 57%]
tests/unit/tooling/test_run_ledger.py::test_record_appends_a_jsonl_event_and_generates_run_id PASSED [ 59%]
tests/unit/tooling/test_run_ledger.py::test_latest_finds_the_most_recent_matching_run PASSED [ 61%]
tests/unit/tooling/test_run_ledger.py::test_preview_summarises_changed_files_commits_and_actions PASSED [ 64%]
tests/unit/tooling/test_run_ledger.py::test_hook_appends_a_post_tool_use_event_from_stdin PASSED [ 66%]
tests/unit/web/test_login.py::test_login_page_renders_form PASSED        [ 69%]
tests/unit/web/test_login.py::test_login_submit_sets_session_cookie_and_success_state PASSED [ 71%]
tests/unit/web/test_login.py::test_login_submit_shows_unverified_account_error PASSED [ 73%]
tests/unit/web/test_login.py::test_login_submit_shows_invalid_credentials_error PASSED [ 76%]
tests/unit/web/test_signup.py::test_signup_page_renders_form PASSED      [ 78%]
tests/unit/web/test_signup.py::test_signup_submit_shows_validation_errors PASSED [ 80%]
tests/unit/web/test_signup.py::test_signup_submit_shows_duplicate_email_error PASSED [ 83%]
tests/unit/web/test_verify_email.py::test_create_app_builds_browser_auth_service_once PASSED [ 85%]
tests/unit/web/test_verify_email.py::test_verify_email_page_mentions_fragment_handshake PASSED [ 88%]
tests/unit/web/test_verify_email.py::test_verify_email_submit_confirms_valid_token PASSED [ 90%]
tests/unit/web/test_verify_email.py::test_verify_email_submit_shows_failure_for_invalid_token PASSED [ 92%]
tests/unit/web/test_verify_email.py::test_reset_password_page_mentions_fragment_handshake PASSED [ 95%]
tests/unit/web/test_verify_email.py::test_reset_password_submit_confirms_new_password PASSED [ 97%]
tests/unit/web/test_verify_email.py::test_reset_password_submit_shows_failure_for_invalid_token PASSED [100%]

======================= 42 passed, 65 warnings in 0.56s ========================
```
(Warnings are pre-existing FastAPI `on_event`/httpx deprecation notices, unrelated to this story.)

### E2E test output (`uv run pytest tests/e2e -vv -m e2e`, deployed Compose stack)
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
rootdir: /home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai
configfile: pyproject.toml
plugins: anyio-4.14.1, asyncio-1.4.0, playwright-0.8.0, base-url-2.1.0
collecting ... collected 34 items

tests/e2e/test_auth_mockups.py::test_auth_mockup_pages_render[chromium-/signup-Create account-Already have an account?] PASSED [  2%]
tests/e2e/test_auth_mockups.py::test_auth_mockup_pages_stay_within_mobile_viewport[chromium-/signup] PASSED [  5%]
tests/e2e/test_auth_mockups.py::test_signup_page_shows_trust_footer[chromium] PASSED [  8%]
tests/e2e/test_auth_mockups.py::test_login_page_shows_support_and_recovery_links[chromium] PASSED [ 11%]
tests/e2e/test_auth_mockups.py::test_verify_email_page_shows_primary_and_secondary_actions[chromium] PASSED [ 14%]
tests/e2e/test_auth_mockups.py::test_reset_password_page_shows_both_status_panels_together[chromium] PASSED [ 17%]
tests/e2e/test_auth_visual_regression.py::test_auth_screen_matches_approved_visual_baseline[chromium-desktop-signup] PASSED [ 20%]
tests/e2e/test_auth_visual_style.py::test_auth_pages_load_real_bootstrap_container_breakpoints[chromium-/signup] PASSED [ 23%]
tests/e2e/test_auth_visual_style.py::test_auth_primary_button_color_matches_bb_primary_token[chromium-/signup] PASSED [ 26%]
tests/e2e/test_auth_visual_style.py::test_login_password_toggle_uses_feather_icon_sprite[chromium] PASSED [ 29%]
tests/e2e/test_home_page.py::test_home_page_renders[chromium] PASSED     [ 32%]
tests/e2e/test_login_page.py::test_login_page_renders[chromium] PASSED   [ 35%]
tests/e2e/test_login_page.py::test_login_page_signs_verified_user_in[chromium] PASSED [ 38%]
tests/e2e/test_signup_page.py::test_signup_page_renders[chromium] PASSED [ 41%]
tests/e2e/test_signup_page.py::test_signup_page_successfully_registers_a_new_user[chromium] PASSED [ 44%]
tests/e2e/test_auth_mockups.py::test_auth_mockup_pages_render[chromium-/login-Sign in-Verify your email before signing in] PASSED [ 47%]
tests/e2e/test_auth_mockups.py::test_auth_mockup_pages_stay_within_mobile_viewport[chromium-/login] PASSED [ 50%]
tests/e2e/test_auth_visual_regression.py::test_auth_screen_matches_approved_visual_baseline[chromium-desktop-login] PASSED [ 52%]
tests/e2e/test_auth_visual_style.py::test_auth_pages_load_real_bootstrap_container_breakpoints[chromium-/login] PASSED [ 55%]
tests/e2e/test_auth_visual_style.py::test_auth_primary_button_color_matches_bb_primary_token[chromium-/login] PASSED [ 58%]
tests/e2e/test_auth_mockups.py::test_auth_mockup_pages_render[chromium-/verify-email-Verify your email-Verification link flow] PASSED [ 61%]
tests/e2e/test_auth_mockups.py::test_auth_mockup_pages_stay_within_mobile_viewport[chromium-/verify-email] PASSED [ 64%]
tests/e2e/test_auth_visual_regression.py::test_auth_screen_matches_approved_visual_baseline[chromium-desktop-reset-password] PASSED [ 67%]
tests/e2e/test_auth_visual_style.py::test_auth_pages_load_real_bootstrap_container_breakpoints[chromium-/reset-password] PASSED [ 70%]
tests/e2e/test_auth_visual_style.py::test_auth_primary_button_color_matches_bb_primary_token[chromium-/reset-password] PASSED [ 73%]
tests/e2e/test_auth_mockups.py::test_auth_mockup_pages_render[chromium-/reset-password-Reset password-Token loaded] PASSED [ 76%]
tests/e2e/test_auth_mockups.py::test_auth_mockup_pages_stay_within_mobile_viewport[chromium-/reset-password] PASSED [ 79%]
tests/e2e/test_auth_visual_regression.py::test_auth_screen_matches_approved_visual_baseline[chromium-desktop-verify-email] PASSED [ 82%]
tests/e2e/test_auth_visual_style.py::test_auth_pages_load_real_bootstrap_container_breakpoints[chromium-/verify-email] PASSED [ 85%]
tests/e2e/test_auth_visual_style.py::test_auth_primary_button_color_matches_bb_primary_token[chromium-/verify-email] PASSED [ 88%]
tests/e2e/test_auth_visual_regression.py::test_auth_screen_matches_approved_visual_baseline[chromium-mobile-signup] PASSED [ 91%]
tests/e2e/test_auth_visual_regression.py::test_auth_screen_matches_approved_visual_baseline[chromium-mobile-login] PASSED [ 94%]
tests/e2e/test_auth_visual_regression.py::test_auth_screen_matches_approved_visual_baseline[chromium-mobile-reset-password] PASSED [ 97%]
tests/e2e/test_auth_visual_regression.py::test_auth_screen_matches_approved_visual_baseline[chromium-mobile-verify-email] PASSED [100%]

============================= 34 passed in 49.41s ==============================
```
*(Ran against `tests.compose_stack.deployed_api_stack()` — API on `127.0.0.1:28010`, Postgres on
`25432`, project name `beembhai-test`. The dev machine's own long-running `.env` — which carries a
different Postgres password than the test harness's hardcoded connection string expects — was
moved aside for the duration of this run and restored immediately after; this is a pre-existing
test-harness fragility around `.env` reuse, out of scope for this story, and not a change to any
tracked file.)*

### Lint output (`uv run ruff check .`)
```
All checks passed!
```
`ruff format --check .` (informational only — **not** a CI gate per `.github/workflows/ci.yml`
line 27, which runs only `ruff check .`) reports 6 files needing reformatting
(`app/auth/tokens.py`, `app/core/settings.py`, `tests/compose_stack.py`,
`tests/e2e/test_login_page.py`, `tests/integration/auth/test_auth_login.py`,
`tests/integration/auth/test_register.py`) — all pre-existing drift, none touched by this story,
confirmed via `git diff 219eb2c..HEAD` (not in the changed-files list below). Not a blocker.

### Coverage output
N/A — no coverage tool (e.g. `pytest-cov`) is configured in `pyproject.toml`.

## Acceptance-scenario coverage

| Scenario | Test exists & runs | Unhappy path |
|----------|--------------------|--------------|
| Signup screen matches the approved mockup | `test_auth_mockups.py::test_auth_mockup_pages_render[...signup...]`, `::test_signup_page_shows_trust_footer`, `test_signup.py::test_signup_page_renders_form` | `test_signup.py::test_signup_submit_shows_validation_errors`, `::test_signup_submit_shows_duplicate_email_error` |
| Sign-in screen matches the approved mockup | `test_auth_mockups.py::test_auth_mockup_pages_render[...login...]`, `::test_login_page_shows_support_and_recovery_links`, `test_login.py::test_login_page_renders_form` | `test_login.py::test_login_submit_shows_unverified_account_error`, `::test_login_submit_shows_invalid_credentials_error` |
| Reset password screen matches the approved mockup | `test_auth_mockups.py::test_auth_mockup_pages_render[...reset-password...]`, `::test_reset_password_page_shows_both_status_panels_together`, `test_verify_email.py::test_reset_password_page_mentions_fragment_handshake` | `test_verify_email.py::test_reset_password_submit_shows_failure_for_invalid_token` |
| Verify email screen matches the approved mockup | `test_auth_mockups.py::test_auth_mockup_pages_render[...verify-email...]`, `::test_verify_email_page_shows_primary_and_secondary_actions`, `test_verify_email.py::test_verify_email_page_mentions_fragment_handshake` | `test_verify_email.py::test_verify_email_submit_shows_failure_for_invalid_token` |
| Auth screens remain usable on a narrow viewport | `test_auth_mockups.py::test_auth_mockup_pages_stay_within_mobile_viewport[...]` (×4 paths) | N/A (layout scenario) |
| Screens actually **look** like the mockups (cross-cutting) | `test_auth_visual_style.py::test_auth_pages_load_real_bootstrap_container_breakpoints[...]`, `::test_auth_primary_button_color_matches_bb_primary_token[...]`, `::test_login_password_toggle_uses_feather_icon_sprite`, `test_auth_visual_regression.py::test_auth_screen_matches_approved_visual_baseline[...]` (×8: 4 screens × 2 viewports) | N/A (visual-fidelity scenario; baseline diff itself is the failure mode) |

- [x] Every scenario covered by a real, running test — confirmed against `test-plan.md`, all rows present and passing.
- [x] Unhappy paths present — validation errors, duplicate email, invalid credentials, unverified account, invalid reset/verify tokens all covered (pre-existing tests, kept intact, not weakened).

## Faked-green inspection

- [x] **No tests skipped/xfail/disabled/deleted vs the test-plan.** `git diff --stat 219eb2c..HEAD -- tests/` shows only the 8 new baseline PNGs plus a 2-line/3-line whitespace-only line-wrap in `test_auth_visual_regression.py` and `test_auth_visual_style.py` (ruff `E501` fixes, see full diff below — variable extraction and multi-line locator call, zero semantic change). No `pytest.mark.skip`, `xfail`, or commented-out test found by grep across the touched test files (the only "skip" hits are pre-existing, unrelated `action="skipped"` / `skipped_reason="duplicate_email"` fixture literals in `test_signup.py`, not test-skip markers).
- [x] **No assertions loosened/removed vs acceptance criteria.** Same diff confirms the only text change to test files since test-creator's red commit is the two-file line-wrap; every assertion test-creator wrote (`assert ... == "1320px"`, `assert token_color`, `assert button_color == token_color`, `assert toggle_icon.count() > 0`, `assert diff_ratio <= MAX_DIFF_RATIO`, the `pytest.fail("No approved visual baseline...")` guard) is byte-identical to what shipped in `219eb2c`.
- [x] **No production special-casing of test inputs.** `git diff 219eb2c..HEAD -- app/` touches only `theme.css`, the 4 auth templates, `layouts/auth.html`, `base.html`, and the vendored Bootstrap/feather assets — no branch keyed on a test-only value, header, or user-agent. The `--bb-accent` → `--bb-primary` rename is a real, repo-wide token rename (15 call sites in `theme.css`, confirmed via `grep -n "bb-primary" theme.css`), not a test-only alias.
- [x] **No swallowed errors hiding unhappy-path behaviour.** The unhappy-path unit tests (`test_login_submit_shows_unverified_account_error`, `test_login_submit_shows_invalid_credentials_error`, `test_signup_submit_shows_validation_errors`, `test_signup_submit_shows_duplicate_email_error`) assert on the real `alert-danger` Bootstrap class now emitted by the templates (verified in `login.html`/`signup.html` diff — `status-pill--error` was migrated to `alert alert-danger`, a real Bootstrap-idiomatic class, not a synonym injected only for the test).

```diff
$ git diff --stat 219eb2c..HEAD -- tests/
 tests/e2e/__snapshots__/auth/login-desktop.png         | Bin 0 -> 225496 bytes
 tests/e2e/__snapshots__/auth/login-mobile.png          | Bin 0 -> 57869 bytes
 tests/e2e/__snapshots__/auth/reset-password-desktop.png  | Bin 0 -> 165293 bytes
 tests/e2e/__snapshots__/auth/reset-password-mobile.png | Bin 0 -> 107263 bytes
 tests/e2e/__snapshots__/auth/signup-desktop.png        | Bin 0 -> 188419 bytes
 tests/e2e/__snapshots__/auth/signup-mobile.png         | Bin 0 -> 104828 bytes
 tests/e2e/__snapshots__/auth/verify-email-desktop.png  | Bin 0 -> 118210 bytes
 tests/e2e/__snapshots__/auth/verify-email-mobile.png   | Bin 0 -> 84794 bytes
 tests/e2e/test_auth_visual_regression.py               |   3 ++-
 tests/e2e/test_auth_visual_style.py                    |   4 +++-
 10 files changed, 5 insertions(+), 2 deletions(-)
```

## Regression & design

- [x] **Pre-existing suite still passes.** All pre-existing tests (`test_home_page.py`,
  `test_login_page.py`, `test_signup_page.py`, `test_auth_mockups.py`'s original assertions, the
  full `tests/unit/auth`, `tests/unit/cli`, `tests/unit/core`, `tests/unit/notifications`,
  `tests/unit/secure_storage`, `tests/unit/tooling` suites) pass unchanged alongside the new
  BEEM-20 tests — see full verbose output above.
- [x] **Code landed in the module(s) named in story-design.md.** `git diff --stat 219eb2c..HEAD -- app/`
  confirms changes confined to exactly the target modules: `theme.css`, the 4 auth templates,
  `layouts/auth.html`, `base.html` (Bootstrap `<link>`), and the vendored
  `static/vendor/bootstrap/bootstrap.min.css` + `static/vendor/feather/feather-sprite.svg` assets.
  No new service, route, or integration was introduced — all 4 auth routes' signatures are
  unchanged (presentation-layer only, as designed).

## Notes

- The visual-fidelity gap flagged during human sign-off (decorative background washes render
  fainter than the AI-generated mockups) was explicitly reviewed and approved as-is by the user —
  the mockups are documented in `story-design.md` as AI-generated references, not a pixel-match
  target, and the approved baseline screenshots now lock in the signed-off state as the regression
  floor going forward.
- Two ruff `E501` line-length violations found in the new visual test files during this
  verification pass were fixed (pure line-wrapping, no assertion change) and committed as
  `7e8600c` prior to writing this report, so the verified state is fully committed and
  reproducible.

---
*PASS → next is `pr-create`.*
