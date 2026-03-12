from __future__ import annotations


def num_islands(grid: list[list[str]]) -> int:
    """
    Count the number of islands in a 2D grid.

    An island is surrounded by water and is formed by connecting adjacent
    lands horizontally or vertically.

    Args:
        grid: A 2D list of '1's (land) and '0's (water)

    Returns:
        The number of islands in the grid
    """
    if not grid or not grid[0]:
        return 0

    rows = len(grid)
    cols = len(grid[0])
    count = 0

    def dfs(r: int, c: int) -> None:
        """Depth-first search to mark all connected land cells."""
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return
        if grid[r][c] != '1':
            return

        # Mark as visited by changing to '0'
        grid[r][c] = '0'

        # Visit all 4 adjacent cells
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                count += 1
                dfs(r, c)

    return count


if __name__ == "__main__":
    # Example test
    grid = [
        ['1', '1', '1', '1', '0'],
        ['1', '1', '0', '1', '0'],
        ['1', '1', '0', '0', '0'],
        ['0', '0', '0', '0', '0']
    ]
    print(f"Number of islands: {num_islands(grid)}")  # Expected: 1
