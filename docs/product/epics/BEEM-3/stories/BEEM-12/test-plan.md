# Test Plan — BEEM-12: Create and list accessible projects

**Epic:** BEEM-3 · **Date:** 2026-07-20 · **Runners:** pytest (unit, in-process SQLite) · pytest against the deployed Docker Compose stack (integration)

## Scenario → test mapping
| # | Acceptance scenario | Layer | Test file::test name | Type |
|---|---------------------|-------|----------------------|------|
| 1 | Admin creates a project with just a name | unit | `tests/unit/projects/test_service.py::test_create_project_by_admin_persists_project_with_name_and_no_bindings` | happy |
| 1 | Admin creates a project with just a name | integration | `tests/integration/projects/test_projects_api.py::test_create_project_endpoint_returns_201_and_persists_project_for_admin` | happy |
| 2 | Missing name is rejected | integration | `tests/integration/projects/test_projects_api.py::test_create_project_endpoint_rejects_missing_name` | unhappy |
| 3 | Signed-in user sees accessible projects | unit | `tests/unit/projects/test_service.py::test_list_accessible_projects_admin_sees_all_projects` | happy |
| 3 | Signed-in user sees accessible projects | unit | `tests/unit/projects/test_service.py::test_list_accessible_projects_member_sees_only_active_memberships` | happy |
| 3 | Signed-in user sees accessible projects | integration | `tests/integration/projects/test_projects_api.py::test_list_projects_endpoint_returns_only_accessible_projects` | happy |
| 4 | Unauthorized project stays hidden | unit | `tests/unit/projects/test_service.py::test_list_accessible_projects_member_sees_only_active_memberships` (`hidden_project` assertion) | unhappy |
| 4 | Unauthorized project stays hidden | integration | `tests/integration/projects/test_projects_api.py::test_list_projects_endpoint_returns_only_accessible_projects` (`hidden_project` assertion) | unhappy |
| 5* | Non-admin cannot create a project | unit | `tests/unit/projects/test_service.py::test_create_project_rejects_non_admin_actor` | unhappy |
| 5* | Non-admin cannot create a project | integration | `tests/integration/projects/test_projects_api.py::test_create_project_endpoint_rejects_non_admin` | unhappy |
| 6* | Unauthenticated requests are rejected | integration | `tests/integration/projects/test_projects_api.py::test_create_project_endpoint_rejects_unauthenticated_request` | unhappy |
| 6* | Unauthenticated requests are rejected | integration | `tests/integration/projects/test_projects_api.py::test_list_projects_endpoint_rejects_unauthenticated_request` | unhappy |

\* Scenarios 5 and 6 aren't separate Gherkin scenarios in the Jira story text, but are direct
consequences of constraints stated in the story's own "Notes / dependencies" ("Only
`platform_role = PLATFORM_ADMIN` may create a project") and the story-design note's authenticated-
session requirement. Included per the "permission cases are part of done" rule.

Also included as a boundary case beyond the four AC scenarios: a deactivated (`is_active=False`)
`Membership` must not grant access, per `data-model.md`/ADR-009's "test `is_active = true`, not
just row existence" rule — covered by `test_list_accessible_projects_member_sees_only_active_memberships`.

## Coverage check
- [x] Every acceptance scenario has at least one test.
- [x] Unhappy paths covered (missing name, non-admin create, unauthenticated access, inactive membership).
- [x] Tests target the interfaces from the approved story-design note (`ProjectService.create_project`,
      `ProjectService.list_accessible_projects`, `SqlAlchemyProjectRepository.*`, `POST`/`GET /api/v1/projects`).

## Red-phase verification
Both new test modules fail at collection with `ModuleNotFoundError: No module named
'app.projects.repository'` — the module the story-design note names as this story's target and
which does not exist yet. This is the expected "feature not built" signal for a story that creates
a module from scratch (not a wrong import path or a broken fixture), matching the walking-skeleton
scaffold's known-good harness.

```
$ uv run pytest tests/unit/projects/ -v
...
ERROR tests/unit/projects/test_service.py
E   ModuleNotFoundError: No module named 'app.projects.repository'
=========================== short test summary info ============================
ERROR tests/unit/projects/test_service.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.12s ===============================

$ uv run pytest tests/integration/projects/ -v
...
ERROR tests/integration/projects/test_projects_api.py
E   ModuleNotFoundError: No module named 'app.projects.repository'
=========================== short test summary info ============================
ERROR tests/integration/projects/test_projects_api.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.15s ===============================
```

The integration collection failure happens before the `deployed_api` fixture (Docker Compose
stack) is invoked, since pytest fails at import time — so no stack was brought up for this red
run. `implement`/`test-verify` will exercise the integration suite against the real deployed stack
once `app/projects/repository.py` and `app/projects/service.py` exist.

## Traceability
**Requirements covered:** FR-001, FR-002

---
*Next: `implement` makes these tests pass without weakening them.*
