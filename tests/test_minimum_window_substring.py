"""Tests for LeetCode #76 - Minimum Window Substring."""
from solutions.minimum_window_substring import min_window


class TestMinimumWindowSubstring:
    def test_example1(self) -> None:
        assert min_window("ADOBECODEBANC", "ABC") == "BANC"

    def test_example2(self) -> None:
        assert min_window("a", "a") == "a"

    def test_no_valid_window(self) -> None:
        assert min_window("a", "aa") == ""

    def test_empty_s(self) -> None:
        assert min_window("", "A") == ""

    def test_empty_t(self) -> None:
        assert min_window("ABC", "") == ""

    def test_t_equals_s(self) -> None:
        assert min_window("abc", "abc") == "abc"

    def test_single_char_match(self) -> None:
        assert min_window("abcdef", "d") == "d"

    def test_duplicates_in_t(self) -> None:
        assert min_window("aaabbbccc", "abc") == "abbbc"

    def test_whole_string_needed(self) -> None:
        assert min_window("ab", "ba") == "ab"

    def test_multiple_valid_windows(self) -> None:
        # "bca" at index 5-7 is length 3, smallest
        result = min_window("adobecabcbanc", "abc")
        assert len(result) == 3
        # The result should contain all of a, b, c
        assert "a" in result and "b" in result and "c" in result
