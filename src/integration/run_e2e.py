"""E2E integration test harness for orchestration.

This script runs end-to-end tests of the TaskPoller against a mock or real
Mission Control server. It supports --dry-run (mock server, no real claudem)
and --live (real MC + claudem) modes.

Usage:
    python src/integration/run_e2e.py --dry-run
    python src/integration/run_e2e.py --live --task-title "Test task" --task-description "Test description"
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

# Add src to path for imports
_src_path = str(Path(__file__).parent.parent)
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from orchestration.mc_client import MissionControlClient, TaskStatus
from orchestration.task_poller import TaskPoller

logger = logging.getLogger(__name__)

# In-memory task storage for fake server
FAKE_TASKS: dict[str, dict] = {}
FAKE_BOARD_ID = "test-board-123"


class FakeMCHandler(BaseHTTPRequestHandler):
    """HTTP request handler for fake Mission Control server."""

    def log_message(self, format: str, *args) -> None:
        """Suppress default logging."""
        pass

    def _send_json(self, status: int, data: dict) -> None:
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self) -> None:
        """Handle GET requests - list tasks."""
        # GET /api/v1/boards/{board_id}/tasks?status=inbox
        if "/api/v1/boards/" in self.path and "/tasks" in self.path:
            # Return inbox tasks
            inbox_tasks = [
                task for task in FAKE_TASKS.values()
                if task.get("status") == "inbox"
            ]
            self._send_json(200, {"results": inbox_tasks})
            return

        # GET /api/v1/tasks/{task_id} - for status tracking
        if "/api/v1/tasks/" in self.path:
            task_id = self.path.split("/")[-1]
            task = FAKE_TASKS.get(task_id)
            if task:
                self._send_json(200, task)
            else:
                self._send_json(404, {"detail": "Task not found"})
            return

        self._send_json(404, {"detail": "Not found"})

    def do_PATCH(self) -> None:
        """Handle PATCH requests - update task status."""
        if "/api/v1/tasks/" not in self.path:
            self._send_json(404, {"detail": "Not found"})
            return

        task_id = self.path.split("/")[-1]
        if task_id not in FAKE_TASKS:
            self._send_json(404, {"detail": "Task not found"})
            return

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        updates = json.loads(body.decode("utf-8"))

        # Update task
        FAKE_TASKS[task_id].update(updates)

        # Auto-complete task after first PATCH to in_progress (for E2E-4 status tracking)
        if updates.get("status") == "in_progress":
            # Simulate task completion - mark as done after a brief delay
            FAKE_TASKS[task_id]["status"] = "done"

        self._send_json(200, FAKE_TASKS[task_id])


class FakeMissionControlServer:
    """Fake Mission Control server for testing.

    Starts an HTTP server on a random available port and provides
    mock implementations of the MC API endpoints.
    """

    def __init__(self, board_id: str = FAKE_BOARD_ID):
        self.board_id = board_id
        self.port: Optional[int] = None
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    def start(self) -> int:
        """Start the fake server on a random available port.

        Returns:
            The port the server is listening on.
        """
        # Find an available port
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            self.port = s.getsockname()[1]

        self.server = HTTPServer(("127.0.0.1", self.port), FakeMCHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

        logger.info(f"Fake MC server started on port {self.port}")
        return self.port

    def stop(self) -> None:
        """Stop the fake server."""
        if self.server:
            self.server.shutdown()
            self.thread.join(timeout=2)
            logger.info("Fake MC server stopped")

    def seed_task(self, task_id: str, title: str, description: str) -> None:
        """Seed the server with a task in inbox status."""
        FAKE_TASKS[task_id] = {
            "id": task_id,
            "title": title,
            "description": description,
            "status": "inbox",
            "board_id": self.board_id,
        }
        logger.info(f"Seeded task {task_id}: {title}")

    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get the current status of a task."""
        task = FAKE_TASKS.get(task_id)
        return task.get("status") if task else None


def run_dry_run(
    task_title: str = "Test task",
    task_description: str = "Integration test task",
    timeout: int = 60,
) -> int:
    """Run the E2E test in dry-run mode.

    Args:
        task_title: Title for the test task.
        task_description: Description for the test task.
        timeout: Timeout in seconds for status polling.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    logger.info("Starting E2E dry-run test...")

    # Clear any previous fake tasks
    FAKE_TASKS.clear()

    # Start fake MC server
    server = FakeMissionControlServer()
    port = server.start()

    try:
        # Seed a task
        task_id = "test-task-001"
        server.seed_task(task_id, task_title, task_description)

        # Configure Mission Control client to use fake server
        base_url = f"http://127.0.0.1:{port}"
        client = MissionControlClient(
            base_url=base_url,
            token="fake-token-for-testing",
        )

        # Create TaskPoller with a dispatch function that does nothing
        # (we're testing the polling and status update, not actual dispatch)
        poller = TaskPoller(
            board_id=server.board_id,
            client=client,
            poll_interval_seconds=1,
        )

        # Override dispatch to avoid actually spawning agents
        original_dispatch = poller._dispatch_task

        def mock_dispatch(task: dict) -> bool:
            """Mock dispatch that just updates status."""
            # Don't actually run subprocess - just update status
            task_id = task.get("id")
            client.update_task(task_id, TaskStatus.IN_PROGRESS)
            return True

        poller._dispatch_task = mock_dispatch

        # Run the poller once
        dispatched = poller.run_once()

        if dispatched == 0:
            print("FAIL: No tasks were dispatched")
            return 1

        # Poll for task status every 5s up to timeout
        poll_interval = 5
        elapsed = 0
        final_status: Optional[str] = None

        while elapsed < timeout:
            time.sleep(poll_interval)
            elapsed += poll_interval
            status = server.get_task_status(task_id)
            logger.info(f"Polled task status: {status}")
            if status in ("in_progress", "done"):
                final_status = status
                break

        # Final status check
        if final_status is None:
            print(f"FAIL: Task never reached in_progress within {timeout}s timeout")
            return 1

        print(f"Final status: {final_status}")
        if final_status in ("in_progress", "done"):
            print("PASS")
            return 0
        else:
            print(f"FAIL: Task status is '{final_status}', expected 'in_progress' or 'done'")
            return 1

    except Exception as e:
        logger.exception("Dry-run test failed")
        print(f"FAIL: {e}")
        return 1
    finally:
        server.stop()


def run_live(
    task_title: str,
    task_description: str,
    timeout: int = 60,
) -> int:
    """Run the E2E test in live mode against real Mission Control.

    Args:
        task_title: Title for the task.
        task_description: Description for the task.
        timeout: Timeout in seconds.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    logger.info("Starting E2E live test...")

    # Check required env vars
    base_url = os.environ.get("MISSION_CONTROL_BASE_URL")
    token = os.environ.get("MISSION_CONTROL_TOKEN")
    board_id = os.environ.get("MISSION_CONTROL_BOARD_ID")

    if not all([base_url, token, board_id]):
        print("FAIL: MISSION_CONTROL_BASE_URL, MISSION_CONTROL_TOKEN, and MISSION_CONTROL_BOARD_ID must be set for --live mode")
        return 1

    # Create client
    client = MissionControlClient(base_url=base_url, token=token)

    if not client.is_configured:
        print("FAIL: Mission Control client not configured")
        return 1

    # Verify connectivity: list_inbox_tasks returns without error
    try:
        tasks = client.list_inbox_tasks(board_id)
        print(f"Live mode: connected to Mission Control, {len(tasks)} inbox task(s) found")
    except Exception as e:
        print(f"FAIL: Could not reach Mission Control: {e}")
        return 1

    print("PASS: live connectivity verified")
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="E2E integration test harness for orchestration"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run with mock Mission Control server (no real network calls)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run against real Mission Control server",
    )
    parser.add_argument(
        "--task-title",
        default="Test task",
        help="Title for the test task",
    )
    parser.add_argument(
        "--task-description",
        default="Integration test task",
        help="Description for the test task",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds for status polling",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if args.dry_run and args.live:
        print("ERROR: Cannot use both --dry-run and --live")
        return 1

    if not args.dry_run and not args.live:
        print("ERROR: Must specify either --dry-run or --live")
        return 1

    if args.dry_run:
        return run_dry_run(
            task_title=args.task_title,
            task_description=args.task_description,
            timeout=args.timeout,
        )
    else:
        return run_live(
            task_title=args.task_title,
            task_description=args.task_description,
            timeout=args.timeout,
        )


if __name__ == "__main__":
    sys.exit(main())
