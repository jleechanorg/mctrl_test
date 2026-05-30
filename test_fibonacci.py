import pytest
from fibonacci import fibonacci


def test_fibonacci_base_cases():
    """Test Fibonacci base cases: 0 and 1."""
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1


def test_fibonacci_small_values():
    """Test Fibonacci calculation for small values."""
    assert fibonacci(2) == 1
    assert fibonacci(3) == 2
    assert fibonacci(4) == 3
    assert fibonacci(5) == 5


def test_fibonacci_larger_value():
    """Test Fibonacci calculation for larger values."""
    assert fibonacci(10) == 55
    assert fibonacci(20) == 6765


def test_fibonacci_negative_raises():
    """Verify that fibonacci raises ValueError for negative input."""
    with pytest.raises(ValueError):
        fibonacci(-1)
