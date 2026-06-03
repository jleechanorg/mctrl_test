"""Second file for multi-file contention symbol-level lock demo.

Six functions in a separate domain. Workers will reserve symbols
ACROSS this file AND multi_func.py via reserve-plan.
"""


def alpha2(x: int) -> int:
    """Returns x plus 1000."""
    return x + 1000


def beta2(x: int) -> int:
    """Returns x plus 2000."""
    return x + 2000


def gamma2(x: int) -> int:
    """Returns x plus 3000."""
    return x + 3000


def delta2(x: int) -> int:
    """Returns x plus 4000."""
    return x + 4000


def epsilon2(x: int) -> int:
    """Returns x plus 5000."""
    return x + 5000


def zeta2(x: int) -> int:
    """Returns x plus 6000."""
    return x + 6000
