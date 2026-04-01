"""Unit tests for Valid Parentheses (LeetCode 20)."""
from valid_parentheses import valid_parentheses


class TestValidParentheses:
    def test_example_1(self) -> None:
        assert valid_parentheses("()") is True

    def test_example_2(self) -> None:
        assert valid_parentheses("()[]{}") is True

    def test_example_3(self) -> None:
        assert valid_parentheses("(]") is False

    def test_nested(self) -> None:
        assert valid_parentheses("{[]}") is True

    def test_empty(self) -> None:
        assert valid_parentheses("") is True

    def test_single_open(self) -> None:
        assert valid_parentheses("(") is False

    def test_interleaved_invalid(self) -> None:
        assert valid_parentheses("([)]") is False

    def test_non_bracket_character_invalid(self) -> None:
        assert valid_parentheses("(a)") is False
