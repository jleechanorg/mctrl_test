#!/usr/bin/env python3
"""Install and start a launchd-managed Symphony daemon for jleechanclaw."""

from __future__ import annotations

import json
import os
import plistlib
import secrets
import socket
import stat
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from orchestration.symphony_daemon import (
    build_launch_agent,
    build_runner_script,
    build_workflow,
)
from orchestration.symphony_plugins import load_plugin


def run(cmd: list[str], check: bool = True) -> None:
    subprocess.run(cmd, check=check)


def port_is_listening(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def pick_port(preferred_port: int, attempts: int = 32) -> int:
    for candidate in range(preferred_port, preferred_port + attempts):
        if not port_is_listening(candidate):
            return candidate
    raise RuntimeError(f"no available Symphony daemon port in [{preferred_port}, {preferred_port + attempts - 1}]")


def main() -> None:
    uid = os.getuid()

    label = os.environ.get("SYMPHONY_DAEMON_LABEL", "ai.symphony.daemon")
    node_name = os.environ.get("SYMPHONY_DAEMON_NODE", "symphonyd")
    requested_port = int(os.environ.get("SYMPHONY_DAEMON_PORT", "19191"))
    port = pick_port(requested_port)
    mise_bin = os.environ.get("MISE_BIN", "/opt/homebrew/bin/mise")

    symphony_elixir_dir = Path(
        os.environ.get("SYMPHONY_ELIXIR_DIR", "~/projects_reference/symphony/elixir")
    ).expanduser().resolve()

    plugin_name = os.environ.get("SYMPHONY_TASK_PLUGIN", "generic_tasks")
    plugin_input_env = os.environ.get("SYMPHONY_TASK_PLUGIN_INPUT")

    runtime_root = Path(
        os.environ.get(
            "SYMPHONY_DAEMON_RUNTIME",
            str(Path.home() / "Library" / "Application Support" / "jleechanclaw" / "symphony_daemon"),
        )
    ).expanduser().resolve()
    workspace_root = runtime_root / "workspaces"
    workflow_path = runtime_root / "WORKFLOW.md"
    runner_path = runtime_root / "run_symphony_daemon.sh"
    stdout_path = runtime_root / "stdout.log"
    stderr_path = runtime_root / "stderr.log"
    metadata_path = runtime_root / "daemon_metadata.json"
    issues_json_path = runtime_root / "issues.json"

    launch_agents_dir = Path.home() / "Library/LaunchAgents"
    plist_path = launch_agents_dir / f"{label}.plist"

    runtime_root.mkdir(parents=True, exist_ok=True)
    workspace_root.mkdir(parents=True, exist_ok=True)
    launch_agents_dir.mkdir(parents=True, exist_ok=True)
    runtime_root.chmod(0o700)
    workspace_root.chmod(0o700)

    existing_cookie: str | None = None
    if metadata_path.exists():
        try:
            existing_cookie = json.loads(metadata_path.read_text(encoding="utf-8")).get("cookie")
        except (json.JSONDecodeError, OSError):
            existing_cookie = None

    cookie = os.environ.get("SYMPHONY_DAEMON_COOKIE") or existing_cookie or secrets.token_hex(16)

    if plugin_input_env:
        plugin_input_path = Path(plugin_input_env).expanduser().resolve()
    elif plugin_name == "generic_tasks":
        plugin_input_path = runtime_root / "generic_tasks.json"
        if not plugin_input_path.exists():
            plugin_input_path.write_text(json.dumps({"tasks": []}, indent=2), encoding="utf-8")
            plugin_input_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    else:
        raise RuntimeError(
            f"SYMPHONY_TASK_PLUGIN_INPUT is required for plugin '{plugin_name}'"
        )

    plugin = load_plugin(plugin_name)
    workflow_spec = plugin.build_workflow_spec()
    issues = plugin.load_issues(str(plugin_input_path))
    task_lines = [f"- {issue.identifier} {issue.title}" for issue in issues]

    workflow_path.write_text(
        build_workflow(
            str(workspace_root),
            workflow_spec.title,
            workflow_spec.intro,
            task_lines,
            workflow_spec.requirements,
        ),
        encoding="utf-8",
    )

    issues_json_path.write_text(
        json.dumps(
            {
                "plugin": plugin_name,
                "issues": [
                    {
                        "id": issue.issue_id,
                        "identifier": issue.identifier,
                        "title": issue.title,
                        "description": issue.description,
                        "labels": issue.labels,
                        "state": "Todo",
                        "assigned_to_worker": True,
                    }
                    for issue in issues
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    runner_path.write_text(
        build_runner_script(
            str(symphony_elixir_dir),
            str(workflow_path),
            node_name,
            cookie,
            port,
            mise_bin=mise_bin,
        ),
        encoding="utf-8",
    )
    runner_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    plist_data = build_launch_agent(
        label=label,
        runner_path=str(runner_path),
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
    )
    with plist_path.open("wb") as f:
        plistlib.dump(plist_data, f)

    metadata = {
        "label": label,
        "node_name": node_name,
        "cookie": cookie,
        "port": port,
        "mise_bin": mise_bin,
        "workflow_path": str(workflow_path),
        "workspace_root": str(workspace_root),
        "runner_path": str(runner_path),
        "plist_path": str(plist_path),
        "task_plugin": plugin_name,
        "task_plugin_input": str(plugin_input_path),
        "issues_json": str(issues_json_path),
        "symphony_elixir_dir": str(symphony_elixir_dir),
        "runtime_root": str(runtime_root),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    metadata_path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    domain_target = f"gui/{uid}/{label}"

    run(["launchctl", "bootout", f"gui/{uid}", str(plist_path)], check=False)
    run(["launchctl", "bootstrap", f"gui/{uid}", str(plist_path)])
    run(["launchctl", "kickstart", "-k", domain_target])

    print(f"label={label}")
    if port != requested_port:
        print(f"requested_port={requested_port}")
        print(f"selected_port={port}")
    print(f"plist={plist_path}")
    print(f"workflow={workflow_path}")
    print(f"workspace_root={workspace_root}")
    print(f"metadata={metadata_path}")


if __name__ == "__main__":
    main()
