## Context

The Telegram channel (`psi-agent channel telegram`) uses `python-telegram-bot` library to connect to Telegram Bot API. Currently, it only supports direct connections, which fails in restricted network environments.

`python-telegram-bot` v20+ supports proxy configuration via the `proxy_url` parameter in `Application.builder()`. This uses Python's built-in `aiohttp` connector with proxy support.

## Goals / Non-Goals

**Goals:**
- Add optional `--proxy` CLI argument accepting proxy URLs
- Support SOCKS5 (`socks5://`), HTTP (`http://`), and HTTPS (`https://`) proxy URLs
- Default behavior unchanged (no proxy when argument not provided)
- Pass proxy to `python-telegram-bot` Application builder

**Non-Goals:**
- Proxy authentication UI/CLI (credentials embedded in URL are supported)
- Proxy connection testing/validation
- Multiple proxy configurations or fallback chains

## Decisions

### Proxy URL Format

Use standard URL format for all proxy types:
- `socks5://host:port` - SOCKS5 proxy
- `socks5://user:pass@host:port` - SOCKS5 with authentication
- `http://host:port` - HTTP proxy
- `https://host:port` - HTTPS proxy

**Rationale**: Standard URL format is widely understood and supported by `aiohttp`. No need for custom parsing logic.

### Configuration Storage

Add `proxy` field to `TelegramConfig` dataclass as `str | None = None`.

**Rationale**: Keeps configuration in one place, follows existing pattern.

### Application Builder Integration

Pass proxy URL to `Application.builder().proxy_url(proxy).build()`.

**Rationale**: Native `python-telegram-bot` support, no custom connector needed.

## Risks / Trade-offs

- **SOCKS5 requires `python-socks` package** → Document in README if users need SOCKS5 support
- **Proxy URL with credentials visible in process list** → Already mitigated by `mask_sensitive_args()` pattern (extend to include `proxy`)
- **Invalid proxy URL causes startup failure** → Clear error message from `aiohttp`, acceptable behavior
