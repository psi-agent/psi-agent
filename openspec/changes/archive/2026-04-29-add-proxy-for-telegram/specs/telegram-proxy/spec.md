## ADDED Requirements

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
- **THEN** the `Application.builder()` SHALL be called with `.proxy_url(proxy_url)`

### Requirement: Proxy argument is masked from process title

The Telegram channel CLI SHALL mask the `--proxy` argument from the process title if it contains credentials.

#### Scenario: Proxy with credentials masked
- **WHEN** `--proxy socks5://user:pass@host:port` is provided
- **THEN** the process title SHALL NOT contain the credentials
- **AND** the process title SHALL show `--proxy ***`
