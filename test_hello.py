from __future__ import annotations

from hello import farewell, hello


def test_hello_default():
    """Test hello function with default name."""
    assert hello() == "HELLO, WORLD!"


def test_hello_custom_name():
    """Test hello function with a custom name."""
    assert hello("Alice") == "HELLO, ALICE!"


def test_hello_returns_string():
    """Verify that hello function returns a string."""
    result = hello("test")
    assert isinstance(result, str)


def test_goodbye_default():
    """Test farewell function with default name."""
    assert farewell() == "Farewell, world!"


def test_goodbye_custom_name():
    """Test farewell function with a custom name."""
    assert farewell("Alice") == "Farewell, Alice!"
