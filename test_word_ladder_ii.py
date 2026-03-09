from __future__ import annotations

from word_ladder_ii import find_ladders


def _normalized(paths: list[list[str]]) -> list[tuple[str, ...]]:
    return sorted(tuple(path) for path in paths)


def test_find_ladders_leetcode_example():
    begin_word = "hit"
    end_word = "cog"
    word_list = ["hot", "dot", "dog", "lot", "log", "cog"]

    expected = [
        ("hit", "hot", "dot", "dog", "cog"),
        ("hit", "hot", "lot", "log", "cog"),
    ]
    assert _normalized(find_ladders(begin_word, end_word, word_list)) == expected


def test_find_ladders_no_path_when_end_missing():
    begin_word = "hit"
    end_word = "cog"
    word_list = ["hot", "dot", "dog", "lot", "log"]
    assert find_ladders(begin_word, end_word, word_list) == []


def test_find_ladders_returns_only_shortest_paths():
    begin_word = "red"
    end_word = "tax"
    word_list = ["ted", "tex", "red", "tax", "tad", "den", "rex", "pee"]

    expected = [
        ("red", "rex", "tex", "tax"),
        ("red", "ted", "tad", "tax"),
        ("red", "ted", "tex", "tax"),
    ]
    assert _normalized(find_ladders(begin_word, end_word, word_list)) == expected


def test_find_ladders_begin_equals_end():
    assert find_ladders("same", "same", ["same", "came"]) == [["same"]]
