#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "launch_claude.sh: missing .env in current directory: $ENV_FILE" >&2
  exit 1
fi

while IFS= read -r line || [[ -n "$line" ]]; do
  case "$line" in
    ''|\#*)
      continue
      ;;
    export\ *)
      line=${line#export }
      ;;
  esac

  case "$line" in
    JIRA*=*|GH_*=*|TOOLSETS=*)
      eval "export $line"
      ;;
  esac
done < "$ENV_FILE"

exec claude "$@"
