"""LeetCode #297 - Serialize and Deserialize Binary Tree

Design an algorithm to serialize and deserialize a binary tree.
Serialization is converting the tree to a string; deserialization
reconstructs the tree from that string.

Approach: BFS level-order traversal using 'null' for missing children.
"""
from __future__ import annotations

from collections import deque


class TreeNode:
    def __init__(self, val: int = 0, left: TreeNode | None = None, right: TreeNode | None = None):
        self.val = val
        self.left = left
        self.right = right


class Codec:
    def serialize(self, root: TreeNode | None) -> str:
        if root is None:
            return "[]"
        result: list[str] = []
        queue: deque[TreeNode | None] = deque([root])
        while queue:
            node = queue.popleft()
            if node is None:
                result.append("null")
            else:
                result.append(str(node.val))
                queue.append(node.left)
                queue.append(node.right)
        # Strip trailing nulls for cleaner output
        while result and result[-1] == "null":
            result.pop()
        return "[" + ",".join(result) + "]"

    def deserialize(self, data: str) -> TreeNode | None:
        data = data.strip()
        if data in ("[]", ""):
            return None
        inner = data[1:-1]
        vals = [v.strip() for v in inner.split(",")]
        if not vals or vals[0] == "null":
            return None
        root = TreeNode(int(vals[0]))
        queue: deque[TreeNode] = deque([root])
        i = 1
        while queue and i < len(vals):
            node = queue.popleft()
            # Left child
            if i < len(vals) and vals[i] != "null":
                node.left = TreeNode(int(vals[i]))
                queue.append(node.left)
            i += 1
            # Right child
            if i < len(vals) and vals[i] != "null":
                node.right = TreeNode(int(vals[i]))
                queue.append(node.right)
            i += 1
        return root
