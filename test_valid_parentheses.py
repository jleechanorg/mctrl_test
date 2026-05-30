"""Unit tests for Valid Parentheses (LeetCode 20)."""
from valid_parentheses import valid_parentheses


class TestValidParentheses:
    def test_example_1(self) -> None:
        """Test valid_parentheses with simple matching parentheses."""
        assert valid_parentheses("()") is True

    def test_example_2(self) -> None:
        """Test valid_parentheses with multiple matching bracket types."""
        assert valid_parentheses("()[]{}") is True

    def test_example_3(self) -> None:
        """Test valid_parentheses with mismatching bracket types."""
        assert valid_parentheses("(]") is False

    def test_nested(self) -> None:
        """Test valid_parentheses with nested matching brackets."""
        assert valid_parentheses("{[]}") is True

    def test_empty(self) -> None:
        """Test valid_parentheses with an empty string."""
        assert valid_parentheses("") is True

    def test_single_open(self) -> None:
        """Test valid_parentheses with a single opening bracket."""
        assert valid_parentheses("(") is False

    def test_interleaved_invalid(self) -> None:
        """Test valid_parentheses with interleaved mismatching brackets."""
        assert valid_parentheses("([)]") is False

    def test_non_bracket_character_invalid(self) -> None:
        """Verify that non-bracket characters make the input invalid."""
        assert valid_parentheses("(a)") is False
