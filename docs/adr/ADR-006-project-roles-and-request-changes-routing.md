# ADR-006: Project-scoped roles and request-changes routing

**Status:** Partially superseded by ADR-007 (2026-07-19) — the fixed `Membership.role` enum and
its "free-form roles rejected" rationale are replaced by an extensible `ProjectRole` catalog. The
`request_changes` routing decision below is unaffected and still stands. · **Date:** 2026-07-10 ·
**Deciders:** Codex + user approval

## Context

The PRD calls for role-based approval eligibility, local auth, and a single-reviewer approval model.
The user also asked for project roles such as `PROJECT_MANAGER`, `DEVELOPER`, and `DEVOPS`. The
workflow needs a deterministic rule for `request_changes`.

## Decision

Use a global `User.platform_role` for platform administration and a project-scoped `Membership.role`
enum for day-to-day governance. For MVP, `request_changes` sends the run back to the immediately
previous step, which creates a new attempt for that step while preserving the review record and the
older attempt history.

## Alternatives considered

- Keeping roles as free-form strings was rejected because approval checks need a stable vocabulary.
- Making all roles global was rejected because governance is project-specific in the MVP.
- Routing `request_changes` to a separate rework queue was rejected because it adds complexity the
  first workflow does not need.

## Consequences

- Approval checks can be enforced consistently across the UI, API, and worker.
- The model supports project-manager, developer, devops, and reviewer style access without
  overfitting to a single organization structure.
- A rejected review has a deterministic path back into the workflow, which keeps the engine simple
  for the MVP.

