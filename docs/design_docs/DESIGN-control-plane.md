# Design — Control Plane / Orchestrator

How a request from the API becomes a running container, how the container's outcome is observed
(including crashes), and how that outcome drives the next step. This is the **control plane** that
sits above the container — referenced throughout the build plan but specified here.

Companion to `DESIGN-remote-results.md` (the result transport + reconciliation decision table).
Linked from `BUILD-PLAN.md` (Phase 0/1 engine work).

---

## One correction that shapes the whole design

The two signals used to classify a step arrive on **two different channels — not both on the queue**:

- **Result payload** → the **container publishes to the result queue** (only if it's alive).
- **Exit status** → a **Watcher polls the container runtime** (Docker API) from outside — this works
  **even when the container crashes**, because a dead container can't publish anything.

Putting the exit status on the queue *via the container* would reintroduce the crash-blindness we
designed against. Keep them on separate channels; the Reconciler joins them.

---

## Components (all stateless except DB + queues)

| Component | Job | State |
|-----------|-----|-------|
| **API** | Validate request; create/advance Run in DB; enqueue a **job**; return fast. Handle approve/comment (enqueue an "advance" job). | none (writes DB) |
| **Job queue** | Backlog of `start-run` / `advance-run` jobs. | the backlog |
| **Orchestrator worker(s)** | Consume jobs; read workflow-as-data + policy; decide the next step; **launch** its container (fire-and-forget); record "running". | none (all in DB) |
| **Runtime interface** | `launch()` / `status()` over Docker API (local or remote). | none |
| **Result queue** | Containers publish `result.json` here. | in-flight results |
| **Watcher** | Poll runtime status of in-flight containers; consume the result queue; record both signals against the step. | none (writes DB) |
| **Reconciler** | Join result + exit + lease/deadline via the decision table; classify each step; enqueue the next job (or park for a checkpoint). | none |
| **DB** | Single source of truth: run/step/attempt state. Controller writes it (never the container directly, per the result design). | the truth |

Everything except DB + queues is **stateless and horizontally scalable** — add workers for more
concurrency. That's what makes the control plane scale to remote/at-scale execution.

---

## Q3 — How an API request becomes a job someone picks up

Standard **producer → queue → worker**:

1. **API** receives "start run" (or an approval). It does **not** do the work: it validates, writes
   a **Run** record (`status = queued`) to the DB, **enqueues a `start-run` job**, and returns
   immediately. The HTTP call is fast; work happens asynchronously.
2. An **Orchestrator worker** (one of a pool) consumes the next job. Any free worker can take any
   job because all state is in the DB — that's the horizontal-scale property.
3. The worker reads the workflow-as-data + policy, decides the **next step**, and launches its
   container. Then it's free for the next job.

**Who picks up the job:** an Orchestrator worker, pulled from the job queue, stateless.

---

## Q1 — Launch without blocking (Launcher vs Watcher)

A step can run many minutes — **nothing should block a thread waiting for it.** Split the roles:

- **Launcher** (inside the Orchestrator worker): `Runtime.launch(image, cmd, env incl.
  run/step/attempt token + result-queue target + secrets ref)`; record "step X attempt N running on
  container C" in the DB; **return**. Fire-and-forget. The worker moves on.
- **Watcher** (separate, always-running loop): observes outcomes of all in-flight containers. It
  learns a container exited by **polling** `Runtime.status(C)` on an interval (works on any Docker,
  local or remote) — with an **event-driven** upgrade later (subscribe to Docker/orchestrator events
  to react instantly instead of polling; poll remains the fallback). The Watcher also consumes the
  **result queue**. Whichever signal arrives (exit status or result message), it records it against
  the step in the DB.

No thread is parked per container; launch is fire-and-forget; a separate Watcher observes fates.

---

## Q2 — Who reconciles the two signals

The **Reconciler** — kept as a **separate component from the Watcher** (Watcher = *observe and
record signals*; Reconciler = *decide what the signals mean and what to do next*). Clean separation:
the Watcher has no policy logic; the Reconciler has no I/O with containers.

Per step, the Reconciler has three inputs landing asynchronously — **result-on-queue**,
**exit-status**, **lease/deadline** — and applies the decision table (from
`DESIGN-remote-results.md`):
- exit 0 + result → **success** → route on the result (next step per workflow/policy).
- exit 0 + no result (after grace) → **`failed_incomplete`**.
- gone / OOM → **`failed_infra`** (transient).
- running past deadline / lease expired → **`failed_timeout`**.
- exit ≠0 + result(handled error / BLOCK) → route on the reported status.

On a terminal classification it **enqueues the next job** (`advance-run`): success → next step;
failure → retry (transient, capped, new `ATTEMPT_NO`) or escalate-to-human (deterministic); a
**checkpoint** → park the run (`awaiting_approval`) and enqueue nothing until the approval arrives.

> **Solo-build pragmatics:** Watcher and Reconciler are *designed* as two components (cleaner, and
> they scale independently), but you can run them **in one process** initially — two loops, one
> deployable — so you don't pay an ops cost while solo. Split them into separate services when scale
> demands. The clean separation now means that split is later a deployment change, not a rewrite.

---

## The whole cycle (it's one loop)

```text
API: validate → write Run(queued) → enqueue start-run job → return
      │
      ▼
Orchestrator worker: consume job → read workflow+policy → decide next step
      → Launcher: Runtime.launch(container, token, result-queue, secrets) → record "running" → free
      │
      ▼  (asynchronously, no one blocking)
Container: runs skill → publishes result.json to RESULT QUEUE  (or dies silently)
      │
      ▼
Watcher: polls Runtime.status(C) [+ consumes result queue] → records exit + result signals in DB
      │
      ▼
Reconciler: join(result, exit, lease/deadline) via decision table → classify step
      ├─ success        → enqueue advance-run (next step)
      ├─ transient fail  → enqueue advance-run (retry, new ATTEMPT_NO, capped)
      ├─ deterministic   → park run, surface to human (escalate)
      └─ checkpoint      → park run (awaiting_approval)
      │
      ▼
(advance-run job) → Orchestrator worker picks it up → … loop until DONE or human gate
```

Jobs create containers; container outcomes create jobs. The **Reconciler is the bridge** that turns
"a container finished or died" back into "here's the next job." Human checkpoints and approvals are
just runs **parked** until an approval enqueues the next advance-job — the same loop, paused.

---

## Why this shape (the properties it buys)

- **No blocking waits** → thousands of concurrent long-running steps without thread-per-container.
- **Crash-safe** → exit status comes from the Watcher polling the runtime, never from the (possibly
  dead) container.
- **Horizontally scalable** → API, workers, watcher, reconciler are stateless; scale by adding
  instances; all truth in DB + queues.
- **Local == remote** → only the Runtime endpoint changes; the control plane is identical.
- **Resumable/parkable** → a run is just DB state + a job; checkpoints and crashes both resolve to
  "park, then enqueue an advance-job later." Suspend/resume falls out for free.

---

## What to build when (solo-friendly)

- **Phase 0/1:** API-enqueues-job; **one** Orchestrator worker; Launcher (fire-and-forget) +
  **Watcher by polling**; Reconciler with the decision table; Watcher+Reconciler **in one process**;
  a real job queue + result queue (even Redis lists to start); DB as source of truth. `ATTEMPT_NO`
  threaded through from day one.
- **Phase 2:** capped retry policy + escalation-to-human UI; lease/heartbeat feeding the Reconciler.
- **Scale:** multiple Orchestrator workers; split Watcher/Reconciler into separate services;
  **event-driven** runtime notifications replacing polling; remote Docker endpoints; K8s/ECS runtime
  adapter behind the same interface.

## The rule
Launch fire-and-forget; observe fate from outside the container (Watcher); decide centrally
(Reconciler); drive everything as jobs on a queue against DB truth. Then local and remote are the
same system, and the control plane scales by adding stateless workers.
