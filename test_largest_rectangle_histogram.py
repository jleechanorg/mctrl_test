"""
Unit tests for LeetCode 84: Largest Rectangle in Histogram
"""

import pytest
from largest_rectangle_histogram import largest_rectangle_area, largest_rectangle_area_brute


class TestLargestRectangleArea:
    """Test cases for largest rectangle in histogram."""

    def test_basic_case(self):
        """Test the classic example from LeetCode."""
        heights = [2, 1, 5, 6, 2, 3]
        assert largest_rectangle_area(heights) == 10

    def test_two_bars(self):
        """Test with two bars."""
        heights = [2, 4]
        assert largest_rectangle_area(heights) == 4

    def test_single_bar(self):
        """Test with single bar."""
        heights = [1]
        assert largest_rectangle_area(heights) == 1

    def test_equal_height_bars(self):
        """Test with all equal heights."""
        heights = [1, 1]
        assert largest_rectangle_area(heights) == 2

    def test_zero_height_bars(self):
        """Test with zero height bars."""
        heights = [0, 0]
        assert largest_rectangle_area(heights) == 0

    def test_increasing_heights(self):
        """Test with strictly increasing heights."""
        heights = [1, 2, 3, 4, 5]
        assert largest_rectangle_area(heights) == 9  # 3 bars of height 3,4,5: 3*3

    def test_decreasing_heights(self):
        """Test with strictly decreasing heights."""
        heights = [5, 4, 3, 2, 1]
        assert largest_rectangle_area(heights) == 9

    def test_valley(self):
        """Test with valley shape - min in middle."""
        heights = [2, 1, 2]
        assert largest_rectangle_area(heights) == 3

    def test_empty(self):
        """Test with empty array."""
        assert largest_rectangle_area([]) == 0

    def test_large_heights(self):
        """Test with large height values."""
        heights = [10000] * 10000
        assert largest_rectangle_area(heights) == 10000 * 10000


class TestLargestRectangleAreaConsistency:
    """Verify optimized solution matches brute force."""

    @pytest.mark.parametrize("heights", [
        [2, 1, 5, 6, 2, 3],
        [2, 4],
        [1],
        [1, 1],
        [0, 0],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [2, 1, 2],
        [1, 3, 2, 5, 4, 6],
        [3, 6, 5, 7, 1, 8],
    ])
    def test_matches_brute_force(self, heights):
        """Verify optimized solution produces same result as brute force."""
        opt_result = largest_rectangle_area(heights)
        brute_result = largest_rectangle_area_brute(heights)
        assert opt_result == brute_result
