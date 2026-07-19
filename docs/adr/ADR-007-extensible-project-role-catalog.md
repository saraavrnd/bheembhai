# ADR-007: Extensible project-role catalog

**Status:** Accepted · **Date:** 2026-07-19 · **Deciders:** saraav + user approval

## Context

`epic-review` on `BEEM-3` surfaced that the project-role vocabulary needs to cover the full
SDLC-phase role set (Business Analyst, Architect, Developer, QA, DevOps, Project Manager,
Reviewer) and that the platform needs to add new project-membership roles at runtime to scale
with business needs, without a schema change or redeploy. ADR-006 had already locked
`Membership.role` to a fixed, closed enum (`PROJECT_MANAGER, DEVELOPER, DEVOPS, REVIEWER`) and
explicitly rejected free-form roles ("approval checks need a stable vocabulary"). This ADR
amends that specific part of ADR-006; ADR-006's `request_changes` routing decision is unaffected
and still stands.

## Decision

Introduce a platform-wide `ProjectRole` catalog: `key` (stable identifier, primary key), `label`,
`is_system_default`, `created_at`. `Membership.role` (and `MembershipUpsertRequest.role`) become a
plain string validated against `ProjectRole.key` at the application layer, rather than an
OpenAPI-level enum — the JSON shape of `Membership` is unchanged, so this is not a breaking
change for any existing consumer.

Seed the catalog at first migration with 7 `is_system_default = true` rows: `PROJECT_MANAGER`,
`DEVELOPER`, `DEVOPS`, `REVIEWER` (already in use), plus `BUSINESS_ANALYST`, `ARCHITECT`, `QA`
(newly added).

New endpoints: `GET /roles` (list the catalog — lets any role picker, including `BEEM-15`'s,
populate dynamically instead of a hardcoded list) and `POST /roles` (add a new role). Only
`platform_role = PLATFORM_ADMIN` may call `POST /roles` — adding a role type is a platform-wide
governance action, distinct from assigning an existing role to a project member (which `BEEM-13`/
`BEEM-15` already allow `PROJECT_MANAGER` to do too).

The catalog is platform-wide, not per-project: every project draws from the same shared role
list. Nothing in the driving requirement asked for project-specific custom roles, and a shared
catalog is the simpler MVP shape; per-project custom roles can be a later amendment if a real
need for it shows up.

## Alternatives considered

- **Open string validated against a config/settings list (not DB-backed):** rejected — this is
  exactly what ADR-006 already ruled out (no stable, queryable vocabulary; adding a role still
  means a config/deploy change, not true runtime extensibility).
- **Grow the fixed enum to 7 values, defer runtime extensibility:** rejected as insufficient —
  the driving requirement explicitly asked for the ability to add roles at runtime, and a fixed
  (even larger) enum still requires a schema change per new role.
- **Per-project custom role catalogs:** rejected for now — no story or stated requirement needs
  project-specific roles; adds scoping/ownership complexity (uniqueness per project vs. global,
  per-project role-management UI) the MVP doesn't need yet.

## Consequences

- Adding a new project role becomes a data operation (`POST /roles`), not a code change —
  satisfies the "scale with business needs" requirement directly.
- `Membership.role`'s JSON shape is unchanged, so `BEEM-12`/`BEEM-13`/`BEEM-15` (and any other
  story already written against `role: string`) don't need to change their contracts, only their
  story text's assumed value set.
- `ProjectRole` is a natural home for future role-level metadata (e.g., an "eligible to approve"
  flag) without another migration — relevant to the still-open BHEEM-8 approval-eligibility gap
  `epic-review` flagged for BEEM-15.
- Referential integrity now depends on `ProjectRole` existing before a `Membership` can reference
  it; the seed migration must run before any membership is created, and `POST /roles` must be
  idempotent-safe against key collisions.
- If a genuine need for per-project custom roles emerges later, this ADR would need a follow-up
  amendment (`ProjectRole.project_id` nullable, scoping rules) rather than a rewrite.
