# Code Review — BEEM-20: UI FIX: Align authentication screens to approved mockups

**Advisory** · **Branch:** `feat/BEEM-19-align-authentication-screens` · **Reviewed vs:** `ae331b9` (tip of BEEM-19, already reviewed separately) · **Date:** 2026-07-18
**Pre-flight:** `verification.md` = PASS
**Scope:** BEEM-20's own commits only (`a399b17`..`bc3c3e4`) — story-design, test-creator, implement,
bugfix, visual baselines, lint fixes, verification report. BEEM-19's prior work has its own
`docs/product/epics/BEEM-3/stories/BEEM-19/code-review.md` and is not re-reviewed here.

## Severity summary
| Critical | High | Medium | Low | Nit |
|:--------:|:----:|:------:|:---:|:---:|
| 0 | 0 | 0 | 0 | 1 |
**Advisory note:** Clean pass — no correctness, security, or standards issues found. One Nit
(test-helper performance) noted for optional future cleanup; nothing blocks `pr-create`.

## Tools run
```
$ uv run ruff check .
All checks passed!

$ uv run ruff format --check .
Would reformat: app/auth/tokens.py
Would reformat: app/core/settings.py
Would reformat: tests/compose_stack.py
Would reformat: tests/e2e/test_login_page.py
Would reformat: tests/integration/auth/test_auth_login.py
Would reformat: tests/integration/auth/test_register.py
6 files would be reformatted, 62 files already formatted
```
The 6 format-drift files are all pre-existing (none touched by BEEM-20's diff, confirmed via
`git diff ae331b9..HEAD --stat`) and `ruff format --check` is not a CI gate
(`.github/workflows/ci.yml` only runs `ruff check .`) — non-blocking, out of scope.

```
$ git diff ae331b9..HEAD --stat
 27 files changed, 806 insertions(+), 134 deletions(-)
```
Scoped diff confirms the change stays inside the modules `story-design.md` named: `theme.css`,
the 4 auth templates, the new `layouts/auth.html` shell, `base.html`'s stylesheet link, the
vendored Bootstrap/feather assets, the new test files, and `pyproject.toml`'s dev-only `Pillow`
addition. No route, service, or data-model file changed.

## Findings

### 1. Coding standards & conventions
| # | Severity | Location | Finding | Proposed fix |
|---|----------|----------|---------|--------------|
| — | — | — | None. Templates consistently use real Bootstrap classes (`form-control`, `btn btn-primary`, `alert alert-*`) instead of the bespoke `auth-callout*` tree they replace; the `--bb-accent`→`--bb-primary` rename was applied at all 15+ call sites with no stray references (`grep -n "bb-accent\b"` shows only the unrelated `--bb-accent-2` token remaining). | — |

### 2. Security audit
| # | Severity | Location | Finding (risk) | Proposed fix |
|---|----------|----------|----------------|--------------|
| — | — | — | None. No new input handling, no new routes/endpoints. `reset_password.html`'s token-fragment script (unchanged logic, only its wrapping block renamed) sets the token via `tokenInput.value = token`, not `innerHTML` — no injection surface. Scanned the full template diff for `target=`, `javascript:`, `innerHTML`, `eval(` — none present. Vendored `bootstrap.min.css` (228K) and `feather-sprite.svg` (56K) are unmodified upstream MIT-licensed files copied verbatim, confirmed by matching the Bootstrap 5.3.3 header banner. `Pillow` was added to the `dev` dependency group only ([pyproject.toml](../../../../../../pyproject.toml) diff), not a runtime dependency. | — |

### 3. Acceptance-criteria intent
| # | Severity | Location | Finding | Proposed fix |
|---|----------|----------|---------|--------------|
| — | — | — | None beyond what `verification.md` already confirmed. Spot-checked the intent behind two non-obvious scenarios: (1) `app/web/templates/auth/login.html` correctly distinguishes the default "verify your email" notice (`alert-warning`, amber) from a submitted-form error (`alert-danger`), matching story-design's explicit callout-treatment split rather than reusing one class for both. (2) `test_reset_password_page_shows_both_status_panels_together` asserts the token-loaded and success aside panels render simultaneously as static content — this matches the mockup's two-panel-always-visible layout, not a state-toggle bug. | — |

### 4. Maintainability
| # | Severity | Location | Finding | Proposed fix |
|---|----------|----------|---------|--------------|
| 1 | Nit | `tests/e2e/test_auth_visual_regression.py:36-49` (`_diff_ratio`) | Per-pixel Python double loop over a 1440×900 (and 390×844) image is O(w·h) in pure Python; works fine today (34 e2e tests ran in ~49s total) but will get slower as more screens/viewports are added to `SCREENS`/`VIEWPORTS`. | Optional: vectorize with `numpy` (`np.abs(a.astype(int) - b.astype(int))`) if this suite grows or CI time becomes a concern. Not worth doing now for 8 baselines. |

## Fix list for `implement` (ordered by severity)
None required. The one Nit is optional and does not need to go through `implement`/`test-verify`
before `pr-create`.

---
*Advisory — blocks nothing. The team picks which findings to fix. Accepted fixes → `implement`
applies them → `test-verify` re-runs → `pr-create`. If all waived → straight to `pr-create`.*
