# Design Sync — BEEM-20: UI FIX: Align authentication screens to approved mockups

**Date:** 2026-07-18 · **Branch:** `feat/BEEM-19-align-authentication-screens`

## Classification
**Incremental change.** No new endpoints, data fields, or module dependencies — this is the
first concrete instance of a theme-adoption decision `docs/ui-conventions.md` had only described
in prose (Bootstrap + EduAdmin assets). Reference docs updated to match reality; no
`tech-design` amendment needed (already covered by the existing "Theme adoption" / "Asset plan"
sections, which anticipated exactly this).

## What changed in the references
- **`docs/ui-conventions.md`**
  - Corrected the assumed Bootstrap version: the theme bundle actually vendored ships **5.3.3**,
    not the 5.3.8 the doc originally named. Noted as intentional, not a gap to close later.
  - Added a "Current state" note under **Asset plan**: only `bootstrap.min.css` and
    `feather-sprite.svg` (the chosen icon set) are copied in so far, scoped to the 4 auth
    screens. The fuller theme set (`style.css`, `vendors_css.css`, `skin_color.css`,
    `template.js`, theme images) is still absent — flagged so a future dashboard-shell
    story-design doesn't assume the shell is already scaffolded.
- **`docs/CHANGELOG-design.md`** — appended a 2026-07-18 entry recording the above.
- **`AGENTS.md`** — no change. No module responsibility, endpoint, or data-entity shift; the
  module map already treats `app/web` as the presentation layer.

## Affected in-progress stories
Checked Jira (`project = BEEM AND status = "In Progress" AND key != BEEM-20`): **none returned.**
No other story is currently in flight against the auth templates, `theme.css`, or the newly
vendored assets. Nothing to flag.

## Hand-off
Docs committed to this branch (`feat/BEEM-19-align-authentication-screens`) so they ride with the
same PR/merge as the code. `pr-create` may proceed to open/update the PR.
