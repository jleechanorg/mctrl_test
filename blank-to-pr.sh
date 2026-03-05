#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./blank-to-pr.sh <repo-name> <github-owner>
# Example:
#   ./blank-to-pr.sh openclaw jleechanorg

REPO_NAME="${1:?repo name required}"
OWNER="${2:-jleechanorg}"
BRANCH="config-snapshot"

if ! command -v gh >/dev/null 2>&1; then
  echo "Missing gh CLI. Install from https://cli.github.com/ and retry." >&2
  exit 1
fi

# 1) Build an empty, publishable baseline
rm -rf /tmp/openclaw-repo-temp
git clone "https://github.com/${OWNER}/${REPO_NAME}.git" /tmp/openclaw-repo-temp >/tmp/openclaw-repo-clone.log 2>&1 || true

if [ -d /tmp/openclaw-repo-temp/.git ]; then
  echo "Repo ${OWNER}/${REPO_NAME} already exists; creating feature branch for PR changes."
  cd /tmp/openclaw-repo-temp
  git switch -c "$BRANCH"
else
  echo "Creating new repository ${OWNER}/${REPO_NAME}..."
  mkdir -p /tmp/openclaw-repo-temp
  cd /tmp/openclaw-repo-temp
  git init
  git switch -c main
  git commit --allow-empty -m "chore: initialize blank repo" >/tmp/openclaw-repo-empty.log 2>&1
  gh repo create "$OWNER/$REPO_NAME" --private --source=. --remote=origin --push
fi

# 2) Create sanitized snapshot, commit to feature branch
TMP_EXPORT="/tmp/openclaw-export-$(date +%s)"
./bootstrap-openclaw-config.sh "$TMP_EXPORT"
cd "$TMP_EXPORT"

git add .
git commit -m "chore: add sanitized OpenClaw config snapshot" >/tmp/openclaw-repo-commit.log 2>&1
if git remote -v | grep -q "origin"; then
  git push -u origin "$BRANCH"
else
  # If this is the newly created repo, add remote and push the feature branch
  gh repo view "$OWNER/$REPO_NAME" --json url --jq '.url' >/dev/null
  git remote add origin "git@github.com:${OWNER}/${REPO_NAME}.git"
  git push -u origin "$BRANCH"
fi

echo "Done. Open PR from branch '$BRANCH' to 'main' with:"
echo "gh pr create --repo ${OWNER}/${REPO_NAME} --base main --head ${BRANCH} --title 'Add sanitized OpenClaw config snapshot' --body 'Blank repo created, then snapshot changes applied on feature branch.'"
