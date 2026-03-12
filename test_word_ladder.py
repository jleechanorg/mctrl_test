"""Tests for Word Ladder (LeetCode 127)."""

import pytest
from word_ladder import ladder_length


def test_basic_transformation():
    """Classic example: hit -> cog."""
    assert ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5


def test_no_path():
    """End word not reachable."""
    assert ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0


def test_end_word_not_in_list():
    """End word missing from word list."""
    assert ladder_length("hit", "cog", ["hot", "dot", "dog"]) == 0


def test_single_step():
    """One letter difference between begin and end."""
    assert ladder_length("a", "c", ["c"]) == 2


def test_longer_chain():
    """Longer transformation chain."""
    word_list = ["hot", "dot", "dog", "lot", "log", "cog"]
    assert ladder_length("hit", "cog", word_list) == 5


def test_empty_word_list():
    """Empty word list returns 0."""
    assert ladder_length("hit", "cog", []) == 0


def test_multiple_paths_returns_shortest():
    """Multiple valid paths; BFS finds the shortest."""
    word_list = ["ted", "tex", "red", "tax", "tad", "den", "rex", "pee"]
    result = ladder_length("red", "tax", word_list)
    assert result == 4  # red -> ted -> tad -> tax or red -> rex -> tex -> tax


def test_no_common_neighbor():
    """Words share no neighbor at all."""
    assert ladder_length("abc", "xyz", ["xyz"]) == 0


def test_two_letter_words():
    """Short words still work correctly."""
    assert ladder_length("ab", "cd", ["ad", "cd"]) == 3  # ab -> ad -> cd
