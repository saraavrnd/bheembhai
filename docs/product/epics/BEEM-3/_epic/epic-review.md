# Epic Review — BEEM-3: Project access, identity & run ownership

**Status:** APPROVED (2 passes) · **Date:** 2026-07-19 · **Stories reviewed:** BEEM-17, BEEM-18, BEEM-19, BEEM-16, BEEM-12, BEEM-13, BEEM-14, BEEM-15, BEEM-21

> Audit trail for the cross-story gap drill run on BEEM-3. **Pass 1** ran right after `user-story`
> produced all eight original stories and before any of BEEM-12/13/15 reached `story-design`.
> **Pass 2** ran after the user separately observed, while looking at the shipped project-list/
> project-create surface, that project *editing*, tool-category scalability, and membership
> add/remove/inactive lifecycle all looked thinner than the rest of the epic — this section covers
> that second pass.

## Pass 1 — role catalog & dependency-note gaps

### Context loaded
- All 8 BEEM-3 stories from `stories.md` (BEEM-17, 18, 19, 16, 12, 13, 14, 15) — full set.
- `epic-map.json` — BEEM-3 covers FR-001 through FR-006.
- `docs/api-contracts/beembhai-api.openapi.yaml` — `User.platformRole` enum
  `[PLATFORM_ADMIN, STANDARD]`; `Membership.role` enum
  `[PROJECT_MANAGER, DEVELOPER, DEVOPS, REVIEWER]`; `POST /projects/{projectId}/members` (upsert).
- `docs/product/PRD.md` — FR-006 wording ("role-based approval eligibility"); line 144 ("Approvals
  are granted by any project member who has the required role defined in policy").
- `docs/product/epics.md` — epic-number-to-Jira-key mapping (Epic 3 Policy = `BHEEM-5`, Epic 6
  Human approvals = `BHEEM-8`).
- `docs/product/epics/BEEM-3/_epic/epic-sequence.md`/`.json` — confirms `BEEM-16` is already a
  firm upstream dependency for `BEEM-12`/`BEEM-13`/`BEEM-15` in the computed build order.
- `docs/product/epics/BEEM-3/stories/BEEM-16/story-design.md` — BEEM-16 already shipped, verified
  (PASS), design-synced; its own notes name BEEM-12/13/15 as consumers of the seeded admin.
- Checked `BHEEM-5` and `BHEEM-8`'s `epic-map.json` entries only far enough to confirm neither
  currently lists FR-006 — relevant to the coverage gap below.

### Gaps found

#### Gap 1 — Cross-story actor & role consistency
- **Stories touched:** BEEM-12, BEEM-13, BEEM-15.
- **What was missing/ambiguous:** All three used "admin"/"project admin" as an actor with no enum
  mapping. Neither `User.platformRole` nor `Membership.role` has an `ADMIN` value.
- **Question asked (round 1):** Is "admin" always `platformRole = PLATFORM_ADMIN`, or can a
  `PROJECT_MANAGER` also perform these actions?
- **Answer (round 1):** Reword all three to `PLATFORM_ADMIN`.
- **Follow-up asked (round 2):** Given the user also said `PROJECT_MANAGER` can edit project
  details (role mapping, integrations) — a direct tension with round 1's answer — which actor(s)
  does each of BEEM-12/13/15 actually require?
- **Answer (round 2):** BEEM-12 = `PLATFORM_ADMIN` only (project creation; no membership exists
  yet to hold a `PROJECT_MANAGER`). BEEM-13 and BEEM-15 = `PLATFORM_ADMIN` **or**
  `Membership.role = PROJECT_MANAGER` for that project.
- **Resulting change:** BEEM-12's actor/preconditions reworded to `platform_role =
  PLATFORM_ADMIN` only. BEEM-13 and BEEM-15's actor/preconditions reworded to
  "`platform_role = PLATFORM_ADMIN`, or `Membership.role = PROJECT_MANAGER` for this project."

#### Gap 2 — Epic-wide scope boundary (BEEM-15 conflated assignment with enforcement)
- **Stories touched:** BEEM-15 (and flags a coverage question for `BHEEM-8`).
- **What was missing/ambiguous:** BEEM-15's ACs 2–5 (eligible/ineligible reviewer approves,
  non-member rejected, approval chooser) all assume a gated-step/workflow concept that isn't
  built in this epic (or anywhere yet) and depend on the required-role-per-step mapping that
  `PRD.md` places in the policy epic (`BHEEM-5`).
- **Question asked:** Should BEEM-15 shrink to just role assignment (AC1), dropping the
  eligibility-enforcement scenarios entirely as a different epic's concern?
- **Answer:** Yes — shrink to role assignment only.
- **Resulting change:** BEEM-15's story statement, ACs, and out-of-scope rewritten to cover only
  "assign a `Membership.role` to a project member." ACs 2–5 removed. Out-of-scope section now
  explicitly names approval-eligibility enforcement as belonging to `BHEEM-8` (Human approvals &
  stage collaboration) once a gated-step concept exists there.
- **Downstream flag (not resolved here):** FR-006 ("role-based approval eligibility") is now only
  half-covered inside BEEM-3 — the *assignment* half. Neither `BHEEM-5`'s nor `BHEEM-8`'s
  `epic-map.json` entry currently lists FR-006. Recommend the PRD owner or `BHEEM-8`'s own
  `user-story`/`epic-review` pass add a story covering the *enforcement* half and decide whether
  `epic-map.json` should list FR-006 under `BHEEM-8` as well. Not changed here — out of this
  review's authority (different epic, not loaded in full).

#### Gap 3 — Dependency-note sanity (one-sided claim)
- **Stories touched:** BEEM-16, BEEM-12, BEEM-13, BEEM-15.
- **What was missing/ambiguous:** BEEM-16's notes claim it is "the prerequisite seed for BEEM-12,
  BEEM-13, and BEEM-15," but none of those three stated the reverse dependency.
- **Question asked:** Should BEEM-12, BEEM-13, and BEEM-15 each state "depends on BEEM-16"?
- **Answer:** Yes, add to all three.
- **Resulting change:** Added "Depends on `BEEM-16` for the first platform admin account" to the
  Notes/dependencies of BEEM-12, BEEM-13, and BEEM-15. Documentation fix only — `epic-sequence`'s
  computed order already builds BEEM-16 first on other grounds.
- **Additional dependency surfaced while rewriting:** BEEM-13 and BEEM-15 both also assume a
  project already has a `PROJECT_MANAGER` membership (per Gap 1's answer) before that actor can
  act — which only exists once `BEEM-12` runs. Added "Depends on `BEEM-12`" to BEEM-13's notes.
  BEEM-15's notes already depend on `BEEM-12` for project membership generally, so no separate
  addition was needed there.

### Architecture impact
Two items need `tech-design` (amend mode) before `story-design` starts on BEEM-13 or BEEM-15 —
neither is resolved here, both are flagged only:

1. **`Membership.role` enum is too narrow and not extensible.** Current spec:
   `[PROJECT_MANAGER, DEVELOPER, DEVOPS, REVIEWER]`. Per the interview, the intended role set is
   the full SDLC-phase list (Business Analyst, Architect, Developer, QA, DevOps, Project
   Manager, Reviewer, …) **and** the platform needs a way to add new project-membership roles at
   runtime to scale with business needs — i.e. a configurable role catalog, not a fixed enum.
   This is a genuine architecture conflict (not a legitimate cross-epic dependency): the current
   schema cannot represent it. Recommend `tech-design` (amend mode) decide the shape (open string
   with validation? a `ProjectRole` reference table? enum-plus-extension?) before BEEM-13 or
   BEEM-15 commits to an interface in `story-design`.
2. **Whether project creation (BEEM-12) should auto-assign the creating admin as
   `PROJECT_MANAGER`, or whether that first mapping is always a separate, explicit BEEM-15 action.**
   Not an architecture conflict per se (both are representable), but a real product-behavior
   question surfaced by Gap 1's answer ("Platform.ADMIN creates a project and first maps a user as
   project manager role") that wasn't disambiguated during this review — left for `story-design`
   to confirm explicitly rather than assumed here, per BEEM-12's Notes/dependencies.

### Story changes summary
`stories.md`:
- **BEEM-12:** Actor/preconditions narrowed to `platform_role = PLATFORM_ADMIN` only. Out-of-scope
  reworded. Notes/dependencies gained the BEEM-16 dependency and a flag that auto-PM-assignment
  on creation is unconfirmed.
- **BEEM-13:** Actor/preconditions widened to `PLATFORM_ADMIN` or `Membership.role =
  PROJECT_MANAGER`. Notes/dependencies gained BEEM-16 and BEEM-12 dependencies, plus a
  clarification that "run user" is any project member, not a distinct role.
- **BEEM-15:** Rescoped from 5 ACs to 1 (role assignment only); actor widened to `PLATFORM_ADMIN`
  or `PROJECT_MANAGER`; out-of-scope now explicitly excludes approval-eligibility enforcement
  (moved conceptually to `BHEEM-8`); Notes/dependencies gained the BEEM-16 dependency and the
  role-catalog architecture flag.

### Requirement coverage check
FR-001 through FR-005 unaffected — still each covered by at least one story's acceptance
criteria, unchanged by this pass. **FR-006 is now only partially covered within BEEM-3** — BEEM-15
covers assignment; enforcement is unassigned to any existing story in any epic's map (see Gap 2's
downstream flag). This is a real, currently-open coverage gap, not resolved by this review since
it requires a decision in `BHEEM-8`'s own scope. `story-map.json` left unchanged (BEEM-15 still
legitimately claims FR-006 for the half it covers); `epic-map.json` left unchanged (FR-006 stays
under BEEM-3, which is still accurate for the assignment half).

### Dependency-note sanity check
Found and reconciled the one-sided BEEM-16 → {BEEM-12, BEEM-13, BEEM-15} claim (Gap 3), plus a
previously-undocumented BEEM-12 → BEEM-13 dependency surfaced while resolving Gap 1. No other
dependency note in `stories.md` refers to a non-existent story key. Build order itself is left to
`epic-sequence` (already correct); this pass only fixed documentation.

**Pass 1 resolution note:** Architecture item #1 above (extensible `Membership.role` catalog) was
resolved by `ADR-007` (extensible `ProjectRole` catalog) and the `data-model.md`/`openapi.yaml`
updates that shipped with it — see Pass 2's context for how that lands on this pass's stories.
Item #2 (auto-PM-assignment on creation) is still open, unchanged by Pass 1 or Pass 2.

---

## Pass 2 — project editing, tool-category scalability, membership lifecycle

### Context loaded
- All 9 current BEEM-3 stories from `stories.md` (including the Pass-1 rewrites and `ADR-007`'s
  role-catalog wording already in place).
- `docs/data-model.md` — `Project`, `Membership`, `ProjectRole`, `IntegrationProvider`,
  `ProjectIntegrationBinding` entities and their relationships.
- `docs/architecture.md` — component/sequence diagrams and the integrations table (Git/GitHub,
  Jira adapter listed as separate integration surfaces; NFR-011 on separately-configurable
  integration concerns).
- `docs/api-contracts/beembhai-api.openapi.yaml` — full `Project`/`ProjectCreateRequest`/
  `ProjectUpdateRequest`/`Membership`/`MembershipUpsertRequest`/`ProjectIntegrationBinding`/
  `ProjectIntegrationBindingUpsertRequest` schemas and the `/projects`, `/projects/{projectId}`,
  `/projects/{projectId}/members`, `/projects/{projectId}/integrations` paths.
- `docs/product/PRD.md` — FR-001/FR-002 wording (project creation is GitHub-specific in the
  current text) and FA-2's FR-007/FR-008/FR-011/FR-012/FR-017/FR-020 (pluggable integration
  providers, Jira marked "Later").
- `docs/product/epic-map.json` and `docs/product/epics.md` — confirmed FR-007 through FR-020
  belong to `BHEEM-4` (Epic 2: Integration providers & secrets vaulting), sequenced immediately
  after this epic (`epic-sequence.md`'s wave table: Epic 2 depends only on Epic 1).
- `docs/adr/ADR-006-*.md` / `ADR-007-*.md` — confirmed the role-catalog pattern this pass reuses as
  precedent for the integration-category question below.

### Gaps found

#### Gap 4 — Cross-epic architecture fit (project↔tool linkage modeled two contradictory ways)
- **Stories touched:** BEEM-12.
- **What was missing/contradictory:** `Project`/`ProjectCreateRequest`/`ProjectUpdateRequest`
  hardcoded `githubRepositoryRef` (required) and `jiraProjectKey` (optional) as named fields, while
  a fully generic `IntegrationProvider`/`ProjectIntegrationBinding` mechanism
  (`integrationCategoryKey`/`integrationProviderKey`, free strings) already existed in the same
  data model and contract for the general case — `BHEEM-4`'s deliverable (FR-007/008/011/012, all
  MVP release, sequenced right after this epic). Neither BEEM-12's story text nor its
  Notes/dependencies mentioned `BHEEM-4` at all despite the direct overlap — the silence itself is
  the gap (checklist category 4).
- **Question asked:** Should project↔tool linkage be the hardcoded fields, the generic bindings
  only, or both?
- **Answer:** Generic bindings only.
- **Resulting change:** BEEM-12 rescoped to create a bare project (name only, zero bindings).
  `githubRepositoryRef`/`jiraProjectKey` are no longer part of project creation or editing.
  BEEM-12's Notes/dependencies now state an explicit dependency on `BHEEM-4` for a project to have
  any GitHub/Jira/other tool actually wired up.
- **Downstream flag (not resolved here):** PRD `FR-001`'s wording ("...with a name and linked
  GitHub repository") no longer matches BEEM-12 after this rescoping. Updating `PRD.md` is outside
  this skill's authority — recommend the `prd` skill (or the PRD owner directly) reword FR-001,
  and re-check `epic-map.json`'s FR-001 assignment still makes sense afterward.

#### Gap 5 — Epic-wide scope boundary (no "edit project" story)
- **Stories touched:** BEEM-12 (new sibling story added: BEEM-21).
- **What was missing:** `PATCH /projects/{projectId}` already existed in the API contract, but no
  story exercised it — a capability the contract implies that no story's acceptance criteria
  covered and no story's out-of-scope even named. This also directly follows from Pass 1's Gap 1
  answer, which stated `PROJECT_MANAGER` should be able to edit project details.
- **Question asked:** Add an "Edit project" story now?
- **Answer:** Yes.
- **Resulting change:** New story `BEEM-21` (Edit project details) added to `stories.md` and
  `story-map.json`, scoped to editing the project's name only (actor: `PLATFORM_ADMIN` or
  `Membership.role = PROJECT_MANAGER` for that project — the same actor pattern as BEEM-13/15).
  Editing integration bindings, workflow-policy pairings, and membership/roles are explicitly
  named as other stories' territory in BEEM-21's out-of-scope, so nothing is now covered twice.

#### Gap 6 — Epic-wide scope boundary (membership lifecycle is add-only)
- **Stories touched:** BEEM-15.
- **What was missing:** BEEM-15 (post-Pass-1) only covered assigning/upserting a `Membership.role`.
  There was no remove or deactivate anywhere — not in any story, not in the API contract (no
  `DELETE` endpoint, no `isActive`/status field on `Membership`) — despite the user's stated intent
  that members can be "added / deleted / inactive."
- **Question asked:** Add remove + deactivate to BEEM-15 now?
- **Answer:** Yes, add both.
- **Resulting change:** BEEM-15 renamed "Manage project membership and roles"; two new scenarios
  added (remove a member's membership; mark a membership inactive). Out-of-scope now explicitly
  excludes reactivating a deactivated membership and the last-remaining-`PROJECT_MANAGER` safeguard
  question, both left for `story-design` to confirm rather than assumed here.

#### Gap 7 — Cross-story / cross-epic architecture fit (integration-category extensibility)
- **Stories touched:** None directly (this is a `BHEEM-4` concern), but it was surfaced by Gap 4's
  rescoping of BEEM-12 and is recorded here since it followed directly from this pass's interview.
- **What was missing:** Providers within an integration category are already pluggable
  (`ProjectIntegrationBinding`/`IntegrationProvider`), but nothing in the architecture explicitly
  guarantees a brand-new *category* itself (e.g. `devops_tools`, alongside the implied
  `code_versioning`/`project_management` categories) can be added without a code change — unlike
  `ADR-007`'s explicit guarantee for `ProjectRole`.
- **Question asked:** Flag this for `BHEEM-4` tech-design, or accept the free-string
  `integrationCategoryKey` as sufficient already?
- **Answer:** Flag it for `BHEEM-4` tech-design.
- **Resulting change:** Recorded below under Architecture impact as an item for `BHEEM-4`'s own
  `tech-design` pass — not resolved here, since it's a different (not-yet-decomposed) epic's
  design decision, not BEEM-3's.

### Architecture impact
Three items need `tech-design` (amend mode) before the affected story-design work starts — none
resolved here, all flagged only:

1. **Drop `githubRepositoryRef`/`jiraProjectKey` from `Project`/`ProjectCreateRequest`/
   `ProjectUpdateRequest`.** Project↔tool linkage should go entirely through
   `ProjectIntegrationBinding` (Gap 4). Recommend `tech-design` (amend mode) update
   `data-model.md`'s `Project` entity and `openapi.yaml`'s three `Project*` schemas accordingly,
   and flag the `prd` skill/PRD owner to reword FR-001.
2. **Add membership removal and an inactive state.** `Membership` needs an `isActive` (or status)
   field and the contract needs a way to remove a membership (a `DELETE
   /projects/{projectId}/members/{membershipId}` endpoint, or a `PATCH` that can set inactive) to
   back BEEM-15's new scenarios (Gap 6). Recommend `tech-design` (amend mode) decide the exact
   shape before `story-design` starts on BEEM-15.
3. **Integration-category extensibility (Gap 7) — flagged for `BHEEM-4`, not decided here.**
   Recommend `BHEEM-4`'s own `tech-design` pass explicitly decide whether `integrationCategoryKey`
   needs a backing catalog (an `IntegrationCategory` table, mirroring `ADR-007`'s `ProjectRole`
   pattern) or whether the existing free string is deliberately sufficient — and write that
   decision down as its own ADR before `BHEEM-4`'s stories commit to an interface. This is outside
   BEEM-3's authority (a different, not-yet-decomposed epic); recorded here only because this
   pass's interview is where it surfaced.

### Story changes summary
`stories.md`:
- **BEEM-12:** Rescoped to name-only project creation; "Missing repository is rejected" scenario
  removed. Out-of-scope reworded to name all integration-provider linkage as `BHEEM-4`'s territory.
  Notes/dependencies gained the explicit `BHEEM-4` dependency and the PRD `FR-001` wording flag.
- **BEEM-21 (new):** Added — edit a project's name, actor `PLATFORM_ADMIN` or `PROJECT_MANAGER`,
  scoped away from integrations/workflow-policy/membership editing (each already owned elsewhere).
- **BEEM-15:** Renamed "Manage project membership and roles"; gained remove and deactivate
  scenarios; out-of-scope gained the reactivation and last-PM-safeguard open questions;
  Notes/dependencies note the new architecture item needed before `story-design`.

### Requirement coverage check
FR-001 through FR-006 are still each covered by at least one story, unchanged in count by this
pass. Two new gaps in *traceability*, not coverage:
- BEEM-12 no longer matches PRD `FR-001`'s literal wording (GitHub is no longer creation-time) —
  flagged above for the PRD owner, not resolved here.
- BEEM-21 (edit project) and BEEM-15's new remove/deactivate scenarios don't map to any existing
  FR/NFR ID — neither invented here nor silently absorbed into FR-001/FR-006; flagged for the PRD
  owner to decide whether a new FR is warranted or these are reasonably implied by existing FR-001/
  FR-002/FR-006 intent. `story-map.json` updated to list BEEM-21 under FR-001 as the closest
  existing match; `epic-map.json` left unchanged (no new FR minted).

### Dependency-note sanity check
BEEM-12 → `BHEEM-4` is a new cross-epic dependency note (Gap 4), and it's one-sided by necessity —
`BHEEM-4` doesn't exist as decomposed stories yet, so there's nothing on the other side to
reconcile against yet. Recommend `BHEEM-4`'s own future `user-story`/`epic-review` pass confirm the
reverse acknowledgment once that epic is decomposed. BEEM-21 and BEEM-15's dependency notes all
point at real, existing story keys (`BEEM-12`, `BEEM-16`); no mismatches found.

---
*Applied: `docs/product/epics/BEEM-3/_epic/stories.md` updated in place for BEEM-12, BEEM-13,
BEEM-15 (Pass 1), and BEEM-12, BEEM-15 again plus new story BEEM-21 (Pass 2). `story-map.json`
updated to add BEEM-21. No Jira keys were used in either pass (no MCP update performed — BEEM-3's
Jira issues, if any exist, were not touched). Next: run `tech-design` (amend mode) on the three
Pass 2 architecture-impact items (drop hardcoded repo/Jira fields, add membership removal/inactive
state, and — separately — flag integration-category extensibility for `BHEEM-4`'s own tech-design
once that epic starts) before `story-design` begins on BEEM-12, BEEM-15, or BEEM-21. BEEM-21 and
the expanded BEEM-15 likely also want an individual `story-review` pass once their contracts are
confirmed (upsert-vs-conflict behavior, validation rules, and the last-PM-safeguard question are
single-story concerns not covered here).*
