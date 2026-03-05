"""Agent registry — persistent mapping of tmux sessions to Mission Control agent IDs.

Maps tmux session names to Mission Control agent IDs without a database.
Persists to ~/.jleechanclaw/agent_registry.json.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


REGISTRY_FILE = Path.home() / ".jleechanclaw" / "agent_registry.json"

# Process-local lock to prevent concurrent load→mutate→save races
_registry_lock = threading.Lock()


@dataclass
class AgentRegistry:
    """Persistent registry mapping tmux session names to MC agent IDs.

    Attributes:
        file_path: Path to the JSON registry file.
    """

    file_path: Path
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Ensure the registry directory exists."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, str]:
        """Load registry from JSON file.

        Returns:
            Dict mapping tmux_name -> mc_agent_id (string keys and values only).
        """
        if not self.file_path.exists():
            return {}
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    return {}
                # Enforce dict[str, str] contract — drop any non-string entries
                return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self, data: dict[str, str]) -> None:
        """Atomically save registry to JSON file via temp file + rename.

        Args:
            data: Dict mapping tmux_name -> mc_agent_id.
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        # Write to temp file in same directory, then rename for atomicity
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=self.file_path.parent, suffix=".tmp"
        )
        try:
            with os.fdopen(tmp_fd, "w") as f:
                tmp_fd = -1  # fdopen took ownership; sentinel so except won't double-close
                json.dump(data, f, indent=2)
            Path(tmp_path).replace(self.file_path)
        except Exception:
            if tmp_fd >= 0:
                os.close(tmp_fd)
            Path(tmp_path).unlink(missing_ok=True)
            raise

    def register(self, tmux_name: str, mc_agent_id: str) -> None:
        """Register a tmux session with its MC agent ID.

        Args:
            tmux_name: Name of the tmux session.
            mc_agent_id: Mission Control agent ID.
        """
        with self._lock:
            data = self._load()
            data[tmux_name] = mc_agent_id
            self._save(data)

    def lookup(self, tmux_name: str) -> Optional[str]:
        """Look up MC agent ID for a tmux session.

        Args:
            tmux_name: Name of the tmux session.

        Returns:
            MC agent ID, or None if not found.
        """
        with self._lock:
            data = self._load()
            return data.get(tmux_name)

    def remove(self, tmux_name: str) -> bool:
        """Remove a tmux session from the registry.

        Args:
            tmux_name: Name of the tmux session.

        Returns:
            True if removed, False if not found.
        """
        with self._lock:
            data = self._load()
            if tmux_name in data:
                del data[tmux_name]
                self._save(data)
                return True
            return False

    def list_all(self) -> dict[str, str]:
        """List all registered tmux sessions and their MC agent IDs.

        Returns:
            Dict mapping tmux_name -> mc_agent_id.
        """
        with self._lock:
            return self._load()
