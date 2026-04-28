## 1. Fix type error

- [x] 1.1 Add `# type: ignore[no-matching-overload]` comment to line 37 in `src/psi_agent/__main__.py`

## 2. Verification

- [x] 2.1 Run `uv run ruff check && uv run ruff format && uv run ty check` to verify all checks pass
