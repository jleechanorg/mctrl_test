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

_ROMAN_TO_INT = {numeral: value for value, numeral in _NUMERAL_MAP}


def to_roman(n: int) -> str:
    """Convert an integer to a Roman numeral string.

    Args:
        n: An integer in the range [1, 3999].

    Returns:
        The Roman numeral representation of n.

    Raises:
        ValueError: If n is not a plain int or is outside [1, 3999].
    """
    if type(n) is not int or n < 1 or n > 3999:
        raise ValueError(f"n must be an integer between 1 and 3999, got {n!r}")
    result = []
    for value, numeral in _NUMERAL_MAP:
        while n >= value:
            result.append(numeral)
            n -= value
    return "".join(result)


def from_roman(s: str) -> int:
    """Convert a Roman numeral string to an integer.

    Args:
        s: A string representing a Roman numeral.

    Returns:
        The integer value of the Roman numeral.

    Raises:
        ValueError: If s is not a string or is not a valid Roman numeral.
    """
    if not isinstance(s, str):
        raise ValueError(f"Input must be a string, got {type(s)!r}")

    i = 0
    result = 0
    while i < len(s):
        # Check for two-character numeral (like CM, IV)
        if i + 1 < len(s) and s[i : i + 2] in _ROMAN_TO_INT:
            result += _ROMAN_TO_INT[s[i : i + 2]]
            i += 2
        elif s[i] in _ROMAN_TO_INT:
            result += _ROMAN_TO_INT[s[i]]
            i += 1
        else:
            raise ValueError(f"Invalid Roman numeral character: {s[i]!r}")

    # Validation: re-convert to ensure it's a standard representation
    # This catches things like 'IIII' or 'MXM' which might otherwise be parsed
    if result < 1 or result > 3999 or to_roman(result) != s:
        raise ValueError(f"Invalid Roman numeral: {s!r}")

    return result
