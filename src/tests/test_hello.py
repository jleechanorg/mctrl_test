"""Tests for hello package."""
from __future__ import annotations

from hello import greet


def test_greet_default() -> None:
    assert greet() == "Hello, World!"


def test_greet_custom_name() -> None:
    assert greet("Alice") == "Hello, Alice!"


def test_greet_returns_string() -> None:
    assert isinstance(greet("Bob"), str)


def test_main_output(capsys) -> None:
    import hello
    hello.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, World!"
