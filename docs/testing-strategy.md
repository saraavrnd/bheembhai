# Testing Strategy

**Status:** Approved · **Date:** 2026-07-10

The testing strategy is TDD-first. For every story, the acceptance criteria are translated into
failing tests before the implementation work starts. The goal is to keep the workflow engine,
approvals, audit trail, and notification behavior correct at the boundaries where regressions would
be expensive.

## Flow

1. Write the story's acceptance criteria in testable form.
2. Encode those criteria as failing tests.
3. Implement the smallest change that makes the tests pass.
4. Add regression tests for any bug fix.
5. Keep the tests close to the requirement IDs they prove.

## Layers

| Layer | Runner | What it covers |
|------|--------|----------------|
| Unit | pytest | Domain rules, validators, role checks, routing decisions, notification matching, and small adapter behavior. |
| Integration | pytest against the deployed Docker Compose stack | API behavior, persistence, routing, state transitions, and service-to-service boundaries exercised through the running containers. |
| API contract | pytest against the generated OpenAPI schema | Request and response validation, enums, and status codes. |
| End-to-end | pytest-playwright + Playwright against the deployed Docker Compose stack | Login, project setup, dashboard views, approval actions, and run inspection in a real browser. |

## Test coverage by feature

| Area | Minimum coverage |
|------|------------------|
| Identity and access | Login, email verification, password reset, role enforcement, project membership checks |
| Integrations | Jira/GitHub selection, Brevo config validation, secure secret persistence, runtime secret injection |
| Workflow and policy | Version pinning, routing rules, policy gate enforcement, request changes loopback |
| Orchestration | Run creation, step decomposition, retry cap, resume after approval, deterministic failure escalation |
| Execution | Attempt lifecycle, runtime death detection, result reconciliation, artifact persistence |
| Approvals | Approve and request changes, comment capture, timestamping, reviewer authorization |
| Observability | State-transition append-only behavior, correlation IDs, cost rollup, trace propagation |
| UI | Loading, empty, error, success states, responsive layout, keyboard operability |

## Canonical test cases

- A project admin can create a project, connect GitHub and Jira, and bind a workflow-policy pair.
- A run created from a source issue key is visible in the project list and the run list.
- A gated step parks the run until an authorized reviewer approves it.
- `request_changes` returns the workflow to the immediately previous step and records the decision.
- A transient container failure creates a new attempt up to the configured retry cap.
- A dead container is detected by runtime status, not by the container reporting its own death.
- Notification subscriptions snapshot recipients at run creation time and dispatch events when the configured transition occurs.
- Stage costs roll into the run total and appear in the dashboard.
- The state-transition log is append-only.

## Test data and fixtures

- Use factory helpers for pure unit tests, but prefer real HTTP calls for integration tests.
- Seed a small fixed workflow for the story-to-PR path so orchestration tests remain readable.
- Keep external adapters behind test doubles unless the test is explicitly an integration or e2e test running against the deployed stack.
- Use deterministic timestamps and IDs in unit tests where possible.

## What we do not test by default

- External provider uptime.
- Brevo delivery success outside the adapter boundary.
- GitHub or Jira production behavior beyond adapter contract checks.
- Human judgment quality on approval comments.

Those are integration boundaries, not app code responsibilities.

## Deployment-backed test rule

- Integration and end-to-end tests should run against the Docker Compose deployment used by the
  local development stack, not against `TestClient` or a local app subprocess, unless a story
  design explicitly documents a narrower exception.
- The deployed API should be treated as the system under test for request/response behavior,
  persistence, routing, and browser journeys.
- Unit tests remain in-process and may still use fakes or direct object construction.
