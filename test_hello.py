from __future__ import annotations

from hello import goodbye, hello


def test_hello_default():
    assert hello() == "Hello, world!"


def test_hello_custom_name():
    assert hello("Alice") == "Hello, Alice!"


def test_hello_returns_string():
    result = hello("test")
    assert isinstance(result, str)


def test_goodbye_default():
    assert goodbye() == "Goodbye, world!"


def test_goodbye_custom_name():
    assert goodbye("Alice") == "Goodbye, Alice!"
