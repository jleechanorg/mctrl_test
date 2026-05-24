import pytest
from hypothesis import given, strategies as st
from df_demo3.roman import from_roman, to_roman


def test_single_digits():
    assert from_roman("I") == 1
    assert from_roman("IV") == 4
    assert from_roman("V") == 5
    assert from_roman("IX") == 9


def test_tens():
    assert from_roman("X") == 10
    assert from_roman("XL") == 40
    assert from_roman("L") == 50
    assert from_roman("XC") == 90


def test_hundreds():
    assert from_roman("C") == 100
    assert from_roman("CD") == 400
    assert from_roman("D") == 500
    assert from_roman("CM") == 900


def test_thousands():
    assert from_roman("M") == 1000
    assert from_roman("MMM") == 3000
    assert from_roman("MMMCMXCIX") == 3999


def test_compound_values():
    assert from_roman("II") == 2
    assert from_roman("III") == 3
    assert from_roman("XIV") == 14
    assert from_roman("LVIII") == 58
    assert from_roman("MCMXCIV") == 1994
    assert from_roman("MMXXIV") == 2024


def test_invalid_type_raises():
    with pytest.raises(ValueError):
        from_roman(123)
    with pytest.raises(ValueError):
        from_roman(None)


def test_invalid_characters_raises():
    with pytest.raises(ValueError):
        from_roman("ABC")
    with pytest.raises(ValueError):
        from_roman("MXM")  # Invalid order (though some might accept it, standard greedy won't)


@given(st.integers(min_value=1, max_value=3999))
def test_roman_round_trip(n):
    """Verify that from_roman(to_roman(n)) == n for all valid n."""
    assert from_roman(to_roman(n)) == n
