from __future__ import annotations

from nqueens import solve_n_queens


def _is_valid_board(board: list[str]) -> bool:
    n = len(board)
    cols: set[int] = set()
    diag_desc: set[int] = set()
    diag_asc: set[int] = set()

    for r, row in enumerate(board):
        if len(row) != n:
            return False

        queens = [c for c, ch in enumerate(row) if ch == "Q"]
        if len(queens) != 1:
            return False

        c = queens[0]
        d_desc = r - c
        d_asc = r + c

        if c in cols or d_desc in diag_desc or d_asc in diag_asc:
            return False

        cols.add(c)
        diag_desc.add(d_desc)
        diag_asc.add(d_asc)

    return True


def test_nqueens_n1_single_solution():
    assert solve_n_queens(1) == [["Q"]]


def test_nqueens_n2_and_n3_no_solution():
    assert solve_n_queens(2) == []
    assert solve_n_queens(3) == []


def test_nqueens_n4_has_two_distinct_solutions():
    solutions = solve_n_queens(4)
    assert len(solutions) == 2
    assert len({tuple(board) for board in solutions}) == 2


def test_nqueens_n4_solutions_are_valid_boards():
    for board in solve_n_queens(4):
        assert _is_valid_board(board)


def test_nqueens_non_positive_n_returns_empty_list():
    assert solve_n_queens(0) == []
    assert solve_n_queens(-1) == []
