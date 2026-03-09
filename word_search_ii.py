from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TrieNode:
    children: dict[str, "TrieNode"] = field(default_factory=dict)
    word: str | None = None


def find_words(board: list[list[str]], words: list[str]) -> list[str]:
    """Return all dictionary words that can be formed on the board."""
    if not board or not board[0] or not words:
        return []

    root = TrieNode()
    for word in words:
        node = root
        for char in word:
            node = node.children.setdefault(char, TrieNode())
        node.word = word

    rows = len(board)
    cols = len(board[0])
    found: list[str] = []

    def dfs(row: int, col: int, node: TrieNode) -> None:
        if row < 0 or col < 0 or row >= rows or col >= cols:
            return

        char = board[row][col]
        if char == "#" or char not in node.children:
            return

        next_node = node.children[char]
        if next_node.word is not None:
            found.append(next_node.word)
            next_node.word = None

        board[row][col] = "#"
        dfs(row + 1, col, next_node)
        dfs(row - 1, col, next_node)
        dfs(row, col + 1, next_node)
        dfs(row, col - 1, next_node)
        board[row][col] = char

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, root)

    return found
