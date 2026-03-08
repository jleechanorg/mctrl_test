# mctrl_test

Minimal Python hello-world package for mctrl integration testing.

## Structure

```
src/
  hello/           # source package
    __init__.py    # greet() and main()
  tests/
    test_hello.py  # pytest tests
pyproject.toml     # package config + pytest settings
.github/
  workflows/
    ci.yml         # GitHub Actions CI
```

## Usage

```bash
python -m pytest src/tests/ -v
```
