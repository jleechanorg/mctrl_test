"""
Test cases for Trapping Rain Water (LeetCode 42)

Comprehensive test suite covering various edge cases and scenarios.
"""

import pytest
from trapping_rain_water import trap, trap_two_pointer, trap_stack, trap_brute_force


class TestTrapRainWater:
    """Test cases for trap function."""

    def test_example_case(self):
        """Example from LeetCode: height = [0,1,0,2,1,0,1,3,2,1,2,1]"""
        height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
        assert trap(height) == 6

    def test_no_water_trapped(self):
        """No water when there's no valley (strictly increasing/decreasing)."""
        # Strictly increasing - no water
        height = [1, 2, 3, 4, 5]
        assert trap(height) == 0

        # Strictly decreasing - no water
        height = [5, 4, 3, 2, 1]
        assert trap(height) == 0

        # Flat - no water
        height = [3, 3, 3, 3]
        assert trap(height) == 0

    def test_simple_valley(self):
        """Simple valley shape."""
        height = [2, 0, 2]
        assert trap(height) == 2

    def test_deep_valley(self):
        """Deep valley with multiple bars."""
        height = [5, 4, 1, 2]
        assert trap(height) == 1  # Water level at 1, trapped = (1-1) + (2-1) = 1

    def test_multiple_valleys(self):
        """Multiple valleys."""
        height = [0, 5, 0, 3, 0, 5, 0]
        # Valley 1 (index 2): min(5,5) - 0 = 5
        # Middle (index 3): min(5,5) - 3 = 2
        # Valley 2 (index 4): min(5,5) - 0 = 5
        # Total: 5 + 2 + 5 = 12
        assert trap(height) == 12

    def test_empty_input(self):
        """Empty array returns 0."""
        assert trap([]) == 0

    def test_single_element(self):
        """Single element returns 0."""
        assert trap([5]) == 0
        assert trap([0]) == 0

    def test_two_elements(self):
        """Two elements cannot trap water."""
        assert trap([1, 2]) == 0
        assert trap([2, 1]) == 0

    def test_all_zero(self):
        """All zeros returns 0 (water level equals ground)."""
        height = [0, 0, 0, 0]
        assert trap(height) == 0

    def test_large_values(self):
        """Works with large height values."""
        height = [10, 0, 10]
        assert trap(height) == 10

    def test_wave_pattern(self):
        """Wave pattern with alternating peaks and valleys."""
        height = [1, 0, 1, 0, 1, 0, 1]
        # Trapped: 0+1+0+1+0+1 = 3
        assert trap(height) == 3

    def test_trap_at_edges(self):
        """Edge cases where water would be at edges (not counted)."""
        # Water at start and end is not counted (no boundary on one side)
        height = [1, 0, 1]
        assert trap(height) == 1

    def test_symmetric_array(self):
        """Symmetric height array."""
        height = [4, 2, 0, 3, 2, 4]
        # Water: index 2 gets 2, index 3 gets 1
        # Actually: min(2,2) - 0 = 2, min(4,4) - 3 = 1
        assert trap(height) == 9

    def test_ascending_then_descending(self):
        """Mountain shape - no water trapped."""
        height = [1, 2, 3, 4, 5, 4, 3, 2, 1]
        assert trap(height) == 0

    def test_single_deep_valley(self):
        """Single deep valley in middle."""
        height = [3, 0, 0, 0, 3]
        # Water level is 3, each inner bar is 0, 3*(3-0) = 9
        assert trap(height) == 9


class TestTwoPointer:
    """Test that two_pointer matches stack solution."""

    @pytest.mark.parametrize("height", [
        [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],
        [1, 0, 1],
        [5, 4, 1, 2],
        [],
        [1, 2, 3, 4, 5],
    ])
    def test_equals_stack_solution(self, height):
        """Two-pointer and stack solutions should match."""
        assert trap_two_pointer(height) == trap_stack(height)


class TestBruteForce:
    """Test brute force against optimized solutions."""

    @pytest.mark.parametrize("height", [
        [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],
        [2, 0, 2],
        [3, 0, 0, 0, 3],
        [1, 0, 1],
    ])
    def test_equals_optimized(self, height):
        """Brute force should match optimized solutions."""
        expected = trap_two_pointer(height)
        assert trap_brute_force(height) == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
