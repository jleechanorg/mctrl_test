"""Unit tests for Valid Parentheses (LeetCode 20)."""
from valid_parentheses import is_valid


class TestValidParentheses:
    def test_example_1(self) -> None:
        assert is_valid("()") is True

    def test_example_2(self) -> None:
        assert is_valid("()[]{}") is True

    def test_example_3(self) -> None:
        assert is_valid("(]") is False

    def test_nested(self) -> None:
        assert is_valid("{[]}") is True

    def test_empty(self) -> None:
        assert is_valid("") is True

    def test_single_open(self) -> None:
        assert is_valid("(") is False

    def test_interleaved_invalid(self) -> None:
        assert is_valid("([)]") is False
