"""Simple hello world application."""
from __future__ import annotations


def greet(name: str = "World") -> str:
    """Return a greeting string."""
    return f"Hello, {name}!"


def main() -> None:
    print(greet())


if __name__ == "__main__":
    main()
