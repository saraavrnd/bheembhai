# Story Design — BEEM-19: Align authentication screens to approved mockups

**Status:** AWAITING APPROVAL · **Epic:** BEEM-3 · **Date:** 2026-07-16
**Domain:** frontend

> Thin design note. Review and approve before test-creator writes tests. Change anything;
> I'll realign and re-confirm.

## Target module(s)
- `app/web/templates/auth/signup.html` for the signup screen.
- `app/web/templates/auth/login.html` for the sign-in screen.
- `app/web/templates/auth/verify_email.html` for the email-verification screen.
- `app/web/templates/auth/reset_password.html` for the password-reset screen.
- `app/web/static/css/theme.css` for the shared auth card, spacing, button, and accent-color treatment.
- `app/web/router.py` only if a small copy or view-model tweak is needed to keep the four screens consistent.

## Interfaces / endpoints
| Kind | Signature | Request → Response |
|------|-----------|--------------------|
| page | `GET /signup` | visitor request → signup form matching `signup-light.png` |
| page | `GET /login` | visitor request → sign-in form matching `signin-unified.png` |
| page | `GET /verify-email` | visitor request → verification landing page matching `verify-email-unified.png` |
| page | `GET /reset-password` | visitor request → password-reset form matching `reset-password.png` |

## Data-model deltas
None. This story changes only the browser presentation layer and keeps the auth flows, token handling, and session behavior intact.

## Reuse
- Existing auth routes and form submission handlers.
- Existing browser auth-card and `status-pill` patterns.
- Existing token-fragment behavior for verification and password reset.
- Existing approval mockups in `output/imagegen/beem-3-ui-mockups/`.

## Approach
Align the four auth screens to one consistent light visual system. Keep `signup-light.png` as the only screen that shows the BheemBhai brand name explicitly; make `signin-unified.png`, `verify-email-unified.png`, and `reset-password.png` feel like the same family without brand-name repetition. Unify the card elevation, border radius, spacing rhythm, button treatment, and accent colors so the pages read as one account-access flow rather than four unrelated comps. Preserve the approved screen-specific content: the sign-in warning, the verification success state, the reset-password helper copy, and the signup trust footer. Avoid introducing any new side rails, onboarding panels, or dark-theme styling.

## Test surface
- [x] Visual: each screen matches its approved mockup at desktop width.
- [x] Visual: the four screens share a consistent light theme and accent palette.
- [x] Visual: auth screens remain usable on a narrow viewport without horizontal scrolling.

## Out of scope
Changing auth behavior, backend routes, token semantics, email delivery, MFA, SSO, social login, or copy outside the approved mockup content.

## Architecture impact
None. This stays inside the existing browser-template and shared-css seams.

## Dependencies discovered (feeds epic-sequence)
- Consumes: `BEEM-18` signup and `BEEM-14` sign-in / verify-email / reset-password behavior.
- Produces: the polished account-access surface that later auth-dependent stories can reuse.
- Effect on sequence: follows the auth-flow stories and stays frontend-only.

## Traceability
**Requirements covered:** FR-005

---
*On approval: next step is `test-creator` (failing tests from these screens and their acceptance criteria), then `implement`.*
