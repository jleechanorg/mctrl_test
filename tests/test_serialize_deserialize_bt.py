"""Tests for LeetCode #297 - Serialize and Deserialize Binary Tree."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "leet_code"))

from serialize_deserialize_bt import Codec, TreeNode


def tree_to_list(root: TreeNode | None) -> list[int | None]:
    """Convert tree to level-order list for easy comparison."""
    if root is None:
        return []
    from collections import deque
    result: list[int | None] = []
    queue: deque[TreeNode | None] = deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            result.append(None)
        else:
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
    while result and result[-1] is None:
        result.pop()
    return result


def build_tree(vals: list[int | None]) -> TreeNode | None:
    """Build tree from level-order list."""
    if not vals or vals[0] is None:
        return None
    from collections import deque
    root = TreeNode(vals[0])
    queue: deque[TreeNode] = deque([root])
    i = 1
    while queue and i < len(vals):
        node = queue.popleft()
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            queue.append(node.right)
        i += 1
    return root


class TestCodec:
    def setup_method(self) -> None:
        self.codec = Codec()

    def _roundtrip(self, root: TreeNode | None) -> None:
        serialized = self.codec.serialize(root)
        restored = self.codec.deserialize(serialized)
        assert tree_to_list(restored) == tree_to_list(root)

    def test_example_1(self) -> None:
        """[1,2,3,null,null,4,5]"""
        root = build_tree([1, 2, 3, None, None, 4, 5])
        self._roundtrip(root)

    def test_empty_tree(self) -> None:
        self._roundtrip(None)

    def test_single_node(self) -> None:
        self._roundtrip(TreeNode(42))

    def test_left_skewed(self) -> None:
        root = TreeNode(1, TreeNode(2, TreeNode(3, TreeNode(4))))
        self._roundtrip(root)

    def test_right_skewed(self) -> None:
        root = TreeNode(1, None, TreeNode(2, None, TreeNode(3, None, TreeNode(4))))
        self._roundtrip(root)

    def test_negative_values(self) -> None:
        root = build_tree([-1, -2, -3])
        self._roundtrip(root)

    def test_large_values(self) -> None:
        root = build_tree([1000, -1000, 999])
        self._roundtrip(root)

    def test_complete_binary_tree(self) -> None:
        root = build_tree([1, 2, 3, 4, 5, 6, 7])
        self._roundtrip(root)

    def test_sparse_tree(self) -> None:
        """Tree with gaps: [1, null, 2, null, 3]"""
        root = build_tree([1, None, 2, None, 3])
        self._roundtrip(root)

    def test_serialize_format(self) -> None:
        root = build_tree([1, 2, 3])
        assert self.codec.serialize(root) == "[1,2,3]"

    def test_serialize_empty(self) -> None:
        assert self.codec.serialize(None) == "[]"

    def test_deserialize_empty(self) -> None:
        assert self.codec.deserialize("[]") is None

    def test_idempotent(self) -> None:
        """Serialize -> deserialize -> serialize gives same string."""
        root = build_tree([1, 2, 3, None, None, 4, 5])
        s1 = self.codec.serialize(root)
        s2 = self.codec.serialize(self.codec.deserialize(s1))
        assert s1 == s2

    def test_deep_tree(self) -> None:
        """Stress: 1000-node deep left-skewed tree."""
        node = None
        for i in range(1000):
            node = TreeNode(i, node)
        self._roundtrip(node)
