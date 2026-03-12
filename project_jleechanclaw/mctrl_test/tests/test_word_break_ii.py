"""Tests for Word Break II solution."""

import pytest
from src.word_break_ii import Solution


class TestWordBreakII:
    def setup_method(self):
        self.sol = Solution()
    
    def test_basic_example(self):
        """Test the basic example from LeetCode."""
        s = "catsanddog"
        wordDict = ["cat", "cats", "and", "sand", "dog"]
        result = self.sol.wordBreak(s, wordDict)
        expected = {"cats and dog", "cat sand dog"}
        assert set(result) == expected
    
    def test_example_2(self):
        """Test the second example from LeetCode."""
        s = "pineapplepenapple"
        wordDict = ["apple", "pen", "applepen", "pine", "pineapple"]
        result = self.sol.wordBreak(s, wordDict)
        expected = {
            "pine apple pen apple",
            "pine applepen apple",
            "pineapple pen apple",
        }
        assert set(result) == expected
    
    def test_no_valid_segmentation(self):
        """Test when no valid segmentation exists."""
        s = "catsdog"
        wordDict = ["cat", "dog"]
        result = self.sol.wordBreak(s, wordDict)
        assert result == []
    
    def test_single_word_pair(self):
        """Test with a single valid word pair."""
        s = "leetcode"
        wordDict = ["leet", "code"]
        result = self.sol.wordBreak(s, wordDict)
        expected = {"leet code"}
        assert set(result) == expected
    
    def test_empty_string(self):
        """Test with empty string."""
        s = ""
        wordDict = ["cat", "dog"]
        result = self.sol.wordBreak(s, wordDict)
        assert result == [""]
    
    def test_repeated_words(self):
        """Test with repeated words in dictionary."""
        s = "aaab"
        wordDict = ["a", "aa", "ab"]
        result = self.sol.wordBreak(s, wordDict)
        # All valid combinations
        assert len(result) > 0
        # Verify each result is valid
        for sentence in result:
            words = sentence.split()
            reconstructed = "".join(words)
            assert reconstructed == s
    
    def test_all_single_chars(self):
        """Test when dictionary contains all single characters."""
        s = "abcd"
        wordDict = ["a", "b", "c", "d"]
        result = self.sol.wordBreak(s, wordDict)
        assert len(result) == 1
        assert result[0] == "a b c d"
    
    def test_overlapping_words(self):
        """Test with overlapping word options."""
        s = "cats"
        wordDict = ["cat", "cats", "s"]
        result = self.sol.wordBreak(s, wordDict)
        expected = {"cat s", "cats"}
        assert set(result) == expected
    
    def test_large_gap(self):
        """Test with large gap that can't be filled."""
        s = "abcd"
        wordDict = ["ab", "cd"]
        result = self.sol.wordBreak(s, wordDict)
        expected = {"ab cd"}
        assert set(result) == expected
    
    def test_dict_not_used_fully(self):
        """Test when dictionary contains unused words."""
        s = "neet"
        wordDict = ["neet", "code", "Interview"]
        result = self.sol.wordBreak(s, wordDict)
        expected = {"neet"}
        assert set(result) == expected
    
    def test_three_words(self):
        """Test with exactly three words in result."""
        s = "blackcat"
        wordDict = ["black", "cat", "c", "at", "blackcat"]
        result = self.sol.wordBreak(s, wordDict)
        # Should have "black c at", "black cat", "blackcat"
        assert len(result) >= 1
        for sentence in result:
            words = sentence.split()
            reconstructed = "".join(words)
            assert reconstructed == s
    
    def test_complex_case(self):
        """Test a more complex case."""
        s = "catsanddog"
        wordDict = ["cat", "cats", "and", "sand", "dog"]
        result = self.sol.wordBreak(s, wordDict)
        assert len(result) == 2
