## 1. Dependency Configuration

- [x] 1.1 Add `[socks]` optional dependency group in `pyproject.toml` with `socksio` package
- [x] 1.2 Update `uv.lock` by running `uv sync`

## 2. Error Handling Implementation

- [x] 2.1 Add proxy validation in `TelegramBot.start()` method to catch missing dependency errors
- [x] 2.2 Create clear error message for missing `socksio` dependency with installation instructions
- [x] 2.3 Update proxy logging to mask credentials properly

## 3. CLI Documentation

- [x] 3.1 Update `Telegram` dataclass docstring to mention SOCKS5 requires extra dependency
- [x] 3.2 Verify `--proxy` argument help text is clear

## 4. Testing

- [x] 4.1 Add test for SOCKS5 proxy configuration without `socksio` (mock the import error)
- [x] 4.2 Add test for HTTP proxy configuration (should work without extra dependencies)
- [x] 4.3 Add test for proxy URL credential masking in logs
- [x] 4.4 Run existing tests to ensure no regressions

## 5. Verification

- [x] 5.1 Run `ruff check` and `ruff format`
- [x] 5.2 Run `ty check` for type checking
- [x] 5.3 Run `pytest` to verify all tests pass
