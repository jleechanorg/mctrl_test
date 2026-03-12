"""
Unit tests for Shortest Path in Binary Matrix (LeetCode 1091)

Given an n x n binary matrix, find the shortest clear path from top-left
to bottom-right where cells contain 0 (not blocked) and path is 8-directionally adjacent.
"""
import pytest
from shortest_path_binary_matrix import shortest_path_binary_matrix, shortest_path_binary_matrix_dfs


class TestShortestPathBinaryMatrix:
    """Test cases for shortest_path_binary_matrix function."""

    def test_example_1(self):
        """LeetCode example 1: path exists with diagonal"""
        grid = [
            [0, 1],
            [1, 0]
        ]
        assert shortest_path_binary_matrix(grid) == 2

    def test_example_2(self):
        """LeetCode example 2: longer path around obstacles"""
        grid = [
            [0, 0, 0],
            [1, 1, 0],
            [1, 1, 0]
        ]
        assert shortest_path_binary_matrix(grid) == 4

    def test_example_3(self):
        """LeetCode example 3: start/end blocked, early guard returns -1"""
        grid = [
            [1, 1, 1, 1],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [1, 1, 1, 1]
        ]
        assert shortest_path_binary_matrix(grid) == -1

    def test_open_endpoints_no_path(self):
        """Start and end are open but no path exists between them"""
        grid = [
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0]
        ]
        # Start (0,0)=0 and end (2,2)=0, but walls block all paths
        assert shortest_path_binary_matrix(grid) == -1

    def test_single_cell_empty(self):
        """Single cell at start/end with 0 - path length is 1"""
        grid = [[0]]
        assert shortest_path_binary_matrix(grid) == 1

    def test_single_cell_blocked(self):
        """Single cell at start/end with 1 - no path"""
        grid = [[1]]
        assert shortest_path_binary_matrix(grid) == -1

    def test_start_blocked(self):
        """Start cell is blocked - no path"""
        grid = [
            [1, 0],
            [0, 0]
        ]
        assert shortest_path_binary_matrix(grid) == -1

    def test_end_blocked(self):
        """End cell is blocked - no path"""
        grid = [
            [0, 0],
            [0, 1]
        ]
        assert shortest_path_binary_matrix(grid) == -1

    def test_diagonal_path(self):
        """Can use diagonal movement for shorter path"""
        grid = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        # Direct diagonal: (0,0) -> (1,1) -> (2,2) = 3 steps
        assert shortest_path_binary_matrix(grid) == 3

    def test_diagonal_blocked(self):
        """Diagonal blocked, must go around"""
        grid = [
            [0, 0, 1],
            [0, 1, 0],
            [1, 0, 0]
        ]
        # Path: (0,0) -> (0,1) -> (1,2) -> (2,2) = 4
        assert shortest_path_binary_matrix(grid) == 4

    def test_no_obstacles(self):
        """Grid with no obstacles - diagonal path"""
        grid = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        # Diagonal: 4 steps
        assert shortest_path_binary_matrix(grid) == 4

    def test_maze_with_walls(self):
        """Complex maze with walls"""
        grid = [
            [0, 1, 1, 1, 1],
            [0, 1, 0, 0, 1],
            [0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        # Path: (0,0)->(1,0)->(2,1)->(3,2)->(4,3)->(4,4) = 6 cells
        result = shortest_path_binary_matrix(grid)
        assert result == 6

    def test_large_grid(self):
        """Larger grid performance test"""
        n = 10
        grid = [[0] * n for _ in range(n)]
        # All zeros - diagonal path = n
        assert shortest_path_binary_matrix(grid) == n

    def test_two_by_two_clear(self):
        """2x2 all clear - can go diagonal"""
        grid = [
            [0, 0],
            [0, 0]
        ]
        assert shortest_path_binary_matrix(grid) == 2

    def test_two_by_two_blocked_diagonal(self):
        """2x2 with wall - can use diagonal to reachable cell"""
        grid = [
            [0, 0],
            [1, 0]
        ]
        # Can go diagonal: (0,0) -> (1,1) = 2 (directly via diagonal)
        assert shortest_path_binary_matrix(grid) == 2


class TestShortestPathBinaryMatrixDFS:
    """Test DFS implementation for consistency with BFS."""

    def test_consistency_with_bfs_basic(self):
        """DFS and BFS should produce same results"""
        grids = [
            [[0, 1], [1, 0]],
            [[0, 0, 0], [1, 1, 0], [1, 1, 0]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        ]
        for grid in grids:
            bfs_result = shortest_path_binary_matrix(grid)
            dfs_result = shortest_path_binary_matrix_dfs(grid)
            assert bfs_result == dfs_result, f"Mismatch for grid {grid}: BFS={bfs_result}, DFS={dfs_result}"

    def test_dfs_no_path(self):
        """DFS returns -1 when no path exists"""
        grid = [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ]
        assert shortest_path_binary_matrix_dfs(grid) == -1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
