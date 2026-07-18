# BheemBhai — Phased Build Plan (Platform Product)

From proven spike → shippable product, sequenced for a **solo, nights-and-weekends** builder. The
governing rule: each phase must be *usable on its own* and leave you with working software, so
momentum never depends on finishing everything. Scope is cut hard on purpose — the spike already
proved the hard part (backend-owned orchestration, suspend/resume across ephemeral containers).

Two locked architectural decisions this plan rests on:
- **Backend workflow is authoritative; skill `next` hints are advisory.**
- **Workflow-as-data + policy-as-overlay** — two separate declarative config layers.

---

## The one-line product

*A web app where a team configures a project, picks a workflow + policy, and runs the PDLC skills
as backend-orchestrated containerized steps — pausing for human review where policy demands, with
full audit and cost tracking.*

---

## Phase map at a glance

| Phase | Theme | Ships | Roughly |
|-------|-------|-------|---------|
| **0** | Harden the spike | The spike as a clean, restartable service; workflow-as-data | weeks |
| **1 (MVP)** | Skeleton + GitHub + engine + audit + **4 seams** | One project, one workflow, run end-to-end; LiteLLM proxy, Agent Runner (1 adapter), Langfuse, per-step cost | the big one |
| **2** | Multi-user + review + notifications | Real teams: roles, multi-reviewer, email/Slack | after MVP is used |
| **3** | Config surface + more tools + more adapters | Users edit workflows/policies; Jira/Azure; skill versioning; Codex/opencode adapters | scaling up |
| **4** | SaaS-readiness | Multi-tenant, budgets, billing, hardened secrets | when going external |

Build in order. Do **not** pull v2/v3 features into MVP — that's the scope trap that kills solo
projects. **Note the seams in Phase 1 are "design the interface + wire ONE implementation," not
"build every provider/agent"** — see "Abstraction layers" below.

---

## Phase 0 — Harden the spike into a service (do this first)

You have a working spike; make it a foundation you can build on without rewrites.

- Consolidate the spike backend into one clean **FastAPI** service: `/runs` create, get, events,
  approve, comments (already designed).
- **Workflow-as-data:** move the hardcoded `story-design → … → pr-create` sequence into a
  declarative workflow file the backend *interprets* (YAML/JSON), not backend `if/else`. This is
  the single most important thing to get right now — it's the product's core and painful to
  retrofit. See "Engine design" below.
- **Policy-as-overlay:** the two policies (`fast`/`strict`) become a separate config that *layers
  on* the workflow (marks which steps gate on human review), not baked into the sequence.
- Persist run state in **SQLite** (fine until Phase 4). Keep engineering artifacts in Git.
- **Exit criterion:** you can define a workflow + policy as data files, POST a run, and watch it
  execute/suspend/resume — with routing driven by `result.json`, not code.

---

## Phase 1 — MVP: skeleton + GitHub + engine + audit

The thinnest thing a real (internal) user can run a project through. Four slices:

### 1a. Platform skeleton (thin)
- Projects (name, repo, workflow, policy) — CRUD.
- Minimal auth — single-user or your company SSO. **No multi-tenant, no role system yet.**
- A run dashboard: list runs, status, where each stopped, cost.

### 1b. One integration, done properly: GitHub
- Only GitHub (your skills already use it). **Skip Jira/Azure for MVP.**
- **Secrets done right from day one** (it's security-critical, not deferrable): per-project GitHub
  token stored encrypted, injected into the container at runtime as env, **never logged**, never in
  `result.json`. This subsystem is small now and horrible to retrofit — build it correctly here.

### 1c. The orchestration engine (the differentiator)
- The backend runs the workflow-as-data: each step → a disposable container → validate
  `result.json` → route on status (`completed`/`checkpoint_pending`/`BLOCK`/`escalation_required`/
  `failed`).
- **Backend owns routing** (authoritative); skill `next` hints are advisory only.
- Suspend/resume across ephemeral containers (proven in the spike).
- **Container failure-path (build with the happy path, not after):** every phase guarded; catchable
  failures publish a classified `result.json`; uncatchable death detected via runtime status + lease;
  transient→auto-retry (capped), deterministic→escalate; side-effecting steps made idempotent;
  controller owns the DB write. See `DESIGN-remote-results.md`.
- **Single-reviewer** approval only (one person approves at a checkpoint). Multi-reviewer is v2.
- **The four seams (design interface + one impl each — see "Abstraction layers"):**
  - **LiteLLM proxy** as the mandatory model-call choke-point (wire Anthropic; providers later).
  - **Agent Runner interface** with one adapter (`ClaudeCodeRunner`; Codex/opencode later).
  - **Langfuse** for traces/observability from the first real runs.
  - **Per-step cost** as a `result.json` field, sourced from the LiteLLM proxy (nearly free once
    the proxy is mandatory), rolled up per run.

### 1d. Audit (basic but first-class)
- Every transition persisted: prev state → next state, trigger, result status, who approved, cost,
  timestamp. Your spike already records transitions — make it a queryable audit log, not just
  internal state.

**MVP exit criterion:** from a browser, an internal user creates a project pointed at a GitHub repo,
starts a workflow under a chosen policy, watches it stream, approves at the story-design and PR
gates, sees it resume in fresh containers, and reads the per-run cost and a full audit trail.

**Explicitly NOT in MVP:** multi-user roles, multi-reviewer, email/Slack, Jira/Azure, user-editable
workflows (they're data files you edit for now), budgets, billing, multi-tenancy, and **extra agent
adapters / extra LLM providers** — the seams are *designed* and wired with one implementation each
in MVP (Claude Code + Anthropic-via-LiteLLM), but Codex/opencode and other providers are Phase 3.

---

## Phase 2 — Real teams: users, roles, review, notifications

Once the MVP core is used and trusted, add the human-collaboration layer.

- **User management + roles** (items 3, 5) — and crucially, **wire roles into policy**: a policy
  gate can require "a QA-role member approves test-verify" or "a lead approves the PR." Roles are
  an *input to policy*, not a cosmetic label. Design them together.
- **Multi-reviewer approval** (item 10.2) — the genuinely hard one. Decide and build: assignment
  (who reviews), quorum (all / majority / any-one), split-decision handling (one approves, one
  requests changes), and timeout (reviewer unavailable → escalate, don't wait forever). Treat this
  as a real feature with its own design, not a checkbox.
- **Notifications** (item 10.1) — start **in-app only**, then add email, then Slack. Fire on stage
  completion and "your review is requested." Don't start with Slack; it's the fiddliest.

**Exit criterion:** a multi-person team runs a project where the right people are notified and must
review at policy-defined gates, including a multi-reviewer gate.

---

## Phase 3 — Config surface + more tools + skill versioning

Turn the data-files into a UI, and broaden reach.

- **Workflow & policy editing in the UI** (items 8, 10.3) — users compose workflows (add/reorder
  steps, set on-pass/fail/blocked routing) and policies (which gates need whom) *without editing
  files*. This is where item 10.3's "customize what's next on pass/fail/blocked" becomes a product
  feature. It's only safe to expose *after* the engine is proven (Phase 1) and roles exist (Phase 2).
- **More integrations** (item 4): Jira, then Azure — each via the secrets subsystem from 1b. Each
  new tool is "add credentials + the MCP wiring," now a repeatable pattern.
- **More agent adapters + LLM providers** (Seams 1 & 2): add `CodexRunner` / `OpenCodeRunner` behind
  the Agent Runner interface, and add providers behind the LiteLLM proxy — both are now
  "implement-behind-an-existing-interface," cheap because the seams were designed in Phase 1.
- **Skill management + versioning** (items 6, 7): projects pin a **skill version**; upgrades are
  deliberate, not automatic (a skill change must not silently break a customer's workflow). This is
  the piece the original list under-specified — design pinning now.

**Exit criterion:** a non-technical lead builds a custom workflow + policy in the UI, attaches Jira
and pinned skills, and runs it.

---

## Phase 4 — SaaS-readiness (when you go external)

Only when moving from internal tool to SaaS product.

- **Multi-tenancy** — real tenant isolation across data, workspaces, and containers.
- **Cost governance / budgets** (gap) — per-project/per-user budgets and hard limits, or a runaway
  workflow burns your API-key money. Urgent the moment external users touch it.
- **Billing** — plans, metering (you already track cost per run — meter on it).
- **Hardened secrets + compliance** — secret rotation, per-tenant isolation, audit export, the
  security posture external customers demand.
- **Scale the runner** — move from local Docker to a real orchestrator (K8s/ECS) and a durable job
  queue.

---

## The three cross-cutting things the original 11 points missed

Fold these in at the phase noted — they're not optional:
1. **Secrets management** — Phase 1b (GitHub), extended each time you add a tool. Security-critical.
2. **Cost governance / budgets** — Phase 4, but keep per-run cost capture from Phase 1 so budgets
   have data to enforce on. With LiteLLM as the mandatory choke-point (Seam 1), the per-call cost
   data budgets need is already there — enforcement (limits, alerts) is the Phase 4 addition.
3. **Failure/retry taxonomy + container failure-path** — introduce in Phase 1 (the engine needs it),
   mature in Phase 2. Two halves: (a) **catchable** failures — the container guards every phase
   (INIT/EXEC/COMMIT/PUBLISH) and still **publishes a classified `result.json`** (`failed_init` /
   `failed_execution` / `failed_commit` / `BLOCK`) with a `transient|deterministic` retry hint, so a
   caught error is reported, never silent; (b) **uncatchable** death (OOM/kill/node-loss) — detected
   by the **runtime exit status + lease**, never the container. Controller retries **transient**
   (capped, fresh `ATTEMPT_NO`, same input commit) and **escalates deterministic** to a human.
   Workspace is safe by construction (retry re-checks-out the input commit); **side-effecting steps
   (`pr-create`, Jira/GitHub) must be idempotent themselves** to survive retry without double-acting.
   Make the **controller the single source of truth** (it writes the DB on consuming the queue
   message) to avoid DB-vs-queue split-brain. Full mechanism + failure-path flow in
   `DESIGN-remote-results.md`.

---

## Abstraction layers — the four seams (design early, implement one each)

Four boundaries make the platform provider/agent/observability-agnostic. The **philosophy is the
same as the spike**: put an interface at a boundary so the thing behind it is swappable and
observable. Your spike already established this pattern (backend + structured contracts + disposable
workers) — these extend it to four more boundaries.

**Solo-builder rule for all four: design the *seam* now (cheap), wire *one* implementation, defer
the rest.** Designing the interface early is nearly free and saves a painful retrofit; implementing
every provider/agent now is the scope trap. So: interface in Phase 0/1, one impl behind it, expand
in Phase 3+.

### Seam 1 — Model provider: LiteLLM as the single choke-point (Phase 1)
**Every model call routes through a LiteLLM proxy — mandatory, no exceptions.** This one decision
buys three things at once: provider-agnosticism (swap/multi-source Anthropic, OpenAI, Bedrock,
local without code changes), centralized keys/rate-limits/fallbacks, and — critically — **per-call
cost metering tagged with run/step id** (see Seam 4). Make it mandatory *from the start*: if any
path bypasses the proxy, you lose the cost choke-point and the agnosticism. Phase 1 wires one
provider (Anthropic) behind it; adding providers later is proxy config, not code.
- **Caveat to respect:** LiteLLM abstracts *direct API calls*. Whether a coding *agent* (Claude
  Code) routes through it depends on the agent honoring a base-URL override — verify per agent
  (Seam 2). LiteLLM is the *model* layer; the agent is a *separate* layer.

### Seam 2 — Agent runtime: an Agent Runner interface (Phase 1 interface, Phase 3 adapters)
Make the coding agent interchangeable (Claude Code / Codex / opencode). Your spike already made this
feasible by moving orchestration out of the agent — each step is now "run a skill in a container,
read `result.json`," so the agent is already a swappable worker. Define one contract:
```text
AgentRunner.run(skill, workspace, inputs, secrets, model_endpoint) ->
    { events_stream, exit_code, result_json_path }
```
Then `ClaudeCodeRunner`, `CodexRunner`, `OpenCodeRunner` are adapters behind it. The backend hands a
step to *a* runner and reads the structured result — it doesn't know which agent ran.
- **The cost this imposes (be honest):** skills must stay to a **common denominator** — no
  dependence on Claude-Code-only features, or agnosticism breaks. This disciplines skill design.
- Phase 1: define the interface, implement **only `ClaudeCodeRunner`**. Phase 3: add Codex/opencode
  adapters. Designing the seam now is cheap; retrofitting after skills grow agent-specific is not.

### Seam 3 — Observability: Langfuse (Phase 1)
Self-hosted Langfuse for traces, per-step spans, prompt/response capture, latency, and cost in one
place. This **upgrades and partly replaces** the CLI's hand-rolled OTEL receiver — right for a CLI,
wrong for a multi-project platform. Introduce in Phase 1 (you want observability from the first real
runs).
- **SaaS caveat:** Langfuse captures prompts/completions = customer code and data. Self-hosted
  (already your choice) is required for data-residency; it becomes a component you operate.
- Pairs with Seam 1: route model calls through LiteLLM *and* trace them in Langfuse → full picture.

### Seam 4 — Per-step cost: a cost interface in the step contract (Phase 1)
This resolves the open problem: the persistent-OTEL-receiver model **does not survive per-step
ephemeral containers**. Fix: cost becomes a **defined field each step produces**, sourced not from
scraping OTEL in a dying container but from the **LiteLLM proxy** (every call metered + tagged with
run/step id) and/or **Langfuse** (cost per trace). The backend rolls step costs up to the run.
- With LiteLLM as the mandatory choke-point (Seam 1), per-step cost is **almost free** — the proxy
  already meters every call by run/step. This is the cleanest cost architecture and the reason to
  make the proxy mandatory.
- `result.json` carries `cost_usd` (or an explicit `cost_unavailable` record); backend aggregates.

### How the four fit together
```text
Backend (workflow-as-data + policy overlay)
  → hands a step to an AgentRunner (Seam 2)
      → agent runs the skill in a disposable container
          → ALL model calls go through LiteLLM proxy (Seam 1)
              → metered per run/step (Seam 4) + traced in Langfuse (Seam 3)
      → writes result.json (incl. cost) + human artifact
  → backend validates result, rolls up cost, routes on status
```
Three of the four (1, 2, 4) are the *same move* — an interface at a boundary — and all four reuse
the spike's contract-driven philosophy.

## Engine design notes (the core to get right in Phase 0/1)

**Workflow-as-data + policy-as-overlay** — two **separate** declarative structures. **Workflow** =
the state machine (steps + on-status routing; the backend *interprets* it, never `if/else`; skill
`next` hints are advisory, the workflow is authoritative). **Policy** = a thin governance overlay
(which steps require human approval + required role; it never adds/removes/reorders steps). Same
workflow + different policy = same steps, different stop points. They join only at the Reconciler's
"is there a gate on this completed step?" check. Boundary test for ambiguous rules: *if removing it
changes which steps run, it's workflow; if it only changes where a human intervenes, it's policy.*
MVP scope: linear+branch workflow, gates-only policy. **Full formats + examples + deferred
expressiveness: `DESIGN-workflow-policy.md`.**

**Entities, state & the notification overlay** — two fixed enums (execution state vs result status),
the execution entities (Project / Run / Step / Attempt), and an append-only **StateTransition event
log** that is the single source powering audit, notifications, metrics, and the dashboard.
**Notifications are a *third* overlay** (parallel to workflow + policy) — a subscription layer over
the event log that can target **raw email/Slack addresses with no user account**, so external
stakeholders get told on chosen state/result events without merging notification logic into flow or
governance. **Full entity model: `DESIGN-entities-state.md`.**

**Cost in the ephemeral model** — the persistent-receiver OTEL model from the CLI tooling doesn't
survive per-step containers, so cost becomes part of the step contract (Seam 4). Best source: the
**LiteLLM proxy** meters every model call tagged by run/step (nearly free once the proxy is
mandatory), and/or **Langfuse** cost-per-trace. Each step emits `cost_usd` in `result.json` (or an
explicit `cost_unavailable`); the backend rolls step costs up to the run. Prefer proxy-sourced cost
over any in-container scraping.

**Remote results & container-death reconciliation** — `result.json`-on-shared-disk is a
single-machine convenience, not a distributed contract. For remote execution, the result travels by
**queue** (large artifacts to object storage, pointer in the queue), the **exit/liveness comes from
the container runtime** (Docker Engine API, local or remote) — never from the container itself,
since a crashed container can't report its own death — and a **reconciler** cross-references result +
runtime status + lease against a deadline to classify every step. Design this from Phase 1 (read
nothing from shared local disk; `attempt_id` idempotency from day one) so remote execution is a
config change, not a re-architecture. **Full design: `DESIGN-remote-results.md`.**

**Control plane / orchestrator** — the components above the container: the **API** enqueues a job
and returns; **Orchestrator workers** consume jobs and **launch containers fire-and-forget** (no
blocking waits); a **Watcher** observes each container's fate from outside (polling the runtime for
exit status now, event-driven later) and consumes the result queue; a **Reconciler** joins the two
signals via the decision table and enqueues the next job (advance / retry / escalate) or parks the
run at a checkpoint. Jobs create containers; container outcomes create jobs — one loop, all
components stateless against DB + queue truth, so it scales by adding workers and is identical local
or remote. **Full design: `DESIGN-control-plane.md`.**

---

## Solo-builder guardrails (so this actually ships)

- **One phase in flight at a time.** Finish and *use* it before starting the next.
- **Each phase ends with working software** you could demo. No phase is "half a rewrite."
- **Resist the pull of v2 features into MVP** — multi-review, Slack, Jira, UI workflow-editing all
  *feel* essential and are all deferrable. The MVP proves the loop; the rest is enhancement.
- **The engine is the moat — spend your best energy there** (Phase 1c), not on CRUD screens
  (skeleton) which you should build as thin as humanly possible.
- Revisit **capacity** at each phase boundary: Phase 4 (SaaS) realistically wants more than solo
  nights-and-weekends. That's the natural point to seek help/funding — don't start it alone.
```
