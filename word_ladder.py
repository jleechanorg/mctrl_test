"""LeetCode 127 - Word Ladder (BFS solution)."""

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


def test_example_1():
    assert ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5


def test_example_2():
    assert ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0


def test_single_step():
    assert ladderLength("hot", "dot", ["dot"]) == 2


def test_no_path():
    assert ladderLength("abc", "xyz", ["abc", "xyz"]) == 0


def test_single_letter_words():
    assert ladderLength("a", "c", ["a", "b", "c"]) == 2


def test_end_word_not_in_list():
    assert ladderLength("hit", "cog", []) == 0


if __name__ == "__main__":
    test_example_1()
    test_example_2()
    test_single_step()
    test_no_path()
    test_single_letter_words()
    test_end_word_not_in_list()
    print("All tests passed!")
