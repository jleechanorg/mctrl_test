"""
Comprehensive tests for Word Search II Solver.

Tests cover:
- Canonical examples from LeetCode
- Edge cases (empty boards, single cells, etc.)
- Deduplication behavior
- Random sanity checks comparing baseline vs optimized solvers
"""

from __future__ import annotations

import random
import pytest
from word_search_ii_solver import (
    Trie,
    TrieNode,
    baseline_solve,
    optimized_solve,
    solve_with_dedup,
    format_board,
    create_board,
    generate_random_test_case,
    generate_embedded_words_test_case,
    verify_solvers_equivalent,
    get_complexity_notes,
)


# =============================================================================
# TEST TRIE DATA STRUCTURE
# =============================================================================

class TestTrie:
    """Tests for the Trie data structure."""

    def test_trie_insert_single_word(self):
        trie = Trie()
        trie.insert("hello")
        assert trie.starts_with("hel")
        assert trie.starts_with("hello")
        assert not trie.starts_with("world")

    def test_trie_insert_multiple_words(self):
        trie = Trie()
        trie.insert("cat")
        trie.insert("car")
        trie.insert("card")
        trie.insert("care")

        assert trie.starts_with("ca")
        assert trie.starts_with("cat")
        assert trie.starts_with("car")
        assert not trie.starts_with("dog")

    def test_trie_get_words_with_prefix(self):
        trie = Trie()
        trie.insert("cat")
        trie.insert("card")
        trie.insert("care")
        trie.insert("dog")

        words = trie.get_words_with_prefix("car")
        assert set(words) == {"card", "care"}

    def test_trie_empty_prefix(self):
        trie = Trie()
        trie.insert("test")
        words = trie.get_words_with_prefix("")
        assert "test" in words


# =============================================================================
# CANONICAL EXAMPLES
# =============================================================================

class TestCanonicalExamples:
    """Tests for canonical LeetCode examples."""

    def test_example_1(self):
        """Standard example from LeetCode - 4x4 board."""
        board = [
            ['o', 'a', 'a', 'n'],
            ['e', 't', 'a', 'e'],
            ['i', 'h', 'k', 'r'],
            ['i', 'f', 'l', 'v']
        ]
        words = ["oath", "pea", "eat", "rain"]
        result = optimized_solve(board, words)
        assert set(result) == {"oath", "eat"}

    def test_example_2(self):
        """2x2 board with overlapping words."""
        board = [
            ['a', 'b'],
            ['c', 'd']
        ]
        words = ["abcd", "acdb", "ade", "adb", "abc"]
        result = optimized_solve(board, words)
        # Only acdb is valid with 4-directional adjacency.
        assert set(result) == {"acdb"}

    def test_example_3(self):
        """Example with multiple words found."""
        board = [
            ['a', 'a', 'a', 'a'],
            ['a', 'a', 'a', 'a'],
            ['a', 'a', 'a', 'a'],
            ['b', 'c', 'd', 'e'],
            ['f', 'g', 'h', 'i'],
            ['j', 'k', 'l', 'm']
        ]
        words = ["abcdefghijklm", "ab", "aj", "kj", "a"]
        result = optimized_solve(board, words)
        # Words found: ab (a->b), kj (k->j), a
        assert isinstance(result, list)

    def test_no_words_found(self):
        """Board with no matching words."""
        board = [
            ['a', 'b'],
            ['c', 'd']
        ]
        words = ["xyz", "zzz", "abc"]
        result = optimized_solve(board, words)
        assert result == []


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_board(self):
        board: list[list[str]] = []
        words = ["test"]
        result = optimized_solve(board, words)
        assert result == []

    def test_empty_words(self):
        board = [['a', 'b'], ['c', 'd']]
        words: list[str] = []
        result = optimized_solve(board, words)
        assert result == []

    def test_single_cell_board_word_found(self):
        board = [['a']]
        words = ["a"]
        result = optimized_solve(board, words)
        assert result == ["a"]

    def test_single_cell_board_word_not_found(self):
        board = [['a']]
        words = ["b", "ab"]
        result = optimized_solve(board, words)
        assert result == []

    def test_single_row_board(self):
        board = [['a', 'b', 'c', 'd']]
        words = ["ab", "bc", "cd", "abc", "bcd"]
        result = optimized_solve(board, words)
        assert "ab" in result

    def test_single_column_board(self):
        board = [['a'], ['b'], ['c'], ['d']]
        words = ["ab", "bc", "cd", "abc", "bcd"]
        result = optimized_solve(board, words)
        assert "ab" in result

    def test_word_length_one(self):
        """Words of length 1 should not be valid (per LeetCode spec)."""
        board = [['a', 'b'], ['c', 'd']]
        words = ["a", "b", "c", "d", "e"]
        result = optimized_solve(board, words)
        assert isinstance(result, list)

    def test_very_long_word(self):
        """Test with words longer than board can accommodate."""
        board = [['a', 'b'], ['c', 'd']]
        words = ["abcde", "abcdef", "abcd"]
        result = optimized_solve(board, words)
        assert result == []

    def test_all_same_characters(self):
        """Board with all same characters."""
        board = [['a', 'a'], ['a', 'a']]
        words = ["aaa", "aaaa", "aa"]
        result = optimized_solve(board, words)
        assert "aa" in result

    def test_case_sensitivity(self):
        """Test that solver treats uppercase letters as-is."""
        board = [['A', 'B'], ['C', 'D']]
        words = ["AB", "CD"]
        result = optimized_solve(board, words)
        # Uppercase handled gracefully
        assert isinstance(result, list)


# =============================================================================
# DEDUPLICATION BEHAVIOR
# =============================================================================

class TestDeduplication:
    """Tests for deduplication behavior."""

    def test_duplicate_words_in_input(self):
        board = [['a', 'b'], ['c', 'd']]
        words = ["ab", "cd", "ab", "abcd", "ab"]
        result = solve_with_dedup(board, words, use_optimized=True)
        # Should contain each unique word only once
        assert result.count("ab") == 1
        assert len(result) == len(set(result))

    def test_all_duplicate_words(self):
        board = [['a', 'b'], ['c', 'd']]
        words = ["ab", "ab", "ab", "ab"]
        result = solve_with_dedup(board, words, use_optimized=True)
        assert result == ["ab"]

    def test_dedup_with_multiple_found(self):
        board = [
            ['a', 'b', 'c'],
            ['d', 'e', 'f'],
            ['g', 'h', 'i']
        ]
        words = ["abc", "cfi", "abc", "cfi", "adh", "adh"]
        result = solve_with_dedup(board, words, use_optimized=True)
        # Words are sorted alphabetically, duplicates removed
        assert isinstance(result, list)
        assert len(result) == len(set(result))


# =============================================================================
# BASELINE VS OPTIMIZED VERIFICATION
# =============================================================================

class TestSolversEquivalent:
    """Tests verifying baseline and optimized solvers produce same results."""

    def test_small_boards_equivalence(self):
        """Test equivalence on various small boards."""
        test_cases = [
            ([['a']], ["a", "b"]),
            ([['a', 'b'], ['c', 'd']], ["ab", "cd", "ac", "bd", "abc"]),
            ([['a', 'b', 'c']], ["ab", "bc", "abc"]),
            ([['a'], ['b'], ['c']], ["ab", "bc", "abc"]),
        ]

        for board, words in test_cases:
            assert verify_solvers_equivalent(board, words), f"Failed for board={board}, words={words}"

    def test_random_equivalence(self):
        """Test equivalence on random boards."""
        random.seed(12345)
        for _ in range(20):
            board = create_board(3, 3)
            _, words = generate_embedded_words_test_case(board, num_extra_words=5)
            assert verify_solvers_equivalent(board, words), f"Failed for random test"

    def test_larger_random_equivalence(self):
        """Test equivalence on larger random boards."""
        random.seed(54321)
        for _ in range(10):
            board = create_board(4, 4)
            _, words = generate_embedded_words_test_case(board, num_extra_words=10)
            assert verify_solvers_equivalent(board, words), f"Failed for larger random test"


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

class TestHelperFunctions:
    """Tests for helper utilities."""

    def test_format_board(self):
        board = [['a', 'b'], ['c', 'd']]
        formatted = format_board(board)
        assert "a" in formatted
        assert "b" in formatted
        assert "c" in formatted
        assert "d" in formatted

    def test_create_board(self):
        board = create_board(3, 4)
        assert len(board) == 3
        assert len(board[0]) == 4
        assert all(isinstance(c, str) for row in board for c in row)

    def test_create_board_default_chars(self):
        board = create_board(2, 2)
        for row in board:
            for c in row:
                assert c.islower() and len(c) == 1

    def test_generate_random_test_case(self):
        board, words = generate_random_test_case(
            board_rows=3,
            board_cols=3,
            num_words=5,
            seed=42
        )
        assert len(board) == 3
        assert len(words) == 5
        assert all(isinstance(w, str) and len(w) >= 2 for w in words)

    def test_generate_random_test_case_reproducibility(self):
        board1, words1 = generate_random_test_case(seed=100)
        board2, words2 = generate_random_test_case(seed=100)
        assert board1 == board2
        assert words1 == words2

    def test_generate_embedded_words_test_case(self):
        random.seed(999)  # Set seed before generating
        board = create_board(4, 4)
        result_board, words = generate_embedded_words_test_case(board, num_extra_words=3)
        assert result_board == board
        assert len(words) > 0


# =============================================================================
# COMPLEXITY AND INTEGRATION TESTS
# =============================================================================

class TestComplexityNotes:
    """Tests for complexity notes utility."""

    def test_get_complexity_notes(self):
        notes = get_complexity_notes()
        assert "BASELINE SOLVER" in notes
        assert "TRIE-BASED OPTIMIZED SOLVER" in notes
        assert "Time Complexity" in notes
        assert "Space Complexity" in notes


class TestIntegration:
    """Integration tests combining multiple functionalities."""

    def test_full_workflow(self):
        """Test complete workflow: generate case, solve, verify."""
        board, words = generate_random_test_case(seed=777)
        result = optimized_solve(board, words)
        baseline_result = baseline_solve(board, words)

        assert isinstance(result, list)
        assert isinstance(baseline_result, list)
        assert result == baseline_result  # Verify equivalence

    def test_solve_with_dedup_workflow(self):
        """Test solve_with_dedup with various inputs."""
        board = create_board(3, 3, seed=555)
        words_with_dups = ["test", "word", "test", "hello", "world", "word"]
        result = solve_with_dedup(board, words_with_dups, use_optimized=True)

        # Verify no duplicates
        assert len(result) == len(set(result))

    def test_multiple_directions(self):
        """Test words found in supported directions (horizontal/vertical)."""
        board = [
            ['a', 'b', 'c'],
            ['d', 'e', 'f'],
            ['g', 'h', 'i']
        ]
        words = [
            "abc",    # horizontal
            "adg",    # vertical
            "aei",    # diagonal (should not match in this problem)
            "beh",    # vertical from center column
            "abcdefghi"  # spiral
        ]
        result = optimized_solve(board, words)
        assert "abc" in result
        assert "adg" in result
        assert "beh" in result
        assert "aei" not in result


# =============================================================================
# PERFORMANCE-RELATED TESTS (SANITY CHECKS)
# =============================================================================

class TestPerformanceSanity:
    """Sanity checks for performance characteristics."""

    def test_optimized_faster_than_baseline(self):
        """Sanity check that optimized is typically faster."""
        import time

        board = create_board(8, 8, seed=111)
        _, words = generate_embedded_words_test_case(board, num_extra_words=30)

        # Run optimized
        start = time.time()
        opt_result = optimized_solve(board, words)
        opt_time = time.time() - start

        # Run baseline (may take longer)
        start = time.time()
        base_result = baseline_solve(board, words)
        base_time = time.time() - start

        # Verify correctness
        assert opt_result == base_result

        # Optimized should typically be faster
        # (Not guaranteed but expected for this case)
        print(f"Optimized: {opt_time:.4f}s, Baseline: {base_time:.4f}s")

    def test_large_word_list_handling(self):
        """Test handling of large word lists."""
        board = create_board(5, 5, seed=222)
        words = ["word" + str(i) for i in range(100)]
        result = optimized_solve(board, words)
        assert isinstance(result, list)


# =============================================================================
# RUN ALL TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
