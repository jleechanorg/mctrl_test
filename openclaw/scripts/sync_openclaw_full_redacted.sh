#!/usr/bin/env bash
set -euo pipefail

# ==========================================
# Full mirror + redact sync for ~/.openclaw
# ==========================================

REPO_DIR="${1:-/tmp/openclaw-repo}"
SRC_DIR="${2:-$HOME/.openclaw}"
DST_DIR="$REPO_DIR/openclaw-config"

mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

if [ -d ".git" ]; then
  echo "Using existing repo at $REPO_DIR"
else
  if command -v gh >/dev/null 2>&1; then
    echo "Cloning jleechanorg/openclaw into $REPO_DIR..."
    gh repo clone jleechanorg/openclaw .
  else
    echo "gh CLI not found. Please clone https://github.com/jleechanorg/openclaw first into $REPO_DIR and re-run." >&2
    exit 1
  fi
fi

mkdir -p "$DST_DIR"
rm -rf "$DST_DIR"/*
mkdir -p "$DST_DIR"

export SRC_DIR DST_DIR
python - <<'PY'
from pathlib import Path
import os, re, shutil

SRC_DIR = Path(os.environ['SRC_DIR'])
DST_DIR = Path(os.environ['DST_DIR'])
LOG = DST_DIR / 'REDACTION_LOG.md'

# Keep snapshots focused and usable
exclude_dirs = {
    '.git', '.next', '.cache', '__pycache__', '.venv', 'node_modules', '.npm',
    '.pnpm-store', '.yarn', '.idea', '.vscode', '.pytest_cache', '.mypy_cache',
    'workspace',  # Exclude workspace - contains user project data, not OpenClaw config
}

def looks_sensitive_path(path: Path) -> bool:
    low = str(path).lower()
    # keep file copies unless extension/filename is highly sensitive
    if any(token in low for token in ['id_rsa', 'id_ed25519', 'credentials', 'secret', 'token', 'password']):
        if path.suffix.lower() in {'.pem', '.key', '.crt', '.p12', '.pfx'}:
            return True
    return False

def is_binary(path: Path) -> bool:
    try:
        with open(path, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except Exception:
        return True

# Redact secret-like lines/assignments conservatively
patterns = [
    re.compile(r'(?im)^[\t ]*(?:export[\t ]+)?(?:[A-Za-z_][A-Za-z0-9_]*_?(?:KEY|KEYS?|TOKEN|SECRET|PASS|PASSWORD)|API[_-]?KEY|CLIENT_SECRET|CLIENTID|CLIENT_ID|CLIENT_SECRET)\s*[:=]\s*.+$'),
    re.compile(r'(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|private[_-]?key|bearer\s+token)\b[^\n]*'),
    re.compile(r'(?i)([\w.-]+@[\w.-]+:\/\/)[^\s"\']+'),  # redact embedded basic-auth URLs
    re.compile(r'(?i)\b(sk-[A-Za-z0-9]{10,}|xox[baprs]-[0-9A-Za-z\-]{10,}|ghp_[A-Za-z0-9]{20,})\b'),
    re.compile(r'"(?:botToken|appToken|token|apiKey|secret|password)"\s*:\s*"[^"]+"'),  # JSON tokens
    re.compile(r'pypi-[A-Za-z0-9_\-]{60,}'),  # PyPI tokens
    re.compile(r'xai-[A-Za-z0-9]{20,}'),  # xAI API keys
    re.compile(r'https://hooks\.slack\.com/services/[A-Z0-9/]+'),  # Slack webhooks
]

redacted_files = []

for root, dirs, files in os.walk(SRC_DIR):
    rel_root = Path(root).relative_to(SRC_DIR)
    dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]

    out_root = DST_DIR / rel_root
    out_root.mkdir(parents=True, exist_ok=True)

    for fn in files:
        if fn == '.DS_Store':
            continue
        srcf = Path(root) / fn
        rel = srcf.relative_to(SRC_DIR)
        dstf = DST_DIR / rel

        # skip noisy non-config artifacts and session logs
        if srcf.suffix.lower() in {'.log', '.db', '.sqlite', '.sqlite3', '.ipynb', '.jsonl'}:
            continue
        if looks_sensitive_path(srcf):
            continue

        if is_binary(srcf):
            shutil.copy2(srcf, dstf)
            continue

        try:
            text = srcf.read_text(encoding='utf-8')
        except Exception:
            shutil.copy2(srcf, dstf)
            continue

        new = text
        changed = False
        for p in patterns:
            if p.search(new):
                new = p.sub('[REDACTED]', new)
                changed = True

        if changed:
            redacted_files.append(str(rel))

        dstf.write_text(new, encoding='utf-8')
        try:
            shutil.copystat(srcf, dstf)
        except Exception:
            pass

LOG.write_text('# Redaction Log\n')
LOG.write_text(LOG.read_text() + f"\nExported from: {SRC_DIR}\nTotal redacted files: {len(redacted_files)}\n\n")
for item in redacted_files:
    LOG.write_text(LOG.read_text() + f"- {item}\n")

print(f"Exported {sum(1 for _ in DST_DIR.rglob('*') if _.is_file())} files")
print(f"Redacted {len(redacted_files)} files")
print(f"Log: {LOG}")
PY

cd "$DST_DIR"
git add .

git status --short

git commit -m "chore: sync ~/.openclaw with sensitive values redacted" || true

git push origin HEAD:main

echo "Done. Commit (if any) pushed to main."
