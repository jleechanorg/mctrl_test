#!/usr/bin/env bash
set -euo pipefail

REPOS=(
  "$HOME/projects/worldarchitect.ai"
  "$HOME/project_jleechanclaw/jleechanclaw"
  "$HOME/project_worldaiclaw/worldai_claw"
)

if ! command -v bun >/dev/null 2>&1; then
  echo "bun is required to install ghost. Install Bun and rerun." >&2
  exit 1
fi

if ! command -v ghost >/dev/null 2>&1; then
  echo "Installing ghost..."
  bun install -g github:notkurt/ghost#main
fi

FAILED=()
for repo in "${REPOS[@]}"; do
  if [[ ! -d "$repo/.git" ]]; then
    echo "Skipping missing repo: $repo"
    continue
  fi

  echo "Enabling ghost in $repo"
  if (cd "$repo" && ghost enable); then
    echo "OK: ghost enabled in $repo"
  else
    echo "WARN: ghost enable failed in $repo" >&2
    FAILED+=("$repo")
  fi
done

if (( ${#FAILED[@]} > 0 )); then
  echo "WARN: ghost setup incomplete for ${#FAILED[@]} repo(s):"
  printf ' - %s\n' "${FAILED[@]}"
  exit 1
fi

echo "Ghost setup complete for all configured repos."
