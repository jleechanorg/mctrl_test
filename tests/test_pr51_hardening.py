from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
OPENCLAW_CONFIG = REPO_ROOT / "openclaw-config" / "openclaw.json"
LAUNCHD_DIR = REPO_ROOT / "openclaw-config" / "launchd"
BEADS_BACKUP_DIR = REPO_ROOT / ".beads" / "backup"

SENSITIVE_PATTERNS = [
    re.compile(r"xoxb-[A-Za-z0-9-]+"),
    re.compile(r"xai-[A-Za-z0-9_-]+"),
    re.compile(r"C0[A-Z0-9]{8,}"),
    re.compile(r"/Users/jleechan"),
    re.compile(r"[A-Za-z0-9._%+-]+@users\.noreply\.github\.com"),
]


def test_mem0_history_db_path_uses_home_placeholder() -> None:
    cfg = json.loads(OPENCLAW_CONFIG.read_text(encoding="utf-8"))
    found: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "historyDbPath" and isinstance(v, str):
                    found.append(v)
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(cfg)
    assert "${HOME}/.openclaw/mem0-history.db" in found


def test_no_runtime_db_or_progress_artifacts_tracked() -> None:
    unexpected = [
        REPO_ROOT / "memory.db",
        REPO_ROOT / "vector_store.db",
        REPO_ROOT / "ralph" / "metrics.json",
        REPO_ROOT / "ralph" / "progress.txt",
    ]
    import subprocess
    tracked = []
    for artifact in unexpected:
        rel = str(artifact.relative_to(REPO_ROOT))
        proc = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=REPO_ROOT, capture_output=True, text=True)
        if proc.returncode == 0:
            tracked.append(rel)
    assert not tracked, f"Runtime artifacts should not be tracked: {tracked}"


def test_no_literal_tokens_in_backup_configs() -> None:
    files = [OPENCLAW_CONFIG]
    files.extend(sorted(LAUNCHD_DIR.glob("*.plist")))

    bad_hits: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pat in SENSITIVE_PATTERNS[:2]:
            if pat.search(text):
                bad_hits.append(f"{path.relative_to(REPO_ROOT)} matches {pat.pattern}")

    assert not bad_hits, "Found literal secrets in backup config files: " + "; ".join(bad_hits)


def test_beads_backup_is_redacted() -> None:
    files = [
        BEADS_BACKUP_DIR / "events.jsonl",
        BEADS_BACKUP_DIR / "issues.jsonl",
    ]

    bad_hits: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pat in SENSITIVE_PATTERNS:
            if pat.search(text):
                bad_hits.append(f"{path.relative_to(REPO_ROOT)} matches {pat.pattern}")

    assert not bad_hits, "Found sensitive data in beads backups: " + "; ".join(bad_hits)
