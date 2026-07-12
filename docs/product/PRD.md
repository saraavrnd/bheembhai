# PRD — BeemBhai

**Status:** Draft · **Owner:** TBD · **Last updated:** 2026-07-09

## 1. Problem & Opportunity

AI coding agents have made individual software development faster, but organizations still lack a governed, observable, team-scale way to orchestrate agents across the full product delivery lifecycle. Work remains siloed in terminals, approvals are manual or absent, costs are opaque, and agent execution is fragile when workflows pause for humans or run remotely. BeemBhai addresses this by turning reusable agent skills into backend-orchestrated, policy-governed, auditable workflows, starting with a story-to-PR SDLC flow and expanding later to the broader product success lifecycle.

## 2. Target Users

| User type | Primary need | Notes |
|-----------|--------------|-------|
| Product and engineering lead | Run governed product-development workflows across projects | Primary MVP buyer/user |
| Developer / agent operator | Execute skills safely against repositories | Needs reproducible, isolated runs |
| Reviewer / approver | Review gated outputs and approve or request changes | May be technical or business user |
| Platform / DevEx admin | Configure integrations, policies, runtimes, and credentials | Owns governance and safety |
| Executive / business stakeholder | Understand progress, cost, ROI, and product-readiness signals | Later scope beyond MVP |

## 3. Goals & Success Metrics

- G1 — Deliver a working governed story-to-PR workflow from story design through PR creation.
- Metric: 90% of MVP demo runs complete or stop at an intentional approval gate without manual backend intervention.
- G2 — Make agent execution auditable and cost-visible.
- Metric: 100% of completed MVP runs show step history, approval history, artifacts, and total model cost.
- G3 — Keep agent, model, and runtime choices replaceable.
- Metric: MVP code exposes one contract each for agent runner, model proxy, and execution runtime.
- G4 — Preserve human control over high-risk steps.
- Metric: 100% of policy-gated steps require an authorized approval before the workflow continues.

## 4. Scope

**In scope (MVP):** project setup, GitHub integration, secure credential storage, workflow and policy definitions stored as versioned DB records, backend-owned orchestration, isolated step execution, result reconciliation, role-based single-reviewer approvals, run dashboard, state-transition audit log, Langfuse tracing, per-step cost capture, email notifications only, local auth with email verification and password reset, and one implementation each for agent runner, model proxy, and local container runtime.

**Out of scope (Later / explicitly not now):** multi-tenant SaaS billing, user-authored workflow builder UI, Jira/Azure integrations, multi-reviewer quorum policies, Slack and other non-email notification channels, Codex/OpenCode adapters, multiple model providers beyond the initial proxy wiring, and non-engineering workflows for marketing, sales, support, finance, RevOps, KPI tracking, and ROI synthesis.

## 5. Feature Areas

| Area code | Feature area | One-line description |
|-----------|--------------|----------------------|
| FA-1 | Projects, Users & Access | Manage projects, users, roles, and allowed workflow-policy pairings. |
| FA-2 | Integrations & Secrets | Connect external systems through pluggable providers without exposing credentials. |
| FA-3 | Workflow & Policy Configuration | Define what runs and where human governance applies. |
| FA-4 | Orchestration Engine | Execute workflow steps, route outcomes, and resume after gates. |
| FA-5 | Agent Runtime & Artifacts | Run agent skills in isolated containers and persist outputs. |
| FA-6 | Approvals & Collaboration | Let authorized humans approve, reject, or escalate gated steps. |
| FA-7 | Observability, Audit & Cost | Trace, audit, and cost every run and step. |
| FA-8 | Platform Expansion & Administration | Prepare the platform for more tools, runtimes, skills, and SaaS controls. |

## 6. Functional Requirements

| ID | Feature area | Requirement (one testable capability) | Release |
|------|--------------|----------------------------------------|---------|
| FR-001 | FA-1 | The system shall allow an admin to create a project with a name and linked GitHub repository. | MVP |
| FR-002 | FA-1 | The system shall list all projects accessible to the signed-in user. | MVP |
| FR-003 | FA-1 | The system shall let an admin assign at least one version-pinned workflow-policy pairing to a project. | MVP |
| FR-004 | FA-1 | The system shall let a run user select only admin-approved workflow-policy pairings for a project. | MVP |
| FR-005 | FA-1 | The system shall support a minimal authenticated user identity with email/password login, email verification activation, and password reset flow. | MVP |
| FR-006 | FA-1 | The system shall support role-based approval eligibility. | MVP |
| FR-007 | FA-2 | The system shall define a pluggable provider interface for each integration category. | MVP |
| FR-008 | FA-2 | The system shall allow a project admin to select the active provider for each configured integration category. | MVP |
| FR-009 | FA-2 | The system shall store provider credentials in secure storage rather than plaintext project records. | MVP |
| FR-010 | FA-2 | The system shall inject scoped provider credentials into an execution attempt only at runtime. | MVP |
| FR-011 | FA-2 | The system shall validate that a configured code repository provider is reachable before saving it as active. | MVP |
| FR-012 | FA-2 | The system shall provide GitHub as the first code repository provider. | MVP |
| FR-013 | FA-2 | The system shall provide Claude Code as the first agent runner provider. | MVP |
| FR-014 | FA-2 | The system shall route LLM calls through LiteLLM as the first LLM integration provider. | MVP |
| FR-015 | FA-2 | The system shall provide Langfuse as the first observability provider. | MVP |
| FR-016 | FA-2 | The system shall provide email notification delivery for MVP and allow the run initiator to choose recipients when execution is triggered. | MVP |
| FR-017 | FA-2 | The system shall support Jira as a project management provider. | Later |
| FR-018 | FA-2 | The system shall support Azure DevOps as a code or project management provider. | Later |
| FR-019 | FA-2 | The system shall support at least one third-party transactional email provider. | Later |
| FR-020 | FA-2 | The system shall allow adding a new provider in an existing integration category without changing workflow definitions. | Later |
| FR-021 | FA-3 | The system shall load workflow definitions from versioned database records. | MVP |
| FR-022 | FA-3 | The system shall validate that every workflow step defines routing for supported result statuses. | MVP |
| FR-023 | FA-3 | The system shall load policy definitions separately from workflow definitions as versioned database records. | MVP |
| FR-024 | FA-3 | The system shall prevent a run user from weakening the policy bound to a selected workflow. | MVP |
| FR-025 | FA-3 | The system shall expose a UI for admins to create and edit workflow definitions. | Later |
| FR-026 | FA-3 | The system shall expose a UI for admins to create and edit policy definitions. | Later |
| FR-027 | FA-4 | The system shall create a run from a project, workflow-policy pairing, and free-form starting story input. | MVP |
| FR-028 | FA-4 | The system shall decompose each run into steps according to the selected workflow definition. | MVP |
| FR-029 | FA-4 | The system shall create a unique attempt identifier for every step execution attempt. | MVP |
| FR-030 | FA-4 | The system shall route the next step from structured result status rather than natural-language agent output. | MVP |
| FR-031 | FA-4 | The system shall park a run in `awaiting_approval` when policy requires human approval on a completed step. | MVP |
| FR-032 | FA-4 | The system shall resume a parked run after an authorized approval from a project user with the required role. | MVP |
| FR-033 | FA-4 | The system shall retry transient execution failures automatically up to 3 attempts per stage. | MVP |
| FR-034 | FA-4 | The system shall escalate deterministic failures without automatic retry. | MVP |
| FR-035 | FA-5 | The system shall launch each step attempt in an isolated disposable container. | MVP |
| FR-036 | FA-5 | The system shall pass run, step, attempt, repository, and skill context into each container. | MVP |
| FR-037 | FA-5 | The system shall require each container to publish a structured result message. | MVP |
| FR-038 | FA-5 | The system shall persist generated artifacts in Git and store stage execution results in the database. | MVP |
| FR-039 | FA-5 | The system shall reconcile container runtime status with published result messages. | MVP |
| FR-040 | FA-5 | The system shall classify missing or incomplete results as timeout, infrastructure, or incomplete failures. | MVP |
| FR-041 | FA-5 | The system shall support a runtime interface that can later swap local Docker for remote execution. | MVP |
| FR-042 | FA-5 | The system shall support additional agent runner adapters beyond the initial implementation. | Later |
| FR-043 | FA-6 | The system shall show approval requests for policy-gated steps. | MVP |
| FR-044 | FA-6 | The system shall let an authorized reviewer approve a gated step. | MVP |
| FR-045 | FA-6 | The system shall let an authorized reviewer request changes on a gated step. | MVP |
| FR-046 | FA-6 | The system shall record approval decisions with actor, timestamp, decision, and comment. | MVP |
| FR-047 | FA-6 | The system shall support multi-reviewer approval rules with quorum handling. | Later |
| FR-048 | FA-6 | The system shall notify configured recipients by email when a run reaches an approval gate or other configured execution event. | MVP |
| FR-049 | FA-7 | The system shall display an execution list with run status and, on selection, the stage results and captured artifacts for that run. | MVP |
| FR-050 | FA-7 | The system shall record every state transition in an append-only event log. | MVP |
| FR-051 | FA-7 | The system shall display per-step result status and artifact links. | MVP |
| FR-052 | FA-7 | The system shall route model calls through a model proxy for metering. | MVP |
| FR-053 | FA-7 | The system shall record per-step model cost in the step result. | MVP |
| FR-054 | FA-7 | The system shall roll up step costs into total run cost. | MVP |
| FR-055 | FA-7 | The system shall send execution traces to Langfuse or the configured observability backend. | MVP |
| FR-056 | FA-8 | The system shall allow projects to pin skill versions. | Later |
| FR-057 | FA-8 | The system shall enforce per-project or per-user cost budgets. | Later |
| FR-058 | FA-8 | The system shall support tenant-level data isolation. | Later |
| FR-059 | FA-8 | The system shall support metered billing based on recorded platform usage. | Later |
| FR-060 | FA-8 | The system shall support governed workflows for non-engineering product dimensions. | Later |

## 7. Non-Functional Requirements

| ID | Category | Requirement | Release |
|------|----------|-------------|---------|
| NFR-001 | Reliability | The orchestrator shall persist run state before launching each step attempt. | MVP |
| NFR-002 | Reliability | The platform shall detect container death without relying on the container to report it. | MVP |
| NFR-003 | Reliability | A resumed run shall not require the previous execution container to still exist. | MVP |
| NFR-004 | Security/Privacy | The platform shall never write integration credentials to logs, result messages, or generated artifacts. | MVP |
| NFR-005 | Security/Privacy | Step execution shall run with isolated filesystem and process boundaries per attempt. | MVP |
| NFR-006 | Security/Privacy | Runtime credentials shall be scoped to the project and action needed by the attempt. | MVP |
| NFR-007 | Auditability | Audit records shall be immutable through normal user-facing workflows. | MVP |
| NFR-008 | Observability | Every run and step shall have a correlation identifier visible in logs and traces. | MVP |
| NFR-009 | Performance | The API shall return a run creation response without waiting for agent execution to complete. | MVP |
| NFR-010 | Performance | The dashboard shall load the latest run state for a project within two seconds under MVP-scale load. | MVP |
| NFR-011 | Maintainability | Workflow, policy, notification, integration provider, agent runner, model proxy, observability, email, and runtime concerns shall remain separately configurable. | MVP |
| NFR-012 | Portability | The runtime abstraction shall not require business logic changes when moving from local to remote container execution. | MVP |
| NFR-013 | Compliance | The platform shall retain approval and state-transition history sufficient to reconstruct who approved what and when. | MVP |
| NFR-014 | Accessibility | User-facing workflow, dashboard, and approval screens shall be keyboard navigable. | MVP |
| NFR-015 | Scalability | The architecture shall allow additional stateless orchestrator workers to process queued jobs. | Later |
| NFR-016 | Tenant Isolation | Tenant data, workspaces, secrets, and observability records shall be isolated for SaaS deployments. | Later |

## 8. Constraints & Assumptions

- The MVP starts with SDLC workflows because the whitepaper says the core execution model is spike-proven there.
- The story-to-PR workflow is the first production flow: story-design -> test-creator -> implement -> test-verify -> code-review -> pr-create.
- Workflow and policy records are versioned in the database; runs pin the selected versions at creation time.
- GitHub is the first integration; Jira and Azure are deferred until the engine and secrets subsystem are stable.
- The backend is authoritative for routing; skill-provided next-step hints are advisory only.
- Execution states and result statuses use the fixed vocabularies defined in `docs/base/design_docs/DESIGN-entities-state.md`.
- Human approval policy is admin-bound and cannot be weakened by the run initiator.
- Approvals are granted by any project member who has the required role defined in policy.
- LiteLLM, Langfuse, one agent runner, and one container runtime are the initial implementations behind replaceable seams.
- MVP authentication uses local auth with email/password, email verification before activation, and password reset by emailed link.
- Admins can assign roles to users; users may have the same role across a project.
- Runs are triggered by users with ADMIN or DEVELOPER capability, create one branch per run, and commit at the end of each stage using store-id-based branch naming.
- Stage results are immutable after completion, and the full structured payload plus artifact references are stored in the database.
- Secrets are stored in Minio and artifacts are committed to Git.
- The first production-ready SDLC workflow is story-to-PR.
- The first agent runner implementation is Claude Code.
- The first deployable MVP routes model usage through LiteLLM for Claude Code.
- Audit logs, traces, and generated artifacts must be retained for at least 50 days.
- Cost governance should warn or stop usage at a $100 threshold when budget enforcement is added.
- Non-engineering dimensions are treated as later governed skill sets, often advisory and dependent on integrated business systems.

## 9. Open Questions

- How should `request_changes` route the workflow after a stage review is completed?

---
*Generated by the `prd` skill. Next step: run `prd-decompose` to turn feature areas into Jira epics.*
