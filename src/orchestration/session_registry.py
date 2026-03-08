from __future__ import annotations

import json
import os
import tempfile
import threading
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

TaskLifecycleStatus = Literal["queued", "in_progress", "needs_human", "finished"]

DEFAULT_REGISTRY_PATH = ".tracking/bead_session_registry.jsonl"

# Process-local lock for registry updates (not needed for cross-process atomicity
# since os.replace is atomic, but prevents race conditions within a process)
_registry_lock = threading.Lock()


@dataclass(frozen=True)
class BeadSessionMapping:
    bead_id: str
    session_name: str
    worktree_path: str
    branch: str
    agent_cli: str
    status: TaskLifecycleStatus
    updated_at: str
    # SHA of HEAD at spawn time — used to detect new commits by the agent.
    # Empty string for legacy entries that predate this field.
    start_sha: str = ""
    # Slack ts of the original trigger message in #all-jleechan-ai — used to
    # thread the completion reply under that message. Empty for non-Slack tasks.
    slack_trigger_ts: str = ""

    @classmethod
    def create(
        cls,
        *,
        bead_id: str,
        session_name: str,
        worktree_path: str,
        branch: str,
        agent_cli: str,
        status: TaskLifecycleStatus,
        start_sha: str = "",
        slack_trigger_ts: str = "",
    ) -> BeadSessionMapping:
        return cls(
            bead_id=bead_id,
            session_name=session_name,
            worktree_path=worktree_path,
            branch=branch,
            agent_cli=agent_cli,
            status=status,
            updated_at=_utcnow_iso(),
            start_sha=start_sha,
            slack_trigger_ts=slack_trigger_ts,
        )

    @classmethod
    def from_dict(cls, payload: dict[str, str]) -> BeadSessionMapping:
        return cls(
            bead_id=str(payload["bead_id"]),
            session_name=str(payload["session_name"]),
            worktree_path=str(payload["worktree_path"]),
            branch=str(payload["branch"]),
            agent_cli=str(payload["agent_cli"]),
            status=str(payload["status"]),  # type: ignore[arg-type]
            updated_at=str(payload["updated_at"]),
            start_sha=str(payload.get("start_sha", "")),
            slack_trigger_ts=str(payload.get("slack_trigger_ts", "")),
        )


def upsert_mapping(
    mapping: BeadSessionMapping,
    *,
    registry_path: str = DEFAULT_REGISTRY_PATH,
) -> None:
    with _registry_lock:
        by_bead: dict[str, BeadSessionMapping] = {
            item.bead_id: item for item in list_mappings(registry_path=registry_path)
        }
        by_bead[mapping.bead_id] = mapping
        _write_all(list(by_bead.values()), registry_path=registry_path)


def update_mapping_status(
    bead_id: str,
    status: TaskLifecycleStatus,
    *,
    from_status: TaskLifecycleStatus | None = None,
    registry_path: str = DEFAULT_REGISTRY_PATH,
) -> bool:
    with _registry_lock:
        items = list_mappings(registry_path=registry_path)
        found = False
        updated_items: list[BeadSessionMapping] = []

        for item in items:
            if item.bead_id == bead_id:
                # CAS guard: if from_status is given, only update if current
                # status matches — prevents double-notification when two
                # reconciler processes overlap.
                if from_status is not None and item.status != from_status:
                    return False
                found = True
                updated_items.append(
                    replace(item, status=status, updated_at=_utcnow_iso())
                )
            else:
                updated_items.append(item)

        if not found:
            return False
        _write_all(updated_items, registry_path=registry_path)
        return True


def get_mapping(
    bead_id: str,
    *,
    registry_path: str = DEFAULT_REGISTRY_PATH,
) -> BeadSessionMapping | None:
    for item in list_mappings(registry_path=registry_path):
        if item.bead_id == bead_id:
            return item
    return None


def list_mappings(*, registry_path: str = DEFAULT_REGISTRY_PATH) -> list[BeadSessionMapping]:
    path = Path(registry_path)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []

    results: list[BeadSessionMapping] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
            results.append(BeadSessionMapping.from_dict(payload))
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            # Skip malformed lines to allow reconciliation to continue
            continue
    return results


def _write_all(
    items: list[BeadSessionMapping],
    *,
    registry_path: str,
) -> None:
    target = Path(registry_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=f"{target.name}.",
            suffix=".tmp",
            dir=str(target.parent),
            delete=False,
        ) as tmp:
            for item in items:
                tmp.write(json.dumps(asdict(item), sort_keys=True))
                tmp.write("\n")
            temp_path = tmp.name
        os.replace(temp_path, target)
        temp_path = None
    finally:
        if temp_path is not None:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def _utcnow_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
