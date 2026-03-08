"""Smoke test for run_e2e.py integration harness.

This test bridges the unit test suite and the integration harness
by running run_e2e.py --dry-run and verifying it passes.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


class TestRunE2ESmoke:
    """Smoke test for E2E harness."""

    def test_run_e2e_dry_run_passes(self):
        """run_e2e.py --dry-run exits 0 and prints PASS."""
        result = subprocess.run(
            [sys.executable, "src/integration/run_e2e.py", "--dry-run"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0, (
            f"Expected exit code 0, got {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "PASS" in result.stdout, (
            f"Expected 'PASS' in output.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
