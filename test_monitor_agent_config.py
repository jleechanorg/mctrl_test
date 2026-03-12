from __future__ import annotations

import os
from pathlib import Path
import stat
import subprocess
import textwrap


REPO_ROOT = Path(__file__).resolve().parent
MONITOR_SCRIPT = REPO_ROOT / "openclaw-config" / "monitor-agent.sh"
MONITOR_PLIST = REPO_ROOT / "openclaw-config" / "launchd" / "ai.openclaw.monitor-agent.plist"
WORKSPACE_ROOT = REPO_ROOT / "openclaw-config" / "workspaces" / "monitor"


def _make_fake_openclaw(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    fake = bin_dir / "openclaw"
    fake.write_text(
        textwrap.dedent(
            """\
            #!/bin/bash
            set -u

            cmd="${1:-}"
            if [ "$cmd" = "agent" ]; then
              printf '%s\\n' "${OPENCLAW_TEST_REPORT:-STATUS=GOOD}"
              exit "${OPENCLAW_TEST_AGENT_RC:-0}"
            fi

            if [ "$cmd" = "message" ] && [ "${2:-}" = "send" ]; then
              printf '%s\\n' "$*" >> "${OPENCLAW_TEST_SEND_LOG:?OPENCLAW_TEST_SEND_LOG required}"
              exit "${OPENCLAW_TEST_SEND_RC:-0}"
            fi

            echo "unexpected invocation: $*" >&2
            exit 90
            """
        ),
        encoding="utf-8",
    )
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    return fake


def _run_monitor(tmp_path: Path, *, report: str, slack_target: str | None) -> tuple[subprocess.CompletedProcess[str], Path]:
    _make_fake_openclaw(tmp_path)
    send_log = tmp_path / "send.log"
    env = os.environ.copy()
    env.update(
        {
            "HOME": str(tmp_path),
            "OPENCLAW_TEST_REPORT": report,
            "OPENCLAW_TEST_SEND_LOG": str(send_log),
        }
    )
    if slack_target is None:
        env.pop("OPENCLAW_MONITOR_SLACK_TARGET", None)
    else:
        env["OPENCLAW_MONITOR_SLACK_TARGET"] = slack_target
    result = subprocess.run(
        ["bash", str(MONITOR_SCRIPT)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    return result, send_log


def test_monitor_problem_status_does_not_alert_when_target_unset(tmp_path: Path) -> None:
    result, send_log = _run_monitor(tmp_path, report="STATUS=PROBLEM", slack_target=None)
    assert result.returncode == 0
    assert not send_log.exists()


def test_monitor_problem_status_alerts_when_target_set(tmp_path: Path) -> None:
    result, send_log = _run_monitor(tmp_path, report="STATUS=PROBLEM", slack_target="C123456")
    assert result.returncode == 0
    assert send_log.exists()
    assert "--target C123456" in send_log.read_text(encoding="utf-8")


def test_monitor_good_status_never_alerts(tmp_path: Path) -> None:
    result, send_log = _run_monitor(tmp_path, report="STATUS=GOOD", slack_target="C123456")
    assert result.returncode == 0
    assert not send_log.exists()


def test_monitor_plist_has_no_literal_slack_placeholder() -> None:
    plist = MONITOR_PLIST.read_text(encoding="utf-8")
    assert "${OPENCLAW_MONITOR_SLACK_TARGET}" not in plist


def test_monitor_script_has_timeout_watchdog() -> None:
    script = MONITOR_SCRIPT.read_text(encoding="utf-8")
    assert "OPENCLAW_MONITOR_AGENT_TIMEOUT_SECONDS" in script
    assert "timeout" in script
    assert "Monitoring agent timed out after" in script


def test_workspace_docs_include_security_guidance() -> None:
    agents = (WORKSPACE_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    bootstrap = (WORKSPACE_ROOT / "BOOTSTRAP.md").read_text(encoding="utf-8")
    tools = (WORKSPACE_ROOT / "TOOLS.md").read_text(encoding="utf-8")
    user = (WORKSPACE_ROOT / "USER.md").read_text(encoding="utf-8")

    assert "Any git commit, push, or PR action" in agents
    assert "mark it with `BOOTSTRAP_COMPLETE: yes`" in agents
    assert "Never store a WhatsApp QR image, Telegram bot token" in bootstrap
    assert "Never commit real credentials" in tools
    assert "Collect only the minimum personal data needed" in user
