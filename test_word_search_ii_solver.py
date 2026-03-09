"""Tests for word_search_ii_solver module."""

from __future__ import annotations

import pytest

from word_search_ii_solver import (
    board_to_string,
    find_words_baseline,
    find_words_optimized,
    generate_random_case,
    normalize_board,
    normalize_words,
)


def _sorted_result(board, words, fn):
    return sorted(fn(board, words))


class TestCanonicalExamples:
    def test_leetcode_example_one(self):
        board = [
            ["o", "a", "a", "n"],
            ["e", "t", "a", "e"],
            ["i", "h", "k", "r"],
            ["i", "f", "l", "v"],
        ]
        words = ["oath", "pea", "eat", "rain"]

        expected = ["eat", "oath"]
        assert _sorted_result(board, words, find_words_optimized) == expected
        assert _sorted_result(board, words, find_words_baseline) == expected

    def test_leetcode_example_two(self):
        board = [["a", "b"], ["c", "d"]]
        words = ["abcb"]
        expected = []

        assert _sorted_result(board, words, find_words_optimized) == expected
        assert _sorted_result(board, words, find_words_baseline) == expected


class TestEdgeCases:
    def test_empty_board(self):
        words = ["a", "abc"]
        assert find_words_optimized([], words) == []
        assert find_words_baseline([], words) == []

    def test_empty_words(self):
        board = [["a", "b"], ["c", "d"]]
        assert find_words_optimized(board, []) == []
        assert find_words_baseline(board, []) == []

    def test_single_cell_board(self):
        board = [["a"]]
        words = ["a", "aa", "b"]

        expected = ["a"]
        assert _sorted_result(board, words, find_words_optimized) == expected
        assert _sorted_result(board, words, find_words_baseline) == expected

    def test_longer_than_board_capacity(self):
        board = [["a", "b"], ["c", "d"]]
        words = ["abcdc", "abcda"]

        assert find_words_optimized(board, words) == []
        assert find_words_baseline(board, words) == []

    def test_non_rectangular_board_raises(self):
        board = [["a", "b"], ["c"]]
        with pytest.raises(ValueError):
            normalize_board(board)

    def test_invalid_cell_raises(self):
        board = [["ab"]]
        with pytest.raises(ValueError):
            normalize_board(board)

    def test_invalid_word_type_raises(self):
        board = [["a"]]
        words = ["a", 3]  # type: ignore[list-item]
        with pytest.raises(ValueError):
            find_words_optimized(board, words)
        with pytest.raises(ValueError):
            find_words_baseline(board, words)


class TestDedupBehavior:
    def test_duplicate_words_input_are_deduped(self):
        board = [
            ["a", "b", "c"],
            ["d", "e", "f"],
            ["g", "h", "i"],
        ]
        words = ["abe", "abe", "ab", "ab", "xyz", ""]

        expected = ["ab", "abe"]
        assert _sorted_result(board, words, find_words_optimized) == expected
        assert _sorted_result(board, words, find_words_baseline) == expected

    def test_multiple_paths_same_word_only_returned_once(self):
        board = [
            ["a", "b"],
            ["b", "a"],
        ]
        words = ["aba"]

        # "aba" can be formed by multiple paths; expected single output entry.
        assert find_words_optimized(board, words) == ["aba"]
        assert find_words_baseline(board, words) == ["aba"]

    def test_normalize_words_removes_empty_and_preserves_order(self):
        words = ["", "x", "y", "x", "", "z", "y"]
        assert normalize_words(words) == ["x", "y", "z"]


class TestUtilities:
    def test_board_to_string(self):
        board = [["a", "b"], ["c", "d"]]
        assert board_to_string(board) == "a b\nc d"

    def test_board_to_string_empty(self):
        assert board_to_string([]) == "<empty board>"

    def test_random_case_generation_basic_shape(self):
        board, words = generate_random_case(3, 4, word_count=10, seed=123)
        assert len(board) == 3
        assert all(len(row) == 4 for row in board)
        assert isinstance(words, list)
        assert all(isinstance(w, str) and w for w in words)

    def test_random_case_generation_zero_words(self):
        board, words = generate_random_case(2, 2, word_count=0, seed=1)
        assert len(board) == 2
        assert len(words) == 0


class TestBaselineOptimizedAgreement:
    @pytest.mark.parametrize("seed", list(range(20)))
    def test_random_small_boards_agree(self, seed: int):
        board, words = generate_random_case(
            4,
            4,
            word_count=16,
            min_word_len=2,
            max_word_len=6,
            alphabet="abcde",
            present_ratio=0.7,
            seed=seed,
        )

        baseline = _sorted_result(board, words, find_words_baseline)
        optimized = _sorted_result(board, words, find_words_optimized)
        assert optimized == baseline

    @pytest.mark.parametrize("seed", [101, 202, 303, 404, 505])
    def test_tiny_dense_alphabet_agree(self, seed: int):
        board, words = generate_random_case(
            3,
            3,
            word_count=20,
            min_word_len=1,
            max_word_len=5,
            alphabet="ab",
            present_ratio=0.5,
            seed=seed,
        )

        baseline = _sorted_result(board, words, find_words_baseline)
        optimized = _sorted_result(board, words, find_words_optimized)
        assert optimized == baseline
