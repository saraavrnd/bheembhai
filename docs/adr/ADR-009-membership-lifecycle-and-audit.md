# ADR-009: Membership lifecycle — removal, deactivation, and audit trail

**Status:** Accepted · **Date:** 2026-07-19 · **Deciders:** saraav + user approval

## Context

A second `epic-review` pass on `BEEM-3` (see `docs/product/epics/BEEM-3/_epic/epic-review.md`,
Pass 2, Gap 6) found that `Membership` was add-only: `BEEM-15` (post-Pass-1) only covered
assigning/upserting a `Membership.role`. There was no way to remove a member's access entirely, no
way to temporarily suspend access without losing role history, and no schema support for either
(`Membership` had no status field, and there was no `DELETE` endpoint) — despite the user's stated
requirement that project members be manageable as "added / deleted / inactive."

Separately, the architecture already treats every privileged, governance-relevant action as
part of one immutable audit spine: `StateTransition` records runs, steps, attempts, approvals, and
notifications (NFR-007, NFR-013). Membership changes — who gets access to a project and what role
they hold — are exactly this kind of action, and were the one privileged surface silently left out
of that pattern.

## Decision

1. Add `Membership.is_active` (boolean, default `true`) to `data-model.md` and to the `Membership`
   / `MembershipUpsertRequest` schemas in `openapi.yaml`. The existing `POST
   /projects/{projectId}/members` upsert (keyed by `userId`) is extended to also accept/return
   `isActive`, so the same endpoint handles assigning a role, reactivating, and deactivating.
2. Add `DELETE /projects/{projectId}/members/{userId}` for hard removal — the membership row is
   deleted outright. Addressed by `userId` (not a separate `membershipId`) to match the existing
   upsert's addressing scheme; `Membership` is already uniquely keyed by `(project_id, user_id)`.
3. Extend `StateTransition.subject_type` to include a new `"membership"` value. This requires no
   schema change — `subject_type` is already a free discriminator column — but every membership
   assign, removal, and deactivation must now append a `StateTransition` row (`from_state`/
   `to_state` describing the role/active-state change, `actor_id` the admin or project manager who
   made it), the same way run/step/attempt/approval mutations already do.

## Alternatives considered

- **Skip auditing membership changes for MVP:** rejected — it breaks the "every privileged action
  is audited" pattern the platform already commits to elsewhere (NFR-013 explicitly wants
  "immutable audit reconstruction"), and membership assignment/removal is precisely the kind of
  governance action that pattern exists for.
- **Model removal as another status value (`REMOVED`) instead of a real `DELETE`:** rejected —
  `BEEM-15`'s acceptance criteria explicitly distinguish "the membership record is deleted" from
  "the membership record is retained... inactive" as two different member-facing behaviors. A true
  `DELETE` keeps the live `Membership` table lean; nothing is lost since `StateTransition` is now
  the durable history of the removal regardless.
- **Address removal by `membershipId` instead of `userId`:** rejected — it would require exposing
  `Membership.id` in URLs and break symmetry with the existing upsert endpoint, for no benefit
  given the `(project_id, user_id)` uniqueness constraint already in place.

## Consequences

- `Membership` gains one new column (`is_active`); `StateTransition` gains a new valid
  `subject_type` value — both additive, no breaking change to existing rows or consumers.
- Any code path that currently treats "a `Membership` row exists" as equivalent to "has active
  project access" — notably `BEEM-12`'s project-list visibility check and `BEEM-13`'s
  workflow-policy-pairing eligibility check — must be updated to also require `is_active = true`.
  This is flagged as a consequence for those stories' own `story-design`/`code-review` to catch;
  it is not a rescoping of either story's stated scope, so it is not rewritten in `stories.md`
  here.
- `BEEM-15`'s own `story-design` still needs to confirm read-path behavior this ADR doesn't
  decide: whether an inactive membership remains visible (with its inactive state shown) in `GET
  /projects/{projectId}/members`, whether reactivating an inactive membership is in scope, and
  whether removing/deactivating a project's last remaining `PROJECT_MANAGER` should be blocked —
  all three were already flagged as open in `BEEM-15`'s out-of-scope section and remain open here.
- `architecture.md`'s audit-spine description is updated alongside this ADR to name membership as
  a covered subject type, consistent with runs/steps/attempts/approvals/notifications.
