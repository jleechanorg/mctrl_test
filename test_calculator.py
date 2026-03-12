"""
Unit tests for Calculator.
"""
from __future__ import annotations

import pytest
from calculator import add, subtract, multiply, divide


class TestCalculator:
    """Test suite for calculator functions."""

    def test_add_basic(self):
        """Test basic addition."""
        assert add(2, 3) == 5

    def test_add_negative(self):
        """Test addition with negative numbers."""
        assert add(-1, -1) == -2

    def test_add_zero(self):
        """Test adding zero."""
        assert add(5, 0) == 5

    def test_subtract_basic(self):
        """Test basic subtraction."""
        assert subtract(10, 3) == 7

    def test_subtract_negative(self):
        """Test subtraction resulting in negative."""
        assert subtract(5, 10) == -5

    def test_multiply_basic(self):
        """Test basic multiplication."""
        assert multiply(3, 4) == 12

    def test_multiply_zero(self):
        """Test multiplying by zero."""
        assert multiply(100, 0) == 0

    def test_divide_basic(self):
        """Test basic division - expects integer return for whole number division.

        This is an intentionally failing test: the implementation returns float (5.0)
        but the test expects integer (5) to demonstrate a type mismatch.
        """
        result = divide(10, 2)
        # Strict type check: expects int but gets float
        assert isinstance(result, int), f"Expected int but got {type(result).__name__}: {result}"

    def test_divide_fraction(self):
        """Test division resulting in fraction."""
        assert divide(7, 2) == 3.5

    def test_divide_by_zero(self):
        """Test dividing by zero raises error."""
        with pytest.raises(ZeroDivisionError):
            divide(10, 0)
