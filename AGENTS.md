# Agents.md

This file provides guidance to Codex/Claude Code when working with code in this repository.

## Project

BheemBhai: a governed, observable platform for orchestrating reusable agent skills across the
software delivery lifecycle, starting with a story-to-PR workflow. The MVP focuses on backend-
orchestrated, policy-governed, auditable runs with isolated execution, stage-by-stage approvals,
and artifact persistence in Git.

**Current state: scaffold only.** Every module under `app/` is an empty stub (a router with zero
routes, or an interface with only a connectivity check implemented). `app/main.py`'s `/health`
and `/` routes are the only working request handlers — they exist to prove Postgres/Redis/object-
storage/secure-storage wiring, not as a feature. Implementing a story means filling in the
relevant module, not creating new top-level structure.

## Project Layout

Every PDLC skill (`tech-design`, `project-scaffold`, `epic-sequence`, `story-design`,
`test-creator`, `implement`, `test-verify`, `pr-create`, `design-sync`, etc.) resolves project
artifact paths from this table — see `.agents/skills/_SHARED-project-layout.md` for the
convention. If a path below ever changes, update it here first; skills read this table, not
their own prose, and never hardcode a path from memory.

| Artifact | Path |
|----------|------|
| Architecture | `docs/architecture.md` |
| Data model | `docs/data-model.md` |
| Tech stack | `docs/tech-stack.md` |
| Testing strategy | `docs/testing-strategy.md` |
| UI conventions | `docs/ui-conventions.md` |
| Product overview | `docs/product-overview.md` |
| Whitepaper | `docs/learn-portal-whitepaper.md` |
| ADRs | `docs/adr/ADR-NNN-*.md` |
| API contracts | `docs/api-contracts/*.openapi.yaml` |
| Design history (proposals) | `docs/design-history/` |
| Design changelog | `docs/CHANGELOG-design.md` |
| PRD | `docs/product/PRD.md` |
| Epics | `docs/product/epics.md` |
| Epic map | `docs/product/epic-map.json` |
| Stories | `docs/product/epics/<EPIC_KEY>/_epic/stories.md` |
| Story map | `docs/product/epics/<EPIC_KEY>/_epic/story-map.json` |
| Epic sequence (plan) | `docs/product/epics/<EPIC_KEY>/_epic/epic-sequence.md` |
| Epic sequence (machine-readable) | `docs/product/epics/<EPIC_KEY>/_epic/epic-sequence.json` |
| Epic review log | `docs/product/epics/<EPIC_KEY>/_epic/epic-review.md` |
| Story review log | `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/story-review.md` |
| Per-story design notes | `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/story-design.md` |
| Test plans | `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/test-plan.md` |
| Verification reports | `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/verification.md` |
| Code-review reports | `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/code-review.md` |
| Design-sync notes | `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/design-sync.md` |


## Rules
 - Ask, Don't assume. If something's unclear, ask before writing a line and no slient guesses about intent, architecture or requirements.
 - Simplest solution first and implemennt the minimum thing that works. No abstractions you didn't request.
 - Dont touch unrelated code and if a file is not part of the current task, leave it.
 - Flag uncertainty explicitly or if you are not confident so before proceeding as confidence without certainty causes more damage than admitting a gap.
