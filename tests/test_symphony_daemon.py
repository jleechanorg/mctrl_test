from __future__ import annotations

from pathlib import Path

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


def test_generic_tasks_plugin_parses_json() -> None:
    fixture = REPO_ROOT / "tests" / "fixtures" / "generic_tasks_fixture.json"
    plugin = load_plugin("generic_tasks")
    issues = plugin.load_issues(str(fixture))

    assert len(issues) == 2
    assert issues[0].identifier == "GEN-1"
    assert "general" in issues[0].labels


def test_swebench_plugin_parses_fixture() -> None:
    fixture = REPO_ROOT / "tests" / "fixtures" / "swe_bench_verified_fixture.json"
    plugin = load_plugin("swe_bench_verified")
    issues = plugin.load_issues(str(fixture))

    assert len(issues) == 1
    assert issues[0].identifier.startswith("SWE-")


def test_sym_skill_exists_and_mentions_keyword() -> None:
    skill_path = REPO_ROOT / "openclaw-config" / "skills" / "sym" / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")

    assert "name: sym" in text
    assert "contains the word **sym**" in text
    assert "scripts/sym-dispatch.sh" in text
