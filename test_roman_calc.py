import pytest
from df_demo3.roman_calc import add, subtract, multiply, divide

def test_roman_addition():
    assert add("I", "I") == "II"
    assert add("XIV", "VI") == "XX"
    assert add("MCMXCIV", "VI") == "MM"

def test_roman_subtraction():
    assert subtract("X", "I") == "IX"
    assert subtract("XX", "XIV") == "VI"

def test_roman_multiplication():
    assert multiply("III", "IV") == "XII"
    assert multiply("X", "X") == "C"

def test_roman_division():
    assert divide("X", "II") == "V"
    assert divide("IX", "III") == "III"
    # Integer division: 10 // 3 = 3 -> III
    assert divide("X", "III") == "III"

def test_invalid_inputs():
    with pytest.raises(ValueError):
        add("invalid", "I")
    with pytest.raises(ValueError):
        subtract("I", "invalid")
    with pytest.raises(ValueError):
        multiply("X", 123)  # type error/value error

def test_overflow_and_underflow():
    # Max roman numeral is 3999 (MMMCMXCIX)
    with pytest.raises(ValueError):
        add("MMMCMXCIX", "I")
    
    # Subtraction resulting in 0 or negative
    with pytest.raises(ValueError):
        subtract("V", "V")
    with pytest.raises(ValueError):
        subtract("V", "VI")

def test_division_by_zero_and_underflow():
    with pytest.raises(ValueError):
        divide("X", "invalid")
    
    # Division resulting in zero (1 // 2 = 0) which is invalid in Roman numerals
    with pytest.raises(ValueError):
        divide("I", "II")

def test_inline_comments_exist():
    import inspect
    import df_demo3.roman_calc as rc
    for func in [rc.add, rc.subtract, rc.multiply, rc.divide]:
        source = inspect.getsource(func)
        # Look for a comment line (starts with #, ignoring whitespace) within the function body
        lines = [line.strip() for line in source.splitlines()]
        has_comment = any(line.startswith("#") for line in lines)
        assert has_comment, f"Function {func.__name__} has no inline comments"

