# Epic Sequence — BEEM-3

**Status:** PROVISIONAL
**Epic:** BEEM-3
**Generated:** 2026-07-12

This sequence is based on the local story map, the existing BEEM-16 story-design note, and the dependency notes in `stories.md`. No explicit Jira blocks links were found in the current issue data, so this is a provisional order that should be refined as more story-design notes land.

## Dependency Graph

### Firm edges
- `BEEM-17` before `BEEM-14`
  - Source: `docs/product/epics/BEEM-3/_epic/stories.md`
  - Reason: BEEM-14 assumes a local user account already exists so it can verify and recover it.
- `BEEM-14` before `BEEM-16`
  - Source: `docs/product/epics/BEEM-3/stories/BEEM-16/story-design.md`
  - Reason: BEEM-16 explicitly reuses the shared auth sign-in / verification flow from BEEM-14.
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
  - Source: `docs/product/epics/BEEM-3/_epic/stories.md`
  - Reason: the story notes describe BEEM-13 as depending on the project access baseline.
- `BEEM-12` before `BEEM-15`
  - Source: `docs/product/epics/BEEM-3/_epic/stories.md`
  - Reason: the story notes describe BEEM-15 as depending on project membership from the access story.

## Waves

### Wave 1
- `BEEM-17`

### Wave 2
- `BEEM-14`

### Wave 3
- `BEEM-16`

### Wave 4
- `BEEM-12`

### Wave 5
- `BEEM-13`
- `BEEM-15`

## Parallel Groups

- `BEEM-13` and `BEEM-15` can be built in parallel once `BEEM-12` is merged, assuming their external epic dependencies are already satisfied.

## Notes

- `BEEM-13` also depends on versioned workflow / policy records from the workflow-definition epic.
- `BEEM-15` also depends on the approval-gate workflow from the orchestration epic.
- Those external dependencies are important for implementation, but they are outside this epic sequence file.
- No cycles were found.

## Approval Gate

Please review this provisional order before I write any Jira `blocks` links:

1. `BEEM-17`
2. `BEEM-14`
3. `BEEM-16`
4. `BEEM-12`
5. `BEEM-13`
6. `BEEM-15`
