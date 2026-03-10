"""
Minimum Window Substring - LeetCode Hard Problem (76)

Given two strings s and t, return the minimum window in s which will contain all
the characters in t (including duplicates). If there is no such window in s that
covers all characters in t, return the empty string "".

This implementation uses the sliding window technique with character frequency tracking.

Time Complexity: O(|s| + |t|) where |s| is length of s and |t| is length of t
Space Complexity: O(|t|) for the character count dictionaries

The algorithm works as follows:
1. Use two pointers (left, right) to form a sliding window
2. Expand right to include characters until window contains all of t
3. Contract left to find the minimum window size
4. Repeat until right reaches the end of s
"""

from __future__ import annotations
from collections import Counter


def min_window(s: str, t: str) -> str:
    """
    Find the minimum window substring in s that contains all characters of t.

    Args:
        s: The source string to search in
        t: The target string containing required characters

    Returns:
        The minimum window substring, or empty string if none exists
    """
    if not s or not t:
        return ""

    # Character frequency of target string
    target_count = Counter(t)
    required_chars = len(target_count)

    # Sliding window pointers and state
    left = 0
    right = 0

    # Tracks how many unique characters in t are satisfied in current window
    formed = 0

    # Window character frequency
    window_counts: dict[str, int] = {}

    # Result tracking: (min_length, left, right)
    min_length = float('inf')
    result_left = 0
    result_right = 0

    while right < len(s):
        # Add character at right to window
        char = s[right]
        window_counts[char] = window_counts.get(char, 0) + 1

        # Check if this char satisfies a requirement
        if char in target_count and window_counts[char] == target_count[char]:
            formed += 1

        # Try to shrink window while it contains all required characters
        while formed == required_chars and left <= right:
            # Update minimum window if current is smaller
            current_length = right - left + 1
            if current_length < min_length:
                min_length = current_length
                result_left = left
                result_right = right

            # Remove character at left from window
            left_char = s[left]
            window_counts[left_char] -= 1

            # Check if removing this char breaks the requirement
            if left_char in target_count and window_counts[left_char] < target_count[left_char]:
                formed -= 1

            left += 1

        right += 1

    return "" if min_length == float('inf') else s[result_left:result_right + 1]


def min_window_brute_force(s: str, t: str) -> str:
    """
    Brute force approach (for testing comparison).

    Time Complexity: O(|s|^2 * |t|) - much slower
    Space Complexity: O(|t|)
    """
    if not s or not t:
        return ""

    target_count = Counter(t)

    result = ""

    for left in range(len(s)):
        for right in range(left, len(s)):
            window = s[left:right + 1]
            window_count = Counter(window)

            # Check if window contains all required chars
            if all(window_count[c] >= target_count[c] for c in target_count):
                if not result or len(window) < len(result):
                    result = window

    return result


# --- Helper functions for testing ---

def is_valid_window(s: str, t: str, window: str) -> bool:
    """
    Check if window contains all characters in t with correct frequencies.
    """
    if not window:
        return not t

    window_count = Counter(window)
    target_count = Counter(t)

    return all(window_count[c] >= target_count[c] for c in target_count)
