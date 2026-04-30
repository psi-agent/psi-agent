# Tasks: Fix Telegram Channel Proxy Configuration

## Overview

This change adds `get_updates_proxy()` to the Telegram bot's Application builder to ensure proxy configuration applies to both API requests and updater polling.

## Tasks

### 1. Update bot.py to set get_updates_proxy

**File**: `src/psi_agent/channel/telegram/bot.py`

**Changes**:
- In `start()` method, add call to `builder.get_updates_proxy()` alongside existing `builder.proxy()` call
- Both calls should use the same proxy URL from `self.config.proxy`

**Implementation**:
```python
if self.config.proxy:
    builder = builder.proxy(self.config.proxy)
    builder = builder.get_updates_proxy(self.config.proxy)  # ADD THIS LINE
    # Log proxy without credentials (show host only)
    proxy_display = self._mask_proxy_credentials(self.config.proxy)
    logger.info(f"Using proxy: {proxy_display}")
```

---

### 2. Update tests to verify both proxy methods are called

**File**: `tests/channel/telegram/test_bot_streaming.py`

**Changes**:
- Update `test_http_proxy_no_extra_dependency` to verify `get_updates_proxy` is called
- Update `test_socks5_proxy_missing_dependency_error` to mock both methods
- Update `test_socks5_proxy_runtime_error` to mock both methods
- Update `test_import_error_non_socksio` to mock both methods
- Update `test_runtime_error_non_socks5` to mock both methods

**Implementation**:
Add `mock_builder.get_updates_proxy.return_value = mock_builder` to each test and add assertion:
```python
mock_builder.get_updates_proxy.assert_called_once_with(<proxy_url>)
```

---

### 3. Run quality checks

**Commands**:
```bash
uv run ruff check src/psi_agent/channel/telegram/bot.py
uv run ruff format src/psi_agent/channel/telegram/bot.py
uv run ty check src/psi_agent/channel/telegram/
uv run pytest tests/channel/telegram/ -v
```

---

### 4. Commit changes

**Commit message**:
```
Fix Telegram proxy configuration for updater polling

The proxy was only being set for bot API requests, not for the
getUpdates long-polling connection. This fix adds get_updates_proxy()
to ensure both connections use the configured proxy.

Fixes #92
```

## Verification

1. Run tests: `uv run pytest tests/channel/telegram/ -v`
2. All tests pass
3. Code passes ruff check and format
4. Code passes ty check
