"""Example test module for session/mt-17."""


def test_example_pass():
    """A simple passing test."""
    assert 1 + 1 == 2


def test_example_strings():
    """Test string operations."""
    assert "hello".upper() == "HELLO"
    assert "hello".replace("l", "r") == "herro"


def test_example_list():
    """Test list operations."""
    assert [1, 2, 3] == [1, 2, 3]
    assert len([1, 2, 3]) == 3
    assert sum([1, 2, 3]) == 6
