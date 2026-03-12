"""
LeetCode Problem 10: Regular Expression Matching
Dynamic Programming Solution

Given an input string s and a pattern p, implement regular expression matching
with support for '.' and '*' where:
- '.' matches any single character
- '*' matches zero or more of the preceding element
"""


def is_match(s: str, p: str) -> bool:
    """
    Check if string s matches pattern p using dynamic programming.

    DP approach: dp[i][j] = True if s[i:] matches p[j:]

    Time Complexity: O(m * n) where m = len(s), n = len(p)
    Space Complexity: O(m * n)

    Args:
        s: Input string (1 <= len(s) <= 20)
        p: Pattern string (1 <= len(p) <= 20)

    Returns:
        True if s matches pattern p, False otherwise
    """
    m, n = len(s), len(p)

    # dp[i][j] = does s[i:] match p[j:]?
    dp = [[False] * (n + 1) for _ in range(m + 1)]

    # Empty string matches empty pattern
    dp[m][n] = True

    # Handle patterns ending with '*' at the start (empty string case)
    for j in range(n - 1):
        if p[j + 1] == '*':
            dp[m][j] = dp[m][j + 2]

    # Fill dp table
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            first_match = (p[j] == s[i] or p[j] == '.')

            if j + 1 < n and p[j + 1] == '*':
                # Two cases:
                # 1. Skip "char*" pattern (zero occurrences)
                # 2. Use "char*" pattern if first_match and match remaining
                dp[i][j] = dp[i][j + 2] or (first_match and dp[i + 1][j])
            else:
                # Normal match: both characters must match and rest must match
                dp[i][j] = first_match and dp[i + 1][j + 1]

    return dp[0][0]


if __name__ == "__main__":
    # Test cases
    test_cases = [
        # Basic cases
        ("aa", "a*", True),
        ("aa", "a", False),
        ("ab", ".*", True),
        ("aab", "c*a*b", True),

        # Edge cases
        ("", "", True),
        ("", "a*", True),  # zero occurrences
        ("a", "", False),
        ("a", "a", True),
        ("a", ".", True),
        ("a", "aa", False),

        # Dot cases
        ("ab", "a.", True),
        ("abc", "...", True),
        ("abcd", "...", False),

        # Star edge cases
        ("", ".*", True),  # zero of any char
        ("abc", ".*c", True),
        ("abc", "a*bc", True),
        ("abc", "a*.*", True),

        # Complex patterns
        ("aaa", "a*a", True),
        ("aaa", "ab*a*c*a", True),
        ("a", "ab*", True),

        # False cases
        ("aaa", "ab*a*c", False),
        ("a", "aa", False),
        ("a", ".", True),
    ]

    print("Running tests...")
    for s, p, expected in test_cases:
        result = is_match(s, p)
        status = "✓" if result == expected else "✗"
        print(f"{status} is_match('{s}', '{p}') = {result} (expected: {expected})")

    print("\nAll tests completed.")
