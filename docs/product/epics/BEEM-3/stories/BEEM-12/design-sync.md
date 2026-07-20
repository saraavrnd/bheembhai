# Design Sync — BEEM-12: Create and list accessible projects

**Date:** 2026-07-20 · **Branch:** `feat/BEEM-12-create-and-list-projects` · **Classification:** No system-level change

## What this story changed (vs current design)
Implemented `GET /projects` and `POST /projects` and gave the `Project`/`Membership` entities a
concrete SQLAlchemy + Postgres persistence path (`app/projects/repository.py`,
`app/projects/service.py`, `app/projects/router.py`), plus an Alembic migration
(`migrations/versions/20260720_0001_create_projects_and_memberships_tables.py`) mirroring the
existing `users` table pattern. Both endpoints match the request/response shapes already
committed in `docs/api-contracts/beembhai-api.openapi.yaml` (`Project`, `ProjectCreateRequest`)
exactly, and both entities were already named in `docs/data-model.md`. This story is the first to
back them with real code — no endpoint shape, field, or relationship changed from what was
already designed.

## Reference updates committed to this branch
- [ ] `architecture.md` — no change (contract already anticipated this)
- [ ] `data-model.md` — no change (entities already named)
- [ ] `api-contracts/` — no change (contract already matched exactly)
- [x] `AGENTS.md` — "Current state" note updated: `app/auth/` and `app/projects/` are real,
      tested modules now, not stubs; the other modules (`integrations`, `runs`, `approvals`,
      `config`, `notifications`) remain stubs.
- [x] `docs/CHANGELOG-design.md` — entry appended for 2026-07-20.

## Affected in-progress stories (flagged for design re-check)
Checked Jira (`project = BEEM AND status in ("In Progress", "In Review")`): only BEEM-12 itself is
in either state. BEEM-13/BEEM-15/BEEM-21 (the stories that will consume the `Project`/`Membership`
tables per `epic-sequence.json`) are all still To Do — nothing to flag.

| Story | Overlap (module / endpoint / entity) | Action |
|-------|--------------------------------------|--------|
| — | none in progress | none needed |

## Structural-change check
None — change was incremental / within the existing architecture. The endpoints and entities were
already fully specified in the committed design; this story only added their first implementation.

---
*Docs committed to the branch; `pr-create` proceeds to merge them atomically with the code.*
