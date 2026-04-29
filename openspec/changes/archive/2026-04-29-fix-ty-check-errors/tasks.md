## 1. Fix Type Checker Errors

- [x] 1.1 Add `# ty: ignore[no-matching-overload]` to `src/psi_agent/__main__.py:37` for tyro.cli call
- [x] 1.2 Add `# ty: ignore[not-iterable]` to `src/psi_agent/session/server.py:140` for AsyncGenerator iteration

## 2. Verification

- [x] 2.1 Run `uv run ty check src` and verify no errors
