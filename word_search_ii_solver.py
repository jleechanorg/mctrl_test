"""
Word Search II - LeetCode Hard Problem Solver

Problem Statement:
Given an m x n board of characters and a list of strings words, return all words
from the list that can be formed by letters of sequentially adjacent cells.

The same cell may not be used more than once in a word. Adjacent cells are those
horizontally or vertically neighboring. The returned words should be in sorted
alphabetical order.

Example 1:
Input: board = [
    ['o','a','a','n'],
    ['e','t','a','e'],
    ['i','h','k','r'],
    ['i','f','l','v']
]
words = ["oath","pea","eat","rain"]
Output: ["eat","oath"]

Example 2:
Input: board = [
    ['a','b'],
    ['c','d']
]
words = ["abcd","acdb","ade","adb","abc"]
Output: ["adb"]

This module provides:
1. Baseline solver: DFS for each word (slower)
2. Trie-based optimized solver (faster)
3. Helper utilities for board formatting and random test case generation
"""

from __future__ import annotations

import random
from typing import Optional


# =============================================================================
# TRIE IMPLEMENTATION
# =============================================================================

class TrieNode:
    """A node in the Trie data structure."""

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.word: Optional[str] = None  # Non-None if this node marks end of a word


class Trie:
    """Trie (prefix tree) for efficient word lookup."""

    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """Insert a word into the trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.word = word

    def starts_with(self, prefix: str) -> bool:
        """Check if any word in the trie starts with the given prefix."""
        node = self._find_node(prefix)
        return node is not None

    def _find_node(self, prefix: str) -> Optional[TrieNode]:
        """Find the node corresponding to the given prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def get_words_with_prefix(self, prefix: str) -> list[str]:
        """Get all words in the trie that start with the given prefix."""
        node = self._find_node(prefix)
        if node is None:
            return []
        words = []
        self._collect_words(node, words)
        return words

    def _collect_words(self, node: TrieNode, words: list[str]) -> None:
        """Recursively collect all words from a given node."""
        if node.word is not None:
            words.append(node.word)
        for child in node.children.values():
            self._collect_words(child, words)


# =============================================================================
# BASELINE SOLVER - DFS FOR EACH WORD (SLOWER)
# =============================================================================

def baseline_solve(board: list[list[str]], words: list[str]) -> list[str]:
    """
    Baseline solver: Check each word individually using DFS.

    This approach is slower because it performs a separate DFS traversal
    for each word in the list.

    Time Complexity: O(m * n * L * W) where:
        - m = number of rows
        - n = number of columns
        - L = average word length
        - W = number of words

    Space Complexity: O(L) for recursion stack

    Args:
        board: 2D list of characters
        words: List of words to search for

    Returns:
        List of words found in the board (sorted)
    """
    if not board or not board[0] or not words:
        return []

    m, n = len(board), len(board[0])
    found_words = set()

    # Create a copy of the board to track visited cells
    def dfs(row: int, col: int, index: int, word: str, visited: list[list[bool]]) -> bool:
        """DFS to check if word can be formed starting from (row, col)."""
        # Base case: all characters matched
        if index == len(word):
            return True

        # Check bounds and if cell matches the next character
        if (row < 0 or row >= m or col < 0 or col >= n or
                visited[row][col] or board[row][col] != word[index]):
            return False

        # Mark as visited
        visited[row][col] = True

        # Explore all four directions
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in directions:
            if dfs(row + dr, col + dc, index + 1, word, visited):
                visited[row][col] = False
                return True

        # Backtrack
        visited[row][col] = False
        return False

    # Try to find each word in the board
    for word in words:
        visited = [[False] * n for _ in range(m)]
        for i in range(m):
            for j in range(n):
                if board[i][j] == word[0]:
                    if dfs(i, j, 0, word, visited):
                        found_words.add(word)
                        break  # Found this word, move to next
            if word in found_words:
                break

    return sorted(found_words)


# =============================================================================
# TRIE-BASED OPTIMIZED SOLVER (FASTER)
# =============================================================================

def optimized_solve(board: list[list[str]], words: list[str]) -> list[str]:
    """
    Optimized solver using Trie: Build a Trie of all words and perform
    a single DFS from each cell to find all matching words.

    This approach is faster because:
    1. We build a Trie once (O(total_characters) where total_characters = sum of word lengths)
    2. We traverse each cell once (O(m*n))
    3. During DFS, we efficiently prune branches that don't match any word prefix

    Time Complexity: O(m * n * 4^L) in worst case, but typically much less
    due to Trie pruning. For a board with W words total character count C:
    - Building Trie: O(C)
    - DFS traversal: O(m * n * 4^k) where k is max word length (with pruning)

    Space Complexity: O(C) for Trie + O(m*n) for visited + O(L) for recursion

    Args:
        board: 2D list of characters
        words: List of words to search for

    Returns:
        List of words found in the board (sorted)
    """
    if not board or not board[0] or not words:
        return []

    m, n = len(board), len(board[0])
    found_words = set()

    # Build Trie from all words
    trie = Trie()
    for word in words:
        trie.insert(word)

    # Track visited cells
    visited = [[False] * n for _ in range(m)]

    def dfs(row: int, col: int, node: TrieNode) -> None:
        """
        DFS from cell (row, col) using Trie navigation.
        Explores all possible word paths from current position.
        """
        # Check bounds and if already visited
        if row < 0 or row >= m or col < 0 or col >= n or visited[row][col]:
            return

        char = board[row][col]

        # If current character is not in Trie children, prune this branch
        if char not in node.children:
            return

        # Move to next node in Trie
        node = node.children[char]
        visited[row][col] = True

        # If this node marks the end of a word, add it to results
        if node.word is not None:
            found_words.add(node.word)
            # Note: We don't stop here because this word might be a prefix
            # of another word that also exists in the board

        # Explore all four directions
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in directions:
            dfs(row + dr, col + dc, node)

        # Backtrack
        visited[row][col] = False

    # Start DFS from each cell
    for i in range(m):
        for j in range(n):
            dfs(i, j, trie.root)

    return sorted(found_words)


# =============================================================================
# SOLVER WITH DEDUPLICATION (HANDLES DUPLICATE WORDS IN INPUT)
# =============================================================================

def solve_with_dedup(board: list[list[str]], words: list[str],
                      use_optimized: bool = True) -> list[str]:
    """
    Solve Word Search II with explicit deduplication handling.

    Handles edge cases:
    - Duplicate words in input list
    - Empty board or words
    - Single cell boards
    - Words of length 1

    Args:
        board: 2D list of characters
        words: List of words to search for (may contain duplicates)
        use_optimized: If True, use Trie-based solver; else use baseline

    Returns:
        List of unique words found in the board (sorted)
    """
    # Handle empty inputs
    if not board or not board[0] or not words:
        return []

    # Remove duplicates while preserving order for consistent output
    unique_words = list(dict.fromkeys(words))

    if use_optimized:
        return optimized_solve(board, unique_words)
    else:
        return baseline_solve(board, unique_words)


# =============================================================================
# HELPER UTILITIES FOR BOARD FORMATTING AND RANDOM CASE GENERATION
# =============================================================================

def format_board(board: list[list[str]]) -> str:
    """
    Format a 2D board as a readable string.

    Args:
        board: 2D list of characters

    Returns:
        Formatted string representation of the board
    """
    if not board:
        return "Empty board"

    lines = []
    for row in board:
        lines.append("[" + ", ".join(f"'{c}'" for c in row) + "]")
    return "\n".join(lines)


def create_board(
    rows: int,
    cols: int,
    chars: str = "abcdefghijklmnopqrstuvwxyz",
    seed: Optional[int] = None,
) -> list[list[str]]:
    """
    Create a board with random lowercase letters.

    Args:
        rows: Number of rows
        cols: Number of columns
        chars: String of characters to choose from
        seed: Optional random seed for reproducibility

    Returns:
        2D list of random characters
    """
    rng = random.Random(seed) if seed is not None else random
    return [[rng.choice(chars) for _ in range(cols)] for _ in range(rows)]


def generate_random_test_case(
    board_rows: int = 4,
    board_cols: int = 4,
    num_words: int = 10,
    word_min_len: int = 2,
    word_max_len: int = 6,
    seed: Optional[int] = None
) -> tuple[list[list[str]], list[str]]:
    """
    Generate a random Word Search II test case.

    This utility creates a board with random letters and generates
    words that may or may not exist in the board for testing purposes.

    Args:
        board_rows: Number of rows in the board
        board_cols: Number of columns in the board
        num_words: Number of words to generate
        word_min_len: Minimum word length
        word_max_len: Maximum word length
        seed: Random seed for reproducibility

    Returns:
        Tuple of (board, words)
    """
    if seed is not None:
        random.seed(seed)

    # Create random board
    board = create_board(board_rows, board_cols)

    # Generate random words
    words = []
    chars = "abcdefghijklmnopqrstuvwxyz"

    for _ in range(num_words):
        length = random.randint(word_min_len, word_max_len)
        word = ''.join(random.choice(chars) for _ in range(length))
        words.append(word)

    return board, words


def generate_embedded_words_test_case(
    board: list[list[str]],
    num_extra_words: int = 5
) -> tuple[list[list[str]], list[str]]:
    """
    Generate words that are partially embedded in the board plus random words.

    This is useful for creating test cases where some words exist and some don't.

    Args:
        board: 2D board
        num_extra_words: Number of extra random words to add

    Returns:
        Tuple of (board, words)
    """
    m, n = len(board), len(board[0])
    chars = "abcdefghijklmnopqrstuvwxyz"

    # Collect some substrings from the board (potential words)
    words_from_board = set()

    # Extract horizontal substrings
    for i in range(m):
        for start in range(n):
            for end in range(start + 1, min(start + 7, n + 1)):
                word = ''.join(board[i][j] for j in range(start, end))
                if len(word) >= 2:
                    words_from_board.add(word)

    # Extract vertical substrings
    for j in range(n):
        for start in range(m):
            for end in range(start + 1, min(start + 7, m + 1)):
                word = ''.join(board[i][j] for i in range(start, end))
                if len(word) >= 2:
                    words_from_board.add(word)

    # Convert to list and shuffle
    embedded_words = list(words_from_board)
    random.shuffle(embedded_words)

    # Add random words that likely don't exist in the board
    extra_words = []
    for _ in range(num_extra_words):
        length = random.randint(3, 6)
        word = ''.join(random.choice(chars) for _ in range(length))
        extra_words.append(word)

    all_words = embedded_words[:min(10, len(embedded_words))] + extra_words
    random.shuffle(all_words)

    return board, all_words


# =============================================================================
# COMPLEXITY ANALYSIS AND VERIFICATION
# =============================================================================

def verify_solvers_equivalent(board: list[list[str]], words: list[str]) -> bool:
    """
    Verify that baseline and optimized solvers produce the same results.

    Args:
        board: 2D board
        words: List of words to search

    Returns:
        True if both solvers produce identical results
    """
    baseline_result = baseline_solve(board, words)
    optimized_result = optimized_solve(board, words)
    return baseline_result == optimized_result


def get_complexity_notes() -> str:
    """
    Get detailed complexity analysis for both solvers.

    Returns:
        String containing complexity analysis
    """
    return """
================================================================================
WORD SEARCH II - COMPLEXITY ANALYSIS
================================================================================

BASELINE SOLVER (DFS per word):
-------------------------------
Time Complexity:  O(m * n * L * W)
    - m, n: board dimensions
    - L: average word length
    - W: number of words

Space Complexity: O(L) for recursion stack per word

The baseline solver is simple but inefficient because:
1. It performs a separate DFS for each word
2. It doesn't share computation between words
3. It may revisit the same board positions multiple times

TRIE-BASED OPTIMIZED SOLVER:
---------------------------
Time Complexity: O(m * n * 4^k) worst case, but typically much less
    - m, n: board dimensions
    - k: maximum word length (with Trie pruning)
    - The 4 is for 4 possible directions from each cell

However, with Trie pruning:
- Branching stops when no word in the dictionary has the current prefix
- Average case is much better than worst case

Space Complexity:
    - Trie: O(C) where C = total characters in all words
    - Visited array: O(m * n)
    - Recursion stack: O(k)

The optimized solver is faster because:
1. Single DFS traversal finds all words
2. Trie enables efficient prefix matching
3. Early pruning of non-matching branches

PRACTICAL PERFORMANCE:
----------------------
For a typical case with:
- 10x10 board
- 100 words with average length 5

Baseline: ~100 * 10*10 * 5 = 50,000 operations (worst case)
Optimized: ~10*10 * 4^5 with pruning ≈ 10,000 operations (typical)

The optimized solver is typically 3-10x faster depending on the data.
================================================================================
"""


# =============================================================================
# CLI ENTRYPOINT
# =============================================================================

def run_sample_cases() -> None:
    """Run sample test cases to demonstrate the solver."""

    print("=" * 70)
    print("WORD SEARCH II - SAMPLE CASES")
    print("=" * 70)

    # Sample 1: Standard case
    print("\n--- Sample 1: Standard 4x4 board ---")
    board1 = [
        ['o', 'a', 'a', 'n'],
        ['e', 't', 'a', 'e'],
        ['i', 'h', 'k', 'r'],
        ['i', 'f', 'l', 'v']
    ]
    words1 = ["oath", "pea", "eat", "rain"]
    print(f"Board:\n{format_board(board1)}")
    print(f"Words: {words1}")
    result1 = optimized_solve(board1, words1)
    print(f"Found (optimized): {result1}")
    result1b = baseline_solve(board1, words1)
    print(f"Found (baseline): {result1b}")
    print(f"Results match: {result1 == result1b}")

    # Sample 2: Duplicate words
    print("\n--- Sample 2: Duplicate words in input ---")
    board2 = [
        ['a', 'b'],
        ['c', 'd']
    ]
    words2 = ["abcd", "acdb", "ade", "adb", "abc", "adb"]  # "adb" is duplicated
    print(f"Board:\n{format_board(board2)}")
    print(f"Words: {words2}")
    result2 = solve_with_dedup(board2, words2, use_optimized=True)
    print(f"Found: {result2}")

    # Sample 3: Edge cases
    print("\n--- Sample 3: Edge cases ---")

    # Single cell
    board3a = [['a']]
    words3a = ["a", "b", "aa"]
    result3a = optimized_solve(board3a, words3a)
    print(f"Single cell board, words={words3a}: {result3a}")

    # Empty board
    board3b: list[list[str]] = []
    words3b = ["test"]
    result3b = optimized_solve(board3b, words3b)
    print(f"Empty board, words={words3b}: {result3b}")

    # Empty words
    board3c = [['a', 'b'], ['c', 'd']]
    words3c: list[str] = []
    result3c = optimized_solve(board3c, words3c)
    print(f"Board 2x2, empty words: {result3c}")

    # Sample 4: Larger random case
    print("\n--- Sample 4: Random test case (seeded for reproducibility) ---")
    board4, words4 = generate_random_test_case(
        board_rows=4,
        board_cols=4,
        num_words=10,
        seed=42
    )
    print(f"Board:\n{format_board(board4)}")
    print(f"Words: {words4}")
    result4_opt = optimized_solve(board4, words4)
    result4_base = baseline_solve(board4, words4)
    print(f"Found (optimized): {result4_opt}")
    print(f"Found (baseline): {result4_base}")
    print(f"Results match: {result4_opt == result4_base}")

    # Sample 5: Performance comparison
    print("\n--- Sample 5: Performance comparison ---")
    import time

    board5 = create_board(10, 10)
    words5, _ = generate_embedded_words_test_case(board5, num_extra_words=50)

    start = time.time()
    result5_opt = optimized_solve(board5, words5)
    opt_time = time.time() - start

    start = time.time()
    result5_base = baseline_solve(board5, words5)
    base_time = time.time() - start

    print(f"Board: 10x10, Words: {len(words5)}")
    print(f"Optimized time: {opt_time:.4f}s, Found: {len(result5_opt)} words")
    print(f"Baseline time: {base_time:.4f}s, Found: {len(result5_base)} words")
    print(f"Speedup: {base_time/opt_time:.2f}x")
    print(f"Results match: {result5_opt == result5_base}")

    print("\n" + "=" * 70)
    print("COMPLEXITY NOTES:")
    print(get_complexity_notes())


if __name__ == "__main__":
    run_sample_cases()
