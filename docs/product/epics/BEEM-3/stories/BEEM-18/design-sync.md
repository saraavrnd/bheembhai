# Design Sync — BEEM-18: Add browser signup page

**Date:** 2026-07-13

## Result

No system-level design change.

The story stayed within the approved architecture:
- Reused the existing shared registration flow in `app/auth/service.py`.
- Reused the established browser auth card and `status-pill` patterns in the Jinja2 UI.
- Added a thin `/signup` page and form submission handler in the existing web router.

## Reference updates

- Added a brief note to `docs/CHANGELOG-design.md`.
- No architecture, data-model, or API-contract updates were required.
- `AGENTS.md` did not need a change for this story.

## Flags

No in-progress stories were flagged.
