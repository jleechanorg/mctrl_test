"""Tests for delta and helper_c in multi_func.py.

Verifies that implementations match their docstrings:
- delta: negation (x -> -x)
- helper_c: decrement (x -> x - 1)
"""

from multi_func import delta, helper_c


def test_delta_negates():
    assert delta(0) == 0
    assert delta(5) == -5
    assert delta(-3) == 3


def test_helper_c_decrements():
    assert helper_c(0) == -1
    assert helper_c(10) == 9
    assert helper_c(1) == 0
