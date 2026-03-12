"""
LeetCode 42 - Trapping Rain Water (Hard)

Given n non-negative integers representing an elevation map where the width of each bar is 1,
compute how much water it can trap after raining.

Example:
Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6
Explanation: The above elevation map is represented by array [0,1,0,2,1,0,1,3,2,1,2,1].
In this case, 6 units of rain water are being trapped.

Time Complexity: O(n) where n = length of height array
Space Complexity: O(1) - only using two pointers
"""

from typing import List


class Solution:
    def trap(self, height: List[int]) -> int:
        """
        Calculate trapped water using two-pointer approach.
        
        The idea: For each position, the water it can trap is determined by
        min(max_left, max_right) - height[i].
        
        Using two pointers, we track max_left and max_right from both ends.
        We always process the side with smaller max height since that's the
        limiting factor for water trapped at that position.
        
        Args:
            height: List of non-negative integers representing elevation
            
        Returns:
            Total units of trapped water
        """
        if not height or len(height) < 3:
            return 0
        
        left = 0
        right = len(height) - 1
        max_left = 0
        max_right = 0
        water = 0
        
        while left < right:
            if height[left] <= height[right]:
                if height[left] >= max_left:
                    max_left = height[left]
                else:
                    water += max_left - height[left]
                left += 1
            else:
                if height[right] >= max_right:
                    max_right = height[right]
                else:
                    water += max_right - height[right]
                right -= 1
        
        return water


# Test cases
if __name__ == "__main__":
    sol = Solution()
    
    # Test case 1: Basic example
    height1 = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
    assert sol.trap(height1) == 6, f"Test 1 failed: {sol.trap(height1)}"
    
    # Test case 2: No water trapped
    height2 = [4, 2, 0, 3, 2, 5]
    assert sol.trap(height2) == 9, f"Test 2 failed: {sol.trap(height2)}"
    
    # Test case 3: Empty/small arrays
    assert sol.trap([]) == 0, "Test 3a failed"
    assert sol.trap([1]) == 0, "Test 3b failed"
    assert sol.trap([1, 2]) == 0, "Test 3c failed"
    
    # Test case 4: No water (descending)
    height4 = [5, 4, 3, 2, 1]
    assert sol.trap(height4) == 0, f"Test 4 failed: {sol.trap(height4)}"
    
    # Test case 5: No water (ascending)
    height5 = [1, 2, 3, 4, 5]
    assert sol.trap(height5) == 0, f"Test 5 failed: {sol.trap(height5)}"
    
    # Test case 6: Single peak
    height6 = [2, 0, 2]
    assert sol.trap(height6) == 2, f"Test 6 failed: {sol.trap(height6)}"
    
    # Test case 7: Multiple peaks
    height7 = [3, 0, 0, 2, 0, 4]
    assert sol.trap(height7) == 10, f"Test 7 failed: {sol.trap(height7)}"
    
    print("All tests passed!")
