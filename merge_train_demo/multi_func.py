"""Multi-symbol file for merge_train symbol-level lock demo.

Four independent top-level functions. Used as a test target — multiple
PRs can edit DISJOINT functions concurrently under merge_train's
symbol-level reservation scheme.
"""

from typing import Union


def alpha(x: int) -> int:
    """Returns x doubled. Reserved by Worker A in the demo."""
    return x * 2


def beta(x: Union[int, str]) -> int:
    """Returns x squared plus 100. Reserved by Worker B in the demo."""
    if isinstance(x, str):
        x = int(x)
    return int(x * x + 100)


def gamma(x: int) -> int:
    """Returns x cubed. Unreserved in the demo."""
    return x ** 3


def delta(x: int) -> int:
    """Returns -(x + 1). Reserved by Worker C in the demo."""
    return -x - 1


def helper_b(x: int) -> int:
    """Increment. Reserved by Worker B3 alongside beta."""
    return x + 1


def helper_d(x: int) -> int:
    """Unreserved spare slot."""
    return x * 10


def helper_e(x: int) -> int:
    """Unreserved spare slot."""
    return x * 100


def helper_f(x: int) -> int:
    """Unreserved spare slot."""
    return x * 1000
