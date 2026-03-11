"""LeetCode 297 - Serialize and Deserialize Binary Tree.

Design an algorithm to serialize a binary tree to a string and
deserialize that string back to the original tree structure.
"""
from __future__ import annotations


class TreeNode:
    def __init__(self, val: int = 0, left: TreeNode | None = None, right: TreeNode | None = None):
        self.val = val
        self.left = left
        self.right = right


class Codec:
    """Pre-order (DFS) serialization using '#' as null sentinel."""

    def serialize(self, root: TreeNode | None) -> str:
        parts: list[str] = []
        self._serialize_dfs(root, parts)
        return ",".join(parts)

    def _serialize_dfs(self, node: TreeNode | None, parts: list[str]) -> None:
        if node is None:
            parts.append("#")
            return
        parts.append(str(node.val))
        self._serialize_dfs(node.left, parts)
        self._serialize_dfs(node.right, parts)

    def deserialize(self, data: str) -> TreeNode | None:
        tokens = iter(data.split(","))
        return self._deserialize_dfs(tokens)

    def _deserialize_dfs(self, tokens) -> TreeNode | None:
        val = next(tokens)
        if val == "#":
            return None
        node = TreeNode(int(val))
        node.left = self._deserialize_dfs(tokens)
        node.right = self._deserialize_dfs(tokens)
        return node
