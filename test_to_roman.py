import pytest
from to_roman import to_roman


def test_single_digits():
    """Test to_roman with single-digit integers."""
    assert to_roman(1) == "I"
    assert to_roman(4) == "IV"
    assert to_roman(5) == "V"
    assert to_roman(9) == "IX"


def test_tens():
    """Test to_roman with multiples of ten."""
    assert to_roman(10) == "X"
    assert to_roman(40) == "XL"
    assert to_roman(50) == "L"
    assert to_roman(90) == "XC"


def test_hundreds():
    """Test to_roman with multiples of a hundred."""
    assert to_roman(100) == "C"
    assert to_roman(400) == "CD"
    assert to_roman(500) == "D"
    assert to_roman(900) == "CM"


def test_thousands():
    """Test to_roman with multiples of a thousand and the maximum value."""
    assert to_roman(1000) == "M"
    assert to_roman(3000) == "MMM"
    assert to_roman(3999) == "MMMCMXCIX"


def test_compound_values():
    """Test to_roman with compound integer values."""
    assert to_roman(2) == "II"
    assert to_roman(3) == "III"
    assert to_roman(14) == "XIV"
    assert to_roman(58) == "LVIII"
    assert to_roman(1994) == "MCMXCIV"
    assert to_roman(2024) == "MMXXIV"


def test_out_of_range_raises():
    """Verify that to_roman raises ValueError for values outside [1, 3999]."""
    with pytest.raises(ValueError):
        to_roman(0)
    with pytest.raises(ValueError):
        to_roman(4000)
    with pytest.raises(ValueError):
        to_roman(-1)
