from __future__ import annotations

from hello import farewell, hello


def test_hello_default():
    assert hello() == "HELLO, WORLD!"


def test_hello_custom_name():
    assert hello("Alice") == "HELLO, ALICE!"


def test_hello_returns_string():
    result = hello("test")
    assert isinstance(result, str)


def test_goodbye_default():
    assert farewell() == "Farewell, world!"


def test_goodbye_custom_name():
    assert farewell("Alice") == "Farewell, Alice!"
