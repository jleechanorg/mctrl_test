from __future__ import annotations

import copy

import pytest

from num_islands import num_islands


def test_example_from_problem():
    """Test the example provided in the problem statement."""
    grid = [
        ['1', '1', '1', '1', '0'],
        ['1', '1', '0', '1', '0'],
        ['1', '1', '0', '0', '0'],
        ['0', '0', '0', '0', '0']
    ]
    assert num_islands(grid) == 1


def test_single_island():
    """Test a grid with a single island."""
    grid = [
        ['1', '1', '1'],
        ['1', '1', '1'],
        ['1', '1', '1']
    ]
    assert num_islands(grid) == 1


def test_multiple_islands():
    """Test a grid with multiple islands."""
    grid = [
        ['1', '1', '0', '0', '0'],
        ['1', '1', '0', '0', '0'],
        ['0', '0', '1', '0', '0'],
        ['0', '0', '0', '1', '1']
    ]
    assert num_islands(grid) == 3


def test_no_islands():
    """Test a grid with no islands (all water)."""
    grid = [
        ['0', '0', '0'],
        ['0', '0', '0'],
        ['0', '0', '0']
    ]
    assert num_islands(grid) == 0


def test_all_land():
    """Test a grid with all land."""
    grid = [
        ['1', '1', '1'],
        ['1', '1', '1']
    ]
    assert num_islands(grid) == 1


def test_single_cell_land():
    """Test a grid with a single land cell."""
    grid = [['1']]
    assert num_islands(grid) == 1


def test_single_cell_water():
    """Test a grid with a single water cell."""
    grid = [['0']]
    assert num_islands(grid) == 0


def test_empty_grid():
    """Test an empty grid."""
    assert num_islands([]) == 0


def test_empty_row():
    """Test a grid with empty row."""
    assert num_islands([[]]) == 0


def test_large_grid():
    """Test a larger grid with scattered islands."""
    grid = [
        ['1', '1', '1', '1', '0'],
        ['1', '1', '0', '1', '0'],
        ['1', '1', '0', '0', '0'],
        ['0', '0', '0', '0', '0'],
        ['1', '0', '1', '0', '1'],
        ['0', '1', '0', '1', '0'],
        ['1', '1', '1', '1', '1']
    ]
    assert num_islands(grid) == 5


def test_grid_not_modified():
    """Test that the original grid is not modified."""
    grid = [
        ['1', '1', '0'],
        ['1', '1', '0'],
        ['0', '0', '1']
    ]
    grid_copy = copy.deepcopy(grid)
    result = num_islands(grid)
    assert result == 3  # Verify the count is correct
    assert grid == grid_copy  # Verify original grid is unchanged
