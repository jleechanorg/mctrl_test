"""
Shortest Path in Binary Matrix - LeetCode 1091

Given an n x n binary matrix grid, return the length of the shortest
clear path in the matrix. If there is no clear path, return -1.

A clear path is a path from the top-left cell (0, 0) to the bottom-right
cell (n - 1, n - 1) such that:
- All the path cells contain 0 (not blocked)
- The path is 8-directionally adjacent (including diagonals)

Time Complexity: O(n^2) - each cell visited at most once in BFS
Space Complexity: O(n^2) - for visited set and queue
"""
from collections import deque
from typing import List


def shortest_path_binary_matrix(grid: List[List[int]]) -> int:
    """
    Find the shortest path from top-left to bottom-right in a binary matrix.

    Uses BFS since all edges have equal weight (unweighted graph).
    8-directional movement is allowed (including diagonals).

    Args:
        grid: n x n binary matrix where 0 = empty, 1 = blocked

    Returns:
        Length of shortest path, or -1 if no valid path exists
    """
    n = len(grid)

    # Edge cases: start or end is blocked
    if not grid or grid[0][0] == 1 or grid[n - 1][n - 1] == 1:
        return -1

    # Single cell - already at destination
    if n == 1:
        return 1

    # BFS setup
    queue = deque([(0, 0, 1)])  # (row, col, path_length)
    visited = {(0, 0)}

    # 8 directions: up, down, left, right, and 4 diagonals
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),  # Cardinal directions
        (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonal directions
    ]

    while queue:
        row, col, length = queue.popleft()

        # Check all 8 neighbors
        for dr, dc in directions:
            nr, nc = row + dr, col + dc

            # Skip if out of bounds
            if not (0 <= nr < n and 0 <= nc < n):
                continue

            # Skip if blocked or already visited
            if grid[nr][nc] == 1 or (nr, nc) in visited:
                continue

            # Found the destination
            if nr == n - 1 and nc == n - 1:
                return length + 1

            # Add to queue
            visited.add((nr, nc))
            queue.append((nr, nc, length + 1))

    # No path exists
    return -1


def shortest_path_binary_matrix_dfs(grid: List[List[int]]) -> int:
    """
    Find shortest path using DFS (less efficient but included for comparison).

    Time Complexity: O(n^2 * 8^n) - exponential in worst case
    Space Complexity: O(n^2) - recursion stack and visited set
    """
    n = len(grid)

    if not grid or grid[0][0] == 1 or grid[n - 1][n - 1] == 1:
        return -1

    if n == 1:
        return 1

    visited = set()
    min_path = float('inf')

    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]

    def dfs(row: int, col: int, length: int) -> None:
        nonlocal min_path

        if length >= min_path:
            return

        if row == n - 1 and col == n - 1:
            min_path = length
            return

        visited.add((row, col))

        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if (0 <= nr < n and 0 <= nc < n and
                    grid[nr][nc] == 0 and (nr, nc) not in visited):
                dfs(nr, nc, length + 1)

        visited.remove((row, col))

    dfs(0, 0, 1)
    return min_path if min_path != float('inf') else -1


def has_path(grid: List[List[int]]) -> bool:
    """Return True if any clear path exists from top-left to bottom-right."""
    return shortest_path_binary_matrix(grid) != -1


def grid_size(grid: List[List[int]]) -> int:
    """Return the size N of an NxN grid (0 for empty)."""
    return len(grid) if grid else 0


if __name__ == "__main__":
    # Example 1
    grid1 = [
        [0, 1],
        [1, 0]
    ]
    print(shortest_path_binary_matrix(grid1))  # 2

    # Example 2
    grid2 = [
        [0, 0, 0],
        [1, 1, 0],
        [1, 1, 0]
    ]
    print(shortest_path_binary_matrix(grid2))  # 4

    # Example 3
    grid3 = [
        [1, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1]
    ]
    print(shortest_path_binary_matrix(grid3))  # -1
