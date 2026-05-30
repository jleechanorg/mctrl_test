"""Second file for multi-file contention demo.

Six functions in a separate domain. Workers will reserve symbols
ACROSS this file AND multi_func.py via reserve-plan.
"""


def alpha2(x: int) -> int:
    return x + 1000


def beta2(x: int) -> int:
    return x + 2000


def gamma2(x: int) -> int:
    return x + 3000


def delta2(x: int) -> int:
    return x + 4000


def epsilon2(x: int) -> int:
    return x + 5000


def zeta2(x: int) -> int:
    return x + 6000
