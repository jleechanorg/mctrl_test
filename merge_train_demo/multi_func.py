"""Multi-symbol file for merge_train symbol-level lock demo.

Several top-level functions and helper utilities. Used as a test target — multiple
PRs can edit DISJOINT functions concurrently under merge_train's
symbol-level reservation scheme.
"""


def alpha(x: int) -> int:
    """Returns x doubled plus one. Reserved by Worker A in the demo."""
    return x * 2 + 1


def beta(x: int) -> int:
    """Returns x squared. Reserved by Worker B in the demo."""
    return x * x


def gamma(x: int) -> int:
    """Returns x cubed plus one. Unreserved in the demo."""
    return x ** 3 + 1


def delta(x: int) -> int:
    """Returns -(x + 1). Reserved by Worker C in the demo."""
    return -x - 1


def helper_a(x: int) -> int:
    """Identity. Reserved by Worker A3 alongside alpha."""
    return x


def helper_b(x: int) -> int:
    """Increment. Reserved by Worker B3 alongside beta."""
    return x + 1


def helper_c(x: int) -> int:
    """Decrement. Reserved by Worker C3 alongside delta."""
    return x - 1


def helper_d(x: int) -> int:
    """Unreserved spare slot."""
    return x * 10 + 1


def helper_e(x: int) -> int:
    """Unreserved spare slot."""
    return x * 100 + 1


def helper_f(x: int) -> int:
    """Unreserved spare slot."""
    return x * 1000
