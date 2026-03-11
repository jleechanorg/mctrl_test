#!/bin/bash
# ralph/lib/metrics.sh — Metrics recording
# Sourced by ralph.sh. All functions take explicit args.

# Record run metrics to JSON
# Usage: record_metrics <outcome> <prd_file> <metrics_file> <workspace> <progress_file> <tool> <run_start>
record_metrics() {
  local outcome="$1" prd_file="$2" metrics_file="$3" workspace="$4"
  local progress_file="$5" tool="$6" run_start="$7"
  local end_ts duration passed=0 total=0 files=0

  end_ts=$(date +%s)
  duration=$((end_ts - run_start))

  if [ -f "$prd_file" ]; then
    total=$(jq '.userStories | length' "$prd_file" 2>/dev/null || echo 0)
    passed=$(jq '[.userStories[] | select(.passes == true)] | length' "$prd_file" 2>/dev/null || echo 0)
  fi

  files=$(find "$workspace" \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.html" -o -name "*.css" \) \
    -newer "$progress_file" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | wc -l | tr -d ' ')

  python3 -c "
import json, sys
d = {
    'outcome': sys.argv[1],
    'duration_seconds': int(sys.argv[2]),
    'duration_human': f'{int(sys.argv[2])//60}m {int(sys.argv[2])%60}s',
    'stories_passed': int(sys.argv[3]),
    'stories_total': int(sys.argv[4]),
    'files_modified': int(sys.argv[5]),
    'tool': sys.argv[6],
    'workspace': sys.argv[7]
}
with open(sys.argv[8], 'w') as f:
    json.dump(d, f)
" "$outcome" "$duration" "$passed" "$total" "$files" "$tool" "$workspace" "$metrics_file"

  echo "📊 Metrics: $metrics_file"
  echo "   $((duration/60))m $((duration%60))s — ${passed}/${total} stories — ${files} files"
}
