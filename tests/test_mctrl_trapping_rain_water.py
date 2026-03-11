"""LeetCode #42 — Trapping Rain Water.

Implementation + focused tests.
"""
from __future__ import annotations


def trap(height: list[int]) -> int:
    """Calculate trapped rain water using two-pointer approach. O(n) time, O(1) space."""
    if len(height) < 3:
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

class TestTrapRainWater:
    """Focused tests for LeetCode #42."""

    def test_classic_example(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_second_example(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

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

    def test_v_shape(self) -> None:
        # [3, 0, 3] traps 3 units
        assert trap([3, 0, 3]) == 3

    def test_w_shape(self) -> None:
        # [3, 0, 3, 0, 3] traps 6 units
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_single_trap(self) -> None:
        assert trap([2, 0, 2]) == 2

    def test_asymmetric(self) -> None:
        # [5, 0, 3] traps 3 (bounded by min(5,3)=3, minus 0)
        assert trap([5, 0, 3]) == 3

    def test_plateau_with_dip(self) -> None:
        assert trap([4, 4, 0, 4, 4]) == 4

    def test_large_values(self) -> None:
        assert trap([100000, 0, 100000]) == 100000

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_deep_pool(self) -> None:
        # [5, 1, 1, 1, 5] → 4*3 = 12
        assert trap([5, 1, 1, 1, 5]) == 12

    def test_staircase_up_down(self) -> None:
        # [1, 2, 3, 2, 1] — pyramid, no water trapped
        assert trap([1, 2, 3, 2, 1]) == 0

    def test_multiple_pools(self) -> None:
        # [3, 0, 1, 0, 3] → pool1: 3+2=5, pool2: 3 → total 8
        assert trap([3, 0, 1, 0, 3]) == 8
