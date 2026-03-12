"""
Sample module with a bug for testing PR workflow.
"""


def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a - b  # Bug: should be a + b


def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


def divide_numbers(a: int, b: int) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
