"""LeetCode #42 — Trapping Rain Water

Given n non-negative integers representing an elevation map where the width
of each bar is 1, compute how much water it can trap after raining.

Implementation uses the two-pointer O(n) time, O(1) space approach.
"""
from __future__ import annotations


def trap(height: list[int]) -> int:
    """Return total units of water trapped between bars.

    Two-pointer approach:
    - Maintain left/right pointers and track max heights from each side.
    - The shorter side determines the water level at each step.
    - Move the pointer on the shorter side inward.
    """
    if not height:
        return 0

    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0

    while left < right:
        if left_max <= right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]

    return water


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
import pytest


class TestTrapRainWater:
    """Focused tests for LeetCode #42."""

    # -- LeetCode provided examples --

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    # -- Edge cases --

    def test_empty(self) -> None:
        assert trap([]) == 0

    def test_single_bar(self) -> None:
        assert trap([5]) == 0

    def test_two_bars(self) -> None:
        assert trap([3, 7]) == 0

    def test_flat(self) -> None:
        assert trap([3, 3, 3, 3]) == 0

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    # -- Structural patterns --

    def test_v_shape(self) -> None:
        # [3, 0, 3] traps 3 units in the middle
        assert trap([3, 0, 3]) == 3

    def test_deep_valley(self) -> None:
        # [5, 0, 0, 0, 5] traps 5*3 = 15
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_asymmetric_walls(self) -> None:
        # [2, 0, 5] — water bounded by shorter wall: 2 units
        assert trap([2, 0, 5]) == 2

    def test_multiple_valleys(self) -> None:
        # [3, 0, 3, 0, 3] — two valleys of 3 each
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_staircase_up_down(self) -> None:
        # [0, 1, 2, 3, 2, 1, 0] — pyramid, no water
        assert trap([0, 1, 2, 3, 2, 1, 0]) == 0

    def test_tall_boundaries_low_middle(self) -> None:
        # [10, 1, 1, 1, 10] — traps 9*3 = 27
        assert trap([10, 1, 1, 1, 10]) == 27

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    # -- Larger / stress --

    def test_alternating(self) -> None:
        # [5, 0, 5, 0, 5] — two pools of 5
        assert trap([5, 0, 5, 0, 5]) == 10

    def test_large_input(self) -> None:
        # 10k bars — should complete quickly
        n = 10_000
        height = [n - abs(n // 2 - i) for i in range(n)]
        result = trap(height)
        assert result >= 0  # sanity — main goal is no timeout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
