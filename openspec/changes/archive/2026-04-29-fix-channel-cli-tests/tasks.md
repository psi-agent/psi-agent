## 1. Fix test structure

- [x] 1.1 Create `tests/channel/cli/` directory
- [x] 1.2 Move `tests/channel/test_cli.py` to `tests/channel/cli/test_cli.py`
- [x] 1.3 Update imports in test file to use new module path

## 2. Update exports

- [x] 2.1 Ensure `send_message` is exported from `channel/cli/cli.py`

## 3. Verification

- [x] 3.1 Run `uv run pytest tests/channel/` to verify tests pass
- [x] 3.2 Run `uv run ruff check && uv run ruff format`
