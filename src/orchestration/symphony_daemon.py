"""Helpers for provisioning a launchd-managed Symphony daemon."""

from __future__ import annotations

from typing import Iterable


def build_workflow(
    workspace_root: str,
    workflow_title: str,
    workflow_intro: str,
    task_lines: Iterable[str],
    requirements: Iterable[str],
) -> str:
    tasks = "\n".join(task_lines)
    req_lines = "\n".join(f"{idx}. {line}" for idx, line in enumerate(requirements, start=1))

    return f"""---
tracker:
  kind: memory
  active_states:
    - Todo
    - In Progress
  terminal_states:
    - Done
polling:
  interval_ms: 1000
workspace:
  root: \"{workspace_root}\"
agent:
  max_concurrent_agents: 1
  max_turns: 4
codex:
  command: codex app-server
  read_timeout_ms: 120000
  approval_policy: never
  thread_sandbox: workspace-write
  turn_sandbox_policy:
    type: workspaceWrite
---
You are running an autonomous coding task.

Task type: {workflow_title}

{workflow_intro}

Assigned items:
{tasks}

Requirements:
{req_lines}

Do not ask for user input unless there is a hard blocker with concrete evidence.
"""


def build_runner_script(
    symphony_elixir_dir: str,
    workflow_path: str,
    node_name: str,
    cookie: str,
    port: int,
    mise_bin: str = "/opt/homebrew/bin/mise",
) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

cd \"{symphony_elixir_dir}\"
export ERL_AFLAGS=\"-sname {node_name} -setcookie {cookie}\"
\"{mise_bin}\" exec -- epmd -daemon || true
exec \"{mise_bin}\" exec -- ./bin/symphony \\
  --i-understand-that-this-will-be-running-without-the-usual-guardrails \\
  --port {port} \\
  \"{workflow_path}\"
"""


def build_launch_agent(
    label: str,
    runner_path: str,
    stdout_path: str,
    stderr_path: str,
) -> dict:
    return {
        "Label": label,
        "ProgramArguments": ["/bin/bash", runner_path],
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": stdout_path,
        "StandardErrorPath": stderr_path,
    }
