from __future__ import annotations

import pytest

from orchestration.trapping_rain_water import trap


# ---------- LeetCode examples ----------

def test_example_1() -> None:
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_example_2() -> None:
    assert trap([4, 2, 0, 3, 2, 5]) == 9


# ---------- Edge cases ----------

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


# ---------- Shape patterns ----------

def test_v_shape() -> None:
    assert trap([3, 0, 3]) == 3


def test_deep_valley() -> None:
    assert trap([5, 0, 0, 0, 5]) == 15


def test_asymmetric_walls() -> None:
    assert trap([5, 0, 0, 0, 2]) == 6


def test_multiple_pools() -> None:
    # Two distinct pools: between 3-2 and between 2-3
    assert trap([3, 0, 2, 0, 3]) == 7


def test_staircase_up_down() -> None:
    assert trap([0, 1, 2, 3, 2, 1, 0]) == 0


def test_plateau_with_dip() -> None:
    assert trap([4, 4, 0, 4, 4]) == 4


# ---------- Larger inputs ----------

def test_all_zeros() -> None:
    assert trap([0] * 100) == 0


def test_single_peak() -> None:
    # Pyramid: no water trapped on a single peak
    h = list(range(50)) + list(range(50, -1, -1))
    assert trap(h) == 0


def test_bathtub() -> None:
    # Tall walls with zeros inside
    h = [10] + [0] * 98 + [10]
    assert trap(h) == 980


def test_sawtooth() -> None:
    # Repeating 0,1,0,1,... — no water (max height is 1, valleys are 0 between equal walls)
    h = [0, 1] * 50
    assert trap(h) == 0


def test_large_random_regression() -> None:
    """Compare two-pointer result against brute-force for a fixed sequence."""
    import random
    rng = random.Random(42)
    h = [rng.randint(0, 100) for _ in range(500)]

    # Brute-force O(n^2) reference
    n = len(h)
    expected = 0
    for i in range(n):
        l_max = max(h[: i + 1])
        r_max = max(h[i:])
        expected += min(l_max, r_max) - h[i]

    assert trap(h) == expected
