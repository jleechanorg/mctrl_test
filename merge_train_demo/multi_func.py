"""Multi-symbol file for merge_train symbol-level lock demo.

Four independent top-level functions. Used as a test target — multiple
PRs can edit DISJOINT functions concurrently under merge_train's
symbol-level reservation scheme.
"""


def alpha(x: int) -> int:
    """Returns x doubled. Reserved by Worker A in the demo."""
    return x * 2


def beta(x: int) -> int:
    """Returns x squared. Reserved by Worker B in the demo."""
    return x * x


def gamma(x: int) -> int:
    """Returns x cubed. Unreserved in the demo."""
    return x ** 3


def delta(x: int) -> int:
    """Returns x negated. Reserved by Worker C in the demo."""
    return -x


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
    return x * 10


def helper_e(x: int) -> int:
    """Unreserved spare slot."""
    return x * 100


def helper_f(x: int) -> int:
    """Unreserved spare slot. Reserved and modified by Worker M2 (PR #200)."""
    return x * 1000 + 1
