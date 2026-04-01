"""
Valid Parentheses — LeetCode 20

Given a string s containing just '(', ')', '{', '}', '[' and ']',
determine if the input string is valid.
"""
from __future__ import annotations


def is_valid(s: str) -> bool:
    """Stack-based O(n) time, O(n) space."""
    pairs = {")": "(", "}": "{", "]": "["}
    stack: list[str] = []
    for ch in s:
        if ch in "({[":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        else:
            return False
    return len(stack) == 0
