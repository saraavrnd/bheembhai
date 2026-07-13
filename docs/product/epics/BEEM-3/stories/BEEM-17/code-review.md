# Code Review — BEEM-17: Register a local user account

**Advisory** · **Branch:** `feat/BEEM-16-bootstrap-initial-platform-admin` · **Reviewed vs:** main · **Date:** 2026-07-13
**Pre-flight:** verification-BEEM-17.md = PASS

## Severity summary
| Critical | High | Medium | Low | Nit |
|:--------:|:----:|:------:|:---:|:---:|
| 0 | 1 | 1 | 0 | 0 |
**Advisory note:** Recommend fixing the 1 High before PR; the Medium is worth addressing in the same pass.

## Tools run
```text
uv run ruff check . -> All checks passed!
uv run bandit -q -r app -> failed to spawn (bandit not installed in this environment)
uv run pip-audit -q -> failed to spawn (pip-audit not installed in this environment)
```

## Findings

### 1. Coding standards & conventions
| # | Severity | Location | Finding | Proposed fix |
|---|----------|----------|---------|--------------|
| 1 | Medium | `app/auth/router.py:20-25` | The new auth-service helper still performs lazy construction on the request path and caches the result in `request.app.state`. That hides bootstrap failures until the first signup request and leaves DB/schema initialization tied to request handling instead of startup, which is inconsistent with the browser-auth bootstrap pattern. | Build and cache the auth service during app startup or a lifespan hook, then have the route only read `app.state.auth_service` and fail fast if it is missing. |

### 2. Security audit
| # | Severity | Location | Finding (risk) | Proposed fix |
|---|----------|----------|----------------|--------------|
| | | | | |

### 3. Acceptance-criteria intent
| # | Severity | Location | Finding | Proposed fix |
|---|----------|----------|---------|--------------|
| 2 | High | `app/auth/service.py:90-110` | Duplicate-email rejection depends only on a pre-insert lookup. Two concurrent registrations with the same email can both pass the lookup and one can then fail with an uncaught unique-constraint error, surfacing a 500 instead of the required 409 Conflict. | Catch the database unique-constraint failure around user creation and translate it into the same duplicate-email path, or use a conflict-aware insert so the duplicate case is handled deterministically at the repository boundary. |

### 4. Maintainability
| # | Severity | Location | Finding | Proposed fix |
|---|----------|----------|---------|--------------|
| | | | | |

## Fix list for `implement` (ordered by severity)
1. [High] Harden `AuthService.register_user(...)` against concurrent duplicate signups by translating the database unique-constraint failure into the duplicate-email response instead of letting it bubble as a 500.
2. [Medium] Move auth-service initialization out of the request path and into app startup or a lifespan hook so `/auth/register` does not hide DB/bootstrap failures behind the first public request.

---
*Advisory — blocks nothing. The team picks which findings to fix. Accepted fixes → `implement` applies them → `test-verify` re-runs → `pr-create`. If all waived → straight to `pr-create`.*
