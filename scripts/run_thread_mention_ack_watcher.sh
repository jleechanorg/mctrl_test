#!/usr/bin/env bash
set -euo pipefail

# Run Slack thread mention ack watcher from any directory in this repo.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"

cd "$ROOT_DIR"
exec python3 -m orchestration.thread_mention_ack_watcher \
  --config "$ROOT_DIR/scripts/thread_mention_ack_config.json" \
  "$@"
