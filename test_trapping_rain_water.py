"""
Tests for Trapping Rain Water solution.
"""

import pytest
from trapping_rain_water import trap, trap_dp, trap_stack


class TestTrap:
    """Test cases for trap (two-pointer solution)."""

    def test_example_1(self):
        """Example from LeetCode problem."""
        height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
        assert trap(height) == 6

    def test_example_2(self):
        """Second example from LeetCode."""
        height = [4, 2, 0, 3, 2, 5]
        assert trap(height) == 9

    def test_no_water_trapped_flat(self):
        """Flat surface traps no water."""
        height = [1, 1, 1, 1, 1]
        assert trap(height) == 0

    def test_no_water_trapped_zero(self):
        """All zeros."""
        height = [0, 0, 0, 0]
        assert trap(height) == 0

    def test_single_element(self):
        """Single element."""
        height = [5]
        assert trap(height) == 0

    def test_two_elements(self):
        """Two elements cannot trap water."""
        height = [1, 2]
        assert trap(height) == 0

    def test_descending(self):
        """Descending height traps no water."""
        height = [5, 4, 3, 2, 1]
        assert trap(height) == 0

    def test_ascending(self):
        """Ascending height traps no water."""
        height = [1, 2, 3, 4, 5]
        assert trap(height) == 0

    def test_bowl_shape(self):
        """Bowl shape traps maximum water."""
        height = [5, 4, 3, 2, 1, 2, 3, 4, 5]
        assert trap(height) == 16

    def test_single_depression(self):
        """Single depression in middle."""
        height = [5, 0, 5]
        assert trap(height) == 5

    def test_multiple_small_depressions(self):
        """Multiple small depressions."""
        height = [3, 0, 2, 0, 4]
        assert trap(height) == 7

    def test_large_values(self):
        """Test with larger height values."""
        height = [5, 4, 1, 2]
        assert trap(height) == 1

    def test_alternating_high_low(self):
        """Alternating pattern."""
        height = [1, 0, 1]
        assert trap(height) == 1


class TestTrapDP:
    """Test cases for trap_dp (dynamic programming solution)."""

    def test_example_1(self):
        height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
        assert trap_dp(height) == 6

    def test_example_2(self):
        height = [4, 2, 0, 3, 2, 5]
        assert trap_dp(height) == 9

    def test_no_water(self):
        height = [1, 2, 3, 4, 5]
        assert trap_dp(height) == 0


class TestTrapStack:
    """Test cases for trap_stack (monotonic stack solution)."""

    def test_example_1(self):
        height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
        assert trap_stack(height) == 6

    def test_example_2(self):
        height = [4, 2, 0, 3, 2, 5]
        assert trap_stack(height) == 9

    def test_no_water(self):
        height = [1, 2, 3, 4, 5]
        assert trap_stack(height) == 0


class TestAllSolutions:
    """Verify all solutions produce the same results."""

    @pytest.mark.parametrize(
        "height",
        [
            [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],
            [4, 2, 0, 3, 2, 5],
            [5, 4, 1, 2],
            [0, 0, 0, 0],
            [1, 2, 3, 4, 5],
            [5, 4, 3, 2, 1],
            [3, 0, 2, 0, 4],
        ],
    )
    def test_all_solutions_equal(self, height):
        """All three solutions should produce identical results."""
        assert trap(height) == trap_dp(height) == trap_stack(height)
