from __future__ import annotations

from pathlib import Path

from hello import hello


def test_hello_default():
    assert hello() == "Hello, world!"


def test_hello_custom_name():
    assert hello("Alice") == "Hello, Alice!"


def test_hello_returns_string():
    result = hello("test")
    assert isinstance(result, str)


def test_smoke_doc_exists():
    doc = Path(__file__).parent / "docs" / "mctrl_smoke_test.md"
    assert doc.exists(), f"Expected {doc} to exist"
    assert "bead rev-2yn" in doc.read_text()
