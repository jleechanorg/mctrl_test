#!/usr/bin/env bash
set -euo pipefail

# Run TaskPoller from any directory in this repo without requiring callers to
# manage PYTHONPATH manually.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"

cd "$ROOT_DIR"
exec python -m orchestration.task_poller "$@"
