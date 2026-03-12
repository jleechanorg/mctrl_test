"""
Tests for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest
from merge_k_lists import (
    Solution,
    ListNode,
    create_linked_list,
    linked_list_to_list,
)


class TestMergeKSortedLists:
    """Test cases for Merge k Sorted Lists."""

    def setup_method(self):
        """Set up test fixtures."""
        self.solution = Solution()

    def test_merge_two_lists_basic(self):
        """Test basic two list merge."""
        l1 = create_linked_list([1, 2, 4])
        l2 = create_linked_list([1, 3, 4])
        result = self.solution.mergeKLists([l1, l2])
        assert linked_list_to_list(result) == [1, 1, 2, 3, 4, 4]

    def test_merge_empty_lists(self):
        """Test with empty list of lists."""
        result = self.solution.mergeKLists([])
        assert result is None

    def test_merge_single_list(self):
        """Test with single non-empty list."""
        l1 = create_linked_list([1, 2, 3])
        result = self.solution.mergeKLists([l1])
        assert linked_list_to_list(result) == [1, 2, 3]

    def test_merge_multiple_empty_lists(self):
        """Test with all None lists."""
        result = self.solution.mergeKLists([None, None, None])
        assert result is None

    def test_merge_mixed_empty_and_nonempty(self):
        """Test with mix of empty and non-empty lists."""
        l1 = create_linked_list([1, 4, 7])
        result = self.solution.mergeKLists([None, l1, None])
        assert linked_list_to_list(result) == [1, 4, 7]

    def test_merge_k_lists_three_lists(self):
        """Test merging three sorted lists."""
        l1 = create_linked_list([1, 4, 7])
        l2 = create_linked_list([2, 5, 8])
        l3 = create_linked_list([3, 6, 9])
        result = self.solution.mergeKLists([l1, l2, l3])
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_merge_with_duplicates(self):
        """Test merging lists with duplicate values."""
        l1 = create_linked_list([1, 1, 1])
        l2 = create_linked_list([1, 1, 1])
        l3 = create_linked_list([1, 1, 1])
        result = self.solution.mergeKLists([l1, l2, l3])
        assert linked_list_to_list(result) == [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def test_merge_large_values(self):
        """Test with large integer values."""
        l1 = create_linked_list([1000, 2000, 3000])
        l2 = create_linked_list([500, 1500, 2500])
        result = self.solution.mergeKLists([l1, l2])
        assert linked_list_to_list(result) == [500, 1000, 1500, 2000, 2500, 3000]

    def test_merge_negative_values(self):
        """Test with negative numbers."""
        l1 = create_linked_list([-5, -3, -1])
        l2 = create_linked_list([-4, -2, 0])
        result = self.solution.mergeKLists([l1, l2])
        assert linked_list_to_list(result) == [-5, -4, -3, -2, -1, 0]

    def test_merge_already_sorted(self):
        """Test when lists together form a sorted sequence."""
        l1 = create_linked_list([1, 2])
        l2 = create_linked_list([3, 4])
        l3 = create_linked_list([5, 6])
        result = self.solution.mergeKLists([l1, l2, l3])
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_heap_method_equivalence(self):
        """Test that heap method produces same results as divide-and-conquer."""
        l1 = create_linked_list([1, 4, 7])
        l2 = create_linked_list([2, 5, 8])
        l3 = create_linked_list([3, 6, 9])

        result_dc = self.solution.mergeKLists([l1, l2, l3])
        result_heap = self.solution.mergeKListsHeap([
            create_linked_list([1, 4, 7]),
            create_linked_list([2, 5, 8]),
            create_linked_list([3, 6, 9]),
        ])

        assert linked_list_to_list(result_dc) == linked_list_to_list(result_heap)

    def test_merge_single_node_lists(self):
        """Test merging lists with single nodes."""
        l1 = create_linked_list([1])
        l2 = create_linked_list([2])
        l3 = create_linked_list([3])
        result = self.solution.mergeKLists([l1, l2, l3])
        assert linked_list_to_list(result) == [1, 2, 3]

    def test_merge_five_lists(self):
        """Test merging five lists of varying lengths."""
        lists = [
            create_linked_list([1, 10, 20]),
            create_linked_list([2, 11, 21]),
            create_linked_list([3, 12, 22]),
            create_linked_list([4, 13, 23]),
            create_linked_list([5, 14, 24]),
        ]
        result = self.solution.mergeKLists(lists)
        expected = [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 20, 21, 22, 23, 24]
        assert linked_list_to_list(result) == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
