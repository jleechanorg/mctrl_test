"""LeetCode #42 — Trapping Rain Water

Two-pointer O(n) time, O(1) space solution + focused tests.
"""
from __future__ import annotations


def trap(height: list[int]) -> int:
    """Calculate trapped rain water using two pointers."""
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


# --------------- Tests ---------------

def test_leetcode_example_1() -> None:
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_leetcode_example_2() -> None:
    assert trap([4, 2, 0, 3, 2, 5]) == 9


def test_empty() -> None:
    assert trap([]) == 0


def test_single_bar() -> None:
    assert trap([5]) == 0


def test_two_bars() -> None:
    assert trap([3, 7]) == 0


def test_flat() -> None:
    assert trap([3, 3, 3, 3]) == 0


def test_ascending() -> None:
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending() -> None:
    assert trap([5, 4, 3, 2, 1]) == 0


def test_valley() -> None:
    # 3 _ _ 3  ->  water = 3+3 = 6
    assert trap([3, 0, 0, 3]) == 6


def test_multiple_valleys() -> None:
    # 5 0 5 0 5  ->  two valleys of depth 5 each
    assert trap([5, 0, 5, 0, 5]) == 10


def test_single_trap() -> None:
    assert trap([2, 0, 2]) == 2


def test_asymmetric_walls() -> None:
    # min(1,3)=1, trapped at index 1 = 1-0 = 1
    assert trap([1, 0, 3]) == 1


def test_large_uniform_valley() -> None:
    # 100 bars of 0 between two walls of height 100
    height = [100] + [0] * 100 + [100]
    assert trap(height) == 100 * 100


def test_staircase_up_down() -> None:
    # 1 2 3 4 3 2 1 — pyramid, no water trapped
    assert trap([1, 2, 3, 4, 3, 2, 1]) == 0


def test_all_zeros() -> None:
    assert trap([0, 0, 0, 0]) == 0
