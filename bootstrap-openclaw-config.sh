#!/usr/bin/env bash
set -euo pipefail

# Usage: ./bootstrap-openclaw-config.sh /tmp/openclaw-export

set -o pipefail
DEST="${1:-./openclaw-export}"
SRC_HOME="/Users/jleechan/.openclaw"
SRC_WS="/Users/jleechan/.openclaw/workspace"

mkdir -p "$DEST"
cd "$DEST"

# Copy a safe, expected baseline (extend as needed)
cp -p "$SRC_HOME/SOUL.md" "${DEST}/" 2>/dev/null || true
cp -p "$SRC_HOME/USER.md" "${DEST}/" 2>/dev/null || true
cp -p "$SRC_HOME/TOOLS.md" "${DEST}/" 2>/dev/null || true
cp -p "$SRC_HOME/IDENTITY.md" "${DEST}/" 2>/dev/null || true
cp -p "$SRC_HOME/BOOTSTRAP.md" "${DEST}/" 2>/dev/null || true
cp -p "$SRC_WS/AGENTS.md" "${DEST}/" 2>/dev/null || true
cp -p "$SRC_WS/HEARTBEAT.md" "${DEST}/" 2>/dev/null || true
cp -p "$SRC_WS/IDENTITY.md" "${DEST}/" 2>/dev/null || true
cp -p "$SRC_WS/USER.md" "${DEST}/" 2>/dev/null || true
cp -p "$SRC_WS/SOUL.md" "${DEST}/" 2>/dev/null || true
cp -p "$SRC_WS/MEMORY.md" "${DEST}/" 2>/dev/null || true

mkdir -p "$DEST/memory"
if [ -d "$SRC_WS/memory" ]; then
  cp -p "$SRC_WS/memory"/*.md "$DEST/memory/" 2>/dev/null || true
fi

# Scrub sensitive text in copied files
cat > "$DEST/.gitignore" <<'EOF'
# Sensitive and local-only files
*.json
*.key
*.pem
*.p12
.env
.env.*
*_secret*
*secret*
*token*
*credential*
EOF

sanitizer () {
  local f="$1"
  # redact key-like env assignments and obvious secret-bearing lines
  sed -i '' \
    -e 's/[Aa][Pp][Ii]_[Kk][Ee][Yy].*/[REDACTED]/g' \
    -e 's/[Ss][Ee][Cc][Rr][Ee][Tt].*/[REDACTED]/g' \
    -e 's/[Tt][Oo][Kk][Ee][Nn].*/[REDACTED]/g' \
    -e 's/[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd].*/[REDACTED]/g' \
    -e 's/[Pp][Aa][Ss][Ss][Pp][Hh][Rr][Aa][Ss][Ee].*/[REDACTED]/g' \
    -e 's/xox[bap]-[A-Za-z0-9-]\{20,\}/[REDACTED_TOKEN]/g' \
    -e 's/[0-9a-zA-Z]\{40,\}/[REDACTED_HASH]/g' \
    "$f" || true
}

find "$DEST" -maxdepth 2 -type f -print0 | while IFS= read -r -d '' f; do
  [ -f "$f" ] || continue
  sanitizer "$f"
done

cat > "$DEST/README.md" <<'EOF'
# OpenClaw Config Snapshot (Sanitized)

This folder contains non-sensitive OpenClaw configuration files exported from:
- /Users/jleechan/.openclaw
- /Users/jleechan/.openclaw/workspace

## Included
- SOUL.md / USER.md / TOOLS.md / IDENTITY.md
- Workspace AGENTS.md, HEARTBEAT.md, SOUL.md, USER.md, IDENTITY.md, MEMORY.md (if present)
- daily `memory/*.md` (markdown only)

## Next step
Run the included helper to create a repo in your GitHub org:

```bash
./create-openclaw-repo.sh <repo-name>
```

If you'd like, I can generate and push a git commit once shell execution is enabled.
EOF

cat > "$DEST/create-openclaw-repo.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:?Usage: create-openclaw-repo.sh <repo-name>}"
OWNER="jleechanorg"

if ! command -v gh >/dev/null 2>&1; then
  echo "Missing gh CLI. Install from https://cli.github.com/ and retry." >&2
  exit 1
fi


git init

gh auth status

gh repo create "$OWNER/$REPO_NAME" --private --source=. --remote=origin --push

git add .
git commit -m "chore: add sanitized OpenClaw config snapshot"
git push -u origin main
EOF
chmod +x "$DEST/create-openclaw-repo.sh"
