"""
Sample module with a bug for testing PR workflow.
"""


def add_numbers(a: int, b: int) -> int:
    """Add two integers together.

    Args:
        a: First integer to add.
        b: Second integer to add.

    Returns:
        The sum of a and b.
    """
    return a + b  # Fixed: was incorrectly using subtraction


def multiply_numbers(a: int, b: int) -> int:
    """Multiply two integers together.

    Args:
        a: First integer to multiply.
        b: Second integer to multiply.

    Returns:
        The product of a and b.
    """
    return a * b


def divide_numbers(a: int, b: int) -> float:
    """Divide the first integer by the second.

    Args:
        a: The dividend (number to be divided).
        b: The divisor (number to divide by).

    Returns:
        The result of a divided by b.

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
