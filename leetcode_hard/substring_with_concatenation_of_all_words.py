from collections import Counter, defaultdict
from typing import List


def find_substring(s: str, words: List[str]) -> List[int]:
    """LeetCode 30: Sliding window by word-length offsets."""
    if not s or not words or not words[0]:
        return []

    word_len = len(words[0])
    words_count = len(words)
    total_len = word_len * words_count
    if len(s) < total_len:
        return []

    target = Counter(words)
    result = []

    for offset in range(word_len):
        left = offset
        window_count = defaultdict(int)
        used = 0

        for right in range(offset, len(s) - word_len + 1, word_len):
            word = s[right : right + word_len]
            if word not in target:
                window_count.clear()
                used = 0
                left = right + word_len
                continue

            window_count[word] += 1
            used += 1

            while window_count[word] > target[word]:
                left_word = s[left : left + word_len]
                window_count[left_word] -= 1
                used -= 1
                left += word_len

            if used == words_count:
                result.append(left)
                left_word = s[left : left + word_len]
                window_count[left_word] -= 1
                used -= 1
                left += word_len

    return result
