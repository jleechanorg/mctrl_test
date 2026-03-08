# mctrl_test

Minimal Python hello world with pytest and CI for mctrl testing.

## Structure

- `app.py` — hello world app with `greet()` and `main()`
- `test_app.py` — pytest tests
- `.github/workflows/ci.yml` — GitHub Actions CI (Python 3.12, MiniMax M2.5 lane)

## Usage

```bash
python app.py
# Hello, World!

pytest -v
```

## CI

GitHub Actions runs on every push and PR:
- Install dependencies
- Run pytest
- Claude lane uses MiniMax M2.5 (Anthropic-compatible API)

## MiniMax Model Mapping

The CI workflow uses MiniMax M2.5 (`MiniMax-M2-5`) via an Anthropic-compatible endpoint
for the Claude lane. Set `MINIMAX_API_KEY` and `MINIMAX_BASE_URL` as repository secrets.
