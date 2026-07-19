# ADR-008: Decouple project creation from tool linkage

**Status:** Accepted · **Date:** 2026-07-19 · **Deciders:** saraav + user approval

## Context

A second `epic-review` pass on `BEEM-3` (see `docs/product/epics/BEEM-3/_epic/epic-review.md`,
Pass 2, Gap 4) found that project↔tool linkage was modeled two contradictory ways at once:

- `Project`, `ProjectCreateRequest`, and `ProjectUpdateRequest` hardcoded `githubRepositoryRef`
  (required) and `jiraProjectKey` (optional) as named fields directly on the project.
- `ADR-005` had already established a fully generic provider-registry mechanism —
  `IntegrationProvider` (a catalog entry per category/provider) and `ProjectIntegrationBinding`
  (a project's selected provider per category, keyed by a free-string `integrationCategoryKey`) —
  specifically so the platform "can support new providers inside an existing integration category
  without changing workflows." That mechanism already existed in `data-model.md` and
  `openapi.yaml` but was never wired to project creation.

The driving requirement (from the user, via `epic-review`) is that the platform must not restrict
project↔tool linkage to GitHub and Jira alone — it needs to scale to arbitrary tool categories
(code-versioning, project-management, dev-ops, and whatever comes next) without a schema or
contract change per new category or provider. Keeping the hardcoded fields alongside the generic
registry does the opposite: every new hardcoded field is itself a schema change, and the two
mechanisms can drift out of sync (e.g. a project's `githubRepositoryRef` disagreeing with its
active `code_versioning` binding).

## Decision

Remove `githubRepositoryRef` and `jiraProjectKey` from `Project`, `ProjectCreateRequest`, and
`ProjectUpdateRequest`. Project creation and editing (`BEEM-12`, `BEEM-21`) requires only a
`name`. All tool linkage — GitHub, Jira, and any future category — goes exclusively through the
existing `ProjectIntegrationBinding` mechanism (`GET`/`PUT /projects/{projectId}/integrations`),
owned by `BHEEM-4` (Integration providers & secrets vaulting).

`GET /projects` (the list endpoint) is unchanged in shape apart from dropping the two removed
fields — it does **not** gain an embedded bindings summary. A client that needs a project's active
tool bindings calls `GET /projects/{projectId}/integrations` separately. This keeps `BEEM-3`'s
contract from committing to a shape for `BHEEM-4`'s data before that epic has been decomposed into
stories or designed in detail.

`data-model.md`'s `Project` entity drops `source_repo` and `source_issue_system` from its key
fields — a project's identity is now just `id, name, slug`.

## Alternatives considered

- **Embed an active-bindings summary in `GET /projects`:** rejected for now — it would save a
  future N+1 lookup for a project-list UI that wants to show "GitHub: org/repo" per row, but it
  couples this epic's contract to a shape `BHEEM-4` hasn't designed yet. Revisit once `BHEEM-4` is
  decomposed and the UI need is concrete.
- **Keep both the hardcoded fields and the generic registry:** rejected — this is the redundancy
  that caused the gap. Two representations of the same fact can disagree, and every new hardcoded
  field defeats the registry's whole purpose.
- **Keep `githubRepositoryRef` only (drop just `jiraProjectKey`), on the theory a project always
  needs *a* repo to ever run anything:** rejected — singling out GitHub as a mandatory field is
  exactly the "restricted to these tools" pattern the driving requirement rejects. Whether a
  project needs at least one active `code_versioning` binding before a run can be created is a
  real precondition, but it belongs to run-creation validation (`BHEEM-6`/`BHEEM-7`), not to the
  shape of `Project` itself.

## Consequences

- A project can now exist with zero tool bindings immediately after creation. Any code path that
  previously assumed a project always has a repository reference (run creation, executor checkout)
  must instead check for an active `code_versioning` `ProjectIntegrationBinding` and handle its
  absence explicitly — flagged for `BHEEM-6`/`BHEEM-7`'s own `story-design`/`epic-review` to pick
  up when those epics reach that point; not resolved here since neither epic is in scope for this
  amendment.
- PRD `FR-001`'s current wording ("...create a project with a name and linked GitHub repository")
  no longer matches project creation. Updating `PRD.md` is outside this skill's authority;
  flagged for the `prd` skill or the PRD owner directly, along with re-checking `epic-map.json`'s
  `FR-001` assignment still makes sense afterward.
- `architecture.md`'s data-flow step 2 and its Git/GitHub traceability row are updated alongside
  this ADR to stop describing project creation as the point where GitHub/Jira get linked.
- `BEEM-12` and `BEEM-21` (`docs/product/epics/BEEM-3/_epic/stories.md`) already reflect this
  shape as of the `epic-review` Pass 2 rewrite; no further story change is needed for this ADR to
  land.
