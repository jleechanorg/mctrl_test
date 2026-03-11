from __future__ import annotations

from trapping_rain_water import trap


class TestTrap:
    """Focused tests for LeetCode #42 Trapping Rain Water."""

    def test_example1(self):
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example2(self):
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    def test_empty(self):
        assert trap([]) == 0

    def test_single_bar(self):
        assert trap([5]) == 0

    def test_two_bars(self):
        assert trap([3, 7]) == 0

    def test_flat(self):
        assert trap([3, 3, 3, 3]) == 0

    def test_ascending(self):
        assert trap([1, 2, 3, 4]) == 0

    def test_descending(self):
        assert trap([4, 3, 2, 1]) == 0

    def test_v_shape(self):
        assert trap([5, 0, 5]) == 5

    def test_all_zeros(self):
        assert trap([0, 0, 0]) == 0

    def test_single_trap(self):
        assert trap([2, 0, 2]) == 2

    def test_multiple_pools(self):
        # Pools at indices 1, 3-4, and 6 all fill to height 3
        assert trap([3, 0, 3, 0, 0, 3, 0, 3]) == 12

    def test_large_values(self):
        assert trap([100000, 0, 100000]) == 100000
