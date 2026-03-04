#!/usr/bin/env bash
set -euo pipefail

# Backup/backup-snapshot of ~/.openclaw into this repo with sensitive redaction.
#
# Outputs a timestamped snapshot under .openclaw-backups/<timestamp>/
# and commits it if changes are detected.
#
# Strategy: rsync for initial mirror (fast, incremental, --delete),
# then Python post-redaction pass on the staged snapshot.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="${HOME}/.openclaw"
SNAP_BASE="$REPO_ROOT/.openclaw-backups"
SNAPSHOT_TS="$(date +"%Y%m%d_%H%M%S")"
SNAPSHOT_DIR="$SNAP_BASE/$SNAPSHOT_TS"

mkdir -p "$SNAP_BASE"
mkdir -p "$SNAPSHOT_DIR"

# ---------------------------------------------------------------------------
# Step 1: rsync mirror — fast, incremental copy; --delete keeps snapshot clean.
# Excludes: nested backup dirs, git metadata, macOS noise.
# ---------------------------------------------------------------------------
rsync -a --delete \
  --exclude='.openclaw-backups' \
  --exclude='.git' \
  --exclude='.DS_Store' \
  "$SRC_DIR/" "$SNAPSHOT_DIR/"

# ---------------------------------------------------------------------------
# Step 2: Post-redaction pass — redact secrets in text files in-place;
# remove high-risk binary key material.
# ---------------------------------------------------------------------------
export SNAPSHOT_DIR SNAPSHOT_TS
python3 - <<'PY'
from pathlib import Path
import os
import re

SNAPSHOT_DIR = Path(os.environ["SNAPSHOT_DIR"])
SNAPSHOT_TS  = os.environ["SNAPSHOT_TS"]

SENSITIVE_PATH_HINTS = [
    "/.ssh/",
    "/.aws/",
    "/.config/",
    "/.kube/",
    ".env",
    "id_rsa",
    "id_ed25519",
]

PATTERNS = [
    re.compile(r"(?im)^[\t ]*(?:export[\t ]+)?(?:[A-Za-z_][A-Za-z0-9_]*_?(?:KEY|KEYS?|TOKEN|SECRET|PASS|PASSWORD)|API[_-]?KEY|CLIENT_SECRET|CLIENTID|CLIENT_ID|CLIENT_SECRET)\s*[:=].+$"),
    re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|private[_-]?key|bearer\s+token)\b[^\n]*"),
    re.compile(r"(?i)\"(?:botToken|appToken|token|apiKey|secret|password)\"\s*:\s*\"[^\"]+\""),
    re.compile(r"(?i)\b(sk-[A-Za-z0-9]{10,}|xox[baprs]-[0-9A-Za-z\-]{10,}|ghp_[A-Za-z0-9]{20,})\b"),
    re.compile(r"(?i)xai-[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)https://hooks\.slack\.com/services/[A-Z0-9/]+"),
    re.compile(r"(?i)pypi-[A-Za-z0-9_\-]{60,}"),
    re.compile(r"(?i)https?://[^:\s]+:[^@\s]+@"),
]

HIGH_RISK_EXTENSIONS = {".pem", ".key", ".p12", ".pfx", ".crt", ".cer", ".der"}


def is_binary(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            return b"\x00" in f.read(4096)
    except Exception:
        return True


def path_is_sensitive(path: Path) -> bool:
    low = str(path).lower()
    if any(token in low for token in SENSITIVE_PATH_HINTS):
        return True
    if any(part.lower() in {"authorized_keys", "known_hosts", "config"} for part in path.parts):
        return True
    return False


for p in SNAPSHOT_DIR.rglob("*"):
    if not p.is_file():
        continue

    # Remove high-risk binary key material entirely.
    if path_is_sensitive(p) and (is_binary(p) or p.suffix.lower() in HIGH_RISK_EXTENSIONS):
        p.unlink()
        continue

    # Skip binary files — no redaction needed.
    if is_binary(p):
        continue

    # Redact secrets in text files in-place.
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        try:
            text = p.read_text(encoding="latin-1")
        except Exception:
            continue

    new = text
    for pattern in PATTERNS:
        new = pattern.sub("[REDACTED]", new)

    if new != text:
        p.write_text(new, encoding="utf-8")

# Write audit manifest.
(SNAPSHOT_DIR / "REDACTION_MANIFEST.txt").write_text(
    "Source: {}\nTimestamp: {}\nStatus: rsync+redacted\n".format(
        os.environ.get("HOME", "") + "/.openclaw", SNAPSHOT_TS
    )
)
PY

cd "$REPO_ROOT"

git add .openclaw-backups/
if git diff --quiet --cached -- .openclaw-backups; then
  echo "No changes to commit."
  git restore --staged .openclaw-backups 2>/dev/null || true
  exit 0
fi

git commit -m "chore: backup ~/.openclaw snapshot $SNAPSHOT_TS" -- .openclaw-backups/

# ---------------------------------------------------------------------------
# Step 3: Update latest/ symlink to newest snapshot (relative, from SNAP_BASE).
# ---------------------------------------------------------------------------
(cd "$SNAP_BASE" && ln -sfn "$SNAPSHOT_TS" latest)

git fetch --quiet origin main
COMMIT_SHA="$(git rev-parse HEAD)"
REMOTE_URL="$(git remote get-url origin)"
if [ -z "${REMOTE_URL}" ]; then
  echo "No origin remote found; skipping push."
  exit 0
fi
REMOTE_HEAD="$(git rev-parse origin/main)"

if ! git merge-base --is-ancestor "$REMOTE_HEAD" "$COMMIT_SHA"; then
  if git merge-base --is-ancestor "$COMMIT_SHA" "$REMOTE_HEAD"; then
    echo "Local branch is behind origin/main; rebasing before push."
    git pull --rebase origin main
    COMMIT_SHA="$(git rev-parse HEAD)"
  else
    echo "Local and origin/main histories diverged. Aborting push."
    echo "Run: git pull --rebase origin main"
    exit 1
  fi
fi

if ! git push origin "HEAD:main"; then
  echo "Push to origin main failed."
  exit 1
fi

if [[ "$REMOTE_URL" == "git@github.com:"* ]]; then
  REPO_PATH="${REMOTE_URL#git@github.com:}"
  REPO_PATH="${REPO_PATH%.git}"
  COMMIT_URL="https://github.com/${REPO_PATH}/commit/${COMMIT_SHA}"
elif [[ "$REMOTE_URL" == "https://github.com/"* ]]; then
  COMMIT_URL="${REMOTE_URL%.git}/commit/${COMMIT_SHA}"
else
  COMMIT_URL="${REMOTE_URL}"
fi

echo "Backup pushed to remote origin/main: ${COMMIT_URL}"
