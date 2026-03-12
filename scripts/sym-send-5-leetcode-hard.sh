#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INPUT_PATH="${1:-$ROOT_DIR/openclaw-config/symphony/leetcode_hard_5.json}"

SYMPHONY_TASK_PLUGIN="leetcode_hard" \
SYMPHONY_TASK_PLUGIN_INPUT="$INPUT_PATH" \
"$ROOT_DIR/scripts/enqueue-symphony-tasks.sh"
