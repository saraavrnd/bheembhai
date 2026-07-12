# Design — Entities, State & the Three Overlays

The data model underneath the platform: the execution entities, the **fixed** state/result
vocabulary they move through, and the **three separate overlays** (workflow, policy, notifications)
that all key off that vocabulary. This is the concrete schema the other design docs assume.

Companion to `DESIGN-workflow-policy.md`, `DESIGN-control-plane.md`, `DESIGN-remote-results.md`.
Linked from `BUILD-PLAN.md`.

---

## The core realization: two axes, and an event log

Two things that are easy to conflate but must be separate:

- **Execution state** — *where a step is in its life* (pending → running → … → completed/failed).
- **Result status** — *what the skill decided* (completed / BLOCK / escalation_required / …).

A step can be execution-state `completed` **and** result-status `BLOCK` at once — two axes, not one.

And the load-bearing insight: **almost every feature is a reaction to a state transition** — so the
model needs a first-class **State-Transition Event Log**, not just "current state" on the row. That
log powers audit, notifications, metrics, and the run dashboard. Transitions are as important as
state.

---

## Fixed vocabularies (enums the whole platform relies on)

Fixed, not skill-extensible — the workflow routes on these, policy reacts to these, notifications
subscribe to these. A shared vocabulary is what lets all three overlays interoperate. Extend
deliberately later; never let a skill invent its own.

### Execution states (a Step/Attempt's lifecycle)
| State | Meaning |
|-------|---------|
| `pending` | created, not yet launched |
| `running` | container launched, executing |
| `awaiting_result` | container exited; Reconciler classifying (the reconciliation window) |
| `awaiting_approval` | completed, parked by a policy gate for a human |
| `retrying` | transient failure; a new attempt is spawned |
| `completed` | done successfully; workflow advanced |
| `failed` | terminal failure (after retries/escalation) |

### Result statuses (what a skill returns — the routing vocabulary)
| Status | Meaning | Typical routing |
|--------|---------|-----------------|
| `completed` | success / happy path | next step |
| `BLOCK` | hard gate failed (e.g. honest-green) | `route_to` (from result.json) |
| `changes_requested` | advisory findings (code-review) | loop back to implement |
| `escalation_required` | needs a higher-level step | e.g. → tech-design |
| `failed_execution` | skill errored — **deterministic** | escalate to human |
| `failed_infra` | OOM / node lost — **transient** | retry (capped) |
| `failed_timeout` | deadline / lease expired — **transient** | retry or escalate |
| `failed_incomplete` | exited but never reported | retry or escalate |

Result statuses carry a **retry class** (`transient` | `deterministic`) that drives the engine's
retry-vs-escalate decision.

---

## Execution entities

### Project
The top container. `id`, `name`, `repo`, **`workflow_ref`** (id+version), **`policy_ref`**
(id+version), **`notification_config_ref`**, integration/credential refs (GitHub etc.), members.

### Run
One execution of a workflow against a project. `id`, `project_id`, `workflow_ref`, `policy_ref`
(pinned versions at start — in-flight runs immune to later edits), `state`
(`queued`/`running`/`awaiting_approval`/`completed`/`failed`), `current_step`, `total_cost_usd`,
timestamps.

### Step
One node of the workflow within a run. `id`, `run_id`, `skill`, `execution_state`,
`latest_result_status`, `cost_usd` (rolled from attempts), the input `commit_id`/tag, output
`commit_id`/tag, timestamps.

### Attempt
One try at a step (retries create new attempts — this is the idempotency unit). `id`, `step_id`,
`attempt_no`, `container_ref`, `execution_state`, `result_status`, `retry_class`, `exit_code`,
`logs_ref`, `cost_usd`, `result_json_ref`, timestamps. **`(run_id, step_id, attempt_no)` is the
token** threaded through the whole control plane; results from superseded attempts are discarded.

### StateTransition (the event log — first-class)
Append-only. `id`, `run_id`, `step_id?`, `attempt_no?`, `from_state`, `to_state`, `result_status?`,
`actor` (system / user id), `reason`, `cost_delta?`, `timestamp`. **This table is the source for
audit, notifications, metrics, and the dashboard.** Everything reacts to rows landing here.

---

## The three overlays (all keyed off the same vocabulary)

### 1. Workflow — *what runs* (routes on result status)
Defined in `DESIGN-workflow-policy.md`. Entities: **Workflow** (id, version, steps) and each step's
**transition map** (`on: {result_status → target}`). Routes on the **result status** enum above.

### 2. Policy — *where humans gate* (reacts to `completed` + role)
Defined in `DESIGN-workflow-policy.md`. Entities:
- **Policy** — id, version, `applies_to` workflow.
- **Gate** — step id, `review: required`, required `role`. (Definition = the rule.)
- **Approval** (runtime) — `id`, `run_id`, `step_id`, `approver` (user), `decision`
  (`approve`/`request_changes`), `comment`, `timestamp`. (Event of satisfying the rule — distinct
  from the Gate definition; this is what audit + "who signed off" queries read.)
Policy reacts to a step reaching execution-state `completed`: gate present → `awaiting_approval`.

### 3. Notifications — *who gets told* (subscribes to state events) — separate overlay
Neither workflow (doesn't change what runs) nor policy (no approval, no gate) — a pure **observer**
on the event log. Entities:
- **NotificationConfig** — id, version, belongs to a project.
- **Subscription** — the rule: `on` (a state/result event, e.g. step `test-verify` →
  `BLOCK`, or run → `completed`), `channel` (`email`|`slack`), `target`, optional `role` (resolve
  to that role's members).
- **Target** — a **raw channel address** (an email, a Slack webhook/channel) **or** a user/role
  reference. **Raw targets need no user account** — so external stakeholders can be notified without
  logging into the platform.
- **NotificationEvent** (runtime) — `id`, subscription_id, triggering transition_id, channel,
  target, `status` (`sent`/`failed`/`retrying`), timestamp — for delivery audit + retry.

```yaml
# NotificationConfig (example)
notifications:
  - on: { step: test-verify, result: BLOCK }
    channel: slack
    target: "#dev-alerts"                 # raw channel — no account needed
  - on: { run: completed }
    channel: email
    target: role:owner                    # resolves to project owner(s)
  - on: { step: pr-create, result: completed }
    channel: email
    target: "stakeholder@partner.com"     # external non-user
```

**How it fires:** a row lands in StateTransition → the notification dispatcher matches it against
active Subscriptions → sends via the channel → records a NotificationEvent. Fully decoupled: adding/
changing who-gets-told never touches workflow or policy. (MVP: in-app + email; Slack next — same
subscription model, just another channel adapter.)

---

## How it all fits (one picture)

```text
Reconciler classifies Attempt  →  writes StateTransition (event log)
      │                                   │
      │                                   ├─→ Notifications: match Subscriptions → send (email/Slack, incl. external)
      │                                   ├─→ Audit: the log IS the audit trail
      │                                   ├─→ Metrics/dashboard: query current state + transition history
      │                                   └─→ Cost: roll attempt cost → step → run
      │
      ├─ result_status → Workflow.on[...] → next step target
      └─ step completed + Policy.gate? → Approval flow (awaiting_approval → Approval record)
```

Three overlays, one shared vocabulary, one event log feeding every feature. Each overlay is edited
independently; none reaches into another.

---

## Features and the entities they need (traceability)

| Feature | Reads/writes |
|---------|--------------|
| Human review gating | Policy.Gate → Run/Step `awaiting_approval` → Approval |
| Notifications (incl. external) | StateTransition → Subscription → NotificationEvent |
| Audit trail | StateTransition (append-only) + Approval |
| Cost roll-up | Attempt.cost → Step → Run.total_cost |
| Run dashboard | Run/Step current state + StateTransition history |
| Retry / escalate | Attempt.result_status + retry_class → new Attempt or escalate |
| Metrics/KPIs (later) | StateTransition history (cycle time, failure rate, cost/story) |

---

## What to build when (solo-friendly)
- **Phase 1:** Project, Run, Step, Attempt, StateTransition (event log — build it now, everything
  needs it), the fixed enums, Approval (single-reviewer), NotificationConfig + Subscription +
  NotificationEvent with **email + in-app** and **raw-target** support.
- **Phase 2:** Slack channel adapter; role-resolved targets; richer subscription matching.
- **Later:** metrics/KPI views over the transition log; per-skill status extension (deliberately).

## The rule
Two axes (execution state vs result status), both **fixed enums**. Three overlays (workflow /
policy / notifications) that never merge, all keyed off those enums. One append-only
**StateTransition** log as the single source that powers audit, notifications, metrics, and the
dashboard. Model the transitions, not just the states.
