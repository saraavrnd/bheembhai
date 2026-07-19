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
- `tests/e2e/__snapshots__/auth/` (new) — stored baseline screenshots (desktop + 390px per screen)
  for the visual-regression layer described under Test surface.
- `pyproject.toml` — add `Pillow` to the `dev` dependency group for baseline pixel-diffing (no
  image-diff tooling exists in the repo today).

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

Plain text/heading-visibility checks (BEEM-19's existing coverage) aren't enough to claim visual
fidelity to a mockup — they can't tell a correctly-styled card from an unstyled `<div>`. This story
adds two layers on top of that baseline, per user decision:

- [x] **Computed-style assertions per mockup detail** — Playwright `page.evaluate` /
      `expect(locator).to_have_css(...)` checks that key elements actually carry the intended
      treatment, e.g.: card `border-radius` and `box-shadow` are non-default/non-zero; the primary
      button's resolved `background-color` matches the `--bb-primary` token; the sign-in
      verify-email callout has the warning/amber treatment; the reset-password token-loaded and
      success panels have their distinct blue/green treatments; the decorative background element
      is present with a non-`none` `background-image`/gradient; real Bootstrap is confirmed loaded
      (e.g. a `.container` resolves Bootstrap's computed `max-width`, not an unset/auto value).
- [x] **Playwright screenshot-baseline regression** — after implementation, capture a full-page
      screenshot per screen (desktop 1440px + mobile 390px) to `tests/e2e/__snapshots__/auth/`
      once you've visually confirmed the render matches the approved mockup. Add a test that
      re-screenshots on every run and asserts the pixel-difference ratio against the stored
      baseline stays under a small tolerance (e.g. <2%, using `Pillow` for the diff — new dev
      dependency, no image-diff tooling exists in the repo today). This doesn't validate day-one
      accuracy — your visual sign-off does — it catches silent drift afterward. This is NOT a diff
      against the mockup PNGs themselves: those are AI-generated design references, not browser
      renders, so font metrics/AA/DPI differ enough that a literal mockup-diff would false-fail a
      correct implementation. The mockups stay the human-reviewed source of truth; the baseline
      locks in whatever render you sign off as matching them.
- [x] Visual: each of the 4 screens matches its approved mockup at desktop width (headings, field
      order, buttons, links, panels/footer all present and visible) — existing coverage, kept.
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

## Addendum — PR #7 review feedback (2026-07-18)

**Status:** APPROVED (user reviewed the deployed screens on PR #7 and gave 18 concrete change
requests, with 3 ambiguous points resolved via follow-up questions before this addendum was
written). This addendum amends acceptance criteria in place; it does not restart the story.

### Resolved ambiguities
- **Password policy:** the signup/reset-password help text claims a 6-char +
  upper/lower/number/symbol policy, but only `len(password) >= 6` is enforced anywhere in code.
  Decision: correct the copy to state the real policy ("At least 6 characters."). Do not add new
  complexity validation.
- **Reset-password "Go home" link:** remove it, and remove the caption below the submit button
  ("Open the link from your email...").
- **Env var typo:** `BEEBHAI_APP_NAME` (missing an "M") is one of a family of `BEEBHAI_*` env
  vars sharing the same typo. Decision: rename the whole family to `BHEEMBHAI_*` for consistency
  (no deployed environments depend on the old names yet).

### New acceptance detail (supersedes/extends the sections above)

**Branding:** every user-facing and code-facing occurrence of `"BeemBhai"` becomes `"BheemBhai"`
(app name default, email sender name, email subject lines, signup/login/reset intro copy, CLI
prog/description, package docstrings, env var family). Infra-only identifiers that aren't display
branding (`minio_access_key`/`minio_secret_key`, the sqlite filename) are explicitly out of scope.

**Login (`GET/POST /login`):**
- Always show a BheemBhai intro blurb under the "Sign in" heading (parity with signup's "Join
  BheemBhai..." blurb) — not just on the pending state.
- Add a "Don't have an account? Sign up" link to `/signup` (parity with signup's reverse link).
- Remove the "Having trouble signing in? Contact support" row entirely.
- The "Verify your email before signing in" notice must NOT render on a plain page load — only
  as the actual error content when a submitted login fails because the account is unverified.
- Email and password fields get the same `.auth-input`/icon-wrapper treatment `signup.html`
  already uses (mail icon, lock icon) — today's gap causes a visible left-padding mismatch.
- "Forgot password?" links to the new `/forgot-password` page (see below), not directly to
  `/reset-password`.
- On a failed sign-in (bad credentials or unverified email), the heading stays "Sign in" (never
  "Sign in failed" / "Verify your email"), and no separate message paragraph duplicates the error
  — only the single errors alert box renders the failure text.

**Forgot password (new `GET/POST /forgot-password`):** a new browser page — email-only form,
reusing `AuthService.request_password_reset` (already exists, `app/auth/service.py:201`) via the
real-email-sender service instance (`_auth_service`, not `_browser_auth_service`, which is built
with `email_sender=None`). Always shows the same non-enumerating "check your email" success
message regardless of whether the account exists/is verified, matching the method's existing
silent-`False` design. Errors during send are caught and shown as a friendly in-page message.

**Reset password (`GET/POST /reset-password`):**
- Remove the "Token loaded" / "Password updated" static aside panels and the split-shell layout
  entirely — collapse to the same single-column card the other 3 screens use.
- Add a `confirm_password` field; server-side validation rejects a mismatch with "Passwords do
  not match." before calling `confirm_password_reset`.
- Remove the "Go home" link and the "Open the link from your email..." caption (per the resolved
  ambiguity above).
- The token arrives via the URL fragment (`#token=...`), invisible server-side. Client-side JS
  must show a visible `alert alert-danger` failure message and hide the form when no token is
  present in the fragment — replacing today's soft hint-text-only behavior.
- Correct the password help text to state the real policy (6 characters only).
- Add a BheemBhai-branded intro line under the heading, parity with signup/login.

**Verify email (`GET/POST /verify-email`):**
- Remove the "Verification link flow" 3-step section and the "Resend email" button entirely.
- The "Verified" status chip and checkmark ring must only render once verification has actually
  succeeded (`state == "success"`) — today they render unconditionally, which is misleading
  before the token is confirmed (same bug class as the login default-warning issue above).
- Client-side JS must show a visible `alert alert-danger` failure message and hide the auto-submit
  form when no token is present in the URL fragment — replacing today's soft hint-text-only
  behavior. Auto-verification itself (extract token from fragment, auto-submit) already works and
  is unchanged.
- On successful verification, replace "Go home" with a "Continue to sign in" link to `/login`.

**Signup (`GET/POST /signup`):**
- Remove the "Enterprise grade security / Data privacy by design / 99.9% platform uptime"
  trust-footer section entirely.
- Correct the password help text to state the real policy (6 characters only).
- Wrap the `register_user(...)` call in `signup_submit()` in try/except; a send failure (e.g. a
  live email-provider error) must render the signup form with a friendly in-page error, never
  FastAPI's default 500 page.

### Test surface additions
All of the above are template/behavior changes on already-covered screens plus one new page
(`/forgot-password`) — extend the existing unit test files per screen (`test_login.py`,
`test_signup.py`, `test_verify_email.py`, reset-password coverage) and `test_auth_mockups.py`'s
parametrized e2e checks; add `test_forgot_password.py`. The visual-regression baselines under
`tests/e2e/__snapshots__/auth/` will need re-capture after implementation (layout changes on all
4 existing screens, plus new baselines for `/forgot-password`) — same capture-after-visual-signoff
flow as the original story run.

### Out of scope (unchanged)
Real password-complexity enforcement (copy-only fix, see resolved ambiguities). Infra credential
identifiers (`minio_*`, sqlite filename). Anything not named above stays as BEEM-20 originally
shipped it.

---
*On approval: next step is `test-creator` (extend the existing test files for the changed/added
screens), then `implement`.*
