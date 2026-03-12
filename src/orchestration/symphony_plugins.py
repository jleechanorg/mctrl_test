from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowSpec:
    title: str
    intro: str
    requirements: list[str]


@dataclass(frozen=True)
class IssueSpec:
    issue_id: str
    identifier: str
    title: str
    description: str
    labels: list[str]


class TaskPlugin:
    name: str

    def build_workflow_spec(self) -> WorkflowSpec:
        raise NotImplementedError

    def load_issues(self, plugin_input_path: str) -> list[IssueSpec]:
        raise NotImplementedError


class GenericTasksPlugin(TaskPlugin):
    name = "generic_tasks"

    def build_workflow_spec(self) -> WorkflowSpec:
        return WorkflowSpec(
            title="General coding tasks",
            intro="Complete assigned engineering tasks with production-ready changes.",
            requirements=[
                "Implement code changes directly in the target repository workspace.",
                "Run targeted tests/lint for changed areas.",
                "Summarize what changed and any residual risks.",
                "Do not ask for user input unless truly blocked.",
            ],
        )

    def load_issues(self, plugin_input_path: str) -> list[IssueSpec]:
        with open(plugin_input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        issues: list[IssueSpec] = []
        for item in data["tasks"]:
            idx = str(item["id"])
            issues.append(
                IssueSpec(
                    issue_id=f"issue-gen-{idx}",
                    identifier=f"GEN-{idx}",
                    title=item["title"],
                    description=item.get("description", ""),
                    labels=["general", *item.get("labels", [])],
                )
            )
        return issues


class LeetCodeHardPlugin(TaskPlugin):
    name = "leetcode_hard"

    def build_workflow_spec(self) -> WorkflowSpec:
        return WorkflowSpec(
            title="LeetCode hard benchmark task",
            intro="Solve the assigned LeetCode Hard problems in Python.",
            requirements=[
                "Create a solutions directory with one Python file per problem slug.",
                "Create tests/test_solutions.py with correctness tests for all assigned problems.",
                "Run python3 -m pytest -q.",
                "Write the command output to bench_report.txt.",
                "If pytest fails, fix and rerun until passing.",
            ],
        )

    def load_issues(self, plugin_input_path: str) -> list[IssueSpec]:
        with open(plugin_input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        issues: list[IssueSpec] = []
        for item in data["problems"]:
            pid = str(item["id"])
            slug = item["slug"]
            title = item["title"]
            issues.append(
                IssueSpec(
                    issue_id=f"issue-lc-{pid}",
                    identifier=f"LC-{pid}",
                    title=title,
                    description=(
                        f"Solve LeetCode {pid} {title} ({slug}) in Python. "
                        "Create tests and record pytest output in bench_report.txt."
                    ),
                    labels=["benchmark", "leetcode", "hard", slug],
                )
            )
        return issues


class SweBenchVerifiedPlugin(TaskPlugin):
    name = "swe_bench_verified"

    def build_workflow_spec(self) -> WorkflowSpec:
        return WorkflowSpec(
            title="SWE-bench Verified benchmark task",
            intro="Resolve assigned SWE-bench Verified instances by patching code and validating tests.",
            requirements=[
                "Read each instance context and implement a minimal fix.",
                "Create a patch summary in bench_report.txt with files touched and rationale.",
                "Run relevant tests for each instance and include pass/fail output.",
                "If tests fail, iterate until passing or document a concrete blocker.",
                "Do not ask for user input.",
            ],
        )

    def load_issues(self, plugin_input_path: str) -> list[IssueSpec]:
        with open(plugin_input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        issues: list[IssueSpec] = []
        for item in data["instances"]:
            instance_id = item["instance_id"]
            repo = item["repo"]
            issues.append(
                IssueSpec(
                    issue_id=f"issue-swe-{instance_id}",
                    identifier=f"SWE-{instance_id}",
                    title=f"{repo} {instance_id}",
                    description=(
                        f"SWE-bench Verified instance {instance_id} in {repo}. "
                        f"Base commit: {item['base_commit']}.\n"
                        f"Problem statement:\n{item['problem_statement']}"
                    ),
                    labels=["benchmark", "swe-bench-verified", repo],
                )
            )
        return issues


_PLUGINS: dict[str, type[TaskPlugin]] = {
    "generic_tasks": GenericTasksPlugin,
    "leetcode_hard": LeetCodeHardPlugin,
    "swe_bench_verified": SweBenchVerifiedPlugin,
}


def list_plugins() -> list[str]:
    return sorted(_PLUGINS)


def load_plugin(name: str) -> TaskPlugin:
    if name not in _PLUGINS:
        available = ", ".join(list_plugins())
        raise ValueError(f"Unknown plugin: {name}. Available: {available}")
    return _PLUGINS[name]()
