from __future__ import annotations

import importlib
import sys
from unittest.mock import MagicMock


def test_invalid_archive_after_days_falls_back_to_default(monkeypatch) -> None:
    monkeypatch.setenv("MCTRL_ARCHIVE_AFTER_DAYS", "seven")
    sys.modules.pop("orchestration.supervisor", None)

    supervisor = importlib.import_module("orchestration.supervisor")

    assert supervisor.ARCHIVE_AFTER_DAYS == 7


def test_invalid_outbox_alert_env_falls_back_to_defaults(monkeypatch) -> None:
    monkeypatch.setenv("MCTRL_OUTBOX_ALERT_THRESHOLD", "many")
    monkeypatch.setenv("MCTRL_OUTBOX_AGE_ALERT_SECONDS", "old")
    monkeypatch.setenv("MCTRL_OUTBOX_ALERT_COOLDOWN_SECONDS", "someday")
    sys.modules.pop("orchestration.supervisor", None)

    supervisor = importlib.import_module("orchestration.supervisor")

    assert supervisor.OUTBOX_ALERT_THRESHOLD == 10
    assert supervisor.OUTBOX_AGE_ALERT_SECONDS == 3600
    assert supervisor.OUTBOX_ALERT_COOLDOWN_SECONDS == 3600


def test_outbox_alert_cooldown_suppresses_repeat_alerts(monkeypatch) -> None:
    sys.modules.pop("orchestration.supervisor", None)
    supervisor = importlib.import_module("orchestration.supervisor")
    supervisor._last_outbox_alert_at = 0.0
    alert = MagicMock(return_value=True)

    monkeypatch.setattr(supervisor, "time", MagicMock(monotonic=MagicMock(return_value=10_000.0)))

    fired_first = supervisor.maybe_alert_outbox_health(
        pending_count=20,
        dead_letter_count=0,
        oldest_age_seconds=8000,
        notify_fn=alert,
        threshold=10,
        age_threshold=3600,
        cooldown_seconds=3600,
    )
    fired_second = supervisor.maybe_alert_outbox_health(
        pending_count=21,
        dead_letter_count=0,
        oldest_age_seconds=8100,
        notify_fn=alert,
        threshold=10,
        age_threshold=3600,
        cooldown_seconds=3600,
    )

    assert fired_first is True
    assert fired_second is False
    assert alert.call_count == 1


def test_first_outbox_alert_bypasses_cooldown(monkeypatch) -> None:
    sys.modules.pop("orchestration.supervisor", None)
    supervisor = importlib.import_module("orchestration.supervisor")
    supervisor._last_outbox_alert_at = None
    alert = MagicMock(return_value=True)
    monkeypatch.setattr(supervisor, "time", MagicMock(monotonic=MagicMock(return_value=5.0)))

    fired = supervisor.maybe_alert_outbox_health(
        pending_count=50,
        dead_letter_count=0,
        oldest_age_seconds=7200,
        notify_fn=alert,
        threshold=10,
        age_threshold=3600,
        cooldown_seconds=3600,
    )

    assert fired is True
    assert alert.call_count == 1


def test_outbox_alert_fires_when_dead_letter_present(monkeypatch) -> None:
    sys.modules.pop("orchestration.supervisor", None)
    supervisor = importlib.import_module("orchestration.supervisor")
    supervisor._last_outbox_alert_at = 0.0
    alert = MagicMock(return_value=True)
    monkeypatch.setattr(supervisor, "time", MagicMock(monotonic=MagicMock(return_value=1000.0)))

    fired = supervisor.maybe_alert_outbox_health(
        pending_count=0,
        dead_letter_count=1,
        oldest_age_seconds=None,
        notify_fn=alert,
        threshold=10,
        age_threshold=3600,
        cooldown_seconds=10,
    )

    assert fired is True
    assert alert.call_count == 1
