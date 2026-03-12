"""
LeetCode 200 - Number of Islands (Hard)

Given a 2D grid of '1's (land) and '0's (water), count the number of islands.
An island is surrounded by water and is formed by connecting adjacent lands
horizontally or vertically.

Example:
Input: grid = [
  ["1","1","1","1","0"],
  ["1","1","0","1","0"],
  ["1","1","0","0","0"],
  ["0","0","0","0","0"]
]
Output: 1

Time Complexity: O(m*n) where m = rows, n = columns
Space Complexity: O(m*n) for recursion stack in worst case
"""

from typing import List


class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        """
        Count the number of islands using DFS.
        
        Args:
            grid: 2D list of '1's (land) and '0's (water)
            
        Returns:
            Number of islands
        """
        if not grid or not grid[0]:
            return 0
        
        rows = len(grid)
        cols = len(grid[0])
        island_count = 0
        
        def dfs(r: int, c: int) -> None:
            """DFS to mark all connected land cells."""
            # Boundary check and water check
            if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == '0':
                return
            
            # Mark as visited by changing to '0'
            grid[r][c] = '0'
            
            # Explore all 4 directions
            dfs(r + 1, c)  # down
            dfs(r - 1, c)  # up
            dfs(r, c + 1)  # right
            dfs(r, c - 1)  # left
        
        # Iterate through all cells
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == '1':
                    island_count += 1
                    dfs(r, c)
        
        return island_count


# Test cases
if __name__ == "__main__":
    sol = Solution()
    
    # Test case 1: Basic example
    grid1 = [
        ["1", "1", "1", "1", "0"],
        ["1", "1", "0", "1", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "0", "0", "0"]
    ]
    assert sol.numIslands(grid1) == 1, "Test 1 failed"
    
    # Test case 2: Multiple islands
    grid2 = [
        ["1", "1", "0", "0", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "1", "1"]
    ]
    assert sol.numIslands(grid2) == 3, "Test 2 failed"
    
    # Test case 3: No islands
    grid3 = [
        ["0", "0"],
        ["0", "0"]
    ]
    assert sol.numIslands(grid3) == 0, "Test 3 failed"
    
    # Test case 4: Single cell island
    grid4 = [["1"]]
    assert sol.numIslands(grid4) == 1, "Test 4 failed"
    
    # Test case 5: Empty grid
    assert sol.numIslands([]) == 0, "Test 5 failed"
    assert sol.numIslands([[]]) == 0, "Test 6 failed"
    
    print("All tests passed!")
