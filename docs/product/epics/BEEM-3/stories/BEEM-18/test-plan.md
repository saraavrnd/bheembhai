# Test Plan — BEEM-18: Add browser signup page

**Epic:** BEEM-3 · **Date:** 2026-07-13 · **Runners:** `pytest`, `pytest-playwright`

## Scenario → test mapping
Every Gherkin scenario must map to at least one test.

| # | Acceptance scenario | Layer | Test file::test name | Type |
|---|---------------------|-------|----------------------|------|
| 1 | Signup page renders the form | e2e | `tests/e2e/test_signup_page.py::test_signup_page_renders` | happy |
| 2 | Successful signup creates an account and shows the next step | e2e | `tests/e2e/test_signup_page.py::test_signup_page_successfully_registers_a_new_user` | happy |
| 3 | Duplicate email signup is rejected | integration | `tests/integration/auth/test_register.py::test_register_endpoint_rejects_duplicate_email` | unhappy |
| 4 | Invalid signup input is rejected | unit | `tests/unit/web/test_signup.py::test_signup_submit_shows_validation_errors` | unhappy |

## Coverage check
- [ ] Every acceptance scenario has at least one test.
- [ ] Unhappy paths covered (invalid input, boundary, permissions where relevant).
- [ ] Tests target the interfaces from the approved story-design note.

## Red-phase verification
Initial BEEM-18 runs failed with `404 Not Found` on `/signup` because the browser route did not
exist yet. The e2e happy-path test also could not find the signup form fields for the same reason.

## Traceability
**Requirements covered:** FR-005

---
*Next: `implement` makes these tests pass without weakening them.*
