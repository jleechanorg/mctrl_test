#!/usr/bin/env python3
"""Extract evidence for memory seeding from PRs, beads, and conversation logs."""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_REPOS = [
    Path("~/projects/worldarchitect.ai").expanduser(),
    Path("~/project_jleechanclaw/jleechanclaw").expanduser(),
    Path("~/project_worldaiclaw/worldai_claw").expanduser(),
]

ANALYSIS_INPUT_PATH = Path("/tmp/openclaw-pattern-analysis-input.json")


def run_command(command: list[str], cwd: Path | None = None) -> str:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def parse_days_ago(value: int) -> str:
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=value)).isoformat()


def infer_repo(repo: Path) -> str:
    try:
        output = run_command(["git", "remote", "get-url", "origin"], cwd=repo)
    except Exception:
        return f"jleechanorg/{repo.name}"
    value = output.strip()
    if value.startswith("git@github.com:"):
        return value.removeprefix("git@github.com:").removesuffix(".git")
    if value.startswith("https://github.com/"):
        return value.removeprefix("https://github.com/").removesuffix(".git")
    return f"jleechanorg/{repo.name}"


def collect_recent_commits(repo: Path, since: str) -> list[dict[str, str]]:
    try:
        output = run_command(
            [
                "git",
                "log",
                "--no-merges",
                f"--since={since}",
                "--date=iso-strict",
                "--pretty=%ad%x1f%s",
            ],
            cwd=repo,
        )
    except Exception:
        return []

    events: list[dict[str, str]] = []
    for line in filter(None, output.splitlines()):
        when_raw, subject = (line.split("\x1f", maxsplit=1) + [""])[:2]
        if not when_raw or not subject:
            continue
        try:
            when = dt.datetime.fromisoformat(when_raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        events.append({"repo": repo.name, "date": when.isoformat(), "subject": subject.strip()})
    return events


def _parse_iso(value: str) -> dt.datetime | None:
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def collect_repo_merged_prs(repo: Path, since: str, limit: int) -> list[dict[str, str]]:
    repo_name = infer_repo(repo)
    try:
        output = run_command(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                repo_name,
                "--state",
                "merged",
                "--limit",
                str(limit),
                "--json",
                "number,title,mergedAt,updatedAt,url,body",
            ]
        )
        payload = json.loads(output)
    except Exception:
        return []

    cutoff = _parse_iso(since)
    if cutoff is None:
        return []

    out: list[dict[str, str]] = []
    for item in payload:
        merged_raw = str(item.get("mergedAt") or "")
        merged_at = _parse_iso(merged_raw)
        if merged_at is None or merged_at < cutoff:
            continue
        out.append(
            {
                "repo": repo_name,
                "date": merged_at.isoformat(),
                "number": str(item.get("number") or ""),
                "title": str(item.get("title") or ""),
                "url": str(item.get("url") or ""),
                "body": str(item.get("body") or ""),
            }
        )
    return out


def _repo_name_from_search_item(item: dict[str, Any]) -> str:
    repo_obj = item.get("repository")
    if isinstance(repo_obj, dict):
        for key in ("nameWithOwner", "fullName", "name"):
            value = repo_obj.get(key)
            if value:
                return str(value)
    return "unknown"


def collect_org_merged_prs(org: str, since: str, limit: int) -> list[dict[str, str]]:
    since_date = since[:10]
    query = f"org:{org} is:pr is:merged merged:>={since_date}"
    try:
        output = run_command(
            [
                "gh",
                "search",
                "prs",
                query,
                "--limit",
                str(limit),
                "--json",
                "number,title,repository,mergedAt,updatedAt,url,body",
            ]
        )
        payload = json.loads(output)
    except Exception:
        return []

    cutoff = _parse_iso(since)
    if cutoff is None:
        return []

    out: list[dict[str, str]] = []
    for item in payload:
        merged_raw = str(item.get("mergedAt") or "")
        merged_at = _parse_iso(merged_raw)
        if merged_at is None or merged_at < cutoff:
            continue
        out.append(
            {
                "repo": _repo_name_from_search_item(item),
                "date": merged_at.isoformat(),
                "number": str(item.get("number") or ""),
                "title": str(item.get("title") or ""),
                "url": str(item.get("url") or ""),
                "body": str(item.get("body") or ""),
            }
        )
    return out


def collect_bead_updates(days: int, limit: int) -> list[dict[str, str]]:
    beads_path = Path("~/.beads/issues.jsonl").expanduser()
    if not beads_path.exists():
        return []

    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    rows: list[dict[str, str]] = []
    for line in beads_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = (
            payload.get("updated_at")
            or payload.get("updatedAt")
            or payload.get("created_at")
            or payload.get("createdAt")
        )
        if not ts:
            continue
        when = _parse_iso(str(ts))
        if when is None or when < cutoff:
            continue
        title = str(payload.get("title") or payload.get("summary") or "").strip()
        if not title:
            continue
        rows.append(
            {
                "id": str(payload.get("id") or payload.get("bead_id") or "unknown"),
                "title": title,
                "status": str(payload.get("status") or ""),
                "priority": str(payload.get("priority") or ""),
                "updated_at": when.isoformat(),
            }
        )

    rows.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
    return rows[:limit]


def _discover_conversation_files(days: int, limit: int) -> list[Path]:
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    patterns = [
        "~/.claude/projects/**/*.jsonl",
        "~/.openclaw/agents/*/sessions/*.jsonl",
        "~/.openclaw/workspace/openclaw-config/agents/*/sessions/*.json",
        "~/projects/worldai_archive/**/proto_genesis_session.json",
        "~/projects/worldai_archive/**/request_responses.jsonl",
        "~/projects/worldarchitect.ai/**/proto_genesis_session.json",
    ]

    candidates: list[tuple[float, Path]] = []
    for pattern in patterns:
        for raw in glob.glob(str(Path(pattern).expanduser()), recursive=True):
            path = Path(raw)
            if not path.is_file():
                continue
            try:
                mtime = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc)
            except OSError:
                continue
            if mtime < cutoff:
                continue
            candidates.append((mtime.timestamp(), path))

    seen: set[Path] = set()
    ordered: list[Path] = []
    for _, path in sorted(candidates, key=lambda item: item[0], reverse=True):
        if path in seen:
            continue
        seen.add(path)
        ordered.append(path)
        if len(ordered) >= limit:
            break
    return ordered


def _normalize_text(text: str, max_len: int = 280) -> str:
    cleaned = " ".join(text.strip().split())
    return cleaned[:max_len]


def _extract_strings(value: Any, out: list[str], max_items: int, depth: int = 0) -> None:
    if len(out) >= max_items or depth > 6:
        return
    if isinstance(value, str):
        snippet = _normalize_text(value)
        if len(snippet) >= 40:
            out.append(snippet)
        return
    if isinstance(value, list):
        for item in value:
            _extract_strings(item, out, max_items, depth + 1)
            if len(out) >= max_items:
                return
        return
    if isinstance(value, dict):
        priority_keys = ["content", "text", "message", "prompt", "response", "output", "input"]
        for key in priority_keys:
            if key in value:
                _extract_strings(value[key], out, max_items, depth + 1)
                if len(out) >= max_items:
                    return
        for item in value.values():
            _extract_strings(item, out, max_items, depth + 1)
            if len(out) >= max_items:
                return


def _sample_conversation_file(path: Path, max_snippets: int) -> list[str]:
    snippets: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return snippets

    if path.suffix == ".jsonl":
        for line in text.splitlines():
            if len(snippets) >= max_snippets:
                break
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            _extract_strings(payload, snippets, max_snippets)
        return snippets

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return snippets
    _extract_strings(payload, snippets, max_snippets)
    return snippets


def collect_conversation_samples(days: int, message_limit: int) -> list[dict[str, str]]:
    files = _discover_conversation_files(days=days, limit=max(message_limit, 40))
    rows: list[dict[str, str]] = []
    for path in files:
        if len(rows) >= message_limit:
            break
        try:
            mtime = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc).isoformat()
        except OSError:
            mtime = ""
        for snippet in _sample_conversation_file(path, max_snippets=4):
            rows.append({"file": str(path), "mtime": mtime, "snippet": snippet})
            if len(rows) >= message_limit:
                break
    return rows


def summarize_activity(
    commits: list[dict[str, str]],
    repo_prs: list[dict[str, str]],
    org_prs: list[dict[str, str]],
    beads: list[dict[str, str]],
    convos: list[dict[str, str]],
) -> dict[str, Any]:
    repo_counts: Counter[str] = Counter()
    for row in commits:
        repo_counts[row.get("repo", "unknown")] += 1
    for row in org_prs:
        repo_counts[row.get("repo", "unknown")] += 1

    bead_status: Counter[str] = Counter(row.get("status", "unknown") or "unknown" for row in beads)

    return {
        "counts": {
            "commits": len(commits),
            "repo_merged_prs": len(repo_prs),
            "org_merged_prs": len(org_prs),
            "bead_updates": len(beads),
            "conversation_samples": len(convos),
        },
        "top_repos": [{"repo": repo, "activity": count} for repo, count in repo_counts.most_common(15)],
        "bead_status": dict(bead_status),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=30, help="Lookback window in days")
    parser.add_argument("--org", default="jleechanorg", help="GitHub org for merged PR search.")
    parser.add_argument(
        "--repo",
        action="append",
        help="Git repo path. May be repeated; defaults to configured set.",
    )
    parser.add_argument(
        "--analysis-output",
        default=str(ANALYSIS_INPUT_PATH),
        help="Path for extracted evidence JSON.",
    )
    parser.add_argument(
        "--pr-limit",
        type=int,
        default=400,
        help="Max merged PRs to fetch for org-wide search.",
    )
    parser.add_argument(
        "--conversation-sample-limit",
        type=int,
        default=120,
        help="Max conversation snippets to include.",
    )
    parser.add_argument(
        "--bead-limit",
        type=int,
        default=400,
        help="Max bead updates to include.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print evidence JSON to stdout in addition to writing file.",
    )
    parser.add_argument(
        "--staging-mode",
        action="store_true",
        help="Write artifacts to /tmp for safe staging execution.",
    )
    return parser.parse_args()


def apply_test_paths(args: argparse.Namespace) -> None:
    if args.staging_mode:
        args.analysis_output = str(ANALYSIS_INPUT_PATH)
        print("Staging mode enabled: writing artifacts to /tmp")


def main() -> int:
    args = parse_args()
    apply_test_paths(args)

    repos = [Path(r).expanduser() for r in (args.repo or [str(p) for p in DEFAULT_REPOS])]
    since = parse_days_ago(args.days)
    until = dt.datetime.now(dt.timezone.utc).isoformat()

    commits: list[dict[str, str]] = []
    repo_prs: list[dict[str, str]] = []
    for repo in repos:
        if not repo.exists():
            print(f"Skipping missing repo: {repo}")
            continue
        commits.extend(collect_recent_commits(repo, since))
        repo_prs.extend(collect_repo_merged_prs(repo, since, min(200, args.pr_limit)))

    org_prs = collect_org_merged_prs(args.org, since, args.pr_limit)
    beads = collect_bead_updates(args.days, args.bead_limit)
    convos = collect_conversation_samples(args.days, args.conversation_sample_limit)

    payload = {
        "goal": "Seed OpenClaw memory from recent org work and conversation evidence.",
        "window": {"since": since, "until": until, "days": args.days},
        "org": args.org,
        "repos": [infer_repo(repo) for repo in repos if repo.exists()],
        "summary": summarize_activity(commits, repo_prs, org_prs, beads, convos),
        "samples": {
            "commits": commits[:200],
            "repo_merged_prs": repo_prs[:200],
            "org_merged_prs": org_prs[: args.pr_limit],
            "bead_updates": beads,
            "conversation_snippets": convos,
        },
    }

    output_path = Path(args.analysis_output).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Analysis input written to {output_path}")

    if args.dry_run:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
