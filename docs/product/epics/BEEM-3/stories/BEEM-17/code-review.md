# Code Review — BEEM-17: Register a local user account

**Advisory** · **Branch:** `feat/BEEM-18-add-browser-signup-page` · **Reviewed vs:** main · **Date:** 2026-07-13
**Pre-flight:** verification-BEEM-17.md = PASS

## Severity summary
| Critical | High | Medium | Low | Nit |
|:--------:|:----:|:------:|:---:|:---:|
| 0 | 0 | 1 | 0 | 0 |

**Advisory note:** 1 Medium — reasonable to fix before PR, but the implementation is otherwise aligned with the story.

## Tools run
```text
uv run ruff check app/auth/service.py app/auth/router.py tests/unit/auth/test_service.py tests/integration/auth/test_register.py -> All checks passed!
```

## Findings

### 1. Coding standards & conventions
No findings.

### 2. Security audit
| # | Severity | Location | Finding (risk) | Proposed fix |
|---|----------|----------|----------------|--------------|
| 1 | Medium | `app/auth/service.py:88-104` | `register_user()` hashes the supplied password before it knows whether the email is already taken. Because Argon2 hashing is intentionally expensive, repeated duplicate-signup attempts still consume the full password-hash cost even though they will be rejected. That makes this public endpoint easier to abuse for CPU and memory exhaustion. | Move `password_hasher.hash(password)` into the create-user branch after the duplicate lookup so rejected duplicate requests return before any expensive hashing work. |

### 3. Acceptance-criteria intent
No findings.

### 4. Maintainability
No findings.

## Fix list for `implement` (ordered by severity)
1. [Medium] Move password hashing in `AuthService.register_user(...)` so duplicate-email requests are rejected before Argon2 runs.

---
Advisory only. If the team accepts the fix, route it through `implement` and re-run `test-verify` before `pr-create`.
