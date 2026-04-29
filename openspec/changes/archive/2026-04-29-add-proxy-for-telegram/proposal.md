## Why

Users in restricted network environments (e.g., behind corporate firewalls, in countries with Telegram restrictions) cannot connect to Telegram Bot API directly. Adding proxy support allows the telegram channel to work in these environments by routing connections through SOCKS5, HTTP, or HTTPS proxies.

## What Changes

- Add optional `proxy` parameter to Telegram channel CLI (`psi-agent channel telegram`)
- Support three proxy types: SOCKS5, HTTP, HTTPS
- Default to `None` (no proxy) for normal operation
- Pass proxy configuration to `python-telegram-bot`'s Application builder

## Capabilities

### New Capabilities

- `telegram-proxy`: Support for proxy configuration in Telegram channel, enabling connections through SOCKS5, HTTP, or HTTPS proxies

### Modified Capabilities

- `telegram-channel`: CLI now accepts optional `--proxy` argument; bot initialization passes proxy to Application builder

## Impact

- **Affected code**: `src/psi_agent/channel/telegram/cli.py`, `src/psi_agent/channel/telegram/config.py`, `src/psi_agent/channel/telegram/bot.py`
- **Dependencies**: `python-telegram-bot` supports proxy via `proxy_url` parameter in Application builder (no new dependencies needed)
- **API**: CLI adds `--proxy` optional argument