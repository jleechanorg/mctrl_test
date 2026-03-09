from __future__ import annotations


def solve_sudoku(board: list[list[str]]) -> None:
    """Solve the 9x9 Sudoku puzzle in-place."""
    full_mask = (1 << 9) - 1
    row_masks = [0] * 9
    col_masks = [0] * 9
    box_masks = [0] * 9
    empties: list[tuple[int, int]] = []

    def bit_for_digit(ch: str) -> int:
        return 1 << (ord(ch) - ord("1"))

    def box_index(r: int, c: int) -> int:
        return (r // 3) * 3 + (c // 3)

    for r in range(9):
        for c in range(9):
            value = board[r][c]
            if value == ".":
                empties.append((r, c))
                continue
            bit = bit_for_digit(value)
            b = box_index(r, c)
            row_masks[r] |= bit
            col_masks[c] |= bit
            box_masks[b] |= bit

    def candidate_mask(r: int, c: int) -> int:
        used = row_masks[r] | col_masks[c] | box_masks[box_index(r, c)]
        return full_mask & ~used

    def pick_next_cell(start: int) -> int:
        best_i = start
        best_count = 10
        for i in range(start, len(empties)):
            r, c = empties[i]
            count = candidate_mask(r, c).bit_count()
            if count < best_count:
                best_count = count
                best_i = i
                if best_count == 1:
                    break
        return best_i

    def place(r: int, c: int, bit: int) -> None:
        b = box_index(r, c)
        row_masks[r] |= bit
        col_masks[c] |= bit
        box_masks[b] |= bit
        board[r][c] = chr(ord("1") + bit.bit_length() - 1)

    def remove(r: int, c: int, bit: int) -> None:
        b = box_index(r, c)
        row_masks[r] ^= bit
        col_masks[c] ^= bit
        box_masks[b] ^= bit
        board[r][c] = "."

    def backtrack(start: int) -> bool:
        if start == len(empties):
            return True

        best_i = pick_next_cell(start)
        empties[start], empties[best_i] = empties[best_i], empties[start]
        r, c = empties[start]
        mask = candidate_mask(r, c)

        while mask:
            bit = mask & -mask
            mask ^= bit
            place(r, c, bit)
            if backtrack(start + 1):
                return True
            remove(r, c, bit)

        empties[start], empties[best_i] = empties[best_i], empties[start]
        return False

    backtrack(0)
