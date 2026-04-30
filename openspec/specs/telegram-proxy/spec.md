## Purpose

Enable Telegram channel to connect through proxy servers for users in restricted network environments.

## Requirements

### Requirement: Telegram channel supports optional proxy configuration

The Telegram channel SHALL accept an optional `--proxy` argument for routing connections through a proxy server.

#### Scenario: Start without proxy
- **WHEN** `psi-agent channel telegram --token <token> --session-socket <path>` is invoked without `--proxy`
- **THEN** the bot SHALL connect directly to Telegram Bot API

#### Scenario: Start with SOCKS5 proxy
- **WHEN** `psi-agent channel telegram --token <token> --session-socket <path> --proxy socks5://host:port` is invoked
- **THEN** the bot SHALL route all connections through the SOCKS5 proxy

#### Scenario: Start with HTTP proxy
- **WHEN** `psi-agent channel telegram --token <token> --session-socket <path> --proxy http://host:port` is invoked
- **THEN** the bot SHALL route all connections through the HTTP proxy

#### Scenario: Start with HTTPS proxy
- **WHEN** `psi-agent channel telegram --token <token> --session-socket <path> --proxy https://host:port` is invoked
- **THEN** the bot SHALL route all connections through the HTTPS proxy

### Requirement: Telegram channel supports proxy with authentication

The Telegram channel SHALL support proxy URLs with embedded credentials.

#### Scenario: SOCKS5 proxy with authentication
- **WHEN** `--proxy socks5://user:password@host:port` is provided
- **THEN** the bot SHALL authenticate with the proxy using the provided credentials

#### Scenario: HTTP proxy with authentication
- **WHEN** `--proxy http://user:password@host:port` is provided
- **THEN** the bot SHALL authenticate with the proxy using the provided credentials

### Requirement: Proxy configuration is passed to python-telegram-bot

The Telegram channel SHALL pass the proxy URL to `python-telegram-bot`'s Application builder.

#### Scenario: Proxy URL passed to Application builder
- **WHEN** a proxy URL is provided via CLI
- **THEN** the `Application.builder()` SHALL be called with `.proxy(proxy_url)`

### Requirement: Proxy argument is masked from process title

The Telegram channel CLI SHALL mask the `--proxy` argument from the process title if it contains credentials.

#### Scenario: Proxy with credentials masked
- **WHEN** `--proxy socks5://user:pass@host:port` is provided
- **THEN** the process title SHALL NOT contain the credentials
- **AND** the process title SHALL show `--proxy ***`

### Requirement: Telegram channel validates proxy dependencies at startup

The Telegram channel SHALL validate that required dependencies are installed for the configured proxy type before attempting to connect.

#### Scenario: SOCKS5 proxy without socksio dependency
- **WHEN** `--proxy socks5://host:port` is provided and `socksio` is not installed
- **THEN** the bot SHALL fail with a clear error message
- **AND** the error message SHALL indicate that `socksio` needs to be installed
- **AND** the error message SHALL suggest installing with `pip install "python-telegram-bot[socks]"` or `uv sync --extra socks`

#### Scenario: HTTP proxy without additional dependencies
- **WHEN** `--proxy http://host:port` is provided
- **THEN** the bot SHALL start successfully without requiring additional dependencies

#### Scenario: HTTPS proxy without additional dependencies
- **WHEN** `--proxy https://host:port` is provided
- **THEN** the bot SHALL start successfully without requiring additional dependencies

### Requirement: Telegram channel CLI documents proxy dependencies

The Telegram channel CLI help text SHALL document the dependency requirements for different proxy types.

#### Scenario: CLI help mentions SOCKS5 dependency
- **WHEN** `psi-agent channel telegram --help` is invoked
- **THEN** the `--proxy` argument description SHALL mention that SOCKS5 proxies require installing the `socks` extra dependency
