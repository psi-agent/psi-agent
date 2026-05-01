## ADDED Requirements

### Requirement: Telegram proxy applies to both API requests and updater polling

The Telegram channel SHALL apply proxy configuration to both bot API requests and the updater's getUpdates polling connection.

#### Scenario: Proxy configured for API requests
- **WHEN** `--proxy <proxy_url>` is provided
- **THEN** the bot SHALL call `builder.proxy(proxy_url)` for bot API requests (sendMessage, getMe, etc.)

#### Scenario: Proxy configured for updater polling
- **WHEN** `--proxy <proxy_url>` is provided
- **THEN** the bot SHALL call `builder.get_updates_proxy(proxy_url)` for the updater's long-polling connection
- **AND** both API requests and polling SHALL use the same proxy

#### Scenario: No proxy configured
- **WHEN** `--proxy` is not provided
- **THEN** the bot SHALL connect directly without proxy for both API requests and polling

### Requirement: Proxy error messages are clear and actionable

The Telegram channel SHALL provide clear error messages when proxy configuration fails.

#### Scenario: SOCKS5 proxy without socksio dependency
- **WHEN** `--proxy socks5://host:port` is provided and `socksio` is not installed
- **THEN** the bot SHALL fail with error message indicating `socksio` needs to be installed
- **AND** the error message SHALL suggest `pip install 'python-telegram-bot[socks]'` or `uv sync --extra socks`

#### Scenario: HTTP proxy works without additional dependencies
- **WHEN** `--proxy http://host:port` is provided
- **THEN** the bot SHALL start successfully without requiring additional dependencies
