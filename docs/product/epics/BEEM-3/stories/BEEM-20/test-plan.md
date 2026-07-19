# Test Plan — BEEM-20: UI FIX: Align authentication screens to approved mockups

**Story folder:** `docs/product/epics/BEEM-3/stories/BEEM-20/`
**Design note:** `story-design.md` (approved)

## Scenario → test mapping

| Scenario | Test(s) |
|----------|---------|
| Signup screen matches the approved mockup | `tests/e2e/test_auth_mockups.py::test_auth_mockup_pages_render[...-/signup-Create account-Already have an account?]` (existing), `tests/e2e/test_auth_mockups.py::test_signup_page_shows_trust_footer` (new), `tests/unit/web/test_signup.py::test_signup_page_renders_form` (existing) |
| Sign-in screen matches the approved mockup | `tests/e2e/test_auth_mockups.py::test_auth_mockup_pages_render[...-/login-Sign in-Verify your email before signing in]` (existing), `tests/e2e/test_auth_mockups.py::test_login_page_shows_support_and_recovery_links` (new), `tests/unit/web/test_login.py::test_login_page_renders_form` (existing) |
| Reset password screen matches the approved mockup | `tests/e2e/test_auth_mockups.py::test_auth_mockup_pages_render[...-/reset-password-Reset password-Token loaded]` (existing), `tests/e2e/test_auth_mockups.py::test_reset_password_page_shows_both_status_panels_together` (new), `tests/unit/web/test_verify_email.py::test_reset_password_page_mentions_fragment_handshake` (existing) |
| Verify email screen matches the approved mockup | `tests/e2e/test_auth_mockups.py::test_auth_mockup_pages_render[...-/verify-email-Verify your email-Verification link flow]` (existing), `tests/e2e/test_auth_mockups.py::test_verify_email_page_shows_primary_and_secondary_actions` (new), `tests/unit/web/test_verify_email.py::test_verify_email_page_mentions_fragment_handshake` (existing) |
| Auth screens remain usable on a narrow viewport | `tests/e2e/test_auth_mockups.py::test_auth_mockup_pages_stay_within_mobile_viewport[...]` (existing) |
| *(cross-cutting, from user feedback)* Screens actually **look** like the mockups, not just contain the right text | `tests/e2e/test_auth_visual_style.py::test_auth_pages_load_real_bootstrap_container_breakpoints[...]` (new), `::test_auth_primary_button_color_matches_bb_primary_token[...]` (new), `::test_login_password_toggle_uses_feather_icon_sprite` (new), `tests/e2e/test_auth_visual_regression.py::test_auth_screen_matches_approved_visual_baseline[...]` (new) |

## New-red confirmation

Run 1 — unit tests (`uv run pytest tests/unit/web/ -q`): 4 failed, 10 passed.
- `test_login.py::test_login_submit_shows_unverified_account_error` — **red**: asserts
  `"alert-danger" in response.text`; current markup still emits `status-pill--error`
  (bespoke hook being migrated to the Bootstrap-idiomatic class this story introduces).
- `test_login.py::test_login_submit_shows_invalid_credentials_error` — same reason.
- `test_signup.py::test_signup_submit_shows_validation_errors` — same reason.
- `test_signup.py::test_signup_submit_shows_duplicate_email_error` — same reason.
- The 10 passing tests are pre-existing content assertions BEEM-19 already satisfies; left
  untouched (not weakened, not re-asserted redundantly).

Run 2 — e2e tests (`uv run pytest tests/e2e/test_auth_mockups.py tests/e2e/test_auth_visual_style.py tests/e2e/test_auth_visual_regression.py -q -m e2e`), against the deployed
Docker Compose stack: **17 failed, 12 passed** in 71.58s.
- 12 passed: the pre-existing `test_auth_mockups.py` content/visibility checks (including the
  4 new ones added this story — trust footer, support/recovery links, verify-email actions,
  reset-password dual panels) — these already pass because BEEM-19 got the right text/elements
  onto the page; they are not this story's red, and are kept as regression coverage.
- 17 failed, all clean assertion/`pytest.fail` reds (no import/fixture/harness errors):
  - `test_auth_pages_load_real_bootstrap_container_breakpoints` × 4 paths — no real Bootstrap
    loaded yet, `.container` doesn't resolve the `1320px` breakpoint.
  - `test_auth_primary_button_color_matches_bb_primary_token` × 4 paths — `AssertionError:
    --bb-primary is not defined on :root` (code only has `--bb-accent` today).
  - `test_login_password_toggle_uses_feather_icon_sprite` — no feather sprite present.
  - `test_auth_screen_matches_approved_visual_baseline` × 8 (4 screens × 2 viewports) — each
    fails with the explicit `pytest.fail("No approved visual baseline ... yet ... Do not
    fabricate a baseline")` message, exactly as designed.

## Notes on scope of new tests

- Pure text-presence duplicates of what BEEM-19 already covers were **not** re-added — only
  genuinely new assertions were written (visibility of links/buttons not previously checked,
  and the two-panel reset-password layout together in one render).
- `status-pill--error` → `alert-danger`: this migrates an existing test *hook* (a CSS class
  used only to detect "an error occurred," not part of the approved mockups) to the
  Bootstrap-idiomatic equivalent introduced by this story's Bootstrap adoption. The underlying
  behavior asserted (error state is shown) is unchanged.
- `--bb-primary` is the token name documented in `docs/ui-conventions.md`'s Color Roles table;
  today's code only defines `--bb-accent`. The new computed-style test enforces the documented
  name, which requires `implement` to introduce/rename the token, not just reuse `--bb-accent`.
- The screenshot-baseline test is written to `pytest.fail` with an explicit "no baseline yet"
  message when `tests/e2e/__snapshots__/auth/<screen>-<viewport>.png` doesn't exist — this is
  the expected red until `implement` captures baselines after your visual sign-off, per
  `story-design.md`'s screenshot-baseline workflow. It must never be satisfied by fabricating a
  baseline from the current (incorrect) render.

---
*On completion of this run: next step is `implement`, whose job is to make exactly these tests
pass without weakening them.*
