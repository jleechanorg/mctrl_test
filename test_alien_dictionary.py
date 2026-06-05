"""
Tests for Alien Dictionary (LeetCode #269)
"""

from __future__ import annotations

import pytest

from alien_dictionary import alien_order, alien_order_dfs


class TestAlienOrder:
    """Test cases for alien_order function."""

    def test_example_1(self):
        """Example from LeetCode: ["wrt","wrf","er","ett","rftt"] -> "wertf" """
        words = ["wrt", "wrf", "er", "ett", "rftt"]
        result = alien_order(words)
        assert result == "wertf"

    def test_example_2(self):
        """Example from LeetCode: ["z","x"] -> "zx" """
        words = ["z", "x"]
        result = alien_order(words)
        assert result == "zx"

    def test_example_3(self):
        """Example from LeetCode: ["z","x","z"] -> "" (cycle) """
        words = ["z", "x", "z"]
        result = alien_order(words)
        assert result == ""

    def test_empty_list(self):
        """Empty input should return empty string."""
        assert alien_order([]) == ""

    def test_single_word(self):
        """Single word should return its unique characters."""
        assert alien_order(["abc"]) == "abc"

    def test_two_words(self):
        """Simple two-word case."""
        assert alien_order(["ab", "ac"]) in ["abc", "acb"]

    def test_prefix_invalid(self):
        """Prefix case is invalid: ["abc", "ab"]"""
        words = ["abc", "ab"]
        result = alien_order(words)
        assert result == ""

    def test_three_letters_distinct_order(self):
        """Three letters with distinct ordering."""
        words = ["caa", "cbb", "cba", "cbb", "cba"]
        # This creates a cycle: c->a, c->b, but a and b conflict
        result = alien_order(["caa", "cbb", "cba"])
        # c comes before both a and b, a and b order is unclear

    def test_complex_case(self):
        """Complex case with multiple characters."""
        words = ["wnlb"]
        result = alien_order(words)
        assert set(result) == set("wnlb")

    def test_multiple_prefix_same(self):
        """Multiple words with same prefix."""
        words = ["a", "b", "a"]
        result = alien_order(words)
        assert result == ""

    def test_all_unique_first_letters(self):
        """All words start with different letters."""
        words = ["a", "b", "c", "d"]
        result = alien_order(words)
        assert result in ["abcd", "abdc", "acbd", "acdb", "adbc", "adcb",
                         "bacd", "badc", "bcad", "bcda", "bdac", "bdca",
                         "cabd", "cadb", "cbad", "cbda", "cdab", "cdba",
                         "dabc", "dacb", "dbac", "dbca", "dcab", "dcba"]

    def test_partial_ordering(self):
        """Partial ordering between characters."""
        words = ["abc", "abd", "aef", "aeg"]
        result = alien_order(words)
        # a comes first, then c/d vs e/g ordering
        assert result[0] == "a"
        # c and e (and d and g) need to maintain their relative orders

    def test_dfs_method(self):
        """Test the DFS-based solution gives same results."""
        test_cases = [
            ["wrt", "wrf", "er", "ett", "rftt"],
            ["z", "x"],
            ["z", "x", "z"],
            ["abc", "ab"],
            ["a", "b", "a"],
        ]

        for words in test_cases:
            bfs_result = alien_order(words)
            dfs_result = alien_order_dfs(words)
            assert bfs_result == dfs_result or (bfs_result == "" and dfs_result == "")


class TestAlienOrderEdgeCases:
    """Edge case tests."""

    def test_single_char_words(self):
        """All single character words."""
        words = ["a", "b", "c"]
        result = alien_order(words)
        assert len(result) == 3

    def test_duplicates_in_same_word(self):
        """Words with duplicate characters."""
        words = ["aa", "ab", "bb"]
        result = alien_order(words)
        assert result == "ab"

    def test_reverse_order(self):
        """Reverse alphabetical order."""
        words = ["c", "b", "a"]
        result = alien_order(words)
        assert result == "cba"

    def test_large_gap_ordering(self):
        """Characters with large gaps in ordering."""
        words = ["az", "ay"]
        result = alien_order(words)
        # a < z or a < y, but z and y relation unclear from single pair

    def test_consistent_ordering_abc(self):
        """Consistent ordering with abc pattern."""
        words = ["ac", "ab", "bb", "bc", "bc", "bc"]
        result = alien_order(words)
        # a < c from first pair
        # No relation between b and c from rest


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
