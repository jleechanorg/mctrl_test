from __future__ import annotations


def hello(name: str = "world") -> str:
    """Return a hello greeting (uppercase)."""
    return f"HELLO, {name.upper()}!"


def farewell(name: str = "world") -> str:
    """Return a farewell greeting."""
    return f"Farewell, {name}!"


if __name__ == "__main__":
    print(hello())
