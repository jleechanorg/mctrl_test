#!/bin/bash
# watch-ralph.sh — Live dashboard for the ralph loop
# Usage: ./watch-ralph.sh [output_file]
#
# Shows: current iteration, story in progress, test results, last commit, remaining stories

set -e

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRD_FILE="$REPO/ralph-prd.json"
PROGRESS_FILE="$REPO/ralph-progress.txt"
OUTPUT_FILE="${1:-$REPO/ralph-output.log}"

# Colors
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
RESET='\033[0m'

clear_screen() { printf '\033[2J\033[H'; }

prd_summary() {
  if [ ! -f "$PRD_FILE" ]; then echo "  (no prd)"; return; fi
  python3 - "$PRD_FILE" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))
stories = d["userStories"]
done = [s for s in stories if s["passes"]]
todo = [s for s in stories if not s["passes"]]
print(f"  {len(done)}/{len(stories)} done  ({len(todo)} remaining)")
print()
for s in stories:
    icon = "✅" if s["passes"] else "⬜"
    wave = s.get("wave", "?")
    print(f"  {icon} W{wave}  [{s['id']}] {s['title']}")
PYEOF
}

last_commit() {
  cd "$REPO"
  git log --oneline -5 2>/dev/null | sed 's/^/  /'
}

last_output_lines() {
  if [ -f "$OUTPUT_FILE" ]; then
    tail -n 20 "$OUTPUT_FILE" | sed 's/^/  /'
  else
    echo "  (output file not found: $OUTPUT_FILE)"
  fi
}

iteration_count() {
  if [ -f "$OUTPUT_FILE" ]; then
    grep -c "Ralph Iteration" "$OUTPUT_FILE" 2>/dev/null || echo "0"
  else
    echo "0"
  fi
}

is_running() {
  if tmux has-session -t ralph-orch 2>/dev/null; then
    echo "yes"
  elif [ -f "$OUTPUT_FILE" ]; then
    local mtime
    mtime=$(python3 -c "import os,sys; print(int(os.path.getmtime(sys.argv[1])))" "$OUTPUT_FILE" 2>/dev/null || echo 0)
    local age=$(( $(date +%s) - mtime ))
    [ "$age" -lt 300 ] && echo "stale" || echo "no"
  else
    echo "no"
  fi
}

render() {
  clear_screen
  local iters=$(iteration_count)
  local status=$(is_running)

  printf "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"
  printf "${BOLD}  Ralph — jleechanclaw Orchestration${RESET}"
  if [ "$status" = "yes" ]; then
    printf "  ${GREEN}● RUNNING${RESET}"
  elif [ "$status" = "stale" ]; then
    printf "  ${YELLOW}◌ STALE (>5min since last output)${RESET}"
  else
    printf "  ${RED}○ NOT RUNNING${RESET}"
  fi
  printf "  ${DIM}iterations: $iters${RESET}\n"
  printf "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"

  printf "\n${CYAN}${BOLD}Stories${RESET}\n"
  prd_summary

  printf "\n${CYAN}${BOLD}Recent Commits${RESET}\n"
  last_commit

  printf "\n${CYAN}${BOLD}Agent Output (last 20 lines)${RESET}\n"
  last_output_lines

  printf "\n${DIM}  Refreshes every 5s  •  Ctrl+C to exit  •  $(date '+%H:%M:%S')${RESET}\n"
}

echo "Watching ralph loop... (Ctrl+C to stop)"
while true; do
  render
  sleep 5
done
