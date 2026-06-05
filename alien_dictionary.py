"""
Alien Dictionary (LeetCode #269)

There is a new alien language that uses the English alphabet. However, the order
among the letters is unknown to you. You are given a list of strings `words`
from this alien language dictionary. The strings in the dictionary are sorted
lexicographically based on the rules of this new language.

Return a string of the unique letters in the new alien language sorted in
lexicographically increasing order. If there is no valid alien dictionary,
return an empty string.

Approach:
---------
This problem can be solved using topological sorting (Kahn's algorithm or DFS):

1. Build a directed graph of character dependencies from adjacent word pairs
2. Detect cycles (invalid dictionary)
3. Perform topological sort to get the correct order

Time Complexity: O(C) where C is total characters across all words
Space Complexity: O(1) - at most 26 nodes in the graph
"""

from __future__ import annotations

from collections import defaultdict, deque


def alien_order(words: list[str]) -> str:
    """
    Determine the alien dictionary order from given sorted words.

    Args:
        words: List of words sorted in alien dictionary order

    Returns:
        String of unique letters in alien dictionary order,
        or empty string if invalid

    Example:
        >>> alien_order(["wrt", "wrf", "er", "ett", "rftt"])
        "wertf"
    """
    if not words:
        return ""

    # Build graph: character -> set of characters that come after it
    graph: dict[str, set[str]] = defaultdict(set)
    in_degree: dict[str, int] = defaultdict(int)

    # Initialize all characters with 0 in-degree
    for word in words:
        for char in word:
            in_degree[char] = 0

    # Build edges from adjacent word pairs
    for i in range(len(words) - 1):
        word1, word2 = words[i], words[i + 1]

        # Check if word1 is prefix of word2 - valid ordering
        # or word2 is prefix of word1 - invalid ordering
        if word1.startswith(word2) and len(word1) > len(word2):
            return ""

        # Find first differing character
        min_len = min(len(word1), len(word2))
        for j in range(min_len):
            if word1[j] != word2[j]:
                # word1[j] comes before word2[j] in alien order
                if word2[j] not in graph[word1[j]]:
                    graph[word1[j]].add(word2[j])
                    in_degree[word2[j]] += 1
                break

    # Topological sort using Kahn's algorithm (BFS)
    # Start with characters that have no incoming edges
    queue = deque([char for char in in_degree if in_degree[char] == 0])
    result = []

    while queue:
        char = queue.popleft()
        result.append(char)

        for neighbor in graph[char]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # If result doesn't contain all characters, there's a cycle
    if len(result) != len(in_degree):
        return ""

    return "".join(result)


# Alternative DFS-based solution
def alien_order_dfs(words: list[str]) -> str:
    """
    Alternative solution using DFS-based topological sort.
    """
    if not words:
        return ""

    # Build graph
    graph: dict[str, set[str]] = defaultdict(set)

    for i in range(len(words) - 1):
        word1, word2 = words[i], words[i + 1]
        min_len = min(len(word1), len(word2))

        if len(word1) > min_len and word1[:min_len] == word2[:min_len]:
            # word1 is longer and has same prefix as word2 - invalid
            return ""

        for j in range(min_len):
            if word1[j] != word2[j]:
                graph[word1[j]].add(word2[j])
                break

    # All characters
    chars = set()
    for word in words:
        chars.update(word)

    # DFS with visited states: 0=unvisited, 1=visiting, 2=visited
    visited: dict[str, int] = {c: 0 for c in chars}
    result: list[str] = []

    def dfs(char: str) -> bool:
        """Returns True if cycle detected (invalid)."""
        visited[char] = 1  # Mark as visiting

        for neighbor in graph.get(char, []):
            if visited[neighbor] == 1:  # Back edge - cycle
                return True
            if visited[neighbor] == 0:
                if dfs(neighbor):
                    return True

        visited[char] = 2  # Mark as visited
        result.append(char)
        return False

    # Process all characters
    for char in chars:
        if visited[char] == 0:
            if dfs(char):
                return ""

    return "".join(reversed(result))


if __name__ == "__main__":
    # Test examples
    test_cases = [
        (["wrt", "wrf", "er", "ett", "rftt"], "wertf"),
        (["z", "x"], "zx"),
        (["z", "x", "z"], ""),
        (["abc", "ab"], ""),
        (["a", "b", "a"], ""),
        (["aac", "aab", "aacx"], "cabx"),
    ]

    print("Testing alien_order:")
    for words, expected in test_cases:
        result = alien_order(words)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {words} -> {result} (expected: {expected})")
