# Verification — BEEM-12: Create and list accessible projects

**Verdict:** PASS (re-verified after code-review fixes) · **Branch:** `feat/BEEM-12-create-and-list-projects` · **Date:** 2026-07-20

> Re-run after `code-review.md`'s 5 findings (1 High, 2 Medium, 2 Low — all accepted and fixed):
> Alembic migration added for `projects`/`memberships`, blank/whitespace and oversized `name`
> now rejected with `422`, unused `find_by_id` dropped, slug-race comment added. Two new
> regression tests cover the previously-uncovered whitespace/oversized-name edge cases. See
> commit `158644b`.

## Suite, lint, coverage
### Commands
- `uv run pytest -vv` (full repo suite, incl. unit + integration against the deployed Docker
  Compose stack + e2e/Playwright)
- `uv run ruff check .`
- `uv run ruff format --check .`
- No coverage-percentage gate is defined in `docs/testing-strategy.md`; scenario coverage is
  checked explicitly below instead.

**Environment note:** this workstation had a stale local `.env` (gitignored, dated 2026-07-16)
whose `POSTGRES_PASSWORD` didn't match the hardcoded `beembhai:beembhai` credentials the
Docker-Compose test harness (`tests/compose_stack.py`) assumes when `.env` already exists. That
mismatch broke every integration test on `main`, not just BEEM-12's (verified by running
`tests/integration/auth/` before touching `.env`, which failed identically). Confirmed this was
pre-existing/local-only, not introduced by this story, then re-ran the suite with `.env`
temporarily moved aside (`.env.local-backup`) so the harness could generate its own known-good
`.env`, and restored the original `.env` immediately after. No repo files were changed by this
workaround.

### Test suite output (re-run after code-review fixes)
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai
configfile: pyproject.toml
testpaths: tests
collecting ... collected 99 items

tests/e2e/... (30 tests) PASSED
tests/integration/auth/test_auth_login.py::test_login_endpoint_sets_session_and_me_returns_current_user PASSED
tests/integration/auth/test_auth_login.py::test_login_endpoint_rejects_unverified_user PASSED
tests/integration/auth/test_auth_login.py::test_password_reset_flow_updates_password_and_rejects_old_password PASSED
tests/integration/auth/test_register.py::test_register_endpoint_creates_user_and_returns_user_shape PASSED
tests/integration/auth/test_register.py::test_register_endpoint_rejects_invalid_input PASSED
tests/integration/auth/test_register.py::test_register_endpoint_rejects_duplicate_email PASSED
tests/integration/main/test_bootstrap_startup.py::test_deployed_api_serves_health_routes PASSED
tests/integration/main/test_health.py::test_health_endpoint_returns_ok PASSED
tests/integration/projects/test_projects_api.py::test_create_project_endpoint_returns_201_and_persists_project_for_admin PASSED
tests/integration/projects/test_projects_api.py::test_create_project_endpoint_rejects_non_admin PASSED
tests/integration/projects/test_projects_api.py::test_create_project_endpoint_rejects_unauthenticated_request PASSED
tests/integration/projects/test_projects_api.py::test_create_project_endpoint_rejects_missing_name PASSED
tests/integration/projects/test_projects_api.py::test_create_project_endpoint_rejects_whitespace_only_name PASSED
tests/integration/projects/test_projects_api.py::test_create_project_endpoint_rejects_name_exceeding_max_length PASSED
tests/integration/projects/test_projects_api.py::test_list_projects_endpoint_returns_only_accessible_projects PASSED
tests/integration/projects/test_projects_api.py::test_list_projects_endpoint_rejects_unauthenticated_request PASSED
tests/unit/auth/test_service.py:: (11 tests) PASSED
tests/unit/cli/test_admin_handler.py:: (3 tests) PASSED
tests/unit/core/test_settings.py:: (3 tests) PASSED
tests/unit/main/test_main.py::test_app_factory_registers_versioned_api_routes PASSED
tests/unit/notifications/test_brevo_email.py:: (2 tests) PASSED
tests/unit/projects/test_project_service.py::test_create_project_by_admin_persists_project_with_name_and_no_bindings PASSED
tests/unit/projects/test_project_service.py::test_create_project_rejects_non_admin_actor PASSED
tests/unit/projects/test_project_service.py::test_list_accessible_projects_admin_sees_all_projects PASSED
tests/unit/projects/test_project_service.py::test_list_accessible_projects_member_sees_only_active_memberships PASSED
tests/unit/secure_storage/test_encryption.py::test_envelope_cipher_round_trip PASSED
tests/unit/secure_storage/test_minio_service.py::test_minio_secure_storage_encrypts_before_persisting PASSED
tests/unit/tooling/test_run_ledger.py:: (4 tests) PASSED
tests/unit/web/test_forgot_password.py:: (5 tests) PASSED
tests/unit/web/test_login.py:: (4 tests) PASSED
tests/unit/web/test_signup.py:: (4 tests) PASSED
tests/unit/web/test_verify_email.py:: (8 tests) PASSED

====================== 99 passed, 139 warnings in 48.06s =======================
```
99 = the original 97 plus the 2 new regression tests added for the code-review-driven fixes
(`test_create_project_endpoint_rejects_whitespace_only_name`,
`test_create_project_endpoint_rejects_name_exceeding_max_length`). Same `.env`-mismatch
workaround as the first run was used (moved aside, restored immediately after); no repo files
changed by it. The `api` container only starts after the `migrate` service completes
successfully (`docker-compose.yml`'s `service_completed_successfully` dependency), so this green
run also confirms the new Alembic migration
(`migrations/versions/20260720_0001_create_projects_and_memberships_tables.py`) applies cleanly.

- [x] Full test suite green
- [x] Lint clean
- [x] Coverage gate met (none defined; scenario coverage checked explicitly below)

### Lint output
```
$ uv run ruff check .
All checks passed!

$ uv run ruff format --check .
Would reformat: app/auth/tokens.py
Would reformat: app/core/settings.py
Would reformat: tests/compose_stack.py
Would reformat: tests/e2e/test_login_page.py
Would reformat: tests/integration/auth/test_auth_login.py
Would reformat: tests/integration/auth/test_register.py
6 files would be reformatted, 66 files already formatted
```
`git diff origin/main -- <those 6 files>` is empty — none were touched by this story; this is
pre-existing format debt on `main`, not a BEEM-12 regression. All files this story added or
changed, including the code-review fix commit, are format-clean, verified separately:
```
$ uv run ruff check app/projects migrations tests/integration/projects
All checks passed!

$ uv run ruff format --check app/projects migrations tests/integration/projects
8 files already formatted
```

### Coverage output
No coverage-percentage tool/gate is configured in this repo (`pyproject.toml` has no
`[tool.coverage]` section; `docs/testing-strategy.md` defines coverage as scenario coverage, not
a percentage). See "Acceptance-scenario coverage" below in place of a numeric gate.

## Acceptance-scenario coverage
| Scenario | Test exists & runs | Unhappy path |
|----------|--------------------|--------------|
| 1. Admin creates a project with just a name | `tests/unit/projects/test_project_service.py::test_create_project_by_admin_persists_project_with_name_and_no_bindings`, `tests/integration/projects/test_projects_api.py::test_create_project_endpoint_returns_201_and_persists_project_for_admin` — both PASSED | happy |
| 2. Missing name is rejected | `tests/integration/projects/test_projects_api.py::test_create_project_endpoint_rejects_missing_name`, `::test_create_project_endpoint_rejects_whitespace_only_name`, `::test_create_project_endpoint_rejects_name_exceeding_max_length` — all PASSED (the latter two added as code-review-driven regression tests) | ✓ |
| 3. Signed-in user sees accessible projects | `tests/unit/projects/test_project_service.py::test_list_accessible_projects_admin_sees_all_projects`, `::test_list_accessible_projects_member_sees_only_active_memberships`, `tests/integration/projects/test_projects_api.py::test_list_projects_endpoint_returns_only_accessible_projects` — all PASSED | happy |
| 4. Unauthorized project stays hidden | Covered by the `hidden_project` assertions inside `test_list_accessible_projects_member_sees_only_active_memberships` and `test_list_projects_endpoint_returns_only_accessible_projects` — both PASSED | ✓ |
| 5*. Non-admin cannot create a project | `tests/unit/projects/test_project_service.py::test_create_project_rejects_non_admin_actor`, `tests/integration/projects/test_projects_api.py::test_create_project_endpoint_rejects_non_admin` — both PASSED | ✓ |
| 6*. Unauthenticated requests rejected | `tests/integration/projects/test_projects_api.py::test_create_project_endpoint_rejects_unauthenticated_request`, `::test_list_projects_endpoint_rejects_unauthenticated_request` — both PASSED | ✓ |

\* Derived from the story's stated constraint and the design note's authenticated-session
requirement, per `test-plan.md`.

- [x] Every scenario covered by a real, running test
- [x] Unhappy paths present

## Faked-green inspection
- [x] No tests skipped/xfail/disabled/deleted vs the test-plan — `grep -rn "skip\|xfail"
  tests/unit/projects/ tests/integration/projects/` returns nothing.
- [x] No assertions loosened/removed vs acceptance criteria — `git diff 0926e96 HEAD --
  tests/integration/projects/test_projects_api.py` shows only two new test functions appended
  (the whitespace-only-name and oversized-name regressions); every existing test and assertion is
  untouched.
- [x] No production special-casing of test inputs — `ProjectService.create_project` /
  `list_accessible_projects` branch only on `actor.platform_role`, not on any test-specific value;
  the new `_name_must_not_be_blank` validator and `max_length=255` in
  `app/projects/router.py` apply uniformly to every request, not just test payloads.
- [x] No swallowed errors hiding unhappy-path behaviour — `PermissionError` and `IntegrityError`
  are translated to HTTP 403/409 explicitly in `app/projects/router.py`; Pydantic validation (422)
  now also covers blank/whitespace and oversized names, not just the omitted-field case; auth
  (401) comes from the reused `_current_user` in `app/auth/router.py`.
- [x] Code-review fixes are real fixes, not test-only patches — the High finding (missing Alembic
  migration) added actual schema-management code (`migrations/versions/20260720_0001_*.py`,
  `migrations/env.py` model registration), not a test workaround; the Mediums changed production
  validation logic in `app/projects/router.py`, each backed by a new failing-then-passing test.

## Regression & design
- [x] Pre-existing suite still passes — all 87 non-BEEM-12 tests from the original run, plus the
  10 BEEM-12 tests from the first pass, all still pass in the 99-test re-run (auth/web/e2e/core/
  cli/tooling/secure_storage all green, zero regressions from the fix commit).
- [x] Code in the module(s) from the story-design note, plus the migration convention the review
  correctly identified as missing — `app/projects/repository.py`, `app/projects/service.py`,
  `app/projects/router.py`, `app/main.py`'s `_startup_project_service` wiring, and
  `migrations/versions/20260720_0001_create_projects_and_memberships_tables.py` (mirroring the
  existing `20260711_0001_create_users_table.py` pattern, not a new architectural concern — this
  repo already uses Alembic as its schema-migration tool via the `migrate` compose service).
  `git diff --stat origin/main -- app/projects tests/unit/projects tests/integration/projects
  app/main.py migrations` shows exactly those files touched, no unplanned scope.

## If BLOCK — issues to fix
None. No blocking issues found.

---
*PASS → next is `pr-create`.*
