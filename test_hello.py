from __future__ import annotations

from hello import hello


def test_hello_default():
    assert hello() == "Hello, world!"


def test_hello_custom_name():
    assert hello("Alice") == "Hello, Alice!"


def test_hello_returns_string():
    result = hello("test")
    assert isinstance(result, str)


def test_hello_preserves_punctuation():
    assert hello("mctrl-test!") == "Hello, mctrl-test!!"
