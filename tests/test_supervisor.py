from __future__ import annotations

import importlib
import sys


def test_invalid_archive_after_days_falls_back_to_default(monkeypatch) -> None:
    monkeypatch.setenv("MCTRL_ARCHIVE_AFTER_DAYS", "seven")
    sys.modules.pop("orchestration.supervisor", None)

    supervisor = importlib.import_module("orchestration.supervisor")

    assert supervisor.ARCHIVE_AFTER_DAYS == 7
