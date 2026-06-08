"""Module for Roman numeral calculator operations.

Provides addition, subtraction, multiplication, and division of Roman numeral strings.
"""

from df_demo3.roman import to_roman, from_roman


def add(a: str, b: str) -> str:
    """Add two Roman numerals.

    Args:
        a: First Roman numeral string.
        b: Second Roman numeral string.

    Returns:
        The Roman numeral sum.

    Raises:
        ValueError: If either operand is invalid or the result is out of range.
    """
    val_a = from_roman(a)
    val_b = from_roman(b)
    return to_roman(val_a + val_b)


def subtract(a: str, b: str) -> str:
    """Subtract the second Roman numeral from the first.

    Args:
        a: First Roman numeral string.
        b: Second Roman numeral string.

    Returns:
        The Roman numeral difference.

    Raises:
        ValueError: If either operand is invalid or the result is out of range.
    """
    val_a = from_roman(a)
    val_b = from_roman(b)
    return to_roman(val_a - val_b)


def multiply(a: str, b: str) -> str:
    """Multiply two Roman numerals.

    Args:
        a: First Roman numeral string.
        b: Second Roman numeral string.

    Returns:
        The Roman numeral product.

    Raises:
        ValueError: If either operand is invalid or the result is out of range.
    """
    val_a = from_roman(a)
    val_b = from_roman(b)
    return to_roman(val_a * val_b)


def divide(a: str, b: str) -> str:
    """Divide the first Roman numeral by the second (integer division).

    Args:
        a: First Roman numeral string.
        b: Second Roman numeral string.

    Returns:
        The Roman numeral quotient.

    Raises:
        ValueError: If either operand is invalid or the result is out of range.
    """
    val_a = from_roman(a)
    val_b = from_roman(b)
    return to_roman(val_a // val_b)

