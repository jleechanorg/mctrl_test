from __future__ import annotations

from word_search_ii import find_words


def test_find_words_leetcode_example():
    board = [
        ["o", "a", "a", "n"],
        ["e", "t", "a", "e"],
        ["i", "h", "k", "r"],
        ["i", "f", "l", "v"],
    ]
    words = ["oath", "pea", "eat", "rain"]
    assert sorted(find_words(board, words)) == ["eat", "oath"]


def test_find_words_deduplicates_multiple_paths():
    board = [
        ["a", "b", "a"],
        ["x", "x", "x"],
    ]
    words = ["ab", "aba", "ab"]
    assert sorted(find_words(board, words)) == ["ab", "aba"]


def test_find_words_empty_inputs():
    assert find_words([], ["a"]) == []
    assert find_words([["a"]], []) == []
