"""
Trapping Rain Water - LeetCode 42 (Hard)

Given n non-negative integers representing an elevation map where the width of each bar is 1,
compute how much water it can trap after raining.

Example:
  Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
  Output: 6
  Explanation: The above elevation map is represented by array [0,1,0,2,1,0,1,3,2,1,2,1].
               In this case, 6 units of rain water are being trapped.

Time Complexity: O(n) - single pass with two pointers
Space Complexity: O(1) - only using constant extra space
"""


def trap_two_pointer(height: list[int]) -> int:
    """
    Two pointer approach - optimal solution.

    For each position, the water it can trap is determined by:
    min(max_left, max_right) - height[i]

    We use two pointers moving from both ends, tracking the maximum
    height seen from each side. At each step, we process the side
    with the smaller max height since that's the limiting factor.

    Args:
        height: List of non-negative integers representing bar heights

    Returns:
        Total units of trapped water
    """
    if not height:
        return 0

    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    water = 0

    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1

    return water


def trap_stack(height: list[int]) -> int:
    """
    Stack-based approach - alternative solution.

    We maintain a stack of indices with decreasing heights.
    When we find a bar higher than the stack top, we can calculate
    trapped water between the stack top and the current position.

    Args:
        height: List of non-negative integers representing bar heights

    Returns:
        Total units of trapped water
    """
    if not height:
        return 0

    stack = []
    water = 0

    for i, h in enumerate(height):
        while stack and h > height[stack[-1]]:
            top = stack.pop()
            if not stack:
                break
            distance = i - stack[-1] - 1
            bounded_height = min(h, height[stack[-1]]) - height[top]
            water += distance * bounded_height
        stack.append(i)

    return water


def trap_brute_force(height: list[int]) -> int:
    """
    Brute force approach - for reference only.

    For each element, find the maximum height to its left and right,
    then water at that position = min(max_left, max_right) - height[i]

    Time: O(n^2), Space: O(1)
    Not recommended for large inputs.

    Args:
        height: List of non-negative integers representing bar heights

    Returns:
        Total units of trapped water
    """
    if not height:
        return 0

    n = len(height)
    water = 0

    for i in range(1, n - 1):
        left_max = max(height[:i])
        right_max = max(height[i + 1:])
        trapped = min(left_max, right_max) - height[i]
        if trapped > 0:
            water += trapped

    return water


# Default export the optimal solution
trap = trap_two_pointer


if __name__ == "__main__":
    # Example usage
    height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
    result = trap(height)
    print(f"Input: {height}")
    print(f"Trapped water: {result}")  # Expected: 6
