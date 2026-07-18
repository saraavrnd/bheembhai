# BheemBhai Epics

Decomposed from [PRD.md](docs/product/PRD.md) for Jira project `BHEEM`.

## Epic 1: Project access, identity & run ownership

**Jira issue:** `BEEM-3`

**Feature area:** FA-1 Projects, Users & Access  
**Release:** MVP  
**Goal:** An admin can create projects, assign roles, and users can register, sign in, verify email, reset passwords, and own runs and approvals with clear access boundaries.

**Covered requirements**
- FR-001
- FR-002
- FR-003
- FR-004
- FR-005
- FR-006

**Labels**
- `fa-1`
- `mvp`

## Epic 2: Integration providers & secrets vaulting

**Jira issue:** `BHEEM-4`

**Feature area:** FA-2 Integrations & Secrets  
**Release:** MVP  
**Goal:** The platform can select active providers per integration category, validate core providers, inject scoped credentials only at runtime, and keep secrets out of plaintext records.

**Covered requirements**
- FR-007
- FR-008
- FR-009
- FR-010
- FR-011
- FR-012
- FR-013
- FR-014
- FR-015
- FR-016
- FR-017
- FR-018
- FR-019
- FR-020
- NFR-004
- NFR-006

**Labels**
- `fa-2`
- `mvp`

## Epic 3: Versioned workflow & policy definitions

**Jira issue:** `BHEEM-5`

**Feature area:** FA-3 Workflow & Policy Configuration  
**Release:** MVP  
**Goal:** Workflow and policy definitions are stored as versioned database records, validated, and enforced so runs cannot weaken the admin-selected governance model.

**Covered requirements**
- FR-021
- FR-022
- FR-023
- FR-024
- FR-025
- FR-026

**Labels**
- `fa-3`
- `mvp`

## Epic 4: Workflow orchestration & retry control

**Jira issue:** `BHEEM-6`

**Feature area:** FA-4 Orchestration Engine  
**Release:** MVP  
**Goal:** A run can be created from free-form input, decomposed into steps, parked for approval, retried automatically up to the stage limit, and failed cleanly when execution cannot recover.

**Covered requirements**
- FR-027
- FR-028
- FR-029
- FR-030
- FR-031
- FR-032
- FR-033
- FR-034
- NFR-001
- NFR-003
- NFR-009

**Labels**
- `fa-4`
- `mvp`

## Epic 5: Isolated skill execution & artifact persistence

**Jira issue:** `BHEEM-7`

**Feature area:** FA-5 Agent Runtime & Artifacts  
**Release:** MVP  
**Goal:** Each step attempt runs in isolation, receives the right context, emits structured results, writes artifacts to Git, and records step execution data durably for traceability.

**Covered requirements**
- FR-035
- FR-036
- FR-037
- FR-038
- FR-039
- FR-040
- FR-041
- FR-042
- NFR-002
- NFR-005
- NFR-012

**Labels**
- `fa-5`
- `mvp`

## Epic 6: Human approvals & stage collaboration

**Jira issue:** `BHEEM-8`

**Feature area:** FA-6 Approvals & Collaboration  
**Release:** MVP  
**Goal:** Policy-gated steps surface approval requests, authorized project-role members can approve or request changes, decisions are recorded, and the UI remains usable for the review workflow.

**Covered requirements**
- FR-043
- FR-044
- FR-045
- FR-046
- FR-047
- FR-048
- NFR-014

**Labels**
- `fa-6`
- `mvp`

## Epic 7: Run observability, audit trail & cost accounting

**Jira issue:** `BHEEM-9`

**Feature area:** FA-7 Observability, Audit & Cost  
**Release:** MVP  
**Goal:** Runs show current state, step history, artifact links, and cost while the system records an immutable transition log and routes traces to the observability backend.

**Covered requirements**
- FR-049
- FR-050
- FR-051
- FR-052
- FR-053
- FR-054
- FR-055
- NFR-007
- NFR-008
- NFR-010
- NFR-013

**Labels**
- `fa-7`
- `mvp`

## Epic 8: Platform expansion & administration readiness

**Jira issue:** `BHEEM-10`

**Feature area:** FA-8 Platform Expansion & Administration  
**Release:** Later / mixed  
**Goal:** The platform keeps the seams open for future skills, budgets, SaaS isolation, and admin-oriented expansion without collapsing the current orchestration model.

**Covered requirements**
- FR-056
- FR-057
- FR-058
- FR-059
- FR-060
- NFR-011
- NFR-015
- NFR-016

**Labels**
- `fa-8`
- `later`
- `mixed`

## Traceability Notes

- Every FR/NFR in the PRD is assigned to exactly one epic above.
- MVP epics are intended to be broken into stories next.
- `request_changes` routing remains an open workflow decision and is intentionally left for a later clarification pass.

## EPICs - Dependencies

| Order | Epic | Depends on | Parallelizable? | Reason |
|---|---|---|---|---|
| 1 | **Epic 1: Project access, identity & run ownership** | None | No | This is the base trust layer. We need users, projects, roles, and ownership before anything else can be safely configured or executed. |
| 2 | **Epic 3: Versioned workflow & policy definitions** | Epic 1 | Yes, after Epic 1 | Workflow and policy records are foundational configuration, and they can be built alongside integrations once identity and project access exist. |
| 3 | **Epic 2: Integration providers & secrets vaulting** | Epic 1 | Yes, after Epic 1 | This establishes shared platform seams like GitHub, secrets, LiteLLM, and observability. It can proceed in parallel with workflow definitions. |
| 4 | **Epic 4: Workflow orchestration & retry control** | Epics 1, 2, 3 | Limited | Core orchestration depends on identity, pinned workflow/policy definitions, and integration plumbing. It should start only after the foundation is in place. |
| 5 | **Epic 5: Isolated skill execution & artifact persistence** | Epic 4, plus Epic 2 plumbing | Limited | The executor needs orchestration to trigger it and integrations to provide runtime context, Git persistence, and result handling. |
| 6 | **Epic 6: Human approvals & stage collaboration** | Epic 4, Epic 5 | Limited | Approvals matter once real runs can pause at gates and resume from actual execution states. |
| 7 | **Epic 7: Run observability, audit trail & cost accounting** | Epics 4, 5, 6 | Yes, partially | The audit and cost model should be wired throughout, but the full dashboards and rollups are best finished after end-to-end runs exist. |
| 8 | **Epic 8: Platform expansion & administration readiness** | MVP foundation | Yes, but later only | This is explicitly later/mixed scope and should wait until the MVP flow is stable. |
