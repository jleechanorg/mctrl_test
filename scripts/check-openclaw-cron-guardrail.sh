#!/usr/bin/env bash
set -euo pipefail

# Guardrail:
# - Forbidden: system crontab usage for OpenClaw reminder/scheduling/automation jobs.
# - Required: OpenClaw gateway cron workflow for reminders/schedules.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

FILES="$(git ls-files '*.md' '*.sh' 'AGENTS.md' 'TOOLS.md' 'README.md')"

had_violations=0

is_guardrail_line() {
  local line="$1"
  echo "$line" | grep -Eiq 'forbidden|do not|never|must not|prohibit|required|not used|legacy|remove|removed'
}

while IFS= read -r file; do
  case "$file" in
    .openclaw-backups/*|openclaw/.openclaw-backups/*|openclaw-config/agents/*|openclaw-config/credentials/*)
      continue
      ;;
  esac

  while IFS=: read -r line_no line; do
    [[ -z "${line_no:-}" ]] && continue

    if is_guardrail_line "$line"; then
      continue
    fi

    if echo "$line" | grep -Eiq 'crontab' && echo "$line" | grep -Eiq 'openclaw|\.openclaw|ai\.openclaw|openclaw-backup|backup-content\.sh'; then
      echo "Guardrail violation: $file:$line_no"
      echo "  $line"
      had_violations=1
    fi
  done < <(rg -n --no-heading -i 'crontab' "$file" || true)
done <<< "$FILES"

if [[ "$had_violations" -ne 0 ]]; then
  echo
  echo "OpenClaw cron guardrail failed."
  echo "Use OpenClaw gateway cron subcommands ('openclaw cron ...') for reminders/schedules."
  echo "Do not add system crontab entries for OpenClaw automation."
  exit 1
fi

echo "OpenClaw cron guardrail check passed."
