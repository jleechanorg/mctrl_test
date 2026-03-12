"""
Unit tests for Shortest Path in Binary Matrix (LeetCode 1293)
"""

import pytest
from shortest_path_binary_matrix import (
    shortest_path_binary_matrix,
    shortest_path_binary_matrix_dfs
)


class TestShortestPathBinaryMatrix:
    """Test cases for shortest_path_binary_matrix function."""

    def test_example_1(self):
        """Example 1: [[0,1],[1,0]] -> 2"""
        grid = [[0, 1], [1, 0]]
        assert shortest_path_binary_matrix(grid) == 2

    def test_example_2(self):
        """Example 2: [[0,0,0],[1,1,0],[1,1,0]] -> 4"""
        grid = [
            [0, 0, 0],
            [1, 1, 0],
            [1, 1, 0]
        ]
        assert shortest_path_binary_matrix(grid) == 4

    def test_example_3(self):
        """Example 3: [[1,1],[1,1]] -> -1 (no path)"""
        grid = [[1, 1], [1, 1]]
        assert shortest_path_binary_matrix(grid) == -1

    def test_single_cell_zero(self):
        """Single cell with 0 should return 1"""
        grid = [[0]]
        assert shortest_path_binary_matrix(grid) == 1

    def test_single_cell_one(self):
        """Single cell with 1 should return -1"""
        grid = [[1]]
        assert shortest_path_binary_matrix(grid) == -1

    def test_start_blocked(self):
        """Start cell blocked should return -1"""
        grid = [[1, 0], [0, 0]]
        assert shortest_path_binary_matrix(grid) == -1

    def test_end_blocked(self):
        """End cell blocked should return -1"""
        grid = [[0, 0], [0, 1]]
        assert shortest_path_binary_matrix(grid) == -1

    def test_diagonal_path(self):
        """Direct diagonal path"""
        grid = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        assert shortest_path_binary_matrix(grid) == 3  # Direct diagonal

    def test_maze_path(self):
        """Maze with obstacles requiring longer path"""
        grid = [
            [0, 0, 0, 0],
            [1, 1, 0, 1],
            [0, 0, 0, 0],
            [0, 1, 1, 0]
        ]
        # Shortest: (0,0)->(0,1)->(1,2)->(2,2)->(3,3) = 5
        assert shortest_path_binary_matrix(grid) == 5

    def test_large_grid(self):
        """Larger grid with no path due to wall"""
        n = 5
        grid = [[0] * n for _ in range(n)]
        # Add a wall blocking all paths
        grid[2] = [1, 1, 1, 1, 1]
        assert shortest_path_binary_matrix(grid) == -1

    def test_all_zeros_5x5(self):
        """5x5 grid with all zeros"""
        grid = [[0] * 5 for _ in range(5)]
        assert shortest_path_binary_matrix(grid) == 5

    def test_two_by_two_clear(self):
        """2x2 all clear"""
        grid = [[0, 0], [0, 0]]
        assert shortest_path_binary_matrix(grid) == 2

    def test_two_by_two_blocked(self):
        """2x2 with middle blocked - can use diagonal"""
        grid = [[0, 0], [1, 0]]
        # Shortest: (0,0)->(1,1) diagonal = 2
        assert shortest_path_binary_matrix(grid) == 2


class TestShortestPathBinaryMatrixDFS:
    """Test cases for DFS alternative solution."""

    def test_consistency_with_bfs(self):
        """DFS should produce same results as BFS"""
        test_grids = [
            [[0, 1], [1, 0]],
            [[0, 0, 0], [1, 1, 0], [1, 1, 0]],
            [[1, 1], [1, 1]],
            [[0]],
            [[0, 0], [0, 0]],
            [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
        ]

        for grid in test_grids:
            bfs_result = shortest_path_binary_matrix(grid)
            dfs_result = shortest_path_binary_matrix_dfs(grid)
            assert bfs_result == dfs_result, f"Grid {grid}: BFS={bfs_result}, DFS={dfs_result}"

    def test_dfs_simple(self):
        """DFS simple case"""
        grid = [[0, 0], [0, 0]]
        assert shortest_path_binary_matrix_dfs(grid) == 2


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_grid(self):
        """Empty grid (0x0) - not a valid input, expect index error or skip"""
        grid = []
        # Empty grid is invalid input - the function cannot process it
        # This test documents the expected behavior
        with pytest.raises(IndexError):
            shortest_path_binary_matrix(grid)

    def test_minimum_size(self):
        """Minimum valid size (1x1)"""
        assert shortest_path_binary_matrix([[0]]) == 1
        assert shortest_path_binary_matrix([[1]]) == -1
