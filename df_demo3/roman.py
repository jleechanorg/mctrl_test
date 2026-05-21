__version__ = "1.0.0"

_NUMERAL_MAP = [
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
]


def to_roman(n: int) -> str:
    if not isinstance(n, int) or n < 1 or n > 3999:
        raise ValueError(f"n must be an integer between 1 and 3999, got {n!r}")
    result = []
    for value, numeral in _NUMERAL_MAP:
        while n >= value:
            result.append(numeral)
            n -= value
    return "".join(result)
