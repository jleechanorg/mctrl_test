"""Tests for Number of Islands solution."""

import pytest
from src.num_islands import Solution


class TestNumIslands:
    def setup_method(self):
        self.sol = Solution()
    
    def test_basic_example(self):
        """Test the basic example from LeetCode."""
        grid = [
            ["1", "1", "1", "1", "0"],
            ["1", "1", "0", "1", "0"],
            ["1", "1", "0", "0", "0"],
            ["0", "0", "0", "0", "0"]
        ]
        assert self.sol.numIslands(grid) == 1
    
    def test_multiple_islands(self):
        """Test with multiple separate islands."""
        grid = [
            ["1", "1", "0", "0", "0"],
            ["1", "1", "0", "0", "0"],
            ["0", "0", "1", "0", "0"],
            ["0", "0", "0", "1", "1"]
        ]
        assert self.sol.numIslands(grid) == 3
    
    def test_no_islands(self):
        """Test with no land cells."""
        grid = [
            ["0", "0"],
            ["0", "0"]
        ]
        assert self.sol.numIslands(grid) == 0
    
    def test_single_island_cell(self):
        """Test with a single island cell."""
        grid = [["1"]]
        assert self.sol.numIslands(grid) == 1
    
    def test_empty_grid(self):
        """Test with empty grid."""
        assert self.sol.numIslands([]) == 0
        assert self.sol.numIslands([[]]) == 0
    
    def test_all_land(self):
        """Test when all cells are land."""
        grid = [
            ["1", "1"],
            ["1", "1"]
        ]
        assert self.sol.numIslands(grid) == 1
    
    def test_all_water(self):
        """Test when all cells are water."""
        grid = [
            ["0", "0", "0"],
            ["0", "0", "0"]
        ]
        assert self.sol.numIslands(grid) == 0
    
    def test_single_row(self):
        """Test with a single row."""
        grid = [["1", "0", "1", "1", "0"]]
        assert self.sol.numIslands(grid) == 2
    
    def test_single_column(self):
        """Test with a single column."""
        grid = [
            ["1"],
            ["1"],
            ["0"],
            ["1"]
        ]
        assert self.sol.numIslands(grid) == 2
