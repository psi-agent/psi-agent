# Spec: Telegram Channel Proxy Configuration

## Overview

The Telegram channel component allows users to run a Telegram bot that communicates with psi-session. For users in regions with restricted access to Telegram, proxy support is essential.

## Requirements

### Functional Requirements

1. **FR-1**: The Telegram channel MUST support HTTP, HTTPS, and SOCKS5 proxy configurations
2. **FR-2**: The proxy configuration MUST apply to both:
   - Bot API requests (sendMessage, getMe, etc.)
   - Updater polling (getUpdates long-polling)
3. **FR-3**: The system MUST provide clear error messages when SOCKS5 proxy is used without the required `socksio` dependency

### Non-Functional Requirements

1. **NFR-1**: Proxy credentials MUST be masked in logs for security
2. **NFR-2**: Error messages MUST include installation instructions for SOCKS5 support

## Interface Specification

### Configuration Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `proxy` | `str \| None` | No | Proxy URL for Telegram API. Supports `http://`, `https://`, `socks5://` formats |
| `stream` | `bool` | No | Enable streaming mode (default: True) |
| `stream_interval` | `float` | No | Minimum interval between message edits (default: 1.0) |

### Proxy URL Format

```
<protocol>://[<username>:<password>@]<host>[:<port>]
```

Examples:
- `http://proxy.example.com:8080`
- `socks5://user:pass@proxy.example.com:1080`
- `https://proxy.example.com:443`

## Behavior Specification

### Startup Sequence

1. Create Application builder with token
2. If proxy is configured:
   a. Call `builder.proxy(proxy_url)` for API requests
   b. Call `builder.get_updates_proxy(proxy_url)` for polling
   c. Log proxy configuration (with masked credentials)
3. Build application
4. Handle potential errors:
   - `ImportError` with "socksio" → Show installation instructions
   - `RuntimeError` with "Socks5" → Show installation instructions
   - Other errors → Re-raise

### Error Messages

**SOCKS5 Missing Dependency:**
```
SOCKS5 proxy support requires the 'socksio' package.
Install it with one of:
  pip install 'python-telegram-bot[socks]'
  uv sync --extra socks
```

## Test Specification

### Unit Tests

1. **Test: HTTP proxy configuration**
   - Given: Config with HTTP proxy
   - When: Bot starts
   - Then: Both `proxy()` and `get_updates_proxy()` are called with proxy URL

2. **Test: SOCKS5 proxy with missing socksio**
   - Given: Config with SOCKS5 proxy, socksio not installed
   - When: Bot starts
   - Then: RuntimeError with installation instructions is raised

3. **Test: Proxy without credentials**
   - Given: Config with proxy URL without credentials
   - When: Bot starts
   - Then: Proxy is configured correctly

4. **Test: Proxy credential masking**
   - Given: Proxy URL with username:password
   - When: Logging proxy configuration
   - Then: Credentials are masked as `***`

## Dependencies

### Required Dependencies

- `python-telegram-bot>=22.0` - Provides `proxy()` and `get_updates_proxy()` methods

### Optional Dependencies

- `socksio>=1.0.0` - Required for SOCKS5 proxy support (optional extra: `[socks]`)
