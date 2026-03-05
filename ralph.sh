#!/bin/bash
# Ralph Wiggum - Long-running AI agent loop for jleechanclaw orchestration
# Usage: ./ralph.sh [--tool minimax|claude|codex] [max_iterations]
#
# Tools:
#   minimax  — Claude Code via MiniMax API (claudem wrapper)
#   claude   — Claude Code via Anthropic API
#   codex    — Codex CLI

set -e

# Parse arguments
TOOL="minimax"  # Default to minimax
MAX_ITERATIONS=30

while [[ $# -gt 0 ]]; do
  case $1 in
    --tool)
      TOOL="$2"
      shift 2
      ;;
    --tool=*)
      TOOL="${1#*=}"
      shift
      ;;
    *)
      if [[ "$1" =~ ^[0-9]+$ ]]; then
        MAX_ITERATIONS="$1"
      fi
      shift
      ;;
  esac
done

if [[ "$TOOL" != "minimax" && "$TOOL" != "claude" && "$TOOL" != "codex" ]]; then
  echo "Error: Invalid tool '$TOOL'. Must be 'minimax', 'claude', or 'codex'."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRD_FILE="$SCRIPT_DIR/ralph-prd.json"
PROGRESS_FILE="$SCRIPT_DIR/ralph-progress.txt"

# Initialize progress file if it doesn't exist
if [ ! -f "$PROGRESS_FILE" ]; then
  echo "# Ralph Progress Log" > "$PROGRESS_FILE"
  echo "Started: $(date)" >> "$PROGRESS_FILE"
  echo "---" >> "$PROGRESS_FILE"
fi

echo "Starting Ralph — Tool: $TOOL — Max iterations: $MAX_ITERATIONS"
echo "PRD: $PRD_FILE"
echo ""

for i in $(seq 1 $MAX_ITERATIONS); do
  echo ""
  echo "==============================================================="
  echo "  Ralph Iteration $i of $MAX_ITERATIONS ($TOOL)"
  echo "==============================================================="

  if [[ "$TOOL" == "minimax" ]]; then
    # Use MiniMax API via Anthropic-compatible endpoint
    # --print streams to stdout; unbuffer ensures line-by-line output to log
    ANTHROPIC_BASE_URL="https://api.minimax.io/anthropic" \
    ANTHROPIC_AUTH_TOKEN="$MINIMAX_API_KEY" \
    ANTHROPIC_MODEL="MiniMax-M2.5" \
    ANTHROPIC_SMALL_FAST_MODEL="MiniMax-M2.5" \
    API_TIMEOUT_MS="3000000" \
    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1" \
    env -u CLAUDECODE \
    claude --dangerously-skip-permissions --print \
      < "$SCRIPT_DIR/ralph-prompt.md" || true
  elif [[ "$TOOL" == "claude" ]]; then
    env -u CLAUDECODE \
    claude --dangerously-skip-permissions --print --model claude-sonnet-4-6 \
      < "$SCRIPT_DIR/ralph-prompt.md" || true
  else
    # codex: pass prompt as argument
    PROMPT=$(cat "$SCRIPT_DIR/ralph-prompt.md")
    codex "$PROMPT" || true
  fi

  # Check completion: all userStories have passes=true in prd.json
  if python3 -c "
import json, sys
try:
    d = json.load(open('$PRD_FILE'))
    sys.exit(0 if all(s['passes'] for s in d['userStories']) else 1)
except Exception as e:
    print(f'PRD check error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
    echo ""
    echo "Ralph completed all tasks! (all passes=true in ralph-prd.json)"
    echo "Completed at iteration $i of $MAX_ITERATIONS"
    exit 0
  fi

  echo "Iteration $i complete. Continuing..."
  sleep 2
done

echo ""
echo "Ralph reached max iterations ($MAX_ITERATIONS) without completing all tasks."
echo "Check $PROGRESS_FILE for status."
exit 1
