"""
LeetCode 140 - Word Break II (Hard)

Given a string s and a dictionary of strings wordDict, add spaces in s to construct a sentence
where each word is a valid dictionary word. Return all such possible sentences in any order.

Example:
Input: s = "catsanddog", wordDict = ["cat","cats","and","sand","dog"]
Output: ["cats and dog","cat sand dog"]

Time Complexity: O(n * 2^n) in worst case where n is string length
Space Complexity: O(n * 2^n) for storing all combinations
"""

from typing import List, Set, Dict


class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> List[str]:
        """
        Find all possible sentence combinations using memoization.
        
        Args:
            s: Input string to break
            wordDict: List of valid words
            
        Returns:
            List of all possible sentences
        """
        wordSet: Set[str] = set(wordDict)
        max_word_len = max(len(w) for w in wordDict) if wordDict else 0
        n = len(s)
        
        # Memoization: pos -> list of sentences from this position
        memo: Dict[int, List[str]] = {}
        
        def backtrack(start: int) -> List[str]:
            if start == n:
                return [""]
            
            if start in memo:
                return memo[start]
            
            result = []
            for end in range(start + 1, min(start + max_word_len + 1, n + 1)):
                word = s[start:end]
                if word in wordSet:
                    # Get all sentences from the rest of the string
                    rest = backtrack(end)
                    for sentence in rest:
                        if sentence:
                            result.append(word + " " + sentence)
                        else:
                            result.append(word)
            
            memo[start] = result
            return result
        
        return backtrack(0)


# Test cases
if __name__ == "__main__":
    sol = Solution()
    
    # Test case 1: Basic example
    s1 = "catsanddog"
    dict1 = ["cat", "cats", "and", "sand", "dog"]
    result1 = sol.wordBreak(s1, dict1)
    expected1 = {"cats and dog", "cat sand dog"}
    assert set(result1) == expected1, f"Test 1 failed: {result1}"
    
    # Test case 2: Multiple possibilities
    s2 = "pineapplepenapple"
    dict2 = ["apple", "pen", "applepen", "pine", "pineapple"]
    result2 = sol.wordBreak(s2, dict2)
    expected2 = {
        "pine apple pen apple",
        "pine applepen apple",
        "pineapple pen apple",
    }
    assert set(result2) == expected2, f"Test 2 failed: {result2}"
    
    # Test case 3: No valid segmentation
    s3 = "catsdog"
    dict3 = ["cat", "dog"]
    result3 = sol.wordBreak(s3, dict3)
    assert result3 == [], f"Test 3 failed: {result3}"
    
    # Test case 4: Single word
    s4 = "leetcode"
    dict4 = ["leet", "code"]
    result4 = sol.wordBreak(s4, dict4)
    expected4 = {"leet code"}
    assert set(result4) == expected4, f"Test 4 failed: {result4}"
    
    # Test case 5: Empty string
    s5 = ""
    dict5 = ["cat", "dog"]
    result5 = sol.wordBreak(s5, dict5)
    assert result5 == [""], f"Test 5 failed: {result5}"
    
    print("All tests passed!")
