"""LeetCode #42 — Trapping Rain Water

Given n non-negative integers representing an elevation map where the width
of each bar is 1, compute how much water it can trap after raining.

Implementation uses the two-pointer O(n) time, O(1) space approach.
"""

from __future__ import annotations


def trap(height: list[int]) -> int:
    """Return total units of water trapped between bars.

    Two-pointer approach: maintain left/right pointers and track the
    running max height from each side. Water at any position is
    determined by the smaller of the two maxes minus the bar height.
    """
    if not height:
        return 0

    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0

    while left < right:
        if height[left] <= height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1

    return water


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestTrappingRainWater:
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
        # [3, 0, 3] -> traps 3 units in the middle
        assert trap([3, 0, 3]) == 3

    def test_deep_valley(self) -> None:
        # [5, 0, 0, 0, 5] -> 4 positions * 5 height = ... wait, 3 inner * 5 = 15
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_asymmetric_walls(self) -> None:
        # [3, 0, 2] -> water limited by min(3,2) = 2, middle holds 2
        assert trap([3, 0, 2]) == 2

    def test_staircase_up_down(self) -> None:
        # [0, 1, 2, 3, 2, 1, 0] -> pyramid, no water
        assert trap([0, 1, 2, 3, 2, 1, 0]) == 0

    def test_multiple_pools(self) -> None:
        # [3, 0, 3, 0, 3] -> two pools of 3 each
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_tall_edges_low_middle(self) -> None:
        # [10, 0, 0, 0, 0, 10] -> 4 * 10 = 40
        assert trap([10, 0, 0, 0, 0, 10]) == 40

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0]) == 0

    def test_single_trap_unit(self) -> None:
        # [1, 0, 1] -> 1 unit
        assert trap([1, 0, 1]) == 1

    # -- Larger / stress --

    def test_large_alternating(self) -> None:
        # [5, 0, 5, 0, 5, 0, 5] -> 3 pools of 5 = 15
        assert trap([5, 0, 5, 0, 5, 0, 5]) == 15

    def test_large_input(self) -> None:
        # 10000 elements, V shape: water = sum of (4999-i) for i in 0..4998 on each side
        n = 10000
        height = list(range(n // 2, -1, -1)) + list(range(1, n // 2 + 1))
        # Each side slopes down from 5000 to 0 and back up
        # Water at position i (left half, after peak) = 5000 - height[i]
        # By symmetry total = 2 * sum(i for i in range(1, 5000)) = 2 * 4999*5000/2
        expected = (n // 2 - 1) * (n // 2) // 2 * 2  # but middle 0 also holds 5000
        # Actually let's just compute it directly
        left_max_arr = []
        lm = 0
        for h in height:
            lm = max(lm, h)
            left_max_arr.append(lm)
        right_max_arr = []
        rm = 0
        for h in reversed(height):
            rm = max(rm, h)
            right_max_arr.append(rm)
        right_max_arr.reverse()
        expected = sum(
            min(left_max_arr[i], right_max_arr[i]) - height[i]
            for i in range(len(height))
        )
        assert trap(height) == expected
