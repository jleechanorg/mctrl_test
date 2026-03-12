"""
Trapping Rain Water - LeetCode 42

Given n non-negative integers representing an elevation map where the width of each bar is 1,
compute how much water it can trap after raining.

Example:
    Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
    Output: 6
    Explanation: The above elevation map is represented by array [0,1,0,2,1,0,1,3,2,1,2,1].
                 In this case, 6 units of rain water are being trapped.

Approach:
    Two Pointer Algorithm - O(n) time, O(1) space
    - Use two pointers starting from both ends
    - Track the maximum height seen from left and right
    - At each position, water trapped = min(left_max, right_max) - height[i]

Time Complexity: O(n) - single pass through the array
Space Complexity: O(1) - only using two pointers and two max variables
"""


def trap(height: list[int]) -> int:
    """
    Calculate how much water can be trapped after raining.

    Args:
        height: List of non-negative integers representing elevation map

    Returns:
        Total units of water that can be trapped

    Examples:
        >>> trap([0,1,0,2,1,0,1,3,2,1,2,1])
        6
        >>> trap([4,2,0,3,2,5])
        9
    """
    if not height or len(height) < 3:
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


def trap_dp(height: list[int]) -> int:
    """
    Dynamic Programming approach - O(n) time, O(n) space.

    Precompute left_max and right_max arrays where:
    - left_max[i] = max height from index 0 to i
    - right_max[i] = max height from index i to n-1

    Water at position i = min(left_max[i], right_max[i]) - height[i]
    """
    if not height or len(height) < 3:
        return 0

    n = len(height)
    left_max = [0] * n
    right_max = [0] * n
    water = 0

    # Build left_max array
    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])

    # Build right_max array
    right_max[n - 1] = height[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])

    # Calculate water trapped at each position
    for i in range(n):
        water += min(left_max[i], right_max[i]) - height[i]

    return water


def trap_stack(height: list[int]) -> int:
    """
    Stack-based approach - O(n) time, O(n) space.

    Use a monotonic decreasing stack to track bars.
    When a higher bar is found, calculate water trapped.
    """
    if not height or len(height) < 3:
        return 0

    stack = []
    water = 0

    for i, h in enumerate(height):
        # While current bar is higher than stack top
        while stack and h > height[stack[-1]]:
            top = stack.pop()
            if not stack:
                break
            distance = i - stack[-1] - 1
            bounded_height = min(h, height[stack[-1]]) - height[top]
            water += distance * bounded_height
        stack.append(i)

    return water


if __name__ == "__main__":
    # Test examples
    print(trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))  # Expected: 6
    print(trap([4, 2, 0, 3, 2, 5]))  # Expected: 9
    print(trap([5, 4, 1, 2]))  # Expected: 1
    print(trap([0, 0, 0, 0]))  # Expected: 0
