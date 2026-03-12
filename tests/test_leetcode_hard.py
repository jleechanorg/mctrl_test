from leetcode_hard.median_of_two_sorted_arrays import find_median_sorted_arrays
from leetcode_hard.merge_k_sorted_lists import ListNode as MergeListNode, merge_k_lists
from leetcode_hard.regular_expression_matching import is_match
from leetcode_hard.reverse_nodes_in_k_group import ListNode as ReverseListNode, reverse_k_group
from leetcode_hard.substring_with_concatenation_of_all_words import find_substring


def _build_merge_list(values):
    dummy = MergeListNode(0)
    tail = dummy
    for value in values:
        tail.next = MergeListNode(value)
        tail = tail.next
    return dummy.next


def _merge_list_to_python(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def _build_reverse_list(values):
    dummy = ReverseListNode(0)
    tail = dummy
    for value in values:
        tail.next = ReverseListNode(value)
        tail = tail.next
    return dummy.next


def _reverse_list_to_python(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def test_median_of_two_sorted_arrays():
    assert find_median_sorted_arrays([1, 3], [2]) == 2.0
    assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5
    assert find_median_sorted_arrays([0, 0], [0, 0]) == 0.0
    assert find_median_sorted_arrays([], [1]) == 1.0


def test_regular_expression_matching():
    assert not is_match("aa", "a")
    assert is_match("aa", "a*")
    assert is_match("ab", ".*")
    assert is_match("aab", "c*a*b")
    assert not is_match("mississippi", "mis*is*p*.")


def test_merge_k_sorted_lists():
    lists = [_build_merge_list([1, 4, 5]), _build_merge_list([1, 3, 4]), _build_merge_list([2, 6])]
    merged = merge_k_lists(lists)
    assert _merge_list_to_python(merged) == [1, 1, 2, 3, 4, 4, 5, 6]
    assert merge_k_lists([]) is None
    assert merge_k_lists([None, _build_merge_list([1])]).val == 1


def test_reverse_nodes_in_k_group():
    head = _build_reverse_list([1, 2, 3, 4, 5])
    assert _reverse_list_to_python(reverse_k_group(head, 2)) == [2, 1, 4, 3, 5]

    head = _build_reverse_list([1, 2, 3, 4, 5])
    assert _reverse_list_to_python(reverse_k_group(head, 3)) == [3, 2, 1, 4, 5]

    head = _build_reverse_list([1, 2])
    assert _reverse_list_to_python(reverse_k_group(head, 3)) == [1, 2]


def test_substring_with_concatenation_of_all_words():
    assert sorted(find_substring("barfoothefoobarman", ["foo", "bar"])) == [0, 9]
    assert find_substring("wordgoodgoodgoodbestword", ["word", "good", "best", "word"]) == []
    assert sorted(find_substring("barfoofoobarthefoobarman", ["bar", "foo", "the"])) == [6, 9, 12]
