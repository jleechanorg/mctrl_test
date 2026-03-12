#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INPUT_PATH="${1:-$ROOT_DIR/openclaw-config/symphony/swe_bench_verified_5.json}"

SYMPHONY_TASK_PLUGIN="swe_bench_verified" \
SYMPHONY_TASK_PLUGIN_INPUT="$INPUT_PATH" \
"$ROOT_DIR/scripts/enqueue-symphony-tasks.sh"
