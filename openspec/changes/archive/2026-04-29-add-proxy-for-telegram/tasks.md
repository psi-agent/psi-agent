## 1. Configuration

- [x] 1.1 Add `proxy: str | None = None` field to `TelegramConfig` dataclass in `config.py`
- [x] 1.2 Update `TelegramConfig` docstring to document the new `proxy` parameter

## 2. CLI

- [x] 2.1 Add `proxy: str | None = None` field to `Telegram` dataclass in `cli.py`
- [x] 2.2 Update `Telegram` docstring to document the new `--proxy` argument
- [x] 2.3 Pass `proxy` to `TelegramConfig` constructor
- [x] 2.4 Update `mask_sensitive_args` call to include `["token", "proxy"]` (proxy may contain credentials)

## 3. Bot Implementation

- [x] 3.1 Modify `TelegramBot.start()` to pass `proxy_url` to `Application.builder()` when proxy is configured
- [x] 3.2 Add debug logging for proxy configuration

## 4. Testing

- [x] 4.1 Add unit tests for `TelegramConfig` with proxy parameter
- [x] 4.2 Add unit tests for CLI parsing with and without `--proxy` argument
- [x] 4.3 Run `ruff check`, `ruff format`, `ty check` to ensure code quality
- [x] 4.4 Run full test suite to verify no regressions
