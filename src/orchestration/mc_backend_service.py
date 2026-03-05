"""Mission Control runtime that co-hosts API server and TaskPoller.

This module is used by launchd/manual startup so the Mission Control backend
and inbox-draining TaskPoller share one supervised service lifecycle.
"""

from __future__ import annotations

import argparse
import logging
import os
import threading
from collections.abc import Mapping

from orchestration.mc_client import MissionControlClient
from orchestration.task_poller import TaskPoller

logger = logging.getLogger(__name__)

POLLER_ENABLE_ENV = "MISSION_CONTROL_IN_PROCESS_POLLER"
BOARD_ID_ENV = "MISSION_CONTROL_BOARD_ID"
POLL_INTERVAL_ENV = "MISSION_CONTROL_POLL_INTERVAL_SECONDS"


def _is_enabled(value: str | None) -> bool:
    """Interpret common truthy/falsy env values."""
    normalized = (value or "").strip().lower()
    return normalized not in {"", "0", "false", "no", "off"}


def _resolve_poll_interval_seconds(env: Mapping[str, str]) -> int | None:
    """Parse optional poll interval override from environment."""
    raw = str(env.get(POLL_INTERVAL_ENV, "")).strip()
    if not raw:
        return None
    try:
        interval = int(raw)
    except ValueError as exc:
        raise RuntimeError(
            f"{POLL_INTERVAL_ENV} must be an integer number of seconds (got {raw!r})"
        ) from exc
    if interval <= 0:
        raise RuntimeError(f"{POLL_INTERVAL_ENV} must be > 0 (got {interval})")
    return interval


def start_in_process_task_poller(
    *,
    board_id: str,
    poll_interval_seconds: int | None = None,
) -> threading.Thread:
    """Start TaskPoller in a daemon thread and return the thread handle."""
    client = MissionControlClient()
    if not client.is_configured:
        raise RuntimeError(
            "Mission Control not configured for TaskPoller "
            "(set MISSION_CONTROL_BASE_URL and MISSION_CONTROL_TOKEN)"
        )

    if poll_interval_seconds is None:
        poller = TaskPoller(
            board_id=board_id,
            client=client,
        )
    else:
        poller = TaskPoller(
            board_id=board_id,
            client=client,
            poll_interval_seconds=poll_interval_seconds,
        )
    thread = threading.Thread(
        target=poller.run_forever,
        name="mission-control-task-poller",
        daemon=True,
    )
    thread.start()
    logger.info("started in-process task poller for board=%s", board_id)
    return thread


def _run_uvicorn(app: str, host: str, port: int) -> None:
    """Run uvicorn server in foreground."""
    import uvicorn

    uvicorn.run(app, host=host, port=port)


def run_service(
    *,
    app: str,
    host: str,
    port: int,
    env: Mapping[str, str] = os.environ,
) -> None:
    """Start poller (optional) and run Mission Control backend server."""
    poller_enabled = _is_enabled(env.get(POLLER_ENABLE_ENV))
    if poller_enabled:
        board_id = str(env.get(BOARD_ID_ENV, "")).strip()
        if not board_id:
            raise RuntimeError(
                f"{BOARD_ID_ENV} is required when {POLLER_ENABLE_ENV} is enabled"
            )
        interval = _resolve_poll_interval_seconds(env)
        start_in_process_task_poller(
            board_id=board_id,
            poll_interval_seconds=interval,
        )
    else:
        logger.info(
            "in-process task poller disabled via %s=%r",
            POLLER_ENABLE_ENV,
            env.get(POLLER_ENABLE_ENV),
        )

    _run_uvicorn(app, host, port)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Mission Control backend with in-process TaskPoller",
    )
    parser.add_argument("--app", default="app.main:app", help="ASGI app import string")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=9010, help="Bind port")
    parser.add_argument(
        "--log-level",
        default=os.environ.get("MC_BACKEND_SERVICE_LOG_LEVEL", "INFO"),
        help="Python log level",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        run_service(app=args.app, host=args.host, port=args.port)
    except RuntimeError as exc:
        logger.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
