## Why

The `--proxy` argument for the Telegram channel does not work when using SOCKS5 proxies because the required dependency `socksio` is not installed. Users who need SOCKS5 proxy support receive a confusing `RuntimeError` at runtime instead of a clear error message at startup. Additionally, there is no validation or helpful error message when proxy configuration fails.

## What Changes

- Add `socksio` as an optional dependency for SOCKS5 proxy support
- Add startup validation for proxy configuration with clear error messages
- Add documentation about proxy dependencies and limitations
- Add integration test to verify proxy configuration is correctly applied

## Capabilities

### New Capabilities

- `telegram-proxy-validation`: Startup validation for proxy configuration with clear error messages

### Modified Capabilities

- `telegram-proxy`: Add requirement for dependency validation and clear error messages when proxy configuration fails

## Impact

- `pyproject.toml`: Add optional dependency for SOCKS5 proxy support
- `src/psi_agent/channel/telegram/bot.py`: Add proxy validation at startup
- `tests/channel/telegram/`: Add tests for proxy validation
- Documentation: Update CLI help and README about proxy dependencies
