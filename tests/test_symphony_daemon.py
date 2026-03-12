from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestration.symphony_daemon import (
    build_launch_agent,
    build_runner_script,
    build_workflow,
)
from orchestration.symphony_plugins import list_plugins, load_plugin


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_build_workflow_uses_memory_tracker_and_operator_defaults() -> None:
    txt = build_workflow(
        workspace_root="/tmp/symphony/workspaces",
        workflow_title="General coding tasks",
        workflow_intro="Handle assigned coding tasks.",
        task_lines=["- TASK-1 Implement feature"],
        requirements=["Run tests", "Report outcomes"],
    )

    assert "kind: memory" in txt
    assert 'root: "/tmp/symphony/workspaces"' in txt
    assert "command: codex app-server" in txt
    assert "approval_policy: never" in txt
    assert "Task type: General coding tasks" in txt
    assert "1. Run tests" in txt


def test_build_runner_uses_default_operator_cli_path() -> None:
    txt = build_runner_script(
        symphony_elixir_dir="/Users/me/projects_reference/symphony/elixir",
        workflow_path="/tmp/symphony/WORKFLOW.md",
        node_name="symphonyd",
        cookie="cookie123",
        port=19191,
    )

    assert '"/opt/homebrew/bin/mise" exec -- ./bin/symphony' in txt
    assert "--i-understand-that-this-will-be-running-without-the-usual-guardrails" in txt
    assert "--port 19191" in txt
    assert "/tmp/symphony/WORKFLOW.md" in txt


def test_build_launch_agent_wires_runner_and_logs() -> None:
    plist = build_launch_agent(
        label="ai.symphony.daemon",
        runner_path="/tmp/symphony/run.sh",
        stdout_path="/tmp/symphony/stdout.log",
        stderr_path="/tmp/symphony/stderr.log",
    )
    assert plist["Label"] == "ai.symphony.daemon"
    assert plist["ProgramArguments"] == ["/bin/bash", "/tmp/symphony/run.sh"]
    assert plist["RunAtLoad"] is True
    assert plist["KeepAlive"] is True


def test_plugin_registry_has_general_and_benchmark_plugins() -> None:
    names = list_plugins()
    assert "generic_tasks" in names
    assert "leetcode_hard" in names
    assert "swe_bench_verified" in names


def test_generic_tasks_plugin_parses_json(tmp_path: Path) -> None:
    fixture = REPO_ROOT / "tests" / "fixtures" / "generic_tasks_fixture.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    temp_fixture = tmp_path / "generic_tasks_fixture.json"
    temp_fixture.write_text(json.dumps(payload), encoding="utf-8")
    plugin = load_plugin("generic_tasks")
    issues = plugin.load_issues(str(temp_fixture))

    assert len(issues) == 2
    assert issues[0].identifier == "GEN-1"
    assert "general" in issues[0].labels


def test_swebench_plugin_parses_fixture(tmp_path: Path) -> None:
    fixture = REPO_ROOT / "tests" / "fixtures" / "swe_bench_verified_fixture.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    temp_fixture = tmp_path / "swe_bench_verified_fixture.json"
    temp_fixture.write_text(json.dumps(payload), encoding="utf-8")
    plugin = load_plugin("swe_bench_verified")
    issues = plugin.load_issues(str(temp_fixture))

    assert len(issues) == 1
    assert issues[0].identifier.startswith("SWE-")


def test_generic_tasks_plugin_raises_clear_error_for_invalid_payload(tmp_path: Path) -> None:
    bad_payload_path = tmp_path / "bad_generic.json"
    bad_payload_path.write_text(json.dumps({"tasks": [{"id": 1}]}), encoding="utf-8")
    plugin = load_plugin("generic_tasks")

    with pytest.raises(ValueError, match="generic_tasks: record\\[0\\].*title"):
        plugin.load_issues(str(bad_payload_path))


def test_swebench_plugin_raises_clear_error_for_invalid_payload(tmp_path: Path) -> None:
    bad_payload_path = tmp_path / "bad_swebench.json"
    bad_payload_path.write_text(json.dumps({"instances": [{}]}), encoding="utf-8")
    plugin = load_plugin("swe_bench_verified")

    with pytest.raises(ValueError, match="swe_bench_verified: record\\[0\\]"):
        plugin.load_issues(str(bad_payload_path))


def test_sym_skill_exists_and_mentions_keyword() -> None:
    skill_path = REPO_ROOT / "openclaw-config" / "skills" / "sym" / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")

    assert "name: sym" in text
    assert "contains the word **sym**" in text
    assert "scripts/sym-dispatch.sh" in text


def test_sym_dispatch_uses_dynamic_task_ids_for_freeform_tasks() -> None:
    dispatch_script = (REPO_ROOT / "scripts" / "sym-dispatch.sh").read_text(encoding="utf-8")
    assert "uuid.uuid4().hex[:12]" in dispatch_script
    assert '"id": "1"' not in dispatch_script


def test_enqueue_script_preserves_explicit_false_assignment_flag() -> None:
    enqueue_script = (REPO_ROOT / "scripts" / "enqueue-symphony-memory-issues.exs").read_text(
        encoding="utf-8"
    )
    assert 'Map.fetch(item, "assigned_to_worker")' in enqueue_script
    assert "assigned_to_worker: assigned_to_worker" in enqueue_script


def test_enqueue_script_resolves_mise_from_env_or_metadata() -> None:
    enqueue_script = (REPO_ROOT / "scripts" / "enqueue-symphony-tasks.sh").read_text(encoding="utf-8")
    assert 'MISE_BIN="${MISE_BIN:-$(jq -r \'.mise_bin // empty\' "$METADATA")}"' in enqueue_script
    assert '"$MISE_BIN" exec -- mix run' in enqueue_script
    assert "Application Support/jleechanclaw/symphony_daemon" in enqueue_script


def test_setup_daemon_defaults_to_private_runtime_and_no_test_fixture_seed() -> None:
    setup_script = (REPO_ROOT / "scripts" / "setup-symphony-daemon.py").read_text(encoding="utf-8")
    assert "Application Support" in setup_script
    assert "tests\" / \"fixtures\" / \"generic_tasks_fixture.json" not in setup_script
    assert "generic_tasks.json" in setup_script


def test_sym_dispatch_and_install_use_private_runtime_default() -> None:
    dispatch_script = (REPO_ROOT / "scripts" / "sym-dispatch.sh").read_text(encoding="utf-8")
    install_script = (REPO_ROOT / "scripts" / "install-symphony-daemon.sh").read_text(
        encoding="utf-8"
    )

    assert "Application Support/jleechanclaw/symphony_daemon" in dispatch_script
    assert "Application Support/jleechanclaw/symphony_daemon" in install_script
    assert "/tmp/jleechanclaw/symphony_daemon" not in dispatch_script
    assert "/tmp/jleechanclaw/symphony_daemon" not in install_script


def test_setup_daemon_avoids_static_cookie_literal() -> None:
    setup_script = (REPO_ROOT / "scripts" / "setup-symphony-daemon.py").read_text(encoding="utf-8")
    assert "jleechanclaw_symphony_cookie" not in setup_script
    assert "secrets.token_hex(16)" in setup_script


def test_plugin_helper_scripts_bootstrap_via_sym_dispatch() -> None:
    leetcode_helper = (REPO_ROOT / "scripts" / "sym-send-5-leetcode-hard.sh").read_text(encoding="utf-8")
    swebench_helper = (
        REPO_ROOT / "scripts" / "sym-send-5-swebench-verified.sh"
    ).read_text(encoding="utf-8")

    assert "--plugin leetcode_hard" in leetcode_helper
    assert "--plugin swe_bench_verified" in swebench_helper
