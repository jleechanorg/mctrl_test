"""
LeetCode 127 - Word Ladder (Hard)

Given two words, beginWord and endWord, and a dictionary wordList,
return the number of words in the shortest transformation sequence
from beginWord to endWord, or 0 if no such sequence exists.

Every adjacent pair of words differs by exactly one letter.
Every intermediate word must be in wordList.
"""

from collections import deque
from typing import List


def ladder_length(begin_word: str, end_word: str, word_list: List[str]) -> int:
    """BFS shortest path from begin_word to end_word changing one letter at a time."""
    word_set = set(word_list)
    if end_word not in word_set:
        return 0

    queue = deque([(begin_word, 1)])
    visited = {begin_word}

    while queue:
        word, depth = queue.popleft()
        for i in range(len(word)):
            for c in "abcdefghijklmnopqrstuvwxyz":
                next_word = word[:i] + c + word[i + 1:]
                if next_word == end_word:
                    return depth + 1
                if next_word in word_set and next_word not in visited:
                    visited.add(next_word)
                    queue.append((next_word, depth + 1))

    return 0
