"""
Tests for sample_buggy module - includes a failing test.
"""
from sample_buggy import add_numbers, multiply_numbers, divide_numbers


def test_add_numbers_basic():
    """Test basic addition."""
    assert add_numbers(1, 2) == 3


def test_add_numbers_negative():
    """Test addition with negative numbers."""
    assert add_numbers(-1, -2) == -3


def test_add_numbers_mixed():
    """Test addition with mixed positive/negative."""
    assert add_numbers(5, -3) == 2


def test_multiply_numbers_basic():
    """Test basic multiplication."""
    assert multiply_numbers(3, 4) == 12


def test_divide_numbers_basic():
    """Test basic division."""
    assert divide_numbers(10, 2) == 5


def test_divide_by_zero():
    """Test division by zero raises error."""
    try:
        divide_numbers(10, 0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Cannot divide by zero" in str(e)
