"""
Pytest-style tests for LeetCode Problem 97: Interleaving String
"""
import pytest
from interleaving_string import is_interleave


class TestIsInterleave:
    """Test cases for is_interleave function."""

    def test_basic_example(self):
        """Basic example from problem: aab + axy = aaxaby"""
        assert is_interleave("aab", "axy", "aaxaby") is True

    def test_not_interleaved(self):
        """Same chars but wrong order"""
        assert is_interleave("aab", "axy", "abaaxy") is False

    def test_empty_s1(self):
        """Only s2 is used"""
        assert is_interleave("", "abc", "abc") is True

    def test_empty_s2(self):
        """Only s1 is used"""
        assert is_interleave("abc", "", "abc") is True

    def test_both_empty(self):
        """Both strings empty"""
        assert is_interleave("", "", "") is True

    def test_both_empty_s3_not_empty(self):
        """Empty s1 and s2 but non-empty s3"""
        assert is_interleave("", "", "a") is False

    def test_different_lengths(self):
        """Length mismatch"""
        assert is_interleave("aab", "axy", "aaxab") is False

    def test_interleaved_order(self):
        """Correct interleaving with different chars"""
        assert is_interleave("abc", "def", "adbecf") is True

    def test_single_char_each_ab(self):
        """Single char each, 'ab' order"""
        assert is_interleave("a", "b", "ab") is True

    def test_single_char_each_ba(self):
        """Single char each, 'ba' order"""
        assert is_interleave("a", "b", "ba") is True

    def test_single_char_each_fail(self):
        """Single char each, duplicate in s3"""
        assert is_interleave("a", "b", "aa") is False

    def test_longer_strings_true(self):
        """Longer interleaved strings"""
        assert is_interleave("aabcc", "dbbca", "aadbbcbcac") is True

    def test_longer_strings_false(self):
        """Longer non-interleaved strings"""
        assert is_interleave("aabcc", "dbbca", "aadbbbaccc") is False

    def test_all_same_char(self):
        """All same characters"""
        assert is_interleave("aaa", "aaa", "aaaaaa") is True
        assert is_interleave("aaa", "aaa", "aaaaa") is False
