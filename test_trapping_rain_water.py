"""Tests for LeetCode 42 - Trapping Rain Water."""

from trapping_rain_water import trap


def test_example_1() -> None:
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_example_2() -> None:
    assert trap([4, 2, 0, 3, 2, 5]) == 9


def test_empty() -> None:
    assert trap([]) == 0


def test_single_element() -> None:
    assert trap([5]) == 0


def test_two_elements() -> None:
    assert trap([3, 4]) == 0


def test_flat() -> None:
    assert trap([3, 3, 3, 3]) == 0


def test_ascending() -> None:
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending() -> None:
    assert trap([5, 4, 3, 2, 1]) == 0


def test_valley() -> None:
    assert trap([3, 0, 3]) == 3


def test_multiple_valleys() -> None:
    assert trap([5, 2, 1, 2, 1, 5]) == 14


def test_single_peak() -> None:
    assert trap([0, 1, 0]) == 0


def test_large_values() -> None:
    assert trap([100000, 0, 100000]) == 100000


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
