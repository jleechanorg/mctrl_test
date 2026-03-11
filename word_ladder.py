from __future__ import annotations

from collections import deque


def ladderLength(beginWord: str, endWord: str, wordList: list[str]) -> int:
    word_set = set(wordList)
    if endWord not in word_set:
        return 0

    queue: deque[tuple[str, int]] = deque([(beginWord, 1)])
    visited: set[str] = {beginWord}

    while queue:
        word, depth = queue.popleft()
        for i in range(len(word)):
            for c in "abcdefghijklmnopqrstuvwxyz":
                next_word = word[:i] + c + word[i + 1:]
                if next_word == endWord:
                    return depth + 1
                if next_word in word_set and next_word not in visited:
                    visited.add(next_word)
                    queue.append((next_word, depth + 1))

    return 0


def test_example_1() -> None:
    assert ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5


def test_example_2() -> None:
    assert ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0


def test_single_step() -> None:
    assert ladderLength("hot", "dot", ["dot"]) == 2


def test_no_path() -> None:
    assert ladderLength("abc", "xyz", ["abc", "xyz"]) == 0


def test_begin_equals_end_in_list() -> None:
    # endWord is reachable in one step
    assert ladderLength("a", "c", ["a", "b", "c"]) == 2


def test_longer_words() -> None:
    assert ladderLength(
        "sand", "acne",
        ["sand", "and", "acnd", "acne", "sane", "ane"],
    ) == 0  # no valid path (different lengths mixed but all same length required)


def test_longer_chain() -> None:
    result = ladderLength(
        "hit", "cog",
        ["hot", "dot", "dog", "lot", "log", "cog"],
    )
    assert result == 5


if __name__ == "__main__":
    # Run basic verification
    print("Example 1:", ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]))
    print("Example 2:", ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log"]))
    print("All tests passed!" if all([
        ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5,
        ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0,
    ]) else "Some tests failed!")
