"""Tests for LeetCode #42 — Trapping Rain Water."""
from __future__ import annotations

from orchestration.trapping_rain_water import trap


class TestTrapBasicExamples:
    """LeetCode provided examples."""

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9


class TestTrapEdgeCases:
    """Edge cases and boundary conditions."""

    def test_empty(self) -> None:
        assert trap([]) == 0

    def test_single_bar(self) -> None:
        assert trap([5]) == 0

    def test_two_bars(self) -> None:
        assert trap([3, 7]) == 0

    def test_flat_surface(self) -> None:
        assert trap([3, 3, 3, 3]) == 0

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0


class TestTrapShapes:
    """Various terrain shapes."""

    def test_v_shape(self) -> None:
        # [3, 0, 3] traps 3 units
        assert trap([3, 0, 3]) == 3

    def test_deep_valley(self) -> None:
        # [5, 0, 0, 0, 5] traps 5*3 = 15
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_asymmetric_walls(self) -> None:
        # [3, 0, 5] — bounded by shorter wall (3), traps 3
        assert trap([3, 0, 5]) == 3

    def test_staircase_down_then_up(self) -> None:
        # [4, 3, 2, 1, 2, 3, 4]
        # Water: 0+1+2+3+2+1+0 = 9
        assert trap([4, 3, 2, 1, 2, 3, 4]) == 9

    def test_multiple_pools(self) -> None:
        # [2, 0, 2, 0, 2] — two pools of 2 each
        assert trap([2, 0, 2, 0, 2]) == 4

    def test_tall_spike_in_middle(self) -> None:
        # [1, 0, 5, 0, 1] — left pool=1, right pool=1
        assert trap([1, 0, 5, 0, 1]) == 2

    def test_plateau_with_dip(self) -> None:
        # [3, 3, 0, 3, 3] traps 3
        assert trap([3, 3, 0, 3, 3]) == 3


class TestTrapLargeInput:
    """Performance / larger inputs."""

    def test_large_symmetric_valley(self) -> None:
        # 1000-wide valley between two walls of height 1000
        height = [1000] + [0] * 998 + [1000]
        assert trap(height) == 1000 * 998

    def test_sawtooth(self) -> None:
        # [0,1,0,1,0,1,...] — each dip traps 1 except edges
        height = [0, 1] * 50
        # Between each pair of 1s there's a 0 that traps 1 unit
        # Positions: 0=0,1=1,2=0,3=1,...,98=0,99=1
        # Trapped at indices 2,4,6,...,98 (every even index except 0) = 49 units
        assert trap(height) == 49
