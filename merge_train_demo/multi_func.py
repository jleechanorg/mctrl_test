"""Multi-symbol file for merge_train symbol-level lock demo.

Four independent top-level functions. Used as a test target -- multiple
PRs can edit DISJOINT functions concurrently under merge_train's
symbol-level reservation scheme.
"""


def alpha(x: int) -> int:
    """Returns x doubled. Reserved by Worker A2 in the demo."""
    return x * 2


def beta(x: int) -> int:
    """Returns x squared plus 100. Reserved by Worker B2 in the demo."""
    return x * x + 100


def gamma(x: int) -> int:
    """Returns x cubed. Unreserved in the demo."""
    return x ** 3


def delta(x: int) -> int:
    """Returns -(x + 1). Reserved by Worker C2 in the demo."""
    return -x - 1
