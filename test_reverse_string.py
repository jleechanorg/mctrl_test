from __future__ import annotations

from reverse_string import reverse_string


def test_reverse_string_empty():
    """Verify reversing an empty string returns an empty string."""
    assert reverse_string("") == ""


def test_reverse_string_single_char():
    """Verify reversing a single character returns the same character."""
    assert reverse_string("a") == "a"


def test_reverse_string_palindrome():
    """Verify palindromes are unchanged when reversed."""
    assert reverse_string("racecar") == "racecar"


def test_reverse_string_hello():
    """Verify a typical word is reversed correctly."""
    assert reverse_string("hello") == "olleh"


def test_reverse_string_with_spaces():
    """Verify strings containing spaces are reversed correctly."""
    assert reverse_string("abc def") == "fed cba"
