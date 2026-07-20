# API regression suite (Hurl)

An ordered, black-box smoke/regression suite for the deployed BheemBhai API. It is meant to run
against a **real deployed environment** (e.g. right after a `docker compose up` / a deploy), not
against the fixture-backed test stack the pytest integration suite (`tests/integration/`) uses.
The two layers are complementary:

| | pytest (`tests/integration/`) | this suite (`tests/regression/`) |
|---|---|---|
| Target | Test-only Docker Compose stack, fresh per run | Any deployed environment |
| Setup | Fixtures, in-process shortcuts (e.g. minting tokens directly) | Only what a real client could do: the `beembhai-admin` CLI + real HTTP calls |
| Tool | pytest | [Hurl](https://hurl.dev) (pinned: 8.0.0) |
| Runs | Every CI run / `test-verify` | Manually, or as a post-deploy smoke check |

## Prerequisites

- `hurl` installed (single static binary): https://hurl.dev/docs/installation.html
- `jq` installed (used to read the bootstrap CLI's JSON result)
- The target API reachable at `BASE_URL` (default `http://localhost:8000`)
- `uv` available to run the bootstrap CLI (`beembhai-admin`)

## Running

```bash
BASE_URL=http://localhost:8000 ./tests/regression/run.sh
```

Optional env vars — either export them, or set them in the repo root `.env` (see the repo root
`.env.example`; that file is gitignored, so real credentials never get committed). `run.sh` reads
only these two specific keys out of the root `.env` if present — it does not source the whole
file, so it can't clobber `DATABASE_URL`/other settings a caller has deliberately configured for
a different target environment:
- `REGRESSION_ADMIN_EMAIL` / `REGRESSION_ADMIN_PASSWORD` — credentials for the platform admin
  the suite bootstraps and logs in as. **Leave these unset for normal use** — `run.sh` defaults
  `REGRESSION_ADMIN_EMAIL` to a per-run-unique address (`regression-admin-<run-id>@example.com`)
  and, if `REGRESSION_ADMIN_PASSWORD` isn't set, generates a fresh random password for that run
  only. Both are required to be per-run-unique because of the cleanup behavior below — see
  "Standing-admin cleanup."

`run.sh`:
1. Runs `beembhai-admin bootstrap-admin --email ... --password ... --verified` first. This is
   idempotent (per `app/auth/service.py`'s `bootstrap_platform_admin`): on a genuinely clean
   environment it creates the admin; if a platform admin already exists it is left untouched and
   the call is a no-op.
2. Runs the `.hurl` files in this directory **in filename order** (`01_...` → `08_...`),
   chaining a single cookie jar across all of them (`hurl -b/-c`) so the session established by
   the login step in `02_auth_admin_login.hurl` carries through to the later files, exactly like
   a real browser/client session.
3. Exits non-zero on the first failing scenario (`hurl --test`), so it's safe to wire into a
   deploy pipeline as a gate if desired.
4. Always deactivates the admin it bootstrapped, whether the run passed or failed — see below.

### Standing-admin cleanup (deactivate on every run)

Every run's cleanup trap deactivates (`beembhai-admin deactivate-user`) the platform admin it
just bootstrapped, **regardless of whether the regression suite passed or failed**. This is
deliberate: a platform-admin account with credentials that live in a script (even a
randomly-generated, per-run password) shouldn't be left standing in the target environment after
the run is over. Rules that make this safe:
- Only an admin this run actually **created** is deactivated — never a pre-existing admin that
  `bootstrap-admin` found and left untouched (idempotent skip). The script tracks this via the
  bootstrap CLI's own JSON `action` field, so it never touches an admin it didn't create.
- Deactivation runs from a `trap ... EXIT` cleanup handler, so it fires on success, on a failing
  `hurl --test`, and on an early script error alike — the script's real exit code is still
  reported to the caller (e.g. CI) either way.
- **Downside, accepted as a known tradeoff:** each run creates a brand-new admin (hence the
  per-run-unique default email above) and leaves it deactivated afterward rather than reusing it.
  Deactivated rows accumulate in the `users` table over repeated runs. Nothing else depends on
  them; they're inert once deactivated (login is rejected with `403`), but they are not deleted.

**Re-running against a persistent (not freshly-recreated) environment:** because of the
always-deactivate behavior above, pinning a *fixed* `REGRESSION_ADMIN_EMAIL` no longer supports
clean reruns the way it might otherwise seem to — the second run's bootstrap would either find
the (now-deactivated) previous row skipped as "already exists" with the wrong credentials, or
collide on the unique email constraint if bootstrap ever created a fresh one. In practice: don't
pin `REGRESSION_ADMIN_EMAIL` for repeat runs; let the per-run-unique default handle it. Pinning
is only useful for reproducing a single run's exact credentials while debugging that same run.

## Scope

Covers every endpoint currently implemented (`app/auth/`, `app/projects/`) — see
`docs/testing-strategy.md` for how this fits the overall test layering. Endpoints in
`docs/api-contracts/beembhai-api.openapi.yaml` that are still stubs (`integrations`, `runs`,
`approvals`, `notifications`, project detail/members/roles) are out of scope until implemented;
add their `.hurl` files alongside the story that builds them.

### Known gap: email-verification-token flows aren't black-box testable

`POST /auth/register` and the password-reset flow send a real verification/reset token by email
via Brevo's HTTP API (`app/notifications/email.py`) — there is no local mail-catcher wired into
the deployed stack. This suite can therefore only exercise:
- registration itself (happy path + duplicate-email + invalid-format rejections),
- login being correctly rejected for an unverified account (`403`),
- the reset-request endpoint's no-enumeration behavior (`204` either way),
- both `/auth/email/verify` and `/auth/password-reset/confirm` rejecting an invalid/unissued
  token (`400`).

It does **not** complete a real "click the emailed link" happy path — that is already covered by
`tests/integration/auth/test_auth_login.py` and `tests/unit/auth/test_service.py`, which mint the
token in-process rather than sending a real email. The bootstrap admin sidesteps this entirely via
the `--verified` flag on `beembhai-admin bootstrap-admin` (`app/cli/admin_handler.py`), added
specifically so this suite has a login-ready account without needing real email delivery.

Also out of scope for this suite: a black-box "non-admin cannot create a project" check, which
would require a second *verified* non-admin account — `--verified` was only added to
`bootstrap-admin`, not `upsert-user`. That permission check is covered by
`tests/unit/projects/test_project_service.py::test_create_project_rejects_non_admin_actor` and
`tests/integration/projects/test_projects_api.py::test_create_project_endpoint_rejects_non_admin`.

## Adding to this suite

- New file per logical flow (not per request) — files that need session continuity (e.g. a
  project's create-then-list) capture and reuse variables *within* the same file; Hurl does not
  share captures across separate files. Cross-file continuity is limited to the shared cookie jar.
- Prefix with the next two-digit number so `ls` order is execution order.
- Use `{{run_id}}` (a per-run unique suffix injected by `run.sh`) in any name/email that must not
  collide across repeated runs against a persistent environment.
