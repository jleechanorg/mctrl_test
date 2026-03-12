"""
Shortest Path in Binary Matrix - LeetCode 1293

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
    Find the shortest path from top-left to bottom-right in a binary grid.

    Uses BFS to find the shortest path since all edges have equal weight.

    Args:
        grid: n x n binary matrix where 0 = empty, 1 = blocked

    Returns:
        Length of shortest clear path, or -1 if no path exists
    """
    n = len(grid)

    # Check if start or end is blocked
    if grid[0][0] == 1 or grid[n-1][n-1] == 1:
        return -1

    # BFS initialization
    queue = deque([(0, 0, 1)])  # (row, col, distance)
    visited = {(0, 0)}

    # 8 directions: up, down, left, right, and 4 diagonals
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),  # cardinal
        (-1, -1), (-1, 1), (1, -1), (1, 1)  # diagonal
    ]

    while queue:
        row, col, dist = queue.popleft()

        # Check if we reached the target
        if row == n - 1 and col == n - 1:
            return dist

        # Explore all 8 neighbors
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            # Check bounds
            if 0 <= new_row < n and 0 <= new_col < n:
                # Check if not visited and not blocked
                if (new_row, new_col) not in visited and grid[new_row][new_col] == 0:
                    visited.add((new_row, new_col))
                    queue.append((new_row, new_col, dist + 1))

    # No path found
    return -1


def shortest_path_binary_matrix_dfs(grid: List[List[int]]) -> int:
    """
    Alternative DFS solution using backtracking (less efficient).

    This is included for comparison - BFS is preferred for shortest path.

    Time Complexity: O(8^(n^2)) worst case - exponential
    Space Complexity: O(n^2) - recursion stack
    """
    n = len(grid)

    if grid[0][0] == 1 or grid[n-1][n-1] == 1:
        return -1

    if n == 1:
        return 1

    visited = set()
    min_distance = float('inf')

    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]

    def dfs(row: int, col: int, dist: int) -> None:
        nonlocal min_distance

        # Pruning: cannot beat current best
        if dist >= min_distance:
            return

        # Reached destination
        if row == n - 1 and col == n - 1:
            min_distance = dist
            return

        visited.add((row, col))

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            if (0 <= new_row < n and 0 <= new_col < n and
                (new_row, new_col) not in visited and
                grid[new_row][new_col] == 0):
                dfs(new_row, new_col, dist + 1)

        visited.remove((row, col))

    dfs(0, 0, 1)

    return min_distance if min_distance != float('inf') else -1


# Example usage and testing
if __name__ == "__main__":
    # Example 1: [[0,1],[1,0]] -> 2
    grid1 = [[0, 1], [1, 0]]
    print(f"Grid 1: {shortest_path_binary_matrix(grid1)}")  # Expected: 2

    # Example 2: [[0,0,0],[1,1,0],[1,1,0]] -> 4
    grid2 = [
        [0, 0, 0],
        [1, 1, 0],
        [1, 1, 0]
    ]
    print(f"Grid 2: {shortest_path_binary_matrix(grid2)}")  # Expected: 4

    # Example 3: [[1,1],[1,1]] -> -1
    grid3 = [[1, 1], [1, 1]]
    print(f"Grid 3: {shortest_path_binary_matrix(grid3)}")  # Expected: -1

    # Example 4: [[0]] -> 1
    grid4 = [[0]]
    print(f"Grid 4: {shortest_path_binary_matrix(grid4)}")  # Expected: 1
