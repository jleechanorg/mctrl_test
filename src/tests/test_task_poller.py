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
