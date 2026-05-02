from __future__ import annotations

from collections import deque


def ladderLength(beginWord: str, endWord: str, wordList: list[str]) -> int:
    if beginWord == endWord:
        return 1
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


# Snake_case alias for PEP 8 consistency with the rest of the repo
ladder_length = ladderLength


if __name__ == "__main__":
    # Run basic smoke checks (not a full test suite — see test_word_ladder.py)
    examples = [
        ("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"], 5),
        ("hit", "cog", ["hot", "dot", "dog", "lot", "log"], 0),
    ]
    for begin, end, words, expected in examples:
        result = ladderLength(begin, end, words)
        print(f"ladderLength({begin!r}, {end!r}, …) = {result}  (expected {expected})")
    print("Smoke checks done.")
