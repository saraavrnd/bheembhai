# Data Model

**Status:** Scaffolded · **Date:** 2026-07-10

This file captures the core entity set so story-level design and implementation can stay aligned
with the approved architecture.

## Core entities

| Entity | Purpose | Key fields |
|--------|---------|------------|
| User | Local identity and authentication subject | id, email, password_hash, platform_role |
| Project | Governed workspace and approval boundary | id, name, slug |
| Membership | Project-scoped role mapping | id, user_id, project_id, role, is_active |
| ProjectRole | Platform-wide catalog of assignable project roles | key, label, is_system_default, created_at |
| IntegrationProvider | Provider catalog entry | id, integration_type, provider_name, config_schema |
| ProjectIntegrationBinding | Project-selected provider binding | id, project_id, integration_type, provider_id |
| WorkflowVersion | Versioned workflow definition | id, project_id, version, status |
| PolicyVersion | Versioned policy definition | id, project_id, version, status |
| NotificationConfiguration | Project notification policy | id, project_id, trigger, channels |
| NotificationSubscription | Run-scoped recipient snapshot | id, run_id, recipient_email, role, trigger |
| NotificationEvent | Notification dispatch log | id, run_id, subscription_id, event_type, status |
| Run | A governed execution instance | id, source_issue_key, workflow_version_id, policy_version_id, status |
| Step | A workflow step inside a run | id, run_id, step_key, execution_state, latest_result_status |
| Attempt | One execution attempt for a step | id, step_id, attempt_number, status, exit_reason |
| StateTransition | Append-only lifecycle event | id, subject_type, subject_id, from_state, to_state, actor_id |
| Approval | Review decision record | id, run_id, reviewer_id, decision, comment |
| Artifact | Output persisted by a run or attempt | id, run_id, step_id, storage_ref, kind |

## Relationships

- A `User` can belong to many `Project`s through `Membership`.
- `Membership.role` references `ProjectRole.key` — a platform-wide, extensible catalog rather than
  a fixed enum, so new roles (e.g. beyond the seeded `PROJECT_MANAGER`, `DEVELOPER`, `DEVOPS`,
  `REVIEWER`, `BUSINESS_ANALYST`, `ARCHITECT`, `QA`) can be added without a schema change. Only
  `platform_role = PLATFORM_ADMIN` may add a new `ProjectRole` (see ADR-007).
- A `Project` holds no tool references of its own — GitHub, Jira, and any other integration
  category are exclusively linked through `ProjectIntegrationBinding`; a `Project` can bind many
  integration providers, but only one active binding per integration type (see ADR-008).
- `Membership.is_active` distinguishes a suspended member (row retained, access revoked) from a
  removed one (row deleted outright); any check for "does this user have active project access"
  must test `is_active = true`, not just row existence (see ADR-009).
- A `Run` belongs to one `Project` and one pinned workflow/policy pair.
- A `Run` has many `Step`s, each `Step` has many `Attempt`s.
- `StateTransition` stores the immutable history for runs, steps, attempts, approvals,
  notifications, and — as of ADR-009 — membership changes (`subject_type = "membership"`:
  assign, remove, deactivate).
- `NotificationSubscription` snapshots the intended recipients when the run starts.

