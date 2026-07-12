#!/usr/bin/env bash
set -euo pipefail

# Ensure Codex can find nvm Node/npm/npx and uvx
export PATH="/home/fusiongamingmasterpc/.nvm/versions/node/v24.16.0/bin:/home/fusiongamingmasterpc/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

PROJECT_ROOT="/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai"
ENV_FILE="$PROJECT_ROOT/.env"
LOG_FILE="$PROJECT_ROOT/.mcp-jira.log"

{
  echo "========================================"
  echo "Starting Jira MCP at $(date)"
  echo "PATH=$PATH"
  echo "npx=$(command -v npx || true)"
  echo "node=$(command -v node || true)"
  echo "uvx=$(command -v uvx || true)"
  echo "ENV_FILE=$ENV_FILE"
  echo "ENV_EXISTS=$(test -f "$ENV_FILE" && echo yes || echo no)"
  echo "========================================"
} >> "$LOG_FILE"

exec /home/fusiongamingmasterpc/.nvm/versions/node/v24.16.0/bin/npx \
  -y dotenv-cli \
  -e "$ENV_FILE" \
  -- /home/fusiongamingmasterpc/.local/bin/uvx mcp-atlassian \
  2>> "$LOG_FILE"