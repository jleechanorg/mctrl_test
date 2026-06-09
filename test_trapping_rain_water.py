from __future__ import annotations

"""Tests for LeetCode 42 - Trapping Rain Water."""

from trapping_rain_water import trap


def test_example_1() -> None:
    """LeetCode example 1: [0,1,0,2,1,0,1,3,2,1,2,1] traps 6."""
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_example_2() -> None:
    """LeetCode example 2: [4,2,0,3,2,5] traps 9."""
    assert trap([4, 2, 0, 3, 2, 5]) == 9


def test_empty() -> None:
    """Empty array traps no water."""
    assert trap([]) == 0


def test_single_element() -> None:
    """Single bar cannot trap water."""
    assert trap([5]) == 0


def test_two_elements() -> None:
    """Two bars cannot trap water."""
    assert trap([3, 4]) == 0


def test_flat() -> None:
    """Flat elevation traps no water."""
    assert trap([3, 3, 3, 3]) == 0


def test_ascending() -> None:
    """Strictly ascending elevation traps no water."""
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending() -> None:
    """Strictly descending elevation traps no water."""
    assert trap([5, 4, 3, 2, 1]) == 0


def test_valley() -> None:
    """Simple valley [3,0,3] traps 3 units."""
    assert trap([3, 0, 3]) == 3


def test_multiple_valleys() -> None:
    """Multiple valleys [5,2,1,2,1,5] trap 14 units."""
    assert trap([5, 2, 1, 2, 1, 5]) == 14


def test_single_peak() -> None:
    """Single peak between two zeros traps no water."""
    assert trap([0, 1, 0]) == 0


def test_large_values() -> None:
    """Large-height valley [100000,0,100000] traps 100000 units."""
    assert trap([100000, 0, 100000]) == 100000


def test_invalid_inputs() -> None:
    """Validate input type and values."""
    import pytest
    with pytest.raises(TypeError):
        trap("not a list")  # type: ignore
    with pytest.raises(TypeError):
        trap([1, 2, "three"])  # type: ignore
    with pytest.raises(TypeError):
        trap([1, 2.5, 3])  # type: ignore
    with pytest.raises(ValueError):
        trap([1, -2, 3])

