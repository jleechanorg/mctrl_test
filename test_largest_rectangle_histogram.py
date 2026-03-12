"""
Tests for Largest Rectangle in Histogram solution.
"""
import pytest
from largest_rectangle_histogram import largest_rectangle_area, largest_rectangle_area_2


class TestLargestRectangleHistogram:
    """Test cases for the largest rectangle in histogram problem."""

    def test_example_cases(self):
        """Test the provided examples."""
        assert largest_rectangle_area([2, 1, 5, 6, 2, 3]) == 10
        assert largest_rectangle_area([2, 4]) == 4
        assert largest_rectangle_area_2([2, 1, 5, 6, 2, 3]) == 10
        assert largest_rectangle_area_2([2, 4]) == 4

    def test_increasing_heights(self):
        """Test with strictly increasing heights."""
        # [1,2,3,4,5] - best rectangle is height 2 spanning 4 bars = 8
        # Wait, let me recalculate:
        # heights: [1, 2, 3, 4, 5]
        # Best: height=3 with width=3 (indices 2,3,4) = 9
        assert largest_rectangle_area([1, 2, 3, 4, 5]) == 9
        assert largest_rectangle_area_2([1, 2, 3, 4, 5]) == 9

    def test_decreasing_heights(self):
        """Test with strictly decreasing heights."""
        # [5,4,3,2,1] - best is height=1 with width=5 = 5
        # Actually height=2 with width=4 = 8
        # height=3 with width=3 = 9
        assert largest_rectangle_area([5, 4, 3, 2, 1]) == 9
        assert largest_rectangle_area_2([5, 4, 3, 2, 1]) == 9

    def test_equal_heights(self):
        """Test with equal heights."""
        assert largest_rectangle_area([1, 1, 1, 1]) == 4
        assert largest_rectangle_area([2, 2, 2]) == 6
        assert largest_rectangle_area_2([1, 1, 1, 1]) == 4

    def test_single_element(self):
        """Test with a single element."""
        assert largest_rectangle_area([1]) == 1
        assert largest_rectangle_area([5]) == 5
        assert largest_rectangle_area_2([1]) == 1

    def test_empty_array(self):
        """Test with empty array."""
        assert largest_rectangle_area([]) == 0
        assert largest_rectangle_area_2([]) == 0

    def test_two_elements(self):
        """Test with two elements."""
        assert largest_rectangle_area([1, 2]) == 2
        assert largest_rectangle_area([2, 1]) == 2
        assert largest_rectangle_area_2([1, 2]) == 2

    def test_large_values(self):
        """Test with larger height values."""
        assert largest_rectangle_area([10000]) == 10000
        assert largest_rectangle_area([1, 10000, 1]) == 10000

    def test_complex_case(self):
        """Test a more complex histogram."""
        # [6, 2, 5, 4, 5, 1, 6]
        # Best: height=4 with width=4 (indices 1-4) = 16
        assert largest_rectangle_area([6, 2, 5, 4, 5, 1, 6]) == 12

    def test_all_zero_heights(self):
        """Test with all zeros."""
        assert largest_rectangle_area([0, 0, 0]) == 0

    def test_alternating_heights(self):
        """Test with alternating high-low pattern."""
        # [1,3,3,2,4,1,5,3,2,9,0,7]
        # The max is height=5 spanning 2 bars = 10, or height=1 spanning 10 bars = 10
        assert largest_rectangle_area([1, 3, 3, 2, 4, 1, 5, 3, 2, 9, 0, 7]) == 10
        assert largest_rectangle_area_2([1, 3, 3, 2, 4, 1, 5, 3, 2, 9, 0, 7]) == 10

    def test_both_solutions_equal(self):
        """Verify both solutions produce the same results."""
        test_cases = [
            [2, 1, 5, 6, 2, 3],
            [2, 4],
            [1, 2, 3, 4, 5],
            [5, 4, 3, 2, 1],
            [1, 1, 1, 1],
            [1],
            [],
            [6, 2, 5, 4, 5, 1, 6],
            [1, 3, 3, 2, 4, 1, 5, 3, 2, 9, 0, 7],
        ]

        for heights in test_cases:
            assert largest_rectangle_area(heights) == largest_rectangle_area_2(heights)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
