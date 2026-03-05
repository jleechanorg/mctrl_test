from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, call

import pytest

from orchestration.mc_client import MCClient, TaskStatus
from orchestration.task_poller import TaskPoller


def _make_client(update_return: Any = {"id": "t1", "status": "dispatching"}) -> MCClient:
    client = MagicMock(spec=MCClient)
    client.update_task.return_value = update_return
    return client


# ---------------------------------------------------------------------------
# TaskStatus enum
# ---------------------------------------------------------------------------


def test_task_status_dispatching_value() -> None:
    assert TaskStatus.DISPATCHING == "dispatching"


# ---------------------------------------------------------------------------
# Feature 1: DISPATCHING atomic state (ORCH-qxw)
# ---------------------------------------------------------------------------


def test_dispatching_set_before_dispatch_fn_called() -> None:
    """DISPATCHING update must happen before the dispatch_fn is invoked."""
    call_order: list[str] = []

    client = MagicMock(spec=MCClient)

    def record_update(task_id: str, status: TaskStatus, **kwargs: Any) -> dict[str, Any]:
        call_order.append(f"update:{status}")
        return {"id": task_id, "status": str(status)}

    client.update_task.side_effect = record_update

    def dispatch_fn(task_id: str) -> tuple[bool, dict[str, Any]]:
        call_order.append("dispatch")
        return (True, {})

    poller = TaskPoller(client=client, board_id="board1", dispatch_fn=dispatch_fn)
    result = poller._dispatch_task("t1")

    assert result is True
    # DISPATCHING must appear before dispatch in the call order
    assert call_order.index(f"update:{TaskStatus.DISPATCHING}") < call_order.index("dispatch")


def test_dispatching_update_none_skips_dispatch_fn() -> None:
    """If DISPATCHING update returns None (task already claimed), dispatch_fn must NOT be called."""
    dispatch_fn = MagicMock(return_value=(True, {}))

    client = MagicMock(spec=MCClient)
    client.update_task.return_value = None  # simulate already-claimed

    poller = TaskPoller(client=client, board_id="board1", dispatch_fn=dispatch_fn)
    result = poller._dispatch_task("t1")

    assert result is False
    dispatch_fn.assert_not_called()


def test_dispatching_update_falsy_skips_dispatch_fn() -> None:
    """Empty dict is a successful response — must proceed with dispatch."""
    dispatch_fn = MagicMock(return_value=(True, {}))

    client = MagicMock(spec=MCClient)
    client.update_task.return_value = {}  # falsy but valid success response

    poller = TaskPoller(client=client, board_id="board1", dispatch_fn=dispatch_fn)
    result = poller._dispatch_task("t1")

    assert result is True
    dispatch_fn.assert_called_once_with("t1")


def test_dispatching_success_path_returns_true() -> None:
    """When DISPATCHING is accepted and dispatch_fn succeeds, _dispatch_task returns True."""
    client = _make_client({"id": "t1", "status": "dispatching"})
    dispatch_fn = MagicMock(return_value=(True, {}))

    poller = TaskPoller(client=client, board_id="board1", dispatch_fn=dispatch_fn)
    result = poller._dispatch_task("t1")

    assert result is True
    dispatch_fn.assert_called_once_with("t1")


# ---------------------------------------------------------------------------
# Feature 2: EXECUTION_FAILED status (ORCH-8w8)
# ---------------------------------------------------------------------------


def test_task_status_execution_failed_value() -> None:
    assert TaskStatus.EXECUTION_FAILED == "execution_failed"


def test_execution_failed_set_on_nonzero_exit(monkeypatch) -> None:
    """_dispatch_via_ai_orch must return EXECUTION_FAILED status in metadata on non-zero exit."""
    import subprocess
    completed = subprocess.CompletedProcess(
        args=["ai_orch", "run", "t1"],
        returncode=1,
        stdout="",
        stderr="subprocess error",
    )
    monkeypatch.setattr("orchestration.task_poller.subprocess.run", lambda *a, **kw: completed)

    client = _make_client()
    poller = TaskPoller(client=client, board_id="board1")
    success, meta = poller._dispatch_via_ai_orch("t1")

    assert success is False
    assert meta["status"] == TaskStatus.EXECUTION_FAILED
    assert meta["exit_code"] == 1


def test_dispatch_task_uses_execution_failed_status(monkeypatch) -> None:
    """_dispatch_task must update to EXECUTION_FAILED (not FAILED) when ai_orch exits non-zero."""
    import subprocess
    completed = subprocess.CompletedProcess(
        args=["ai_orch", "run", "t1"],
        returncode=2,
        stdout="",
        stderr="error",
    )
    monkeypatch.setattr("orchestration.task_poller.subprocess.run", lambda *a, **kw: completed)

    client = MagicMock(spec=MCClient)
    client.update_task.return_value = {"id": "t1", "status": "dispatching"}
    poller = TaskPoller(client=client, board_id="board1")
    result = poller._dispatch_task("t1")

    assert result is False
    # Second update_task call must use EXECUTION_FAILED
    calls = client.update_task.call_args_list
    assert len(calls) == 2
    _, kwargs_or_args = calls[1][0], calls[1]
    update_status = calls[1][0][1]
    assert update_status == TaskStatus.EXECUTION_FAILED


def test_dispatch_task_uses_failed_status_on_exception() -> None:
    """When dispatch_fn raises, _dispatch_task must update to FAILED (not EXECUTION_FAILED)."""
    client = MagicMock(spec=MCClient)
    client.update_task.return_value = {"id": "t1", "status": "dispatching"}

    def raising_dispatch(task_id: str) -> tuple[bool, dict]:
        raise RuntimeError("unexpected error")

    poller = TaskPoller(client=client, board_id="board1", dispatch_fn=raising_dispatch)
    result = poller._dispatch_task("t1")

    assert result is False
    calls = client.update_task.call_args_list
    assert len(calls) == 2
    assert calls[1][0][1] == TaskStatus.FAILED
