"""LeetCode #42 — Trapping Rain Water.

Implementation + focused pytest tests.
"""
from __future__ import annotations


def trap(height: list[int]) -> int:
    """Calculate trapped rainwater using two-pointer approach.

    For each position, water trapped = min(max_left, max_right) - height[i].
    Two pointers converge from both ends, maintaining running maxes.

    Time: O(n), Space: O(1).
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


# --------------- tests ---------------

class TestTrapRainWater:
    """Focused tests for LeetCode #42."""

    def test_leetcode_example1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_leetcode_example2(self) -> None:
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
        assert trap([3, 0, 3]) == 3

    def test_w_shape(self) -> None:
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_single_pool(self) -> None:
        assert trap([5, 1, 5]) == 4

    def test_asymmetric_walls(self) -> None:
        # Water bounded by shorter wall: 2 units
        assert trap([2, 0, 5]) == 2

    def test_plateau_middle(self) -> None:
        assert trap([5, 2, 2, 2, 5]) == 9

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0]) == 0

    def test_large_values(self) -> None:
        assert trap([10000, 0, 10000]) == 10000

    def test_staircase_up_down(self) -> None:
        assert trap([1, 2, 3, 2, 1]) == 0

    def test_complex_terrain(self) -> None:
        # [3,1,2,1,3]: pos1=2, pos2=1, pos3=2 → total 5
        assert trap([3, 1, 2, 1, 3]) == 5
