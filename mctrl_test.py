"""LeetCode #42 — Trapping Rain Water

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


# --------------- tests ---------------

def test_classic_example() -> None:
    """The classic LeetCode example 1."""
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_example_2() -> None:
    """LeetCode example 2."""
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


def test_v_shape() -> None:
    """Simple valley: 3 0 3 → traps 3."""
    assert trap([3, 0, 3]) == 3


def test_deep_valley() -> None:
    """5 0 0 0 5 → traps 15."""
    assert trap([5, 0, 0, 0, 5]) == 15


def test_asymmetric_walls() -> None:
    """Shorter wall limits water: 2 0 5 → traps 2."""
    assert trap([2, 0, 5]) == 2


def test_multiple_valleys() -> None:
    """3 0 3 0 3 → two valleys of 3 each = 6."""
    assert trap([3, 0, 3, 0, 3]) == 6


def test_staircase_up_down() -> None:
    """0 1 2 3 2 1 0 → no trapping (pyramid)."""
    assert trap([0, 1, 2, 3, 2, 1, 0]) == 0


def test_plateau_with_dip() -> None:
    """5 5 1 5 5 → traps 4."""
    assert trap([5, 5, 1, 5, 5]) == 4


def test_large_values() -> None:
    """Works with large bar heights."""
    assert trap([100000, 0, 100000]) == 100000


def test_all_zeros() -> None:
    assert trap([0, 0, 0, 0]) == 0


def test_single_trap_unit() -> None:
    """1 0 1 → traps exactly 1."""
    assert trap([1, 0, 1]) == 1
