# Proposal: Fix Telegram Channel Proxy Configuration

## Summary

Fix the proxy configuration for the Telegram channel so that users can successfully connect to Telegram through HTTP/SOCKS5 proxies.

## Motivation

Users have reported that configuring a proxy for the Telegram channel does not work. This prevents users in regions with restricted access to Telegram from using the bot functionality.

## Problem Analysis

### Current Implementation

The current implementation in `src/psi_agent/channel/telegram/bot.py` uses:

```python
if self.config.proxy:
    builder = builder.proxy(self.config.proxy)
```

### Investigation Findings

1. **API Version Compatibility**: The `proxy()` method was added in python-telegram-bot v20.7. Current version is 22.7, so this is not the issue.

2. **SOCKS5 Dependency**: For SOCKS5 proxies, the `socksio` package is required. This is already defined as an optional dependency (`pip install "psi-agent[socks]"`).

3. **Missing `get_updates_proxy`**: The `proxy()` method sets the proxy for bot API calls (like `sendMessage`, `getMe`), but the updater's `start_polling()` uses a **separate** HTTP connection for `getUpdates`. This connection needs `get_updates_proxy()` to be set separately.

   According to the python-telegram-bot documentation:
   - `proxy()`: Sets proxy for general bot API requests
   - `get_updates_proxy()`: Sets proxy specifically for the `getUpdates` long-polling connection

   **This is the root cause**: Without `get_updates_proxy()`, the updater cannot connect to Telegram through the proxy when polling for updates.

4. **Error Handling**: The current error handling catches `ImportError` and `RuntimeError` for socksio-related issues, which is correct.

### Root Cause

The proxy is only being set for general API requests, not for the `getUpdates` polling connection. The updater's long-polling mechanism uses a separate HTTP client that needs its own proxy configuration.

## Proposed Solution

### 1. Set Both Proxy Methods

Update the `start()` method in `bot.py` to set both `proxy()` and `get_updates_proxy()`:

```python
if self.config.proxy:
    builder = builder.proxy(self.config.proxy)
    builder = builder.get_updates_proxy(self.config.proxy)
```

### 2. Improve Error Messages

Enhance error handling to provide clearer guidance when proxy configuration fails.

### 3. Add Tests

Add tests that verify both proxy methods are called on the builder.

## Impact

- **Users with HTTP/HTTPS proxies**: Will now work correctly for both API calls and polling
- **Users with SOCKS5 proxies**: Will work after installing the `socks` extra dependency
- **Users without proxy**: No change in behavior

## Implementation Plan

1. Modify `src/psi_agent/channel/telegram/bot.py` to set `get_updates_proxy()`
2. Update tests in `tests/channel/telegram/test_bot_streaming.py` to verify both proxy methods are called
3. Run all quality checks (ruff, ty, pytest)
