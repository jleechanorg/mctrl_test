from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
MONITOR_SCRIPT = REPO_ROOT / "openclaw-config" / "monitor-agent.sh"
MONITOR_PLIST = REPO_ROOT / "openclaw-config" / "launchd" / "ai.openclaw.monitor-agent.plist"


def test_monitor_alerts_only_on_problem_status() -> None:
    script = MONITOR_SCRIPT.read_text(encoding="utf-8")
    assert 'if grep -q "STATUS=PROBLEM" <<<"$REPORT"; then' in script
    assert "non-PROBLEM status; Slack delivery suppressed." in script


def test_monitor_plist_has_no_literal_slack_placeholder() -> None:
    plist = MONITOR_PLIST.read_text(encoding="utf-8")
    assert "${OPENCLAW_MONITOR_SLACK_TARGET}" not in plist
