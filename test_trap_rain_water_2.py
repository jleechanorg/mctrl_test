from __future__ import annotations

import pytest
from trap_rain_water_2 import trap_rain_water_2


def test_example_from_problem():
    """Test the example from the problem statement."""
    height_map = [
        [1, 4, 3, 1, 3, 2],
        [3, 2, 1, 3, 2, 4],
        [2, 3, 3, 2, 3, 1],
    ]
    assert trap_rain_water_2(height_map) == 4


def test_no_water_trapped_flat_terrain():
    """Test flat terrain - no water should be trapped."""
    height_map = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1],
    ]
    assert trap_rain_water_2(height_map) == 0


def test_no_water_trapped_single_row():
    """Test single row - no water can be trapped."""
    height_map = [[1, 2, 3, 2, 1]]
    assert trap_rain_water_2(height_map) == 0


def test_no_water_trapped_single_column():
    """Test single column - no water can be trapped."""
    height_map = [[1], [2], [3], [2], [1]]
    assert trap_rain_water_2(height_map) == 0


def test_no_water_trapped_too_small():
    """Test too small matrix - no water can be trapped."""
    assert trap_rain_water_2([[1]]) == 0
    assert trap_rain_water_2([[1, 2]]) == 0
    assert trap_rain_water_2([[1], [2]]) == 0


def test_bowl_shape():
    """Test bowl shape - water should be trapped in the middle."""
    height_map = [
        [5, 5, 5, 5, 5],
        [5, 1, 1, 1, 5],
        [5, 1, 1, 1, 5],
        [5, 5, 5, 5, 5],
    ]
    # Interior: 2 rows x 3 cols = 6 cells at height 1, border at height 5
    # Water trapped: 6 * (5-1) = 24
    assert trap_rain_water_2(height_map) == 24


def test_multiple_basins():
    """Test multiple basins - water trapped in multiple depressions."""
    height_map = [
        [3, 3, 3, 3, 3, 3],
        [3, 1, 1, 3, 1, 3],
        [3, 1, 1, 3, 1, 3],
        [3, 3, 3, 3, 3, 3],
    ]
    # 6 interior cells at height 1, border at height 3
    # Water trapped: 6 * (3-1) = 12
    assert trap_rain_water_2(height_map) == 12


def test_empty_matrix():
    """Test empty matrix - should return 0."""
    assert trap_rain_water_2([]) == 0
    assert trap_rain_water_2([[]]) == 0


def test_returns_integer():
    """Test that the function returns an integer."""
    height_map = [[1, 2], [2, 1]]
    result = trap_rain_water_2(height_map)
    assert isinstance(result, int)


def test_large_border_small_interior():
    """Test large border with small interior."""
    height_map = [
        [10, 10, 10, 10, 10],
        [10, 1, 1, 1, 10],
        [10, 1, 1, 1, 10],
        [10, 1, 1, 1, 10],
        [10, 10, 10, 10, 10],
    ]
    # Interior is at height 1, border at height 10
    # Water trapped in 3x3 interior: (10-1) * 9 = 81
    assert trap_rain_water_2(height_map) == 81


def test_sloped_terrain():
    """Test sloped terrain from one side."""
    height_map = [
        [1, 2, 3, 4, 5],
        [1, 2, 3, 4, 5],
        [1, 2, 3, 4, 5],
    ]
    # No enclosed basin - water flows off
    assert trap_rain_water_2(height_map) == 0


def test_peak_in_middle():
    """Test peak in the middle - water drains around it."""
    height_map = [
        [5, 5, 5, 5, 5],
        [5, 3, 3, 3, 5],
        [5, 3, 5, 3, 5],
        [5, 3, 3, 3, 5],
        [5, 5, 5, 5, 5],
    ]
    # 8 cells around the peak at height 3, border at height 5
    # Water trapped: 8 * (5-3) = 16
    assert trap_rain_water_2(height_map) == 16


def test_large_matrix_200x200():
    """Test with maximum size matrix (200x200) - sanity check."""
    n = 200
    # Simple bowl shape
    height_map = [[10] * n for _ in range(n)]
    for i in range(1, n - 1):
        for j in range(1, n - 1):
            height_map[i][j] = 1

    # (n-2)^2 cells with water depth 9
    expected = (n - 2) * (n - 2) * 9
    assert trap_rain_water_2(height_map) == expected
