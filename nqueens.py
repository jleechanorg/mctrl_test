from __future__ import annotations


def solve_n_queens(n: int) -> list[list[str]]:
    """Return all distinct N-Queens board configurations."""
    if n <= 0:
        return []

    results: list[list[str]] = []
    queens: list[int] = [-1] * n
    used_cols: set[int] = set()
    used_diag_desc: set[int] = set()  # row - col
    used_diag_asc: set[int] = set()   # row + col

    def build_board() -> list[str]:
        return ["." * c + "Q" + "." * (n - c - 1) for c in queens]

    def backtrack(row: int) -> None:
        if row == n:
            results.append(build_board())
            return

        for col in range(n):
            d_desc = row - col
            d_asc = row + col
            if col in used_cols or d_desc in used_diag_desc or d_asc in used_diag_asc:
                continue

            queens[row] = col
            used_cols.add(col)
            used_diag_desc.add(d_desc)
            used_diag_asc.add(d_asc)

            backtrack(row + 1)

            used_cols.remove(col)
            used_diag_desc.remove(d_desc)
            used_diag_asc.remove(d_asc)
            queens[row] = -1

    backtrack(0)
    return results
