"""Tests for LeetCode 42 - Trapping Rain Water."""

from __future__ import annotations

from trapping_rain_water import trap


def test_example_1() -> None:
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_example_2() -> None:
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
    assert trap([5, 0, 5]) == 5


def test_multiple_valleys() -> None:
    assert trap([3, 0, 2, 0, 4]) == 7


def test_all_zeros() -> None:
    assert trap([0, 0, 0]) == 0


def test_large_values() -> None:
    assert trap([100000, 0, 100000]) == 100000


if __name__ == "__main__":
    import sys
    # Run all test functions
    failed = 0
    for name, obj in list(globals().items()):
        if name.startswith("test_") and callable(obj):
            try:
                obj()
                print(f"PASS: {name}")
            except AssertionError as e:
                print(f"FAIL: {name} - {e}")
                failed += 1
    sys.exit(failed)
