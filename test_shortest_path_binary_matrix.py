"""
Unit tests for Shortest Path in a Grid with Obstacle Elimination (LeetCode 1293)
"""

import pytest
from shortest_path_binary_matrix import shortest_path_binary_matrix


class TestShortestPathBinaryMatrix:
    """Test cases for shortest_path_binary_matrix function."""

    def test_example_1_obstacle_removal(self):
        """Can remove obstacle to find shorter path"""
        grid = [
            [0, 1, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        # With k=1, can remove obstacle at (0,1): (0,0)->(0,1)->(1,1)->(2,1)->(2,2) = 5
        # Or go around: (0,0)->(1,0)->(2,0)->(2,1)->(2,2) = 5
        assert shortest_path_binary_matrix(grid, 1) == 5

    def test_k_zero_blocked_path(self):
        """k=0 can't pass through obstacle"""
        grid = [
            [0, 1, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        # Must go around: (0,0)->(1,0)->(2,0)->(2,1)->(2,2) = 5
        assert shortest_path_binary_matrix(grid, 0) == 5

    def test_single_cell_zero(self):
        """Single cell with 0 should return 1"""
        grid = [[0]]
        assert shortest_path_binary_matrix(grid, 0) == 1

    def test_single_cell_obstacle_with_k(self):
        """Single cell with 1 but k>=1 should return 1"""
        grid = [[1]]
        assert shortest_path_binary_matrix(grid, 1) == 1

    def test_single_cell_obstacle_no_k(self):
        """Single cell with 1 but k=0 should return -1"""
        grid = [[1]]
        assert shortest_path_binary_matrix(grid, 0) == -1

    def test_start_blocked_no_removals(self):
        """Start cell blocked with k=0 should return -1"""
        grid = [[1, 0], [0, 0]]
        assert shortest_path_binary_matrix(grid, 0) == -1

    def test_start_blocked_with_removals(self):
        """Start cell blocked but k>=1 should work"""
        grid = [[1, 0], [0, 0]]
        # Remove start: (0,0)->(0,0)->(0,1)->(1,1) = 4
        assert shortest_path_binary_matrix(grid, 1) == 3

    def test_end_blocked_no_removals(self):
        """End cell blocked with k=0 should return -1"""
        grid = [[0, 0], [0, 1]]
        assert shortest_path_binary_matrix(grid, 0) == -1

    def test_end_blocked_with_removals(self):
        """End cell blocked but k>=1 should work"""
        grid = [[0, 0], [0, 1]]
        assert shortest_path_binary_matrix(grid, 1) == 3

    def test_clear_path_no_removals_needed(self):
        """Clear path with no obstacles"""
        grid = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        assert shortest_path_binary_matrix(grid, 0) == 5

    def test_grid_with_wall_insufficient_k(self):
        """Grid with wall - even k=1 can pass by removing edge obstacle"""
        grid = [
            [0, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
        # Path: (0,0)->(0,1)->(0,2)->remove (1,2)->(2,2) = 5 steps
        assert shortest_path_binary_matrix(grid, 1) == 5

    def test_grid_with_wall_no_k(self):
        """Grid with wall but k=0 - cannot pass"""
        grid = [
            [0, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
        # Full wall cannot be crossed with 4-directional movement
        assert shortest_path_binary_matrix(grid, 0) == -1

    def test_path_around_multiple_obstacles(self):
        """Navigate around multiple obstacles"""
        grid = [
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0]
        ]
        # Need to remove some obstacles or go around
        result = shortest_path_binary_matrix(grid, 3)
        assert result > 0

    def test_empty_grid(self):
        """Empty grid should return -1"""
        grid = []
        assert shortest_path_binary_matrix(grid, 0) == -1


class TestEdgeCases:
    """Edge case tests."""

    def test_two_by_two_clear(self):
        """2x2 all zeros"""
        grid = [[0, 0], [0, 0]]
        assert shortest_path_binary_matrix(grid, 0) == 3

    def test_two_by_two_with_obstacle(self):
        """2x2 with one obstacle"""
        grid = [[0, 1], [0, 0]]
        # Go around: (0,0)->(1,0)->(1,1) = 3
        assert shortest_path_binary_matrix(grid, 0) == 3
        # Remove: (0,0)->(0,1)->(1,1) = 3
        assert shortest_path_binary_matrix(grid, 1) == 3

    def test_minimum_k(self):
        """k=0 with no obstacles"""
        grid = [[0]]
        assert shortest_path_binary_matrix(grid, 0) == 1

    def test_large_k(self):
        """Large k should not affect result if path clear"""
        grid = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        assert shortest_path_binary_matrix(grid, 100) == 5
