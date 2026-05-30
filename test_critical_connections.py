"""
Unit tests for LeetCode 1192: Critical Connections in a Network
"""

import pytest
from critical_connections import critical_connections


class TestCriticalConnections:
    """Test cases for critical_connections function."""

    def test_basic_example(self):
        """Test the basic example from LeetCode."""
        n = 4
        connections = [[0, 1], [1, 2], [2, 0], [1, 3]]
        result = critical_connections(n, connections)
        # [1, 3] is the only critical connection
        assert len(result) == 1
        assert [1, 3] in result or [3, 1] in result

    def test_no_critical_connections(self):
        """Test when there are no bridges (cycle graph)."""
        n = 3
        connections = [[0, 1], [1, 2], [2, 0]]
        result = critical_connections(n, connections)
        assert result == []

    def test_linear_chain(self):
        """Test linear chain where all edges are bridges."""
        n = 4
        connections = [[0, 1], [1, 2], [2, 3]]
        result = critical_connections(n, connections)
        assert len(result) == 3

    def test_single_node(self):
        """Test with single node - no connections."""
        n = 1
        connections = []
        result = critical_connections(n, connections)
        assert result == []

    def test_two_nodes_one_connection(self):
        """Test with two nodes and single connection."""
        n = 2
        connections = [[0, 1]]
        result = critical_connections(n, connections)
        assert len(result) == 1

    def test_disconnected_graph(self):
        """Test with disconnected components."""
        n = 5
        connections = [[0, 1], [1, 2], [3, 4]]
        result = critical_connections(n, connections)
        # Edges [0,1] and [1,2] are bridges in their component
        # Edge [3,4] is also a bridge
        assert len(result) == 3

    def test_complex_graph(self):
        """Test with more complex graph structure."""
        n = 6
        connections = [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4], [4, 5], [5, 3]]
        result = critical_connections(n, connections)
        # Edge [1, 3] is the only bridge
        assert len(result) == 1

    def test_multiple_bridges_in_tree(self):
        """Test a tree with multiple branches."""
        n = 7
        connections = [
            [0, 1], [1, 2], [1, 3], [3, 4], [3, 5], [5, 6]
        ]
        result = critical_connections(n, connections)
        # All edges in a tree are bridges
        assert len(result) == 6


class TestCriticalConnectionsEdgeCases:
    """Edge case tests."""

    def test_large_component_with_cycles(self):
        """Test graph with many nodes and cycles."""
        n = 5
        # Create a cycle with bridges on both sides
        connections = [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4]]
        result = critical_connections(n, connections)
        # Both [2, 3] and [3, 4] are bridges
        assert len(result) == 2

    def test_bidirectional_connections_order(self):
        """Test that result order doesn't matter."""
        n = 3
        connections = [[0, 1], [1, 2]]
        result = critical_connections(n, connections)
        assert len(result) == 2
        # Check both possible orderings
        for edge in result:
            assert sorted(edge) in [[0, 1], [1, 2]]
