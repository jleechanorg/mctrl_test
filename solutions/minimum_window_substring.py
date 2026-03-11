"""LeetCode #76 - Minimum Window Substring (Hard)

Given two strings s and t of lengths m and n respectively, return the minimum
window substring of s such that every character in t (including duplicates)
is included in the window. If there is no such window, return "".

Time complexity: O(m + n). Space complexity: O(m + n).
"""
from __future__ import annotations

from collections import Counter


def min_window(s: str, t: str) -> str:
    if not t or not s:
        return ""

    need = Counter(t)
    required = len(need)  # number of unique chars we need
    formed = 0            # unique chars in current window at desired frequency

    window_counts: dict[str, int] = {}
    best = (float("inf"), 0, 0)  # (length, left, right)

    left = 0
    for right, char in enumerate(s):
        window_counts[char] = window_counts.get(char, 0) + 1

        if char in need and window_counts[char] == need[char]:
            formed += 1

        # Contract the window from the left
        while formed == required:
            length = right - left + 1
            if length < best[0]:
                best = (length, left, right)

            left_char = s[left]
            window_counts[left_char] -= 1
            if left_char in need and window_counts[left_char] < need[left_char]:
                formed -= 1
            left += 1

    return "" if best[0] == float("inf") else s[best[1]: best[2] + 1]
