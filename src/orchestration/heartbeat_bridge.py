"""Heartbeat bridge: sync gateway agent state to Mission Control.

Reads openclaw agent status and upserts each agent into the Mission Control
board as an agent record with a current heartbeat timestamp.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orchestration.mc_client import MissionControlClient

logger = logging.getLogger(__name__)


def sync_agents_to_mission_control(
    *,
    board_id: str,
    client: MissionControlClient,
) -> None:
    """Fetch live agents from openclaw gateway and upsert them to Mission Control.

    This is a best-effort sync — individual agent failures are logged as warnings
    and do not raise, so the heartbeat loop can continue.
    """
    import subprocess
    import json

    try:
        result = subprocess.run(
            ["openclaw", "agents", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            logger.warning(
                "openclaw agents list failed (exit %d): %s",
                result.returncode,
                result.stderr.strip(),
            )
            return
        agents = json.loads(result.stdout)
    except FileNotFoundError:
        logger.warning("openclaw CLI not found; skipping agent sync")
        return
    except Exception as exc:  # noqa: BLE001
        logger.warning("heartbeat_bridge: failed to list agents: %s", exc)
        return

    for agent in agents:
        agent_id = agent.get("id") or agent.get("agentId")
        if not agent_id:
            continue
        try:
            client.upsert_agent(
                board_id=board_id,
                agent_id=agent_id,
                metadata=agent,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "heartbeat_bridge: failed to upsert agent %s: %s", agent_id, exc
            )
