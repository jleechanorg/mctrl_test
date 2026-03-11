"""Tests for LeetCode 297 - Serialize and Deserialize Binary Tree."""
from __future__ import annotations

from serialize_deserialize import Codec, TreeNode


def tree_to_list(root: TreeNode | None) -> list:
    """BFS level-order list for easy comparison (trailing Nones trimmed)."""
    if root is None:
        return []
    result, queue = [], [root]
    while queue:
        node = queue.pop(0)
        if node:
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append(None)
    while result and result[-1] is None:
        result.pop()
    return result


def build_tree(vals: list) -> TreeNode | None:
    """Build tree from level-order list (None = absent node)."""
    if not vals:
        return None
    root = TreeNode(vals[0])
    queue, i = [root], 1
    while queue and i < len(vals):
        node = queue.pop(0)
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            queue.append(node.right)
        i += 1
    return root


codec = Codec()


def roundtrip(root: TreeNode | None) -> list:
    return tree_to_list(codec.deserialize(codec.serialize(root)))


class TestSerializeDeserialize:
    def test_example_tree(self):
        #       1
        #      / \
        #     2   3
        #        / \
        #       4   5
        root = build_tree([1, 2, 3, None, None, 4, 5])
        assert roundtrip(root) == [1, 2, 3, None, None, 4, 5]

    def test_empty_tree(self):
        assert roundtrip(None) == []

    def test_single_node(self):
        assert roundtrip(TreeNode(42)) == [42]

    def test_left_skewed(self):
        root = build_tree([1, 2, None, 3])
        assert roundtrip(root) == [1, 2, None, 3]

    def test_right_skewed(self):
        root = build_tree([1, None, 2, None, 3])
        assert roundtrip(root) == [1, None, 2, None, 3]

    def test_negative_values(self):
        root = build_tree([-1, -2, -3])
        assert roundtrip(root) == [-1, -2, -3]

    def test_large_values(self):
        root = build_tree([1000, -1000, 999])
        assert roundtrip(root) == [1000, -1000, 999]

    def test_complete_binary_tree(self):
        root = build_tree([1, 2, 3, 4, 5, 6, 7])
        assert roundtrip(root) == [1, 2, 3, 4, 5, 6, 7]

    def test_serialize_format(self):
        root = TreeNode(1, TreeNode(2), TreeNode(3))
        assert codec.serialize(root) == "1,2,#,#,3,#,#"

    def test_idempotent_double_roundtrip(self):
        root = build_tree([1, 2, 3, None, None, 4, 5])
        s1 = codec.serialize(root)
        s2 = codec.serialize(codec.deserialize(s1))
        assert s1 == s2
