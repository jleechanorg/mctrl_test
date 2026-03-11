"""LeetCode #42 — Trapping Rain Water

Implementation + focused tests.

Given n non-negative integers representing an elevation map where the width
of each bar is 1, compute how much water it can trap after raining.
"""
from __future__ import annotations


def trap(height: list[int]) -> int:
    """Two-pointer O(n) time, O(1) space solution."""
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


# --------------- tests ---------------

import pytest


class TestTrappingRainWater:
    """Focused tests for LeetCode #42."""

    # --- LeetCode examples ---

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    # --- Edge cases ---

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

    # --- Shape patterns ---

    def test_v_shape(self) -> None:
        # [3, 0, 3] traps 3 units
        assert trap([3, 0, 3]) == 3

    def test_deep_v(self) -> None:
        # [5, 0, 0, 0, 5] traps 15
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_asymmetric_v(self) -> None:
        # [3, 0, 2] — bounded by min(3,2)=2, traps 2
        assert trap([3, 0, 2]) == 2

    def test_w_shape(self) -> None:
        # Two valleys
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_staircase_up_down(self) -> None:
        # [0,1,2,3,2,1,0] — symmetric mountain, no water
        assert trap([0, 1, 2, 3, 2, 1, 0]) == 0

    def test_plateau_with_dip(self) -> None:
        # [4, 4, 1, 4, 4]
        assert trap([4, 4, 1, 4, 4]) == 3

    # --- Stress / larger inputs ---

    def test_alternating(self) -> None:
        # [5,0,5,0,5,0,5] — three pools of 5 each
        assert trap([5, 0, 5, 0, 5, 0, 5]) == 15

    def test_large_uniform_pool(self) -> None:
        # 1000-wide pool between two walls of height 1000
        height = [1000] + [0] * 998 + [1000]
        assert trap(height) == 998_000

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_single_trap_unit(self) -> None:
        assert trap([1, 0, 1]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
