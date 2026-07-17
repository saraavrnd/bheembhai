# Story Design — BEEM-20: UI FIX: Align authentication screens to approved mockups

**Status:** AWAITING APPROVAL · **Epic:** BEEM-3 · **Date:** 2026-07-17
**Domain:** frontend
**Continues:** BEEM-19 (open PR #7, unmerged) — same branch, same 4 screens, corrective pass.

> Thin design note. Review and approve before test-creator writes tests. Change anything;
> I'll realign and re-confirm.

## Why BEEM-19 wasn't enough

BEEM-19 rebuilt the four auth templates (`signup.html`, `login.html`, `reset_password.html`,
`verify_email.html`) with correct copy/field structure but on a fully hand-rolled CSS file
(`app/web/static/css/theme.css`, ~1040 lines). `base.html` loads only that file — no real
Bootstrap, no EduAdmin theme assets are present anywhere in the repo, even though
`docs/ui-conventions.md` (approved 2026-07-10) already mandates Bootstrap 5.3.8 + the EduAdmin
`bs5/main-mini-sidebar` shell as the framework. That scaffold step was never executed. The
templates approximate Bootstrap class names (`btn btn-primary`, `form-control`, `container`) that
aren't backed by a real Bootstrap stylesheet, and icons are emoji glyphs (✉ 🔒 🛡) instead of a
real icon set. Net effect: content/order is right, visual fidelity to the mockups is not.

Note: the approved mockups (`signin-unified.png`, `signup-light.png`, `reset-password.png`,
`verify-email-unified.png`) are a clean, light, minimal SaaS card style — they do **not** resemble
EduAdmin's own literal auth pages (`auth_login.html` is a dark-background, icon-prefixed-input,
red-button, social-login layout). So this story pulls EduAdmin in as the underlying **framework**
(real Bootstrap + one real icon set), not as a skin — the mockups stay the pixel-level source of
truth, per user decision.

## Target module(s)
- `app/web/static/vendor/bootstrap/bootstrap.min.css` (new) — real Bootstrap 5.3.3, copied
  verbatim from `ui_theme/.../bs5/assets/vendor_components/bootstrap/dist/css/bootstrap.min.css`.
  (Repo's `ui-conventions.md` says 5.3.8; the vendored theme bundle ships 5.3.3 — noting the
  version delta, not blocking on it since the theme itself only provides 5.3.3.)
- `app/web/static/vendor/feather/feather-sprite.svg` (new) — single SVG icon sprite, copied from
  `bs5/assets/icons/feather-icons/feather-sprite.svg`. Chosen as "the one icon set" per
  ui-conventions.md; feather's thin-line marks (mail, link, check-circle, shield, lock, eye,
  eye-off, refresh-cw) match the mockups' icon style and need no jQuery/JS runtime for static use
  (`<svg><use href="...#icon-name"></use></svg>`).
- `app/web/templates/layouts/auth.html` (new) — the shared auth shell named in
  `docs/ui-conventions.md`'s template tree (`templates/layouts/auth.html`). Loads Bootstrap +
  theme.css, renders the centered-card wrapper and per-screen decorative background, replaces each
  auth template's own `{% extends "base.html" %}` + repeated section/container markup.
- `app/web/templates/auth/signup.html`, `login.html`, `reset_password.html`, `verify_email.html`
  — rebuilt to extend `layouts/auth.html` and use real Bootstrap grid/card/form primitives
  (`container`, `row`, `col-*`, `card`, `form-control`, `input-group`, `btn btn-primary`) instead
  of the bespoke `auth-*` class tree, with feather icons replacing the emoji glyphs. Field
  `id`/`name` attributes, form `action`/`method`, and the token-fragment JS in reset/verify stay
  unchanged — this is a presentation-layer rebuild, not a behavior change.
- `app/web/static/css/theme.css` — kept as the BheemBhai override layer (the role
  `docs/ui-conventions.md`'s asset plan assigns to `custom.css`); auth-specific rules rewritten to
  match the 4 mockups (spacing, card elevation/radius, button color/gradient, decorative
  background shapes, typography weight) on top of real Bootstrap instead of redefining Bootstrap
  primitives from scratch. Non-auth rules in the file are untouched.
- `app/web/templates/base.html` — add the Bootstrap stylesheet link ahead of `theme.css` so the
  override layer continues to win on cascade order.

## Interfaces / endpoints
| Kind | Signature | Request → Response |
|------|-----------|--------------------|
| page | `GET /signup` | visitor request → signup form matching `signup-light.png`, incl. trust-footer |
| page | `GET /login` | visitor request → sign-in form matching `signin-unified.png`, incl. verify-email callout, forgot-password + contact-support links |
| page | `GET /reset-password` | visitor request (valid token) → two-panel layout matching `reset-password.png`: form panel + token-loaded/success info panel |
| page | `GET /verify-email` | visitor request (valid token) → verification-flow panel (`email-sent` → `link-clicked` → `email-verified`) matching `verify-email-unified.png`, auto-verifies from the URL fragment as today |

No route signatures, request/response shapes, or auth semantics change.

## Data-model deltas
None. Presentation layer only.

## Reuse
- Existing auth routes, form handlers, token-fragment JS (reset/verify), and CSS custom-property
  design tokens (`--bb-primary`, `--bb-surface`, `--bb-text`, `--bb-muted`, `--bb-danger`,
  `--bb-success`) already defined in `theme.css`.
- Existing field `id`/`name` contracts and the `.signup-success` test hook (still asserted by the
  current e2e/unit tests per BEEM-19's `verification.md`).
- EduAdmin's real Bootstrap 5.3.3 build and feather-icons sprite, copied minimally — not the
  theme's `vendors_css.css` aggregate (that pulls in ~30 unrelated demo-plugin stylesheets:
  charts, datatables, colorpickers, etc.) and not `style.css`/`skin_color.css` (729 KB / 40 KB of
  dashboard-chrome rules the auth screens don't use, and whose literal auth-page skin the mockups
  already reject). Those two files are deferred to whichever future story builds the authenticated
  `main-mini-sidebar` dashboard shell, where they're actually exercised — pulling them in here
  would be scope creep past "fix the 4 auth screens."

## Approach
Introduce a real Bootstrap 5.3.3 stylesheet and one icon sprite as the foundation (closing the
`ui-conventions.md` gap for the auth surface), keep `theme.css` as the single BheemBhai override
layer on top of it, and add a shared `layouts/auth.html` shell so the four screens stop duplicating
the outer wrapper. Rebuild each screen's markup on Bootstrap primitives and re-tune the override
CSS against the four approved PNGs pixel-by-pixel: white/near-white card, `border-radius` and
shadow matching the mockups, blue primary button (flat on signin/signup/verify, subtle gradient on
reset-password's "Update password"), feather icons for mail/lock/eye/shield/check/link/refresh,
and the per-screen decorative background (soft blue wave bottom-left on sign-in, dot-grid corners
on signup, blue-to-lavender gradient on reset-password, plain white on verify-email). Preserve all
existing copy, field order, states (verify-email warning, signup success, reset token-loaded/
success panels, verify-email flow steps), and the 390px no-horizontal-scroll requirement.

## Test surface
- [x] Visual: each of the 4 screens matches its approved mockard at desktop width (headings, field
      order, buttons, links, panels/footer all present and visible).
- [x] Visual: the four screens share the same Bootstrap-based light theme, accent color, and card
      treatment.
- [x] Functional: reset-password token-loaded panel and post-update success panel both render at
      the right times; verify-email's 3-step flow and auto-verify-from-fragment behavior keep
      working.
- [x] Visual: auth screens remain usable (no horizontal scroll) on a 390px viewport.

## Out of scope
Changing auth behavior, backend routes, token semantics, email delivery, MFA/SSO/social login, or
copy outside the approved mockup content. Copying the EduAdmin dashboard shell assets
(`style.css`, `skin_color.css`, `vendors_css.css`, `template.js`, sidebar/topbar chrome) — that's
the authenticated-shell scaffold gap, tracked separately, not this story.

## Architecture impact
None. `docs/ui-conventions.md` already approved Bootstrap + EduAdmin-asset adoption; this story
executes that decision for the auth surface only. No ADR needed.

## Dependencies discovered (feeds epic-sequence)
- Continues: `BEEM-19` (same branch/PR, not a new dependency edge).
- Produces: the real-Bootstrap + feather-icon foundation that the authenticated dashboard shell
  story can extend later (that story will still need to add `style.css`/`skin_color.css`/sidebar
  assets on top).

## Traceability
**Requirements covered:** FR-005

---
*On approval: next step is `test-creator` (failing tests from these screens and their acceptance
criteria), then `implement`.*
