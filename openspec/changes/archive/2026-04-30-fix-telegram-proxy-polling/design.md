# Design: Telegram Channel Proxy Configuration Fix

## Architecture Context

The Telegram channel component uses python-telegram-bot's `Application` class, which has two separate HTTP clients:

1. **Bot API Client**: Used for all bot API calls (sendMessage, editMessageText, getMe, etc.)
2. **Updater Client**: Used specifically for `getUpdates` long-polling

Each client has its own proxy configuration, which must be set separately.

## Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    TelegramBot                          │
│                                                         │
│  ┌─────────────────┐     ┌─────────────────────────┐   │
│  │   Application   │────▶│      Bot API Client     │   │
│  │    (Builder)    │     │  (proxy() configured)   │   │
│  │                 │     │                         │   │
│  │                 │     └─────────────────────────┘   │
│  │                 │                                    │
│  │                 │     ┌─────────────────────────┐   │
│  │                 │────▶│     Updater Client      │   │
│  │                 │     │ (get_updates_proxy()    │   │
│  │                 │     │     configured)         │   │
│  └─────────────────┘     └─────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │    Telegram API       │
              │  (via Proxy Server)   │
              └───────────────────────┘
```

## Implementation Design

### Modified Code: bot.py

**Current Implementation:**
```python
if self.config.proxy:
    builder = builder.proxy(self.config.proxy)
```

**New Implementation:**
```python
if self.config.proxy:
    builder = builder.proxy(self.config.proxy)
    builder = builder.get_updates_proxy(self.config.proxy)
    # Log proxy without credentials (show host only)
    proxy_display = self._mask_proxy_credentials(self.config.proxy)
    logger.info(f"Using proxy: {proxy_display}")
```

### Method: `get_updates_proxy()`

This method was introduced in python-telegram-bot v20.7 alongside `proxy()`. Both methods accept the same proxy URL format:
- String URL: `"http://proxy.example.com:8080"`
- httpx.Proxy object
- httpx.URL object

Both use the same underlying HTTPXRequest class, so the proxy URL format is identical.

## Error Handling Design

### Error Flow

```
Application.builder()
    .proxy(url)
    .get_updates_proxy(url)
    .build()
    │
    ├─▶ ImportError (socksio) ──▶ RuntimeError (installation instructions)
    │
    ├─▶ RuntimeError (Socks5) ──▶ RuntimeError (installation instructions)
    │
    └─▶ Success
```

### Error Handling Code

The existing error handling is correct and will catch errors from both proxy configurations:

```python
try:
    self._app = builder.build()
except ImportError as e:
    if "socksio" in str(e).lower():
        msg = (
            "SOCKS5 proxy support requires the 'socksio' package.\n"
            "Install it with one of:\n"
            "  pip install 'python-telegram-bot[socks]'\n"
            "  uv sync --extra socks"
        )
        raise RuntimeError(msg) from e
    raise
except RuntimeError as e:
    if "Socks5" in str(e):
        msg = (
            "SOCKS5 proxy support requires the 'socksio' package.\n"
            "Install it with one of:\n"
            "  pip install 'python-telegram-bot[socks]'\n"
            "  uv sync --extra socks"
        )
        raise RuntimeError(msg) from e
    raise
```

## Test Design

### Test Cases

1. **`test_bot_with_both_proxy_methods_called`**
   - Mock Application.builder()
   - Verify both `proxy()` and `get_updates_proxy()` are called with same URL

2. **`test_http_proxy_with_both_methods`**
   - Use HTTP proxy URL
   - Verify builder methods are called correctly
   - Verify app builds successfully

3. **`test_socks5_proxy_missing_dependency_both_methods`**
   - Verify error is caught regardless of which method triggers it

### Test Implementation Strategy

Update existing tests in `TestProxyValidation` class to verify both methods are called:

```python
@pytest.mark.asyncio
async def test_http_proxy_no_extra_dependency(self):
    """Test HTTP proxy works without extra dependencies."""
    config = TelegramConfig(
        token="test-token",
        session_socket="/tmp/test.sock",
        proxy="http://localhost:8080",
    )
    bot = TelegramBot(config)

    mock_builder = MagicMock()
    mock_builder.token.return_value = mock_builder
    mock_builder.proxy.return_value = mock_builder
    mock_builder.get_updates_proxy.return_value = mock_builder  # NEW
    mock_builder.build.return_value = mock_app

    with patch("psi_agent.channel.telegram.bot.Application.builder", return_value=mock_builder):
        await bot.start()

    # Verify both methods are called
    mock_builder.proxy.assert_called_once_with("http://localhost:8080")
    mock_builder.get_updates_proxy.assert_called_once_with("http://localhost:8080")
```

## Security Considerations

The existing `_mask_proxy_credentials()` method correctly handles credential masking for logging. No changes needed.

## Compatibility

- python-telegram-bot v20.7+: Required (already using v22.7)
- socksio v1.0.0+: Optional for SOCKS5 (already defined in optional dependencies)