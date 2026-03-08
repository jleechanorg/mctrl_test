"""Mission Control backend runtime (API + optional heartbeat mirror only).

Task start/dispatch must come from direct OpenClaw -> ai_orch flow.
The legacy in-process TaskPoller start path is intentionally disabled.
"""

from __future__ import annotations

import argparse
import logging
import os
import threading
from collections.abc import Mapping

from orchestration.heartbeat_bridge import sync_agents_to_mission_control
from orchestration.mc_client import MissionControlClient

logger = logging.getLogger(__name__)

POLLER_ENABLE_ENV = "MISSION_CONTROL_IN_PROCESS_POLLER"
BOARD_ID_ENV = "MISSION_CONTROL_BOARD_ID"
HEARTBEAT_INTERVAL_ENV = "MISSION_CONTROL_HEARTBEAT_INTERVAL_SECONDS"
LEGACY_POLL_INTERVAL_ENV = "MISSION_CONTROL_POLL_INTERVAL_SECONDS"  # Legacy fallback
DEFAULT_HEARTBEAT_INTERVAL = 60


def _is_enabled(value: str | None) -> bool:
    """Interpret common truthy/falsy env values."""
    normalized = (value or "").strip().lower()
    return normalized not in {"", "0", "false", "no", "off"}


def start_in_process_heartbeat_poller(
    *,
    board_id: str,
    interval_seconds: int = DEFAULT_HEARTBEAT_INTERVAL,
) -> tuple[threading.Thread, threading.Event]:
    """Start HeartbeatPoller in a daemon thread and return (thread, stop_event) handle."""
    client = MissionControlClient()
    if not client.is_configured:
        raise RuntimeError(
            "Mission Control not configured for HeartbeatPoller "
            "(set MISSION_CONTROL_BASE_URL and MISSION_CONTROL_TOKEN)"
        )

    stop_event = threading.Event()

    def _run() -> None:
        # Sync immediately on start so agents appear before the first interval elapses.
        try:
            sync_agents_to_mission_control(board_id=board_id, client=client)
        except Exception as exc:
            logger.warning("heartbeat sync failed (initial): %s", exc)
        while not stop_event.wait(interval_seconds):
            try:
                sync_agents_to_mission_control(board_id=board_id, client=client)
            except Exception as exc:
                logger.warning("heartbeat sync failed: %s", exc)  # Never crash the loop

    thread = threading.Thread(
        target=_run,
        name="mission-control-heartbeat-poller",
        daemon=True,
    )
    thread.start()
    logger.info(
        "started in-process heartbeat poller for board=%s interval=%ds",
        board_id,
        interval_seconds,
    )
    return thread, stop_event


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
    """Start optional heartbeat mirror and run Mission Control backend server."""
    if _is_enabled(env.get(POLLER_ENABLE_ENV)):
        logger.warning(
            "%s is set but ignored; in-process TaskPoller startup is disabled",
            POLLER_ENABLE_ENV,
        )

    board_id = str(env.get(BOARD_ID_ENV, "")).strip()
    if board_id:
        # Check new env var first, then fall back to legacy
        heartbeat_interval_raw = str(env.get(HEARTBEAT_INTERVAL_ENV, "")).strip()
        if not heartbeat_interval_raw:
            heartbeat_interval_raw = str(env.get(LEGACY_POLL_INTERVAL_ENV, "")).strip()
        if heartbeat_interval_raw:
            try:
                heartbeat_interval = int(heartbeat_interval_raw)
            except ValueError as exc:
                raise RuntimeError(
                    f"{HEARTBEAT_INTERVAL_ENV} must be an integer number of seconds"
                    f" (got {heartbeat_interval_raw!r})"
                ) from exc
            if heartbeat_interval <= 0:
                raise RuntimeError(
                    f"{HEARTBEAT_INTERVAL_ENV} must be > 0 (got {heartbeat_interval})"
                )
        else:
            heartbeat_interval = DEFAULT_HEARTBEAT_INTERVAL
        start_in_process_heartbeat_poller(
            board_id=board_id,
            interval_seconds=heartbeat_interval,
        )
    else:
        logger.info(
            "heartbeat poller disabled: no %s configured",
            BOARD_ID_ENV,
        )

    _run_uvicorn(app, host, port)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Mission Control backend (heartbeat mirror optional)",
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
