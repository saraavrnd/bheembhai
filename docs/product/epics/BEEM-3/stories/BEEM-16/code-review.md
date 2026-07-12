# Code Review — BEEM-16: Bootstrap initial platform admin

**Advisory** · **Branch:** `feat/BEEM-16-bootstrap-initial-platform-admin` · **Reviewed vs:** main · **Date:** 2026-07-12
**Pre-flight:** [verification.md](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/docs/product/epics/BEEM-3/stories/BEEM-16/verification.md) = PASS

## Severity summary
| Critical | High | Medium | Low | Nit |
|:--------:|:----:|:------:|:---:|:---:|
| 0 | 0 | 3 | 0 | 0 |
**Advisory note:** Recommend fixing the 3 Medium findings before PR; they affect the public verification path, security of the emailed token, and transaction behavior around external I/O.

## Tools run
```
$ uv run ruff check .
All checks passed!

$ uv run python - <<'PY'
import importlib.util
for name in ('bandit', 'pip_audit', 'safety'):
    print(f'{name}={importlib.util.find_spec(name) is not None}')
PY
bandit=False
pip_audit=False
safety=False
```

## Findings

### 1. Coding standards & conventions
| # | Severity | Location | Finding | Proposed fix |
|---|----------|----------|---------|--------------|
| 1 | Medium | [app/web/router.py:37-56](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/app/web/router.py#L37) | The verification page builds a fresh database engine and repository on every request, then calls `ensure_schema()` inside the request path. That is a poor fit for the repo's startup/migration boundary and it turns a public GET endpoint into a place that repeatedly touches schema state and connection pools. | Move auth/repository construction to app startup or a cached dependency, reuse the shared service/repository, and remove `ensure_schema()` from the request path. If the route stays sync-only, prefer a plain `def` handler so FastAPI can run it in the threadpool instead of blocking the event loop. |

### 2. Security audit
| # | Severity | Location | Finding (risk) | Proposed fix |
|---|----------|----------|----------------|--------------|
| 1 | Medium | [app/auth/service.py:155-188](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/app/auth/service.py#L155) | Email-verification and password-reset tokens are embedded directly in query-string URLs. Those tokens can leak via browser history, access logs, referrer headers, and copy/paste sharing, which makes the activation/reset link more sensitive than it needs to be. | Prefer a landing page that receives only a short-lived opaque identifier, then POSTs the token in the request body, or use a fragment plus client-side submission so the raw token does not travel in the URL. At minimum, set a strict referrer policy and keep the token one-time and short-lived. |

### 3. Acceptance-criteria intent
No separate acceptance-criteria gap was found beyond the verified scenarios. The story matches the updated bootstrap intent, and the bootstrap-specific scenarios are covered by running tests.

### 4. Maintainability
| # | Severity | Location | Finding | Proposed fix |
|---|----------|----------|---------|--------------|
| 1 | Medium | [app/auth/service.py:45-105](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/app/auth/service.py#L45) | The bootstrap and upsert flows keep a database transaction open while waiting on outbound Brevo delivery. That couples write latency to a remote API, increases the chance of lock contention/timeouts, and makes the persistence step harder to evolve independently from notification delivery. | Split persistence from notification delivery with an outbox or after-commit dispatch step. If the MVP keeps the current shape, extract the shared "persist then notify" workflow into one helper so the transaction boundary is explicit and easier to test. |

## Fix list for `implement` (ordered by severity)
1. [Medium] Rework the `/verify-email` path to reuse a shared auth/repository service instead of creating a new engine and schema on every request, and make the handler sync if the implementation remains sync-only.
2. [Medium] Remove raw verification/reset tokens from query-string URLs and move the token through a safer POST or fragment-based handoff.
3. [Medium] Separate database writes from Brevo delivery so the write transaction does not remain open across network I/O; if needed, introduce an outbox or after-commit notification step.

---
*Advisory — blocks nothing. The team picks which findings to fix. Accepted fixes → `implement` applies them → `test-verify` re-runs → `pr-create`. If all waived → straight to `pr-create`.*
