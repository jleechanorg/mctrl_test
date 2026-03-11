"""Focused tests for LeetCode #42 — Trapping Rain Water.

Tests all three implementations against the same cases to ensure correctness.
"""

from __future__ import annotations

import pytest

from orchestration.trapping_rain_water import (
    trap_prefix_max,
    trap_stack,
    trap_two_pointer,
)

IMPLEMENTATIONS = [trap_two_pointer, trap_stack, trap_prefix_max]


@pytest.fixture(params=IMPLEMENTATIONS, ids=lambda f: f.__name__)
def trap(request: pytest.FixtureRequest):
    return request.param


# --- LeetCode examples ---


def test_example_1(trap) -> None:
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_example_2(trap) -> None:
    assert trap([4, 2, 0, 3, 2, 5]) == 9


# --- Edge cases ---


def test_empty(trap) -> None:
    assert trap([]) == 0


def test_single(trap) -> None:
    assert trap([5]) == 0


def test_two_elements(trap) -> None:
    assert trap([3, 7]) == 0


def test_flat(trap) -> None:
    assert trap([3, 3, 3, 3]) == 0


def test_ascending(trap) -> None:
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending(trap) -> None:
    assert trap([5, 4, 3, 2, 1]) == 0


def test_v_shape(trap) -> None:
    # [3, 0, 3] traps 3 units
    assert trap([3, 0, 3]) == 3


def test_all_zeros(trap) -> None:
    assert trap([0, 0, 0, 0]) == 0


# --- Structural patterns ---


def test_single_valley(trap) -> None:
    assert trap([2, 0, 2]) == 2


def test_deep_valley(trap) -> None:
    assert trap([5, 0, 0, 0, 5]) == 15


def test_multiple_valleys(trap) -> None:
    # [3,0,3,0,3] = 3 + 3 = 6
    assert trap([3, 0, 3, 0, 3]) == 6


def test_staircase_up_down(trap) -> None:
    # [0,1,2,3,2,1,0] — pyramid, no trapping
    assert trap([0, 1, 2, 3, 2, 1, 0]) == 0


def test_asymmetric_walls(trap) -> None:
    # [5, 0, 0, 0, 2] — bounded by min(5,2)=2, width 3 → 6
    assert trap([5, 0, 0, 0, 2]) == 6


def test_tall_spike_in_middle(trap) -> None:
    # [1, 0, 5, 0, 1] — left side: min(1,5)=1 over 1 cell = 1
    #                  — right side: min(5,1)=1 over 1 cell = 1 → total 2
    assert trap([1, 0, 5, 0, 1]) == 2


def test_plateau_with_dip(trap) -> None:
    # [4, 4, 1, 4, 4] — dip of 3 over 1 cell → 3
    assert trap([4, 4, 1, 4, 4]) == 3


def test_large_uniform_pool(trap) -> None:
    # [10, 0, 0, ...(98 zeros)..., 10] = 10 * 98 = 980
    height = [10] + [0] * 98 + [10]
    assert trap(height) == 980
