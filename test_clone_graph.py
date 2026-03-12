from __future__ import annotations

import pytest
from clone_graph import (
    Node,
    clone_graph,
    clone_graph_dfs,
    build_graph,
    graph_to_adj_list,
)


class TestNode:
    """Tests for the Node class."""

    def test_node_creation(self):
        node = Node(1)
        assert node.val == 1
        assert node.neighbors == []

    def test_node_with_neighbors(self):
        node1 = Node(1)
        node2 = Node(2)
        node1.neighbors = [node2]
        assert node1.neighbors == [node2]
        assert node1.neighbors[0].val == 2

    def test_node_equality(self):
        node1 = Node(1)
        node2 = Node(1)
        node3 = Node(2)
        assert node1 == node2
        assert node1 != node3

    def test_node_hash(self):
        node1 = Node(1)
        node2 = Node(1)
        assert hash(node1) == hash(node2)


class TestBuildGraph:
    """Tests for building a graph from adjacency list."""

    def test_build_simple_graph(self):
        adj_list = [[1, 2], [0, 2], [0, 1]]
        root = build_graph(adj_list)

        assert root is not None
        assert root.val == 0
        assert len(root.neighbors) == 2
        neighbor_vals = {n.val for n in root.neighbors}
        assert neighbor_vals == {1, 2}

    def test_build_single_node(self):
        adj_list = [[]]
        root = build_graph(adj_list)

        assert root is not None
        assert root.val == 0
        assert root.neighbors == []

    def test_build_linear_graph(self):
        adj_list = [[1], [0, 2], [1]]
        root = build_graph(adj_list)

        assert root is not None
        assert root.val == 0
        assert len(root.neighbors) == 1
        assert root.neighbors[0].val == 1


class TestCloneGraph:
    """Tests for the clone_graph function."""

    def test_clone_single_node(self):
        adj_list = [[]]
        root = build_graph(adj_list)
        cloned = clone_graph(root)

        assert cloned is not None
        assert cloned.val == root.val
        assert cloned is not root  # Different object
        assert cloned.neighbors == []

    def test_clone_simple_graph(self):
        adj_list = [[1, 2], [0, 2], [0, 1]]
        root = build_graph(adj_list)
        cloned = clone_graph(root)

        assert cloned is not None
        assert cloned.val == 0

        # Check structure is preserved
        cloned_adj = graph_to_adj_list(cloned)
        assert cloned_adj == adj_list

    def test_clone_graph_no_shared_references(self):
        """Ensure cloned nodes are different objects from original."""
        adj_list = [[1, 2], [0, 2], [0, 1]]
        root = build_graph(adj_list)
        cloned = clone_graph(root)

        # Clone should have different nodes
        assert cloned is not root
        for cloned_neighbor in cloned.neighbors:
            for original_neighbor in root.neighbors:
                assert cloned_neighbor is not original_neighbor

    def test_clone_linear_graph(self):
        adj_list = [[1], [0, 2], [1, 3], [2]]
        root = build_graph(adj_list)
        cloned = clone_graph(root)

        cloned_adj = graph_to_adj_list(cloned)
        assert cloned_adj == adj_list

    def test_clone_none_returns_none(self):
        result = clone_graph(None)
        assert result is None

    def test_clone_larger_graph(self):
        # Create a larger graph: 5 nodes in a cycle
        adj_list = [[1, 4], [0, 2], [1, 3], [2, 4], [3, 0]]
        root = build_graph(adj_list)
        cloned = clone_graph(root)

        cloned_adj = graph_to_adj_list(cloned)
        assert cloned_adj == adj_list


class TestCloneGraphDFS:
    """Tests for the DFS version of clone_graph."""

    def test_dfs_clone_simple_graph(self):
        adj_list = [[1, 2], [0, 2], [0, 1]]
        root = build_graph(adj_list)
        cloned = clone_graph_dfs(root)

        assert cloned is not None
        assert cloned.val == 0
        cloned_adj = graph_to_adj_list(cloned)
        assert cloned_adj == adj_list

    def test_dfs_clone_single_node(self):
        adj_list = [[]]
        root = build_graph(adj_list)
        cloned = clone_graph_dfs(root)

        assert cloned is not None
        assert cloned.val == 0
        assert cloned is not root

    def test_dfs_clone_none_returns_none(self):
        result = clone_graph_dfs(None)
        assert result is None


class TestGraphToAdjList:
    """Tests for converting graph back to adjacency list."""

    def test_single_node(self):
        node = Node(0)
        result = graph_to_adj_list(node)
        assert result == [[]]

    def test_simple_graph(self):
        adj_list = [[1, 2], [0, 2], [0, 1]]
        root = build_graph(adj_list)
        result = graph_to_adj_list(root)
        assert result == adj_list


class TestExample:
    """Test the example from the problem statement."""

    def test_example_case(self):
        # Input: adjList = [[1,2],[0,2],[0,1]]
        # Output: [[1,2],[0,2],[0,1]]
        adj_list = [[1, 2], [0, 2], [0, 1]]
        root = build_graph(adj_list)
        cloned = clone_graph(root)

        assert cloned is not None
        cloned_adj = graph_to_adj_list(cloned)
        assert cloned_adj == adj_list
