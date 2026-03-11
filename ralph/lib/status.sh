#!/bin/bash
# ralph/lib/status.sh — Status monitor display functions
# Extracted from ralph.sh show_status(). All functions take explicit args.

# Format a progress bar string
# Usage: bar=$(format_progress_bar <passed> <total> <bar_len>)
format_progress_bar() {
  local passed="$1" total="$2" bar_len="${3:-40}"
  local pct=0 filled=0 empty="$bar_len" bar=""

  if [ "$total" -gt 0 ] 2>/dev/null; then
    pct=$((passed * 100 / total))
    filled=$((pct * bar_len / 100))
    empty=$((bar_len - filled))
  fi

  [ "$filled" -gt 0 ] && bar=$(printf '%0.s█' $(seq 1 $filled 2>/dev/null))
  [ "$empty" -gt 0 ] && bar+=$(printf '%0.s░' $(seq 1 $empty 2>/dev/null))
  [ -z "$bar" ] && bar=$(printf '%0.s░' $(seq 1 $bar_len 2>/dev/null))

  echo "[$bar] ${pct}% ($passed/$total)"
}

# Format phase/story status table
# Usage: output=$(format_story_status <prd_file>)
format_story_status() {
  local prd_file="$1"
  local prefixes prefix label p_total p_done status

  echo "  ┌─────────────────────────────────┬────────┬────────┐"
  echo "  │ Phase                           │ Status │ Count  │"
  echo "  ├─────────────────────────────────┼────────┼────────┤"

  prefixes=$(jq -r '[.userStories[].id | split("-")[0] + "-"] | unique | sort | .[]' "$prd_file" 2>/dev/null)
  for prefix in $prefixes; do
    [ -z "$prefix" ] && continue
    label=$(printf "%-31s" "$prefix")
    p_total=$(jq --arg p "$prefix" '[.userStories[] | select(.id | startswith($p))] | length' "$prd_file" 2>/dev/null || echo 0)
    p_done=$(jq --arg p "$prefix" '[.userStories[] | select(.id | startswith($p)) | select(.passes == true)] | length' "$prd_file" 2>/dev/null || echo 0)

    if [ "$p_done" -eq "$p_total" ]; then
      status="  DONE"
    elif [ "$p_done" -gt 0 ]; then
      status="  WIP "
    else
      status="  ----"
    fi
    printf "  │ %s │%s │  %d/%-3d │\n" "$label" "$status" "$p_done" "$p_total"
  done

  echo "  └─────────────────────────────────┴────────┴────────┘"
}

# Format the next incomplete story
# Usage: next=$(format_next_story <prd_file>)
format_next_story() {
  local prd_file="$1"
  jq -r '[.userStories[] | select(.passes == false)][0] | "\(.id): \(.title)"' "$prd_file" 2>/dev/null || echo "N/A"
}

# Format the last N lines of progress file
# Usage: tail_out=$(format_progress_tail <progress_file> <n>)
format_progress_tail() {
  local progress_file="$1" n="${2:-15}"
  tail -"$n" "$progress_file" 2>/dev/null
}

# Full show_status function (uses the pieces above)
# Usage: show_status <prd_file> <progress_file> <repo_root>
show_status() {
  local prd_file="$1" progress_file="$2" repo_root="$3"
  local total passed pct

  echo "╔══════════════════════════════════════════════════════════╗"
  echo "║            🐺 RALPH STATUS MONITOR                     ║"
  echo "╠══════════════════════════════════════════════════════════╣"
  echo "║  $(date '+%Y-%m-%d %H:%M:%S')                                    ║"
  echo "╚══════════════════════════════════════════════════════════╝"
  echo ""

  total=$(jq '.userStories | length' "$prd_file" 2>/dev/null || echo 0)
  passed=$(jq '[.userStories[] | select(.passes == true)] | length' "$prd_file" 2>/dev/null || echo 0)

  echo "  Progress: $(format_progress_bar "$passed" "$total" 40)"
  echo ""
  format_story_status "$prd_file"
  echo ""
  echo "  Next story: $(format_next_story "$prd_file")"
  echo ""

  echo "  Recent commits:"
  git -C "$repo_root" log --format="    %C(yellow)%h%Creset %C(cyan)%ar%Creset (%ci) %s" -8 2>/dev/null || echo "    (git history unavailable)"
  echo ""

  echo "  ── Last progress entries ──────────────────────────────"
  format_progress_tail "$progress_file" 15
  echo ""
}
