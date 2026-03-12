"""
LeetCode Problem 124: Binary Tree Maximum Path Sum

A path in a binary tree is a sequence of nodes where each pair of adjacent
nodes in the sequence has an edge connecting them. A node can only appear
in the sequence at most once. Note that the path does not need to pass
through the root.

The path sum of a path is the sum of the node's values in the path.
Given the root of a binary tree, return the maximum path sum.
"""


class TreeNode:
    """Definition for a binary tree node."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def max_path_sum(root: TreeNode | None) -> int:
    """
    Calculate the maximum path sum in a binary tree.

    A path is defined as any sequence of nodes starting from any node
    and ending at any node, where each pair of adjacent nodes is connected
    by an edge. The path does not need to pass through the root.

    Uses DFS with max gain calculation. For each node, we compute:
    - The max gain from this node to any descendant (used by parent)
    - The max path sum that passes through this node (for global max)

    Args:
        root: The root of the binary tree

    Returns:
        The maximum path sum possible in the tree

    Time Complexity: O(n) where n is the number of nodes
    Space Complexity: O(h) where h is the height of the tree (recursion stack)
    """
    max_sum = float('-inf')

    def dfs(node: TreeNode | None) -> int:
        nonlocal max_sum
        if node is None:
            return 0

        # Calculate max gain from left and right subtrees
        # We take max(0, ...) because we can choose to not include
        # a subtree if it would decrease our sum
        left_gain = max(dfs(node.left), 0)
        right_gain = max(dfs(node.right), 0)

        # Maximum path sum that passes through this node
        # This could be the new global maximum
        path_through_node = node.val + left_gain + right_gain
        max_sum = max(max_sum, path_through_node)

        # Return the max gain this node can provide to its parent
        # Parent can only use one branch (either left or right)
        return node.val + max(left_gain, right_gain)

    dfs(root)
    return max_sum


# Test cases
if __name__ == "__main__":
    # Test 1: Example from problem
    # Tree: -10,9,20,null,null,15,7
    #        -10
    #       /   \
    #      9    20
    #          /  \
    #         15   7
    # Path: 9 + (-10) + 20 + 15 + 7 = 42
    root1 = TreeNode(-10)
    root1.left = TreeNode(9)
    root1.right = TreeNode(20)
    root1.right.left = TreeNode(15)
    root1.right.right = TreeNode(7)
    assert max_path_sum(root1) == 42, f"Expected 42, got {max_path_sum(root1)}"
    print("Test 1 passed: Example tree returns 42")

    # Test 2: Single node
    root2 = TreeNode(1)
    assert max_path_sum(root2) == 1, f"Expected 1, got {max_path_sum(root2)}"
    print("Test 2 passed: Single node returns its value")

    # Test 3: Negative values
    root3 = TreeNode(-2)
    root3.left = TreeNode(-1)
    assert max_path_sum(root3) == -1, f"Expected -1, got {max_path_sum(root3)}"
    print("Test 3 passed: Tree with negative values")

    # Test 4: All positive
    root4 = TreeNode(2)
    root4.left = TreeNode(-1)
    root4.right = TreeNode(3)
    assert max_path_sum(root4) == 5, f"Expected 5, got {max_path_sum(root4)}"
    print("Test 4 passed: Path 2 + (-1) + 3 = 4, max is 2 + 3 = 5")

    # Test 5: More complex tree
    #        1
    #       / \
    #      2   3
    #     / \   \
    #    4   5   6
    root5 = TreeNode(1)
    root5.left = TreeNode(2)
    root5.right = TreeNode(3)
    root5.left.left = TreeNode(4)
    root5.left.right = TreeNode(5)
    root5.right.right = TreeNode(6)
    # Best path: 5 + 2 + 1 + 3 + 6 = 17
    assert max_path_sum(root5) == 17, f"Expected 17, got {max_path_sum(root5)}"
    print("Test 5 passed: Complex tree returns 17")

    # Test 6: Single negative node
    root6 = TreeNode(-5)
    assert max_path_sum(root6) == -5, f"Expected -5, got {max_path_sum(root6)}"
    print("Test 6 passed: Single negative node returns its value")

    print("\nAll tests passed!")
