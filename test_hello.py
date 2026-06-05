from __future__ import annotations

from hello import farewell, greet, hello


def test_hello_default():
    """Test hello function with default name."""
    assert hello() == "HELLO, WORLD!"


def test_hello_custom_name():
    """Test hello function with a custom name."""
    assert hello("Alice") == "HELLO, ALICE!"


def test_hello_returns_string():
    """Verify that hello function returns a string."""
    result = hello("test")
    assert isinstance(result, str)


def test_goodbye_default():
    """Test farewell function with default name."""
    assert farewell() == "Farewell, world!"


def test_goodbye_custom_name():
    """Test farewell function with a custom name."""
    assert farewell("Alice") == "Farewell, Alice!"


def test_greet_world():
    assert greet("World") == "Hello, World!"


def test_greet_name():
    assert greet("Jeffrey") == "Hello, Jeffrey!"


def test_greet_docstring_references_hello():
    """Verify that greet's docstring documents its difference from hello."""
    assert greet.__doc__ is not None
    assert "hello" in greet.__doc__.lower()


def test_greet_title_cases_lowercase_name():
    """Verify that greet function formats name in title-case."""
    assert greet("jeffrey") == "Hello, Jeffrey!"
    assert greet("bob smith") == "Hello, Bob Smith!"


def test_greet_docstring_example_consistent():
    """Verify that greet's docstring contains a consistent example."""
    assert greet.__doc__ is not None
    assert "Hello, Name!" in greet.__doc__


def test_greet_differs_from_hello():
    """Verify that greet output is different from hello output."""
    assert greet("jeffrey") != hello("jeffrey")
    assert greet("jeffrey") == "Hello, Jeffrey!"
    assert hello("jeffrey") == "HELLO, JEFFREY!"


def test_greet_default_argument():
    """Verify that greet supports a default argument of 'world'."""
    assert greet() == "Hello, World!"


def test_greet_mixed_and_uppercase_name():
    """Verify that greet title-cases mixed-case and uppercase inputs."""
    assert greet("jEfFrEy") == "Hello, Jeffrey!"
    assert greet("JEFFREY") == "Hello, Jeffrey!"


def test_greet_internal_capitalization_limitation():
    """Verify how greet handles names with internal capitalization.

    Note: This test documents the known limitation of using Python's str.title(),
    where internal capitalization is lost (e.g., 'McGregor' becomes 'Mcgregor').
    """
    assert greet("McGregor") == "Hello, Mcgregor!"



