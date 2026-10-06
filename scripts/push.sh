#!/usr/bin/env bash
# push.sh — Push code to the team repo, then submit the AI log to the BTC server.
#
# Usage:
#   bash scripts/push.sh [<branch>] [-- <extra git push args>]
#
# Examples:
#   bash scripts/push.sh                 # push current branch to origin
#   bash scripts/push.sh main            # push 'main' to origin
#   bash scripts/push.sh feature/x -u    # push and set upstream
#
# Behaviour:
#   1. Pushes the given (or current) branch to 'origin'.
#   2. Submits .ai-log/session.jsonl via scripts/submit_log.py.
#
# Notes:
#   - The repo already installs a git pre-push hook (scripts/setup_hooks.sh)
#     that also runs submit_log.py. This script is the explicit, manual
#     counterpart requested by the team: one command to push + submit.
#   - submit_log.py never aborts the push on a server error; it keeps logs
#     locally and retries next time.

set -euo pipefail

REMOTE="origin"

# Resolve branch: first non-flag arg, else current branch.
BRANCH=""
EXTRA_ARGS=()
for arg in "$@"; do
  if [ -z "$BRANCH" ] && [[ "$arg" != -* ]]; then
    BRANCH="$arg"
  else
    EXTRA_ARGS+=("$arg")
  fi
done

if [ -z "$BRANCH" ]; then
  BRANCH="$(git rev-parse --abbrev-ref HEAD)"
fi

echo "[push] Pushing '$BRANCH' to '$REMOTE'..."
git push "${EXTRA_ARGS[@]}" "$REMOTE" "$BRANCH"

echo "[push] Submitting AI log..."
bash scripts/_pyrun.sh scripts/submit_log.py || true

echo "[push] Done."
