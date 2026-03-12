"""LeetCode 98: Validate Binary Search Tree

Given the root of a binary tree, determine if it is a valid binary search tree (BST).

A valid BST is defined as:
- The left subtree of a node contains only nodes with keys less than the node's key
- The right subtree of a node contains only nodes with keys greater than the node's key
- Both subtrees must also be binary search trees
"""

from __future__ import annotations
from typing import Optional


class TreeNode:
    """Definition for a binary tree node."""

    def __init__(self, val: int = 0, left: 'TreeNode' = None, right: 'TreeNode' = None):
        self.val = val
        self.left = left
        self.right = right


def is_valid_bst(root: Optional[TreeNode]) -> bool:
    """Determine if a binary tree is a valid BST using recursion with valid range checking.

    Args:
        root: The root node of the binary tree.

    Returns:
        True if the tree is a valid BST, False otherwise.
    """

    def validate(node: Optional[TreeNode], min_val: Optional[int], max_val: Optional[int]) -> bool:
        # Empty tree is a valid BST
        if node is None:
            return True

        # Check if current node violates BST constraints
        if min_val is not None and node.val <= min_val:
            return False
        if max_val is not None and node.val >= max_val:
            return False

        # Recursively validate left and right subtrees
        # Left subtree: all values must be less than current node's value
        # Right subtree: all values must be greater than current node's value
        return (
            validate(node.left, min_val, node.val) and
            validate(node.right, node.val, max_val)
        )

    return validate(root, None, None)


# ============== Test Cases ==============

def test_valid_bst_simple():
    """Test: [2,1,3] -> true"""
    #     2
    #    / \
    #   1   3
    root = TreeNode(2)
    root.left = TreeNode(1)
    root.right = TreeNode(3)
    assert is_valid_bst(root) is True


def test_invalid_bst_left_child_greater():
    """Test: [5,1,4,null,null,3,6] -> false
    The right subtree has node 3 which is less than root 5
    """
    #     5
    #    / \
    #   1   4
    #      / \
    #     3   6
    root = TreeNode(5)
    root.left = TreeNode(1)
    root.right = TreeNode(4)
    root.right.left = TreeNode(3)
    root.right.right = TreeNode(6)
    assert is_valid_bst(root) is False


def test_invalid_bst_duplicate_values():
    """Test: [2,2,2] -> false
    Left child equals root (not less), right child equals root (not greater)
    """
    #     2
    #    / \
    #   2   2
    root = TreeNode(2)
    root.left = TreeNode(2)
    root.right = TreeNode(2)
    assert is_valid_bst(root) is False


def test_single_node():
    """Test: [1] -> true"""
    root = TreeNode(1)
    assert is_valid_bst(root) is True


def test_empty_tree():
    """Test: [] -> true (empty tree is valid BST)"""
    assert is_valid_bst(None) is True


def test_left_skewed_bst():
    """Test: [5,4,6] -> false (6 in left subtree violates BST)"""
    #     5
    #    / \
    #   4   6  <- 6 is in right but still invalid because
    #              6 > 5 is fine, but this tests the structure
    root = TreeNode(5)
    root.left = TreeNode(4)
    root.right = TreeNode(6)
    # This is actually valid - let me fix this test
    # Correct left skewed:
    #     3
    #    /
    #   2
    #    \
    #     4  <- 4 violates because it's in left subtree but > 3
    root = TreeNode(3)
    root.left = TreeNode(2)
    root.left.right = TreeNode(4)
    assert is_valid_bst(root) is False


def test_right_skewed_valid():
    """Test: [1,null,2,null,3] -> true (valid right-skewed BST)"""
    #     1
    #      \
    #       2
    #        \
    #         3
    root = TreeNode(1)
    root.right = TreeNode(2)
    root.right.right = TreeNode(3)
    assert is_valid_bst(root) is True


def test_large_value_range():
    """Test boundary values: -2^31 and 2^31-1"""
    #     0
    #    / \
    # -2147483648  2147483647
    root = TreeNode(0)
    root.left = TreeNode(-2147483648)
    root.right = TreeNode(2147483647)
    assert is_valid_bst(root) is True


def test_nested_invalid():
    """Test deeper invalid structure"""
    #     5
    #    / \
    #   1   6
    #      / \
    #     4   7  <- 4 < 5 violates
    root = TreeNode(5)
    root.left = TreeNode(1)
    root.right = TreeNode(6)
    root.right.left = TreeNode(4)
    root.right.right = TreeNode(7)
    assert is_valid_bst(root) is False


if __name__ == "__main__":
    # Run quick sanity check
    print("Running tests...")
    test_valid_bst_simple()
    test_invalid_bst_left_child_greater()
    test_invalid_bst_duplicate_values()
    test_single_node()
    test_empty_tree()
    test_left_skewed_bst()
    test_right_skewed_valid()
    test_large_value_range()
    test_nested_invalid()
    print("All tests passed!")
