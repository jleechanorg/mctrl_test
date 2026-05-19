from __future__ import annotations

from reverse_string import reverse_string


def test_reverse_string_empty():
    assert reverse_string("") == ""


def test_reverse_string_single_char():
    assert reverse_string("a") == "a"


def test_reverse_string_palindrome():
    assert reverse_string("racecar") == "racecar"


def test_reverse_string_hello():
    assert reverse_string("hello") == "olleh"


def test_reverse_string_with_spaces():
    assert reverse_string("abc def") == "fed cba"
