# Code Review — BEEM-12: Create and list accessible projects

**Advisory** · **Branch:** `feat/BEEM-12-create-and-list-projects` · **Reviewed vs:** origin/main · **Date:** 2026-07-20
**Pre-flight:** verification.md = PASS

## Severity summary
| Critical | High | Medium | Low | Nit |
|:--------:|:----:|:------:|:---:|:---:|
| 0 | 1 | 2 | 2 | 0 |
**Advisory note:** Recommend fixing the 1 High (missing Alembic migration) before merge — it's a
real production-deployment gap, not a style nit. The two Mediums are worth a quick fix too since
they're small. Lows are optional.

## Tools run
```
$ uv run ruff check app/projects tests/unit/projects tests/integration/projects app/main.py
All checks passed!

$ uv run ruff format --check app/projects tests/unit/projects tests/integration/projects app/main.py
7 files already formatted

$ git diff --stat origin/main -- app/projects app/main.py
 app/main.py                 |  5 +++++
 app/projects/repository.py  | 193 ++++++++++++++++++++++
 app/projects/router.py      | 56 ++++++++++++++++++++++++++--
 app/projects/service.py     | 27 +++++++++
 4 files changed, 281 insertions(+), 1 deletion(-)
```
No dependency/secret scanner is configured in this repo; reviewed by reading the diff directly
against `references/security-audit-checklist.md`.

## Findings

### 1. Coding standards & conventions
| # | Severity | Location | Finding | Proposed fix |
|---|----------|----------|---------|--------------|
| 1 | High | `app/projects/repository.py:83` (`ensure_schema`), missing file under `migrations/versions/` | The repo's established convention for new persisted tables is an Alembic migration — see `migrations/versions/20260711_0001_create_users_table.py` for the `users` table, and `docker-compose.yml`'s dedicated `migrate` service (`alembic upgrade head`) that every other service depends on before starting. BEEM-12 adds two new tables (`projects`, `memberships`) with **no migration**, relying solely on `Base.metadata.create_all()` via `ensure_schema()` at app startup. This works in dev/tests (same DB user has DDL rights, `create_all` is `checkfirst=True`-safe), but it means: (a) these tables have no tracked schema history or downgrade path, (b) the `migrate` service — the thing ops actually runs before rollout — never creates them, so a deployment that locks down the API process's DB grants (a reasonable hardening step) would leave `projects`/`memberships` never created, and (c) two `api` replicas starting concurrently both run `create_all` with no coordination, which is usually safe but isn't the pattern the rest of the schema uses. | Add an Alembic migration (`migrations/versions/<ts>_create_projects_and_memberships_tables.py`) mirroring the users-table migration: `op.create_table` for both tables + the unique index on `projects.slug` + FK constraints. Keep `ensure_schema()` if it's still useful for pure-unit-test setups, but the migration should be the schema of record. |
| 2 | Low | `app/projects/repository.py:96-99` (`find_by_id`) | `SqlAlchemyProjectRepository.find_by_id` is dead code — nothing in this story's routes/service calls it (grep across `app/` and `tests/` finds zero callers). It mirrors `SqlAlchemyUserRepository.find_by_id`, which *is* used, but adding an unused public method ahead of the story that needs it (likely BEEM-13/15) is a small deviation from "minimum viable code." | Either drop it until a story needs it, or leave it with a one-line note that it's added for the upcoming project-detail story — either is fine, just flagging so it's a conscious choice, not an oversight. |

### 2. Security audit
| # | Severity | Location | Finding (risk) | Proposed fix |
|---|----------|----------|----------------|--------------|
| — | — | — | AuthN (401 via `_current_user`) and AuthZ (403 via `platform_role`/active-`Membership` scoping) are both correctly enforced on both routes, matching `story-design.md`'s intent. No hard-coded secrets, no raw SQL (all queries go through SQLAlchemy's expression API, so no injection surface), no PII beyond what's already exposed by the reused `UserRecord`. Nothing to flag here beyond finding #3 below (input-length validation), which is really a robustness issue with a minor DoS-shaped edge (large payload → DB error) rather than an exploitable hole. | — |

### 3. Acceptance-criteria intent
| # | Severity | Location | Finding | Proposed fix |
|---|----------|----------|---------|--------------|
| 3 | Medium | `app/projects/router.py:17-18` (`ProjectCreateRequest.name`) | `name: str = Field(min_length=1)` has no `max_length`, but the `projects.name` column is `String(255)` (`app/projects/repository.py:23`). A request with a `name` longer than 255 chars passes Pydantic validation, then fails at the DB layer with an uncaught `sqlalchemy.exc.DataError`/driver error — that's an unhandled 500, not the clean `422` the acceptance criteria imply for invalid input. (Note: the rest of the codebase, e.g. `app/auth/router.py`'s email/password fields, also lacks `max_length` — this isn't a new pattern, but it's a real gap this story's own column constraint makes concrete and testable.) | Add `max_length=255` to `ProjectCreateRequest.name` so oversized input gets a clean `422` instead of a DB-level 500. |
| 4 | Medium | `app/projects/router.py:17-18` + `app/projects/repository.py:159-160` (`_unique_slug_in_session`) | The acceptance criterion "missing name is rejected" is tested for `{}` and `{"name": ""}`, but a whitespace-only name (e.g. `{"name": "   "}`) passes Pydantic's `min_length=1` (length-1+ strings of whitespace count), then `_unique_slug_in_session` strips it down to `""` and falls back to the literal slug `"project"`. The result: an admin can create a project whose display `name` is literally `"   "` with a generic `project`/`project-2`/... slug — almost certainly not the intent behind "just a name," and not covered by the current test-plan. | Either reject blank-after-strip names at the API layer (e.g. a Pydantic `field_validator` that strips and re-checks `min_length`), or explicitly decide this is acceptable and note it — but right now it's an unconsidered gap rather than a decision. |

### 4. Maintainability
| # | Severity | Location | Finding | Proposed fix |
|---|----------|----------|---------|--------------|
| 5 | Low | `app/projects/repository.py:159-169` (`_unique_slug_in_session`) | The uniqueness check is a non-atomic check-then-insert (`SELECT` for collision, then `INSERT`, no row lock). Under concurrent requests creating projects with the same `name`, both could pass the `SELECT` before either commits, and the second `INSERT` fails on the DB unique constraint. This is already handled correctly (`IntegrityError` → `409` in `router.py:53-56`), so it's not a bug — just worth a short comment noting the race is expected and handled by the 409 path, so a future reader doesn't "fix" it into something more complex. | Optional: a one-line comment on `_unique_slug_in_session` noting the race is intentionally left to the DB constraint + 409 mapping. |

## Fix list for `implement` (ordered by severity)
1. [High] Add an Alembic migration for `projects` and `memberships` (mirrors `users`' migration; keeps the `migrate` service as the real schema authority).
2. [Medium] Add `max_length=255` to `ProjectCreateRequest.name` to match the `projects.name` column and avoid an unhandled 500 on oversized input.
3. [Medium] Reject whitespace-only `name` (strip + re-validate `min_length`) so "missing name is rejected" covers the whitespace case the test-plan didn't anticipate.
4. [Low] Decide on `find_by_id` (drop or keep with a forward-looking note).
5. [Low] Optional comment on the slug race/409 handling.

---
*Advisory — blocks nothing. The team picks which findings to fix. Accepted fixes → `implement`
applies them → `test-verify` re-runs → `pr-create`. If all waived → straight to `pr-create`.*
