#!/usr/bin/env bash
# Ordered, black-box API regression suite. Runs the .hurl files in this directory, in filename
# order, against a real deployed BheemBhai API — intended for a clean environment right after
# deployment, not the fixture-backed pytest integration stack (see tests/regression/README.md).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Optional local override, reusing the repo's existing root .env (gitignored, see .env.example)
# — lets REGRESSION_ADMIN_EMAIL / REGRESSION_ADMIN_PASSWORD be pinned for repeat runs against a
# persistent environment without ever committing real credentials to the script. Only these two
# keys are pulled out of .env (not sourced wholesale): the root .env also carries DATABASE_URL,
# Postgres/Brevo/Jira/GH credentials, etc. for the app and its own tooling, and blindly exporting
# all of it here could silently override settings this script's caller already configured on
# purpose (e.g. pointing BASE_URL/DATABASE_URL at a different deployment than the local .env).
# Already-exported env vars always win over the .env file.
if [ -f "$REPO_ROOT/.env" ]; then
  : "${REGRESSION_ADMIN_EMAIL:=$(grep -E '^REGRESSION_ADMIN_EMAIL=' "$REPO_ROOT/.env" | tail -n1 | cut -d= -f2-)}"
  : "${REGRESSION_ADMIN_PASSWORD:=$(grep -E '^REGRESSION_ADMIN_PASSWORD=' "$REPO_ROOT/.env" | tail -n1 | cut -d= -f2-)}"
fi

RUN_ID="$(date +%s)-$$"

BASE_URL="${BASE_URL:-http://localhost:${API_PORT:-8000}}"
# Defaults to a per-run-unique email (not a fixed address) because the admin bootstrapped here is
# always deactivated at the end of the run (see the cleanup trap below), so a fixed email would
# collide with its own now-deactivated row on the very next run. If you pin
# REGRESSION_ADMIN_EMAIL yourself, you're responsible for it being unique per run too.
ADMIN_EMAIL="${REGRESSION_ADMIN_EMAIL:-regression-admin-${RUN_ID}@example.com}"
if [ -n "${REGRESSION_ADMIN_PASSWORD:-}" ]; then
  ADMIN_PASSWORD="$REGRESSION_ADMIN_PASSWORD"
else
  # No credential is hardcoded in the script: generate a fresh, unguessable password for this
  # run. This account only needs to be known to this script (bootstrap immediately followed by
  # login), so a random per-run secret is more secure than a static committed default — it can't
  # be reused by anyone who reads the script/repo. Pin REGRESSION_ADMIN_PASSWORD (env var or the
  # repo root .env) if you want a specific password instead of a generated one.
  ADMIN_PASSWORD="$(openssl rand -base64 24 | tr -d '=+/')Aa1!"
  echo "==> No REGRESSION_ADMIN_PASSWORD set; generated a random one-time password for this run."
fi

NEW_USER_EMAIL="regression-user-${RUN_ID}@example.com"
NEW_USER_PASSWORD="RegressionUser123!"
OVERSIZED_PROJECT_NAME="$(printf 'A%.0s' $(seq 1 256))"

if ! command -v hurl >/dev/null 2>&1; then
  echo "error: hurl is not installed (this suite is pinned to hurl 8.0.0)." >&2
  echo "       see https://hurl.dev/docs/installation.html" >&2
  exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq is not installed (needed to read the bootstrap-admin result)." >&2
  exit 1
fi

COOKIE_JAR="$(mktemp)"
CREATED_ADMIN_EMAIL=""

cleanup() {
  local exit_code=$?
  rm -f "$COOKIE_JAR"
  # Only ever deactivate the admin THIS run created — never an admin bootstrap-admin found
  # already existing (idempotent skip), which could be a real, unrelated platform admin.
  if [ -n "$CREATED_ADMIN_EMAIL" ]; then
    echo "==> Deactivating regression admin (${CREATED_ADMIN_EMAIL}) so it can't be reused"
    uv run beembhai-admin deactivate-user --email "$CREATED_ADMIN_EMAIL" >/dev/null 2>&1 || true
  fi
  exit "$exit_code"
}
trap cleanup EXIT

echo "==> Bootstrapping platform admin (idempotent, verified) at ${BASE_URL}"
BOOTSTRAP_RESULT="$(uv run beembhai-admin bootstrap-admin \
  --email "$ADMIN_EMAIL" \
  --password "$ADMIN_PASSWORD" \
  --verified)"
echo "$BOOTSTRAP_RESULT"
if [ "$(echo "$BOOTSTRAP_RESULT" | jq -r '.action')" = "created" ]; then
  CREATED_ADMIN_EMAIL="$ADMIN_EMAIL"
else
  # bootstrap-admin found a pre-existing admin and left it untouched; ADMIN_EMAIL/PASSWORD below
  # won't match it, so login in 02_auth_admin_login.hurl is expected to fail — this only happens
  # against an environment that already has a platform admin outside this script's control.
  echo "==> A platform admin already existed; bootstrap was skipped (nothing to deactivate)." >&2
fi

printf '# Netscape HTTP Cookie File\n' >"$COOKIE_JAR"

echo "==> Running ordered API regression suite against ${BASE_URL}"
for file in "$SCRIPT_DIR"/*.hurl; do
  echo "--- $(basename "$file")"
  hurl --test \
    --variable base_url="$BASE_URL" \
    --variable admin_email="$ADMIN_EMAIL" \
    --variable admin_password="$ADMIN_PASSWORD" \
    --variable run_id="$RUN_ID" \
    --variable new_user_email="$NEW_USER_EMAIL" \
    --variable new_user_password="$NEW_USER_PASSWORD" \
    --variable oversized_project_name="$OVERSIZED_PROJECT_NAME" \
    --cookie "$COOKIE_JAR" \
    --cookie-jar "$COOKIE_JAR" \
    "$file"
done

echo "==> All regression scenarios passed"
