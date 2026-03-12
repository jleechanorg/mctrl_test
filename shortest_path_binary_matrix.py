"""
Shortest Path in a Grid with Obstacle Elimination - LeetCode 1293

Given an n x n grid and an integer k, you can remove at most k obstacles
(cells with value 1). Find the shortest path from (0, 0) to (n-1, n-1).

Movement is 4-directional (up, down, left, right).

Time Complexity: O(n^2 * k) - BFS with k dimension
Space Complexity: O(n^2 * k) - visited states
"""

from collections import deque
from typing import List


def shortest_path_binary_matrix(grid: List[List[int]], k: int) -> int:
    """
    Find the shortest path from top-left to bottom-right in a grid,
    removing at most k obstacles.

    Uses BFS with 3D visited set (row, col, remaining_k) to track
    the minimum obstacles used to reach each cell.

    Args:
        grid: n x n binary matrix where 0 = empty, 1 = obstacle
        k: maximum number of obstacles that can be removed

    Returns:
        Length of shortest path, or -1 if no valid path exists
    """
    n = len(grid)

    # Edge case: empty grid
    if n == 0:
        return -1

    # Edge case: single cell
    if n == 1:
        return 1 if grid[0][0] <= k else -1

    # Start or end has too many obstacles to remove
    if grid[0][0] > k or grid[n-1][n-1] > k:
        return -1

    # BFS: (row, col, obstacles_used, distance)
    # Track obstacles_used since visiting same cell with fewer used is better
    queue = deque([(0, 0, grid[0][0], 1)])

    # visited[row][col] = minimum obstacles used to reach this cell
    # Using list of lists instead of dict for performance
    visited = [[float('inf')] * n for _ in range(n)]
    visited[0][0] = grid[0][0]

    # 4 directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        row, col, used, dist = queue.popleft()

        # Early exit if we reached destination
        if row == n - 1 and col == n - 1:
            return dist

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            # Check bounds
            if 0 <= new_row < n and 0 <= new_col < n:
                # Calculate new obstacles used if moving to this cell
                new_used = used + grid[new_row][new_col]

                # Only proceed if:
                # 1. Haven't exceeded k removals
                # 2. Either haven't visited this cell, or reached with fewer obstacles used
                if new_used <= k and new_used < visited[new_row][new_col]:
                    visited[new_row][new_col] = new_used
                    queue.append((new_row, new_col, new_used, dist + 1))

    # No path found within k obstacle removals
    return -1


# Example usage and testing
if __name__ == "__main__":
    # Example 1: grid = [[0,1,0],[0,0,0],[0,0,0]], k = 1 -> 4
    # Path: (0,0)->(0,1 remove)->(1,1)->(2,1)->(2,2)
    grid1 = [
        [0, 1, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    print(f"Example 1: {shortest_path_binary_matrix(grid1, 1)}")  # Expected: 4

    # Example 2: grid = [[0,1,0],[0,0,0],[0,0,0]], k = 2 -> 4
    # Direct diagonal-ish path using 2 removals
    grid2 = [
        [0, 1, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    print(f"Example 2: {shortest_path_binary_matrix(grid2, 2)}")  # Expected: 4

    # Example 3: grid = [[0,1,0],[0,0,0],[0,0,0]], k = 0 -> -1
    # Can't remove the obstacle
    grid3 = [
        [0, 1, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    print(f"Example 3: {shortest_path_binary_matrix(grid3, 0)}")  # Expected: -1

    # Example 4: 1x1 grid
    grid4 = [[0]]
    print(f"Example 4: {shortest_path_binary_matrix(grid4, 0)}")  # Expected: 1
