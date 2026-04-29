## MODIFIED Requirements

### Requirement: Telegram channel provides CLI entry point

The Telegram channel SHALL provide a CLI command `psi-channel-telegram` for starting the bot.

#### Scenario: CLI starts with token argument
- **WHEN** `psi-channel-telegram --token <token> --session-socket <path>` is invoked
- **THEN** the bot SHALL initialize and connect to the session

#### Scenario: CLI starts with token and proxy argument
- **WHEN** `psi-channel-telegram --token <token> --session-socket <path> --proxy <proxy_url>` is invoked
- **THEN** the bot SHALL initialize with proxy configuration and connect to the session

#### Scenario: Missing token shows error
- **WHEN** `psi-channel-telegram` is invoked without `--token`
- **THEN** the CLI SHALL display an error and exit

### Requirement: Telegram channel uses tyro dataclass CLI pattern

The Telegram channel CLI SHALL use a dataclass with `__call__` method for tyro integration.

#### Scenario: Dataclass CLI implementation
- **WHEN** the telegram CLI module is defined
- **THEN** it SHALL use a `@dataclass` class named `Telegram`
- **AND** the class SHALL have a `__call__` method that executes the command

#### Scenario: CLI parameters as dataclass fields
- **WHEN** the `Telegram` dataclass is defined
- **THEN** `token`, `session_socket`, and `proxy` SHALL be dataclass fields
- **AND** `proxy` SHALL be optional with default value `None`
- **AND** tyro SHALL automatically generate CLI arguments from these fields

### Requirement: CLI masks sensitive token from process title

The Telegram channel CLI SHALL mask the `--token` and `--proxy` arguments from the process title immediately after parsing.

#### Scenario: Token masked in process title
- **WHEN** `psi-channel-telegram` is started with `--token 123456:ABC`
- **THEN** the process title SHALL NOT contain the token value
- **AND** the process title SHALL show `--token ***`

#### Scenario: Proxy with credentials masked in process title
- **WHEN** `psi-channel-telegram` is started with `--proxy socks5://user:pass@host:port`
- **THEN** the process title SHALL NOT contain the proxy credentials
- **AND** the process title SHALL show `--proxy ***`