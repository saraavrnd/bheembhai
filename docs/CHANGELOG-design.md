# Design Changelog

## 2026-07-10

- Approved the initial BeemBhai architecture and stack.
- Added the server-rendered UI, modular monolith process boundaries, and plugin-based integrations.
- Added architecture diagrams to the committed design.
- Scaffolded the repository skeleton for the walking-skeleton phase.

## 2026-07-12

- Recorded BEEM-16 bootstrap-admin story completion as an incremental auth-flow implementation within the approved architecture.

## 2026-07-13

- Recorded BEEM-17 local user registration as an incremental auth-flow implementation within the approved architecture.
- Recorded BEEM-18 browser signup as a thin UI addition that reuses the approved auth registration flow and existing Jinja2 auth-card patterns.
- Recorded BEEM-14 sign-in, verification, and password-reset flows as incremental auth/session behavior within the approved architecture.

## 2026-07-16

- Recorded BEEM-19 authentication screen alignment and password-policy update as a frontend and validation refinement within the approved auth flow.

## 2026-07-18

- Recorded BEEM-20: vendored real Bootstrap 5.3.3 (`app/web/static/vendor/bootstrap/bootstrap.min.css`) and the feather-icons sprite (`app/web/static/vendor/feather/feather-sprite.svg`) — the first concrete instance of the theme adoption `docs/ui-conventions.md` had only described. Scope limited to the 4 auth screens; `ui-conventions.md` updated to note the actual vendored Bootstrap version (5.3.3, not 5.3.8) and that the fuller theme asset set (`style.css`, `vendors_css.css`, `skin_color.css`, `template.js`) remains deferred to the future authenticated-dashboard-shell story.
