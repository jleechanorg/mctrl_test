"""
LeetCode 407 - Trapping Rain Water II
Hard Problem

Given an m x n integer matrix heightMap representing the height of each unit cell,
return the volume of water it can trap after raining.

Approach: Use a min-heap (priority queue) to simulate water flow.
1. Start with all boundary cells in the min-heap (sorted by height)
2. Process cells from lowest to highest
3. For each cell, check neighbors and calculate water trapped
4. Use visited set to track processed cells

Time Complexity: O(m * n * log(m * n))
Space Complexity: O(m * n)
"""

import heapq
from typing import List


class Solution:
    def trapRainWater(self, heightMap: List[List[int]]) -> int:
        if not heightMap or not heightMap[0]:
            return 0
            
        rows = len(heightMap)
        cols = len(heightMap[0])
        
        # visited set to track processed cells
        visited = set()
        min_heap = []
        
        # Add all boundary cells to the heap
        for r in range(rows):
            for c in [0, cols - 1]:
                heapq.heappush(min_heap, (heightMap[r][c], r, c))
                visited.add((r, c))
        
        for c in range(cols):
            for r in [0, rows - 1]:
                if (r, c) not in visited:
                    heapq.heappush(min_heap, (heightMap[r][c], r, c))
                    visited.add((r, c))
        
        # Directions: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        water_trapped = 0
        
        while min_heap:
            height, r, c = heapq.heappop(min_heap)
            
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                
                if not (0 <= nr < rows and 0 <= nc < cols):
                    continue
                    
                if (nr, nc) in visited:
                    continue
                    
                visited.add((nr, nc))
                
                neighbor_height = heightMap[nr][nc]
                
                # If neighbor is lower, water can be trapped
                if neighbor_height < height:
                    water_trapped += height - neighbor_height
                    # Push the water level (current height) to heap
                    heapq.heappush(min_heap, (height, nr, nc))
                else:
                    # No water trapped, push neighbor's actual height
                    heapq.heappush(min_heap, (neighbor_height, nr, nc))
        
        return water_trapped


# Test cases
if __name__ == "__main__":
    sol = Solution()
    
    # Test 1: Basic case
    heightMap1 = [
        [1, 4, 3, 1, 3, 2],
        [3, 2, 1, 3, 2, 4],
        [2, 3, 3, 2, 3, 1]
    ]
    print(f"Test 1: {sol.trapRainWater(heightMap1)}")  # Expected: 4
    
    # Test 2: No water trapped
    heightMap2 = [
        [3, 3, 3, 3, 3],
        [3, 1, 3, 1, 3],
        [3, 1, 3, 1, 3],
        [3, 3, 3, 3, 3]
    ]
    print(f"Test 2: {sol.trapRainWater(heightMap2)}")  # Expected: 8
    
    # Test 3: Single row/col
    heightMap3 = [
        [1, 2, 3],
    ]
    print(f"Test 3: {sol.trapRainWater(heightMap3)}")  # Expected: 0
    
    # Test 4: Larger case
    heightMap4 = [
        [5, 5, 5, 5, 5],
        [5, 2, 2, 2, 5],
        [5, 2, 1, 2, 5],
        [5, 2, 2, 2, 5],
        [5, 5, 5, 5, 5]
    ]
    print(f"Test 4: {sol.trapRainWater(heightMap4)}")  # Expected: 28
