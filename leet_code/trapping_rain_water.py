"""
Trapping Rain Water - LeetCode Hard #42

Given n non-negative integers representing an elevation map where the width
of each bar is 1, compute how much water it can trap after raining.

Example 1:
Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6

Example 2:
Input: height = [4,2,0,3,2,5]
Output: 9

Constraints:
- n == height.length
- 1 <= n <= 2 * 10^4
- 0 <= height[i] <= 10^5

Time Complexity: O(n)
Space Complexity: O(1) using two-pointer approach
"""

from __future__ import annotations
from typing import List


def trap(height: List[int]) -> int:
    """
    Calculate trapped rain water using two-pointer technique.

    The key insight: water at any position is determined by
    min(max_left, max_right) - height[position].

    Two pointers converge from both ends. We track the running
    max from each side. The pointer with the smaller max moves
    inward, because water at that side is bounded by its own max
    (the other side is guaranteed to be at least as tall).

    Args:
        height: List of non-negative integers representing elevation map.

    Returns:
        Total units of trapped water.
    """
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


# --------------- pytest tests ---------------

def test_example_1() -> None:
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_example_2() -> None:
    assert trap([4, 2, 0, 3, 2, 5]) == 9


def test_no_bars() -> None:
    assert trap([]) == 0


def test_single_bar() -> None:
    assert trap([5]) == 0


def test_two_bars() -> None:
    assert trap([3, 4]) == 0


def test_flat() -> None:
    assert trap([3, 3, 3, 3]) == 0


def test_ascending() -> None:
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending() -> None:
    assert trap([5, 4, 3, 2, 1]) == 0


def test_v_shape() -> None:
    # walls of 3, valley of 0 => 3 units
    assert trap([3, 0, 3]) == 3


def test_deep_valley() -> None:
    assert trap([5, 0, 0, 0, 5]) == 15


def test_multiple_valleys() -> None:
    # Two separate pools
    assert trap([3, 0, 3, 0, 3]) == 6


def test_staircase_then_drop() -> None:
    assert trap([0, 1, 2, 3, 2, 1, 0]) == 0


def test_large_values() -> None:
    assert trap([100000, 0, 100000]) == 100000


def test_single_trap() -> None:
    assert trap([2, 0, 2]) == 2


def test_asymmetric_walls() -> None:
    # Water bounded by shorter wall (2), depth 2 at middle
    assert trap([5, 0, 2]) == 2


def test_complex_terrain() -> None:
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_all_zeros() -> None:
    assert trap([0, 0, 0, 0]) == 0


def test_plateau_with_dip() -> None:
    assert trap([4, 4, 0, 4, 4]) == 4


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
