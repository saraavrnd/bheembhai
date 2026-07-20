# Story Design — BEEM-12: Create and list accessible projects

**Status:** AWAITING APPROVAL · **Epic:** BEEM-3 · **Date:** 2026-07-19
**Domain:** backend

> Thin design note. Review and approve before test-creator writes tests. Change anything;
> I'll realign and re-confirm.

## Target module(s)
`app/projects/` — new `repository.py` and `service.py`, plus routes added to the existing
(currently empty-stub) `app/projects/router.py`. Wired into `app/main.py` the same way
`auth_service` is: a `build_project_service()` factory assigned to `app.state.project_service`
on startup.

## Interfaces / endpoints
| Kind | Signature | Request → Response |
|------|-----------|--------------------|
| Route | `POST /api/v1/projects` | `ProjectCreateRequest {name: str}` → `201 Project {id, name, activeWorkflowVersionId: null, activePolicyVersionId: null}` |
| Route | `POST /api/v1/projects` (empty/whitespace name) | same request shape → `422` (Pydantic `min_length=1` validation, no project created) |
| Route | `GET /api/v1/projects` | none → `200 {items: Project[]}`, scoped to the signed-in user (see Approach) |
| Service | `ProjectService.create_project(*, name: str, actor: UserRecord) -> ProjectRecord` | raises `PermissionError` if `actor.platform_role != ADMIN_ROLE` |
| Service | `ProjectService.list_accessible_projects(*, actor: UserRecord) -> list[ProjectRecord]` | all projects if `actor.platform_role == ADMIN_ROLE`, else projects joined through an active `Membership` for `actor.id` |
| Repository | `SqlAlchemyProjectRepository.create_project_in_session(session, *, name) -> ProjectRecord` | mirrors `SqlAlchemyUserRepository`'s session-scoped pattern |
| Repository | `SqlAlchemyProjectRepository.list_all_in_session(session) -> list[ProjectRecord]` | for platform-admin oversight listing |
| Repository | `SqlAlchemyProjectRepository.list_for_member_in_session(session, user_id) -> list[ProjectRecord]` | joins `Membership` where `user_id = :user_id AND is_active = true` |

Both routes require an authenticated session (reuse `_current_user`-style dependency, see Reuse).
Creation additionally requires `platform_role == ADMIN_ROLE`, returned as `403`.

## Data-model deltas
Two new SQLAlchemy models under `app/projects/repository.py` (neither exists in code yet, only in
`data-model.md`/`openapi.yaml`):
- **`Project`** table: `id (uuid pk), name (str, not null), slug (str, unique, indexed), created_at, updated_at`.
  `activeWorkflowVersionId`/`activePolicyVersionId` stay `NULL` — no story yet populates them.
- **`Membership`** table: `id (uuid pk), project_id (fk→projects.id), user_id (fk→users.id), role (str), is_active (bool, default true), created_at, updated_at`.
  BEEM-12 does **not** expose any endpoint to write `Membership` rows (that's BEEM-15) — the table
  is created here only so `list_accessible_projects` has something to join against, and so
  test-creator can seed membership rows directly through the repository to exercise the
  "sees accessible projects" / "unauthorized project stays hidden" scenarios ahead of BEEM-15.
  `ProjectRole` (the role catalog FK target) is BEEM-15/ADR-007 territory — `Membership.role` is
  stored as a plain string here, not validated against a catalog, since nothing in this story
  writes it.

## Reuse
- `app.core.db.Base`, `create_database_engine`, `create_session_factory` — same engine/session
  plumbing as `app/auth/repository.py`.
- Session-scoped repository pattern (`session_scope`, `*_in_session` methods, dataclass records)
  copied from `SqlAlchemyUserRepository`.
- `app/auth/router.py`'s `_current_user(request)` pattern for pulling the signed-in user off
  `request.session["user_id"]` via the auth repository — reused as-is (importing from
  `app.auth.router`, not duplicated), since project routes need the same signed-in-user lookup.
- `ADMIN_ROLE` constant from `app.auth.repository` for the platform-admin check.
- `app.main.create_app`'s `@app.on_event("startup")` + `app.state.<x>_service` wiring convention.

## Approach
Add `Project` and `Membership` ORM models and a `SqlAlchemyProjectRepository` mirroring the auth
repository's session-scoped style. `ProjectService.create_project` enforces the `PLATFORM_ADMIN`
check, generates a slug from the name (simple slugify, uniqueness enforced by a DB unique
constraint — collision handling out of scope, first-come wins with a 409 on integrity error,
matching the `IntegrityError` pattern in `auth/service.py`), and persists via the repository.
`ProjectService.list_accessible_projects` branches on `actor.platform_role`: `ADMIN_ROLE` gets
`list_all_in_session`, everyone else gets `list_for_member_in_session` (inner join on active
`Membership`). The router layer stays thin: parse/validate request, resolve the current user,
call the service, map `PermissionError` → `403`, `IntegrityError`/`ValueError` → `409`/`422` as
appropriate, serialize `ProjectRecord` → the `Project` schema.

## Test surface
- [x] Unit: `ProjectService.create_project` (admin succeeds, non-admin raises `PermissionError`),
      `ProjectService.list_accessible_projects` (admin sees all, member sees only their active
      memberships, inactive/absent membership excluded).
- [x] Integration: `POST /api/v1/projects` (admin 201, non-admin 403, missing name 422, name not
      persisted on rejection), `GET /api/v1/projects` (two-accessible/one-hidden scenario from
      the acceptance criteria, seeding `Membership` rows directly via the repository since no
      endpoint creates them yet).
- [ ] E2E: none — no UI for this story; project creation/listing is API-only at this stage.

## Out of scope
Restated from the story: any integration/tool binding (GitHub, Jira, etc. — `BHEEM-4`'s
`ProjectIntegrationBinding`), assigning additional project roles beyond what BEEM-12 itself
touches (BEEM-12 assigns none — first `PROJECT_MANAGER` mapping is BEEM-15's job per the story's
own notes, which supersedes the older "initial project-manager mapping created here" phrasing —
confirmed zero memberships at creation), workflow-policy pairing, run execution.

## Architecture impact
None — fits existing architecture. `Project` and `Membership` are already named in `data-model.md`
and `openapi.yaml`; this story is the first to give them a concrete persistence path.

## Dependencies discovered (feeds epic-sequence)
- Consumes: first platform-admin account (`platform_role = ADMIN_ROLE`) — produced by `BEEM-16`.
- Also consumes: nothing from `BEEM-14`/`BEEM-17` directly beyond the general authenticated-session
  mechanism already in place (`app/auth`), which those stories already produced and merged.
- Effect on sequence: matches the current provisional order (`BEEM-12` wave 4, depends on
  `BEEM-16` only) — no change needed. Note for the record: `BEEM-13`/`BEEM-15`/`BEEM-21` (wave 5)
  consume the `Project`/`Membership` tables this story creates, confirming their existing
  `depends_on: [BEEM-12]` edges (already firm per epic-sequence.json).

## Traceability
**Requirements covered:** FR-001, FR-002

---
*On approval: next step is `test-creator` (failing tests from these interfaces + the story's
acceptance criteria), then `implement`.*
