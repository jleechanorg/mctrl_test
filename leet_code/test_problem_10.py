"""
Test cases for LeetCode Problem 10: Regular Expression Matching
"""
import pytest
from problem_10_regex_match import is_match


class TestIsMatch:
    """Test cases for is_match function."""

    # Basic pattern matching
    def test_basic_match_star(self):
        assert is_match("aa", "a*") is True

    def test_basic_no_match(self):
        assert is_match("aa", "a") is False

    def test_dot_star_matches_all(self):
        assert is_match("ab", ".*") is True

    def test_star_can_repeat_previous(self):
        assert is_match("aab", "c*a*b") is True

    # Edge cases
    def test_empty_string_empty_pattern(self):
        assert is_match("", "") is True

    def test_empty_string_star_pattern(self):
        assert is_match("", "a*") is True

    def test_nonempty_empty_pattern(self):
        assert is_match("a", "") is False

    def test_exact_match(self):
        assert is_match("a", "a") is True

    def test_dot_matches_any(self):
        assert is_match("a", ".") is True

    def test_no_match_different_lengths(self):
        assert is_match("a", "aa") is False

    # Dot (.) tests
    def test_dot_single_char(self):
        assert is_match("ab", "a.") is True

    def test_dot_multiple_chars(self):
        assert is_match("abc", "...") is True

    def test_dot_not_enough_chars(self):
        assert is_match("abcd", "...") is False

    # Star (*) edge cases
    def test_dot_star_empty_string(self):
        assert is_match("", ".*") is True

    def test_dot_star_any_chars(self):
        assert is_match("abc", ".*c") is True

    def test_char_star_match(self):
        assert is_match("abc", "a*bc") is True

    def test_char_star_dot_star(self):
        assert is_match("abc", "a*.*") is True

    # Complex patterns
    def test_multiple_stars(self):
        assert is_match("aaa", "a*a") is True

    def test_complex_pattern(self):
        assert is_match("aaa", "ab*a*c*a") is True

    def test_char_star_at_end(self):
        assert is_match("a", "ab*") is True

    # False cases
    def test_pattern_too_long(self):
        assert is_match("aaa", "ab*a*c") is False

    def test_exact_no_match(self):
        assert is_match("a", "aa") is False
