"""Tests for app.py."""
from __future__ import annotations

import subprocess
import sys

from app import greet


def test_greet_default() -> None:
    assert greet() == "Hello, World!"


def test_greet_custom_name() -> None:
    assert greet("Alice") == "Hello, Alice!"


def test_greet_returns_string() -> None:
    assert isinstance(greet("Bob"), str)


def test_main_output(capsys) -> None:
    import app
    app.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, World!"


def test_module_runs_as_script() -> None:
    result = subprocess.run(
        [sys.executable, "app.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "Hello, World!"
