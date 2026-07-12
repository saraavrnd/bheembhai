# Design — Remote Result Transport & Container-Death Reconciliation

How a skill step's result gets from a container (local **or** on a remote machine) back to the
BheemBhai controller reliably — including the case where the container **crashes before reporting**.
This is the operational heart of the platform; it ties together three things flagged separately: the
`result.json` contract, the failure/retry taxonomy, and remote execution.

Linked from `BUILD-PLAN.md` (Phase 0/1 engine work).

---

## The problem in one sentence

`result.json`-on-shared-disk works only because the controller and container share a filesystem.
The moment the container runs on a **remote** machine, "read the file it wrote" breaks — so we must
separate the **result contract** (keep as-is) from the **result transport** (must change), and we
must be able to detect a container that **died without reporting**.

## The one principle that drives the whole design

**A component cannot report its own death.** A container that segfaults, gets OOM-killed, or whose
machine is yanked **cannot send a "I failed" message** — it's already gone. Therefore:

> Crash detection must come from **outside** the container — from the thing that launched it and
> outlives it (the container runtime). Never ask the container "did you crash?"; ask the **runtime**
> "is it alive, and how did it exit?"

This forces the result and the exit status to come from **two independent sources**.

---

## The three signals (from three sources)

Every step is classified by cross-referencing three things, arriving from three places:

| Signal | Source | Tells us | Survives a crash? |
|--------|--------|----------|-------------------|
| **Result payload** | the container → **queue** | what it produced (success / handled error + `result.json` contents) | No — only exists if it lived |
| **Exit / liveness** | the **runtime** (Docker Engine API) | did it exit, with what code; is it still running | **Yes** — the runtime watches the child die |
| **Lease / heartbeat** | the container → controller, periodically | "still working" (for long steps) | No — absence *is* the signal |

The result payload alone is never trusted to mean "done," and its **absence** is never interpreted
alone — it's always cross-referenced with the runtime's exit status.

---

## Component: the Runtime abstraction (your stated requirement)

Your requirement — *"manage Docker on a remote machine and get the launched container's exit
status"* — is exactly this interface. Keep it thin; it answers only two questions:

```text
Runtime.launch(image, cmd, env, mounts, token) -> container_handle
Runtime.status(container_handle) -> { state: running|exited|gone, exit_code?: int }
```

- **First implementation: Docker Engine API** — identical locally (Unix socket) or remotely
  (TCP/TLS). Point it at a different endpoint; nothing above it changes.
- **Swappable later:** a K8s/ECS adapter behind the same interface if you outgrow raw Docker — the
  reconciler above doesn't change. (Same "design the seam, wire one impl" rule as the other
  abstraction layers.)
- **`state: gone`** = the runtime can't find the container at all (node lost, OOM reaped) — treated
  as an infra crash.

The reconciler sits **above** this interface and needs nothing more than `status()` + the queue.

---

## Transport: queue for the result, object storage for large artifacts

- **Result payload → queue.** On finish, the container publishes a small message to the result
  queue, keyed by `run/step/attempt` token: `{ token, status, result_json | error, artifact_ref? }`.
  The controller consumes it.
- **Large artifacts → object storage** (MinIO/S3), not the queue. If a step produces big output, it
  writes the artifact to object storage and puts only a **pointer** (`artifact_ref`) in the queue
  message. Queues are for signals, not payloads.
- **Exit code → runtime**, never the queue (a crashed container can't enqueue its exit code).

---

## The reconciler: the decision table (the core logic)

The controller tracks each step's three signals against a **deadline** and classifies:

| Runtime status | Result on queue? | Conclusion | Action |
|----------------|------------------|------------|--------|
| exited 0 | yes | **Success** | validate payload → route on it |
| exited 0 | no (within grace) | **Wait** | short grace window — publish can lag exit |
| exited 0 | no (after grace) | **`failed_incomplete`** | exited clean but never reported → failure; keep logs |
| exited ≠0 | yes (handled error) | **Handled failure** | route on the error the container reported |
| exited ≠0 | no | **Crash** | `failed_incomplete` → retry/escalate |
| running past deadline | no | **Timeout** | kill container → `failed_timeout` |
| running, lease expired | no | **Hung/dead early** | kill → `failed_timeout` (caught faster than deadline) |
| gone (OOM/node lost) | no | **Infra failure** | `failed_infra` → retry (likely transient) |

**The insight:** "no result" has *three different causes* (bug that didn't report / crash /
still-running-timeout) and *three different responses* — distinguishable **only** because the runtime
status is a second, independent signal. Same symptom, cross-referenced to a cause.

---

## Lease / heartbeat (for long-running steps)

A skill step can run many minutes. A single final deadline is too coarse — a hung container would
hold a slot for the whole timeout. So:

- The container **renews a lease** every N seconds (a heartbeat: "still working, turn 12").
- If the lease **expires** (no heartbeat for N), the controller declares it dead **without** waiting
  for the full deadline — catching "the machine froze" fast.
- The heartbeat is an **independent liveness signal**: even if runtime `status()` lags, a missing
  heartbeat flags trouble. Belt and suspenders.
- Keep N generous enough that a legitimately busy step (a long model call) doesn't false-expire —
  tune against real step durations.

---

## Idempotency: surviving retries and zombies (do not skip)

Once you retry failed steps, a classic hazard appears: the controller thinks a container died and
retries it, but the "dead" one was merely slow — now **both** publish a result.

- Every attempt gets a unique **`attempt_id`** (part of the `run/step/attempt` token).
- The controller tracks the **currently-live attempt** per step. It accepts a queue result **only**
  for that attempt; results from **superseded attempts are discarded** (logged, not applied).
- This makes late/duplicate results harmless — a zombie container's belated success can't corrupt a
  run you'd already retried.
- Same token also lets object-storage artifacts be namespaced per attempt (no overwrite races).

---

## End-to-end flow (local and remote, identical)

```text
1. Controller: create run/step/attempt token; record "attempt live".
2. Runtime.launch(agent image, skill cmd, env incl. token + queue target + result-bucket creds).
3. Container runs the skill via the agent; renews lease every N seconds.
4a. Graceful: container publishes { token, status, result_json | error, artifact_ref? } to queue,
    writes any large artifact to object storage, exits.
4b. Crash: container dies — NO queue message. Runtime.status() will report exited≠0 or gone.
5. Controller reconciles (decision table) using: queue result (maybe absent) + Runtime.status()
   + lease + deadline.
6. Classify → route per workflow/policy. Discard results from non-live attempts.
```

This flow is **byte-for-byte the same whether the container is local or on a remote Docker host** —
the only thing that changes is the Runtime endpoint. That is the property that makes it scale.

---

## Container failure-path behavior (the unhappy paths)

The happy path (INIT → execute → commit → publish) is only half the design. The container must
behave correctly when things go wrong, and — because a container **cannot report its own death** —
the system splits failure handling into two halves: what the container reports for **catchable**
failures, and what the **runtime + reconciler** infer for **uncatchable** ones.

### Two classes of failure

**Catchable (the container is still alive to report):** Git checkout failed, context/prompt
missing, the code agent returned an error, validation of its own output failed, a commit failed.
→ The container's job: **still publish a `result.json`, with a failure status and a reason**, so the
controller learns *why*, not just *that*. A caught failure is a normal, reported outcome — not
silence.

**Uncatchable (the container is dead and cannot report):** OOM-kill, `SIGKILL`, node/machine lost,
kernel panic, network partition mid-publish. → The container reports **nothing**. Detection is the
**runtime's** job (exit status / "gone") plus the **lease** expiring, reconciled per the decision
table above. Never expect a message from a dead container.

### What the container does on a catchable failure (wrap every phase)

Each phase (INIT, EXECUTE, COMMIT, PUBLISH) runs inside a guard. On a caught error, the container:
1. **Classifies** the failure into a status:
   - `failed_init` — couldn't set up (checkout/context/secret retrieval failed). Usually
     **transient** (retry may fix) — but a bad COMMIT_ID is **deterministic** (retry won't).
   - `failed_execution` — the agent ran but errored/produced invalid output. Often
     **deterministic** (same input → same failure); flag for escalation rather than blind retry.
   - `BLOCK` / `escalation_required` — not a failure: a *handled* control outcome the skill emits
     (e.g. test-verify BLOCK). Reported normally, routed by policy.
   - `failed_commit` — work done but couldn't persist to Git. **Transient**, safe to retry (the
     input commit is unchanged; redo is clean).
2. **Captures diagnostics** — writes logs / the agent's error output to object storage under the
   `run/step/attempt` key (not into the queue message; keep that small).
3. **Publishes `result.json` with the failure status**, `reason`, `retry_hint`
   (`transient` | `deterministic`), and a `logs_ref`. Then exits **non-zero**.
4. **Emits a `failed`/`error` trace to Langfuse** so the failure is observable, not just logged.

So a catchable failure produces the SAME transport as success — a queue message keyed by attempt —
just with a failure status. The controller routes it via the workflow/policy on-fail branch.

### What the runtime + reconciler do on an uncatchable death

No queue message arrives. The reconciler (decision table above) uses runtime status + lease +
deadline to classify:
- exited non-zero, no result → **crash** → `failed_incomplete`.
- gone / OOM / node lost → **`failed_infra`** (transient — retry likely fixes).
- running past deadline / lease expired → **`failed_timeout`** (kill, then retry or escalate).
The controller then applies the retry policy — **without** ever having heard from the container.

### Retry classification (transient vs deterministic)

The controller decides retry from the failure class, not blindly:
- **Transient** (`failed_init` non-deterministic, `failed_commit`, `failed_infra`,
  `failed_timeout`) → **auto-retry**, capped (e.g. max 2), fresh container, new `ATTEMPT_NO`, same
  input COMMIT_ID.
- **Deterministic** (`failed_execution`, bad-commit `failed_init`, repeated failure of a
  "transient" class past the cap) → **do NOT blind-retry**; halt the step and **escalate to a
  human** (surface the reason + logs in the UI). Retrying a deterministic failure just burns money
  on the same failure.

### Idempotency across a retry (the parts that must be safe)

Because a retry launches a fresh container on the same input commit:
- **Workspace is safe by construction** — checkout of the input COMMIT_ID reproduces the exact
  starting state; uncommitted work from the dead attempt is simply gone and re-done. Clean.
- **External side effects are NOT automatically safe** — a step that opened a PR or transitioned
  Jira before dying could be redone by the retry → double-action. **Side-effecting steps
  (`pr-create`, anything touching Jira/GitHub state) must be idempotent themselves**: before
  acting, check "does this PR/transition already exist for this run/step?" and no-op if so. Mark
  which steps are side-effecting; design those defensively.

### The two-writes ordering (DB vs queue)

The container does two writes at the end (update DB, publish to queue). To avoid "DB says done but
no queue signal" silent stalls, make the **controller the single source of truth**: the container
**publishes to the queue only**; the **controller** writes the DB record when it consumes the
message. One writer, one ordering, no split-brain. (If the container must write the DB directly,
publish to the queue *last* and treat the queue — not the DB — as the completion signal, so a
half-done container never looks "done.")

### Failure-path flow (mirror of the happy path)

```text
INIT ─guard→ fail? → classify(failed_init) → logs→storage → result.json(fail) → queue → exit≠0
EXEC ─guard→ fail? → classify(failed_execution|BLOCK|escalation) → logs → result.json → queue → exit
COMMIT ─guard→ fail? → classify(failed_commit) → result.json(fail) → queue → exit≠0
PUBLISH fails, or container KILLED anywhere above →
        NO message → runtime exit status + lease expiry → reconciler → failed_incomplete|infra|timeout
Controller → retry (transient, capped, new ATTEMPT_NO) OR escalate to human (deterministic)
```

### The rule
Every phase is guarded and reports a *classified* failure on the same transport as success; the
container never dies silently on a *catchable* error; and for *uncatchable* death, detection is the
runtime's job, not the container's. Design this from Phase 1 alongside the happy path — the failure
paths are where the majority of production incidents live.

---

## What to build when (solo-friendly)

- **Phase 0/1 (now):** Runtime interface over the **Docker Engine API** (local endpoint first, but
  coded as if remote — no shared-disk reads). Result via queue keyed by `run/step/attempt`. The
  reconciler decision table. **Final-deadline** timeout. `attempt_id` idempotency from day one (it's
  cheap now, brutal to retrofit). **Container failure-path from day one too:** guard every phase,
  publish classified failures on the queue, controller-owns-the-DB-write (single source of truth),
  and side-effect idempotency for `pr-create`-type steps. Happy path and failure path are one
  design, not two projects.
- **Phase 1/2:** add the **lease/heartbeat** for long steps; object-storage artifact + logs handoff;
  mature the transient-vs-deterministic retry policy (caps, escalation-to-human UI).
- **Later (scale):** point the Runtime at **remote** Docker hosts (config change, not code); a
  K8s/ECS adapter behind the same interface only if you outgrow raw Docker.

## The rule to hold onto
Design every step of the result path **as if the container is already remote and might be dead** —
read nothing from shared local disk, and classify "no result" only against an independent runtime
signal. Do that from Phase 1 and remote execution is a config change, not a re-architecture.
