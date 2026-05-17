from __future__ import annotations


def hello(name: str = "world") -> str:
    """Return a hello greeting (uppercase)."""
    return f"HELLO, {name.upper()}!"


def goodbye(name: str = "world") -> str:
    """Return a goodbye greeting."""
    return f"Goodbye, {name}!"


if __name__ == "__main__":
    print(hello())
