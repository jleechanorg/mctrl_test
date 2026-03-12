from __future__ import annotations

import heapq
from typing import List


def trap_rain_water_2(height_map: List[List[int]]) -> int:
    """
    Calculate how much water can be trapped after raining using BFS with min-heap.

    Args:
        height_map: An m x n integer matrix representing the height of each unit cell.

    Returns:
        The total amount of water that can be trapped.

    Algorithm:
        1. Use BFS with a min-heap (priority queue)
        2. Start with all border cells in the heap
        3. Track visited cells to avoid reprocessing
        4. For each cell popped from the heap:
           - Track the minimum boundary height
           - Check if water can be trapped (if neighbor height < min height)
           - If so, add water amount to result
           - Push unvisited neighbors with max(current height, neighbor height)
    """
    if not height_map or not height_map[0]:
        return 0

    m = len(height_map)
    n = len(height_map[0])

    # For small matrices (1 row or 1 column), no water can be trapped
    if m <= 2 or n <= 2:
        return 0

    # Min-heap: (height, row, col)
    heap: List[tuple[int, int, int]] = []
    visited = [[False] * n for _ in range(m)]

    # Add all border cells to the heap
    for i in range(m):
        for j in range(n):
            if i == 0 or i == m - 1 or j == 0 or j == n - 1:
                heapq.heappush(heap, (height_map[i][j], i, j))
                visited[i][j] = True

    # Directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    water_trapped = 0

    while heap:
        height, row, col = heapq.heappop(heap)

        # Check all 4 neighbors
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            # Skip if out of bounds or already visited
            if new_row < 0 or new_row >= m or new_col < 0 or new_col >= n:
                continue
            if visited[new_row][new_col]:
                continue

            # Mark as visited
            visited[new_row][new_col] = True

            neighbor_height = height_map[new_row][new_col]

            # If neighbor is lower than current boundary height, water can be trapped
            if neighbor_height < height:
                water_trapped += height - neighbor_height
                # Push with the current boundary height (water level)
                heapq.heappush(heap, (height, new_row, new_col))
            else:
                # Push with neighbor's actual height
                heapq.heappush(heap, (neighbor_height, new_row, new_col))

    return water_trapped


if __name__ == "__main__":
    # Example from problem statement
    height_map = [
        [1, 4, 3, 1, 3, 2],
        [3, 2, 1, 3, 2, 4],
        [2, 3, 3, 2, 3, 1],
    ]
    result = trap_rain_water_2(height_map)
    print(f"Example 1: {result}")  # Expected: 4
