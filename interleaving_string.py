"""
LeetCode Problem 97: Interleaving String
Given strings s1, s2, and s3, determine if s3 is formed by interleaving s1 and s2.
"""


def is_interleave(s1: str, s2: str, s3: str) -> bool:
    """
    Determine if s3 is an interleaving of s1 and s2 using dynamic programming.

    dp[i][j] = True if s3[0:i+j] is an interleaving of s1[0:i] and s2[0:j]

    Time Complexity: O(m*n) where m = len(s1), n = len(s2)
    Space Complexity: O(m*n), can be optimized to O(min(m, n))
    """
    m, n = len(s1), len(s2)

    # Quick check: length must match
    if m + n != len(s3):
        return False

    # Base case: empty strings
    if m == 0:
        return s2 == s3
    if n == 0:
        return s1 == s3

    # dp[i][j] represents if s3[0:i+j] can be formed by interleaving s1[0:i] and s2[0:j]
    dp = [[False] * (n + 1) for _ in range(m + 1)]

    # Base case: empty s1 and empty s2
    dp[0][0] = True

    # Fill first row (using only s2)
    for j in range(1, n + 1):
        dp[0][j] = dp[0][j - 1] and s2[j - 1] == s3[j - 1]

    # Fill first column (using only s1)
    for i in range(1, m + 1):
        dp[i][0] = dp[i - 1][0] and s1[i - 1] == s3[i - 1]

    # Fill the rest of the table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            k = i + j - 1  # Index in s3
            # Either take from s1 or s2
            dp[i][j] = (dp[i - 1][j] and s1[i - 1] == s3[k]) or \
                       (dp[i][j - 1] and s2[j - 1] == s3[k])

    return dp[m][n]


# Test cases
if __name__ == "__main__":
    # Test 1: Basic example from problem
    assert is_interleave("aab", "axy", "aaxaby") == True, "Test 1 failed"

    # Test 2: Not interleaved
    assert is_interleave("aab", "axy", "abaaxy") == False, "Test 2 failed"

    # Test 3: Empty s1
    assert is_interleave("", "abc", "abc") == True, "Test 3 failed"

    # Test 4: Empty s2
    assert is_interleave("abc", "", "abc") == True, "Test 4 failed"

    # Test 5: Both empty
    assert is_interleave("", "", "") == True, "Test 5 failed"

    # Test 6: Both empty, s3 not empty
    assert is_interleave("", "", "a") == False, "Test 6 failed"

    # Test 7: Different lengths
    assert is_interleave("aab", "axy", "aaxab") == False, "Test 7 failed"

    # Test 8: Characters match but wrong order
    assert is_interleave("abc", "def", "adbecf") == True, "Test 8 failed"

    # Test 9: Single character each
    assert is_interleave("a", "b", "ab") == True, "Test 9 failed"
    assert is_interleave("a", "b", "ba") == True, "Test 10 failed"
    assert is_interleave("a", "b", "aa") == False, "Test 11 failed"

    # Test 12: Longer strings
    assert is_interleave("aabcc", "dbbca", "aadbbcbcac") == True, "Test 12 failed"
    assert is_interleave("aabcc", "dbbca", "aadbbbaccc") == False, "Test 13 failed"

    print("All tests passed!")
