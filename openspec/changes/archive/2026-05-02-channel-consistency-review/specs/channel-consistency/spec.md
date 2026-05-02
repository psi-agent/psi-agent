## ADDED Requirements

### Requirement: Channel module architecture consistency

All channel submodules (cli, repl, telegram) SHALL follow a three-layer separation pattern:
- `cli.py`: CLI entry point using tyro
- `config.py`: Configuration dataclass
- `client.py`: HTTP client for session communication

#### Scenario: CLI module has three-layer structure
- **WHEN** examining `src/psi_agent/channel/cli/` directory
- **THEN** it SHALL contain `cli.py`, `config.py`, and `client.py` files

#### Scenario: Config class provides socket_path method
- **WHEN** using any channel config class (CliConfig, ReplConfig, TelegramConfig)
- **THEN** it SHALL have a `socket_path()` method returning `anyio.Path`

### Requirement: Channel logging granularity

All channel modules SHALL follow consistent logging granularity:
- DEBUG level: request body, response body, streaming chunks, connection details
- INFO level: component startup, request received, response sent

#### Scenario: Startup logging at INFO level
- **WHEN** starting any channel component (cli, repl, telegram)
- **THEN** it SHALL log "Starting psi-channel-<name>" at INFO level

#### Scenario: Request body logging at DEBUG level
- **WHEN** sending a request to session
- **THEN** the full request body SHALL be logged at DEBUG level in JSON format

#### Scenario: Streaming chunk logging at DEBUG level
- **WHEN** receiving a streaming chunk from session
- **THEN** content and reasoning chunks SHALL be logged at DEBUG level

### Requirement: Request body structure

All channel requests to session SHALL include the following fields:
- `model`: MUST be "session"
- `messages`: Array of message objects with `role` and `content`
- `stream`: Boolean for streaming mode

#### Scenario: Request body includes model field
- **WHEN** sending a request from any channel (cli, repl, telegram)
- **THEN** the request body SHALL include `"model": "session"`

#### Scenario: Telegram request includes user field
- **WHEN** sending a request from telegram channel
- **THEN** the request body SHALL include `"user": "telegram:<user_id>"`

### Requirement: Error response format

All channel error responses SHALL use the format: `f"Error: <description>"`

#### Scenario: Connection error format
- **WHEN** connection to session fails
- **THEN** the error message SHALL be `f"Error: Failed to connect to session at {socket_path}"`

#### Scenario: HTTP error format
- **WHEN** session returns non-200 status
- **THEN** the error message SHALL be `f"Error: Session returned status {status_code}"`

#### Scenario: Timeout error format
- **WHEN** request times out
- **THEN** the error message SHALL be `"Error: Request timeout"`

### Requirement: Async context manager logging

All channel client classes SHALL log resource cleanup in `__aexit__`:
- Session close: log at DEBUG level
- Connector close: log at DEBUG level

#### Scenario: Connector close logging
- **WHEN** exiting client async context
- **THEN** connector close SHALL be logged at DEBUG level

### Requirement: Module exports

All channel submodules SHALL export their public classes via `__init__.py`:
- cli: `Cli`, `CliConfig`, `CliClient`
- repl: `Repl`, `ReplConfig`, `ReplClient`
- telegram: `Telegram`, `TelegramConfig`, `TelegramClient`

#### Scenario: Telegram module exports public classes
- **WHEN** importing from `psi_agent.channel.telegram`
- **THEN** `Telegram`, `TelegramConfig`, `TelegramClient` SHALL be available

### Requirement: Streaming content handling

All channel streaming handlers SHALL use consistent content checking:
- Check `content is not None` before appending to buffer
- Check `content` (truthy) before logging and callback

#### Scenario: Empty content string handling
- **WHEN** streaming chunk has `content: ""`
- **THEN** it SHALL be appended to buffer but not logged or passed to callback

#### Scenario: None content handling
- **WHEN** streaming chunk has no content field or `content: null`
- **THEN** it SHALL NOT be appended to buffer