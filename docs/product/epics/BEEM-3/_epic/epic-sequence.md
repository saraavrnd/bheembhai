# Epic Sequence — BEEM-3

**Status:** REFINED (partial) — re-run of the 2026-07-12 provisional sequence
**Epic:** BEEM-3
**Generated:** 2026-07-19

Since the last run, `BEEM-17`, `BEEM-14`, `BEEM-16`, `BEEM-18`, `BEEM-19`, and `BEEM-20` were
designed and built (all status **Done**). Their `story-design.md` notes now supply firm
produces/consumes edges that replace the earlier coarse guesses for those stories — this is the
refinement loop described in the skill. `BEEM-20` (a same-branch corrective pass on `BEEM-19`,
linked in Jira via a "Cloners" relationship) is newly folded into the graph; it wasn't in the
original story-map. `BEEM-21` (edit project details) was added by the round-2 `epic-review` pass
and has no `story-design` yet, so its edges are still provisional.

`BEEM-12`, `BEEM-13`, `BEEM-15`, and `BEEM-21` remain **To Do** and have no `story-design` notes
yet — their edges are still provisional, sourced from `stories.md`/`epic-review.md` text. Per the
skill's re-run rule, the waves for the six already-built stories are recorded as history and are
**not** reordered; only the remaining stories' order is live for `story-implement` to act on.

Jira was checked for explicit "blocks" links: none exist. The only issue link found is a
"Cloners" relationship between `BEEM-19` and `BEEM-20`, which isn't a blocks edge but confirms the
build sequencing (`BEEM-20` continues `BEEM-19` on the same branch).

## Dependency Graph

### Firm edges
- `BEEM-17` before `BEEM-14`
  - Source: `story-design.md` (BEEM-14 and BEEM-17, "Dependencies discovered")
  - Reason: BEEM-14 consumes the `users` row BEEM-17's registration produces.
- `BEEM-17` before `BEEM-18`
  - Source: `docs/product/epics/BEEM-3/stories/BEEM-18/story-design.md`
  - Reason: BEEM-18 consumes BEEM-17's registration API and verification-email flow.
- `BEEM-18` before `BEEM-19`
  - Source: `docs/product/epics/BEEM-3/stories/BEEM-19/story-design.md`
  - Reason: BEEM-19 consumes BEEM-18's signup page.
- `BEEM-14` before `BEEM-19`
  - Source: `docs/product/epics/BEEM-3/stories/BEEM-19/story-design.md`
  - Reason: BEEM-19 consumes BEEM-14's sign-in / verify-email / reset-password behavior.
- `BEEM-14` before `BEEM-16`
  - Source: `docs/product/epics/BEEM-3/stories/BEEM-16/story-design.md`
  - Reason: BEEM-16 consumes the shared auth sign-in/verification flow from BEEM-14.
- `BEEM-19` before `BEEM-20`
  - Source: `docs/product/epics/BEEM-3/stories/BEEM-20/story-design.md`
  - Reason: BEEM-20 is an explicit same-branch corrective pass continuing BEEM-19's unmerged PR
    (also reflected as a "Cloners" link in Jira), not an independent produces/consumes edge.
- `BEEM-16` before `BEEM-12`
  - Source: `docs/product/epics/BEEM-3/stories/BEEM-16/story-design.md`
  - Reason: BEEM-16 produces the first platform admin account that BEEM-12 consumes.
- `BEEM-16` before `BEEM-13`
  - Source: `docs/product/epics/BEEM-3/stories/BEEM-16/story-design.md`
  - Reason: BEEM-16 produces the first platform admin account that BEEM-13 consumes.
- `BEEM-16` before `BEEM-15`
  - Source: `docs/product/epics/BEEM-3/stories/BEEM-16/story-design.md`
  - Reason: BEEM-16 produces the first platform admin account that BEEM-15 consumes.

### Provisional edges
- `BEEM-12` before `BEEM-13`
  - Source: `docs/product/epics/BEEM-3/_epic/stories.md` / `epic-review.md`
  - Reason: BEEM-13 needs the project's `PROJECT_MANAGER` membership, which only exists once
    BEEM-12 runs. No `story-design` for BEEM-13 yet to confirm firm.
- `BEEM-12` before `BEEM-15`
  - Source: `docs/product/epics/BEEM-3/_epic/stories.md`
  - Reason: BEEM-15 depends on project membership from BEEM-12. No `story-design` for BEEM-15 yet.
- `BEEM-12` before `BEEM-21`
  - Source: `docs/product/epics/BEEM-3/_epic/stories.md`
  - Reason: BEEM-21 edits a project, which must already exist (created by BEEM-12).
- `BEEM-16` before `BEEM-21`
  - Source: `docs/product/epics/BEEM-3/_epic/stories.md`
  - Reason: BEEM-21 depends on the first platform admin account from BEEM-16. BEEM-21 was added
    after BEEM-16 was designed, so this is not in BEEM-16's own design note.

## Waves

### Wave 1 — Done
- `BEEM-17`

### Wave 2 — Done
- `BEEM-14`
- `BEEM-18`

### Wave 3 — Done
- `BEEM-16`
- `BEEM-19`

### Wave 4 — mixed
- `BEEM-12` *(To Do — eligible now, its only dependency `BEEM-16` is Done)*
- `BEEM-20` *(Done)*

### Wave 5 — To Do
- `BEEM-13`
- `BEEM-15`
- `BEEM-21`

## Parallel Groups

- `BEEM-13`, `BEEM-15`, and `BEEM-21` can be built in parallel once `BEEM-12` is merged, assuming
  their external epic dependencies (below) are already satisfied.

## Notes

- `BEEM-13` also depends on versioned workflow/policy records from the workflow-definition epic
  (`BHEEM-?`, not yet decomposed).
- `BEEM-15` also depends on the approval-gate workflow from the orchestration epic.
- `BEEM-12` also depends on `BHEEM-4` (Epic 2: Integration providers & secrets vaulting) per
  `epic-review.md`'s round-2 pass; `BHEEM-4` is sequenced immediately after this epic.
- These external, cross-epic dependencies matter for implementation but are outside this epic's
  sequence file.
- Waves 1–4's `BEEM-14/16/17/18/19/20` are already built and merged; they are recorded here as
  history and are not being reordered. Only `BEEM-12`, `BEEM-13`, `BEEM-15`, `BEEM-21` are live for
  `story-implement`.
- No cycles were found.

## Approval Gate

Please review this refined order before I write any Jira `blocks` links. Since no "blocks" links
currently exist in Jira, all 13 edges below are new:

**Already built (historical record):**
1. `BEEM-17` blocks `BEEM-14`
2. `BEEM-17` blocks `BEEM-18`
3. `BEEM-18` blocks `BEEM-19`
4. `BEEM-14` blocks `BEEM-19`
5. `BEEM-14` blocks `BEEM-16`
6. `BEEM-19` blocks `BEEM-20`
7. `BEEM-16` blocks `BEEM-12`
8. `BEEM-16` blocks `BEEM-13`
9. `BEEM-16` blocks `BEEM-15`

**Live for `story-implement` (provisional, pending each story's own `story-design`):**
10. `BEEM-12` blocks `BEEM-13`
11. `BEEM-12` blocks `BEEM-15`
12. `BEEM-12` blocks `BEEM-21`
13. `BEEM-16` blocks `BEEM-21`

## Approved

All 13 edges above were approved and all 13 `Blocks` links were created in Jira on 2026-07-19
(provisional edges carry a link comment noting they're inferred and may change once that story
gets its own `story-design`). `story-implement` should pick `BEEM-12` next — it's the only To Do
story with all dependencies already Done.
