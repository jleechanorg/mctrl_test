"""
Test suite for Minimum Window Substring (LeetCode 76)

Comprehensive edge case coverage including:
- Standard cases
- Edge cases with empty strings
- Single character strings
- Duplicate characters in t
- No valid window
- Window equals t
- Window equals s
- All same characters
- Various character types (uppercase, lowercase, special chars)
"""

import pytest
from minimum_window_substring import min_window, min_window_brute_force, is_valid_window


class TestMinWindowSubstring:
    """Test cases for min_window function."""

    # --- Standard test cases from LeetCode ---

    def test_standard_case_1(self):
        """Standard case: s = 'ADOBECODEBANC', t = 'ABC'"""
        s = "ADOBECODEBANC"
        t = "ABC"
        result = min_window(s, t)
        assert result == "BANC"
        assert is_valid_window(s, t, result)

    def test_standard_case_2(self):
        """Standard case: s = 'a', t = 'a'"""
        s = "a"
        t = "a"
        result = min_window(s, t)
        assert result == "a"
        assert is_valid_window(s, t, result)

    def test_standard_case_3(self):
        """Standard case: s = 'a', t = 'aa'"""
        s = "a"
        t = "aa"
        result = min_window(s, t)
        assert result == ""
        # Empty result is correct when t cannot be formed from s

    # --- Edge cases: empty strings ---

    def test_empty_s(self):
        """Edge case: empty source string"""
        s = ""
        t = "ABC"
        result = min_window(s, t)
        assert result == ""

    def test_empty_t(self):
        """Edge case: empty target string"""
        s = "ADOBECODEBANC"
        t = ""
        result = min_window(s, t)
        assert result == ""

    def test_both_empty(self):
        """Edge case: both strings empty"""
        s = ""
        t = ""
        result = min_window(s, t)
        assert result == ""

    # --- Edge cases: single character ---

    def test_single_char_s_single_char_t_match(self):
        """Single char in s matches single char in t"""
        s = "a"
        t = "a"
        result = min_window(s, t)
        assert result == "a"

    def test_single_char_s_single_char_t_no_match(self):
        """Single char in s doesn't match t"""
        s = "a"
        t = "b"
        result = min_window(s, t)
        assert result == ""

    def test_long_s_single_char_t(self):
        """Long s with single char t at end"""
        s = "abcdefghijklmnopqrstuvwxyz"
        t = "z"
        result = min_window(s, t)
        assert result == "z"
        assert is_valid_window(s, t, result)

    # --- Duplicate characters in t ---

    def test_duplicates_in_t(self):
        """t contains duplicate characters"""
        s = "AAABBBCCC"
        t = "AB"
        result = min_window(s, t)
        assert result == "AB"
        assert is_valid_window(s, t, result)

    def test_multiple_duplicates_in_t(self):
        """t contains multiple duplicates"""
        s = "AAABAAABBBCC"
        t = "AAB"
        result = min_window(s, t)
        # Minimum window should contain at least 2 As and 1 B
        assert is_valid_window(s, t, result)
        assert len(result) <= 4  # Should be at most "AAB" or "AAB"

    def test_all_same_chars_t(self):
        """All characters in t are the same"""
        s = "AAABBBCCCAAA"
        t = "AAA"
        result = min_window(s, t)
        assert result == "AAA"
        assert is_valid_window(s, t, result)

    # --- No valid window ---

    def test_no_valid_window(self):
        """s doesn't contain any character from t"""
        s = "abcdef"
        t = "xyz"
        result = min_window(s, t)
        assert result == ""

    def test_no_valid_window_partial(self):
        """s contains some but not all characters from t"""
        s = "abc"
        t = "abcd"
        result = min_window(s, t)
        assert result == ""

    # --- Window equals t or s ---

    def test_window_equals_t(self):
        """Minimum window is exactly t"""
        s = "XYZABCXYZ"
        t = "ABC"
        result = min_window(s, t)
        assert result in ["ABC", "ABCX", "XABC", "ABCZ", "ZABC"]
        assert is_valid_window(s, t, result)

    def test_window_equals_s(self):
        """Minimum window is entire s"""
        s = "ABC"
        t = "ABC"
        result = min_window(s, t)
        assert result == "ABC"
        assert is_valid_window(s, t, result)

    def test_s_contains_t_at_beginning(self):
        """t appears at the beginning of s"""
        s = "ABCDEFGHIJ"
        t = "ABC"
        result = min_window(s, t)
        assert result == "ABC"
        assert is_valid_window(s, t, result)

    def test_s_contains_t_at_end(self):
        """t appears at the end of s"""
        s = "XYZABC"
        t = "ABC"
        result = min_window(s, t)
        assert result == "ABC"
        assert is_valid_window(s, t, result)

    # --- Various character types ---

    def test_uppercase_only(self):
        """Both strings contain only uppercase letters"""
        s = "ABCDEFABC"
        t = "ABC"
        result = min_window(s, t)
        assert result == "ABC"
        assert is_valid_window(s, t, result)

    def test_lowercase_only(self):
        """Both strings contain only lowercase letters"""
        s = "abcdefabc"
        t = "abc"
        result = min_window(s, t)
        assert result == "abc"
        assert is_valid_window(s, t, result)

    def test_mixed_case(self):
        """Mixed case letters"""
        s = "aBcDeFbAc"
        t = "BcA"
        result = min_window(s, t)
        # Should find a window with B, c, A (case-sensitive)
        assert is_valid_window(s, t, result)

    def test_special_characters(self):
        """Strings contain special characters"""
        s = "@#$%@#$%ABC"
        t = "@#$"
        result = min_window(s, t)
        assert is_valid_window(s, t, result)

    def test_numbers_in_strings(self):
        """Strings contain numbers"""
        s = "12345ABC123"
        t = "123"
        result = min_window(s, t)
        assert result == "123"
        assert is_valid_window(s, t, result)

    # --- Long strings ---

    def test_long_s(self):
        """Long source string"""
        s = "A" * 10000 + "BCD" + "A" * 10000
        t = "BCD"
        result = min_window(s, t)
        assert result == "BCD"
        assert is_valid_window(s, t, result)

    # --- Complexity/performance validation ---

    def test_correctness_against_brute_force(self):
        """Verify algorithm against brute force for small inputs"""
        test_cases = [
            ("ADOBECODEBANC", "ABC"),
            ("a", "a"),
            ("a", "aa"),
            ("ABC", "ABC"),
            ("ABC", "ABCD"),
            ("AAABBBCCC", "AB"),
            ("XYZABCXYZ", "ABC"),
            ("abcdef", "xyz"),
            ("abcabcbb", "abc"),
            ("bbbbbb", "b"),
        ]

        for s, t in test_cases:
            expected = min_window_brute_force(s, t)
            result = min_window(s, t)
            # Both should be valid windows (might have multiple valid answers)
            # Only validate non-empty results
            if result:
                assert is_valid_window(s, t, result), f"Failed for s={s}, t={t}"
            if expected:
                assert len(result) == len(expected), f"Length mismatch for s={s}, t={t}"


class TestIsValidWindow:
    """Test cases for helper function is_valid_window."""

    def test_valid_full_match(self):
        """Window contains all chars in t"""
        assert is_valid_window("ADOBECODEBANC", "ABC", "BANC") is True

    def test_valid_partial_match(self):
        """Window contains extra chars but all required"""
        assert is_valid_window("ADOBECODEBANC", "ABC", "ADOBEC") is True

    def test_invalid_missing_char(self):
        """Window missing a required character"""
        assert is_valid_window("ADOBECODEBANC", "ABC", "BAN") is False

    def test_invalid_insufficient_count(self):
        """Window has insufficient count of a character"""
        assert is_valid_window("ADOBECODEBANC", "ABC", "AB") is False

    def test_empty_window_empty_t(self):
        """Empty window with empty t"""
        assert is_valid_window("ABC", "", "") is True

    def test_empty_window_nonempty_t(self):
        """Empty window with non-empty t"""
        assert is_valid_window("ABC", "D", "") is False

    def test_window_with_duplicates(self):
        """Window has more than required count"""
        assert is_valid_window("AAA", "A", "AA") is True
        assert is_valid_window("AAA", "A", "AAA") is True
