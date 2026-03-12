"""
Find Median from Data Stream - LeetCode Hard Problem 295

The median is the middle value in an ordered list of numbers.

For example:
- For [1, 2, 3], the median is 2
- For [1, 2], the median is (1 + 2) / 2 = 1.5

Design a data structure that supports:
- addNum(num): Add a number to the data structure
- findMedian(): Return the median of all numbers added so far

Both operations must run in O(log n) time.

Time Complexity:
- addNum: O(log n)
- findMedian: O(1)

Space Complexity: O(n) where n is the number of elements

Approach:
Use two heaps:
- max_heap (lower half): stores the smaller half of numbers (as negatives for max-heap behavior)
- min_heap (upper half): stores the larger half of numbers

Invariant: |max_heap| == |min_heap| or |max_heap| = |min_heap| + 1
This ensures the median is always at the top of max_heap (if it has more elements)
or the average of both tops (if they're equal size).
"""

from __future__ import annotations
import heapq
from typing import Optional


class MedianFinder:
    """
    A data structure that supports adding numbers and finding the median
    in O(log n) and O(1) time respectively.

    Uses two heaps:
    - max_heap: stores the smaller half (as negative values for max-heap behavior)
    - min_heap: stores the larger half
    """

    def __init__(self):
        """Initialize the MedianFinder."""
        # max_heap for lower half (inverted to make it a max-heap)
        self.max_heap: list[float] = []
        # min_heap for upper half
        self.min_heap: list[float] = []

    def addNum(self, num: float) -> None:
        """
        Add a number to the data structure.

        Args:
            num: The number to add

        Algorithm:
        1. Always add to max_heap first (as negative for max-heap behavior)
        2. Then move the largest element from max_heap to min_heap
        3. If min_heap has more elements, move the smallest back to max_heap
        4. This maintains the invariant: max_heap has equal or one more element
        """
        # Add to max_heap (negated for max-heap behavior)
        heapq.heappush(self.max_heap, -num)

        # Balance: move the largest from max_heap to min_heap
        heapq.heappush(self.min_heap, -heapq.heappop(self.max_heap))

        # Ensure max_heap has at least as many elements as min_heap
        if len(self.max_heap) < len(self.min_heap):
            heapq.heappush(self.max_heap, -heapq.heappop(self.min_heap))

    def findMedian(self) -> float:
        """
        Return the median of all numbers in the data structure.

        Returns:
            The median value

        Logic:
        - If max_heap has more elements, its top is the median
        - Otherwise, the median is the average of both tops
        """
        if len(self.max_heap) > len(self.min_heap):
            # Odd number of elements - median is top of max_heap
            return -self.max_heap[0]
        else:
            # Even number of elements - median is average of both tops
            return (-self.max_heap[0] + self.min_heap[0]) / 2.0


if __name__ == "__main__":
    # Test Example from problem:
    # Input: ['MedianFinder', 'addNum', 'addNum', 'findMedian', 'addNum', 'findMedian']
    #        [[], [1], [2], [], [3], []]
    # Output: [null, null, null, 1.5, null, 2.0]

    mf = MedianFinder()
    results = []

    # MedianFinder()
    results.append(None)

    # addNum(1)
    mf.addNum(1)
    results.append(None)

    # addNum(2)
    mf.addNum(2)
    results.append(None)

    # findMedian() -> 1.5
    median = mf.findMedian()
    results.append(median)
    assert median == 1.5, f"Expected 1.5, got {median}"

    # addNum(3)
    mf.addNum(3)
    results.append(None)

    # findMedian() -> 2.0
    median = mf.findMedian()
    results.append(median)
    assert median == 2.0, f"Expected 2.0, got {median}"

    print(f"Example test: {results}")
    assert results == [None, None, None, 1.5, None, 2.0]

    # Additional test cases
    print("\nAdditional tests:")

    # Test: Single element
    mf2 = MedianFinder()
    mf2.addNum(1)
    assert mf2.findMedian() == 1.0
    print("Test single element: PASS")

    # Test: Two elements
    mf3 = MedianFinder()
    mf3.addNum(1)
    mf3.addNum(2)
    assert mf3.findMedian() == 1.5
    print("Test two elements: PASS")

    # Test: Three elements (odd)
    mf4 = MedianFinder()
    mf4.addNum(1)
    mf4.addNum(2)
    mf4.addNum(3)
    assert mf4.findMedian() == 2.0
    print("Test three elements: PASS")

    # Test: Four elements (even)
    mf5 = MedianFinder()
    mf5.addNum(1)
    mf5.addNum(2)
    mf5.addNum(3)
    mf5.addNum(4)
    assert mf5.findMedian() == 2.5
    print("Test four elements: PASS")

    # Test: Negative numbers
    mf6 = MedianFinder()
    mf6.addNum(-1)
    mf6.addNum(-2)
    mf6.addNum(-3)
    assert mf6.findMedian() == -2.0
    print("Test negative numbers: PASS")

    # Test: Mixed positive and negative
    mf7 = MedianFinder()
    mf7.addNum(-1)
    mf7.addNum(0)
    mf7.addNum(1)
    assert mf7.findMedian() == 0.0
    print("Test mixed positive/negative: PASS")

    # Test: Large dataset
    mf8 = MedianFinder()
    for i in range(1, 101):
        mf8.addNum(float(i))
    assert mf8.findMedian() == 50.5
    print("Test 100 elements: PASS")

    print("\nAll tests passed!")
