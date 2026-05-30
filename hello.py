from __future__ import annotations


def hello(name: str = "world") -> str:
    """Return a hello greeting (uppercase)."""
    return f"HELLO, {name.upper()}!"


def farewell(name: str = "world") -> str:
    """Return a farewell greeting."""
    return f"Farewell, {name}!"


def greet(name: str) -> str:
    """Return a title-case greeting for the given name.

    Unlike hello(), which returns an uppercase greeting, this function
    returns a standard title-case formatting (e.g., "Hello, name!").
    """
    return f"Hello, {name.title()}!"


if __name__ == "__main__":
    print(hello())
