from __future__ import annotations

from word_ladder import ladderLength


def test_example_1() -> None:
    assert ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5


def test_example_2() -> None:
    assert ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0


def test_single_step() -> None:
    assert ladderLength("hot", "dot", ["dot"]) == 2


def test_no_path() -> None:
    assert ladderLength("abc", "xyz", ["abc", "xyz"]) == 0


def test_begin_equals_end() -> None:
    # beginWord == endWord: already at the target
    assert ladderLength("a", "a", ["a", "b", "c"]) == 1


def test_longer_words() -> None:
    assert ladderLength(
        "sand", "acne",
        ["sand", "and", "acnd", "acne", "sane", "ane"],
    ) == 0  # no valid single-letter transformation path from "sand" to "acne"


def test_longer_chain() -> None:
    # Same words as example_1 with "cot" detour — BFS finds hit→hot→dot→cot→cog (length 4),
    # which is a genuinely different path from the test_example_1 chain
    assert ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cot", "cog"]) == 4
