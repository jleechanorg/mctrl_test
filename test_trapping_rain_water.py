"""
Tests for LeetCode 42 - Trapping Rain Water
"""

from __future__ import annotations

import pytest
from trapping_rain_water import trap, trap_dp, trap_stack


class TestTrappingRainWater:
    """Test cases for trap function (two-pointer approach)."""

    def test_example1(self):
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example2(self):
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    def test_empty(self):
        assert trap([]) == 0

    def test_single_element(self):
        assert trap([0]) == 0

    def test_two_elements(self):
        assert trap([0, 1]) == 0
        assert trap([1, 0]) == 0

    def test_no_water_trapped(self):
        assert trap([1, 2, 3, 4, 5]) == 0
        assert trap([5, 4, 3, 2, 1]) == 0

    def test_flat_surface(self):
        assert trap([1, 1, 1, 1]) == 0

    def test_valley(self):
        assert trap([2, 0, 2]) == 2

    def test_multiple_valleys(self):
        assert trap([3, 0, 0, 2, 0, 4]) == 10

    def test_with_zeros(self):
        assert trap([0, 0, 0, 0]) == 0

    def test_single_bar_walls(self):
        # Only one side is bounded
        assert trap([2, 0, 2]) == 2
        assert trap([0, 2, 0]) == 0


class TestTrappingRainWaterDP:
    """Test cases for trap_dp (dynamic programming approach)."""

    def test_same_as_two_pointer(self):
        height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
        assert trap_dp(height) == trap(height)

    def test_example2(self):
        assert trap_dp([4, 2, 0, 3, 2, 5]) == 9


class TestTrappingRainWaterStack:
    """Test cases for trap_stack (monotonic stack approach)."""

    def test_same_as_two_pointer(self):
        height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
        assert trap_stack(height) == trap(height)

    def test_example2(self):
        assert trap_stack([4, 2, 0, 3, 2, 5]) == 9


class TestAllMethods:
    """Verify all methods produce the same results."""

    @pytest.mark.parametrize(
        "height",
        [
            [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],
            [4, 2, 0, 3, 2, 5],
            [1, 0, 1],
            [5, 4, 1, 2],
            [1, 2, 3, 4, 5],
            [],
            [0],
            [1, 2, 3, 2, 1],
        ],
    )
    def test_all_methods_equal(self, height):
        """All three approaches should produce the same result."""
        assert trap(height) == trap_dp(height) == trap_stack(height)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
