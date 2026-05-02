## ADDED Requirements

### Requirement: CLI module follows three-layer architecture

The CLI module SHALL follow the three-layer separation pattern consistent with other channel modules.

#### Scenario: CLI module has config class
- **WHEN** examining `src/psi_agent/channel/cli/` directory
- **THEN** it SHALL contain a `config.py` file with `CliConfig` dataclass

#### Scenario: CLI module has client class
- **WHEN** examining `src/psi_agent/channel/cli/` directory
- **THEN** it SHALL contain a `client.py` file with `CliClient` class
- **AND** `CliClient` SHALL implement async context manager pattern

#### Scenario: CLI config provides socket_path method
- **WHEN** using `CliConfig` class
- **THEN** it SHALL have a `socket_path()` method returning `anyio.Path`

### Requirement: CLI client async context manager logging

The CLI client SHALL log resource cleanup in `__aexit__` at DEBUG level.

#### Scenario: Connector close logging
- **WHEN** exiting `CliClient` async context
- **THEN** connector close SHALL be logged at DEBUG level

### Requirement: CLI startup logging

The CLI SHALL log startup at INFO level.

#### Scenario: Startup logging at INFO level
- **WHEN** starting CLI channel
- **THEN** it SHALL log "Starting psi-channel-cli" at INFO level

### Requirement: CLI request body includes model field

The CLI request body SHALL include the `model` field.

#### Scenario: Request body structure
- **WHEN** CLI sends request to session
- **THEN** the request body SHALL include `"model": "session"`

### Requirement: CLI error response format

The CLI SHALL use consistent error response format.

#### Scenario: Connection error format
- **WHEN** connection to session fails
- **THEN** the error message SHALL be `f"Error: Failed to connect to session at {socket_path}"`

#### Scenario: HTTP error format
- **WHEN** session returns non-200 status
- **THEN** the error message SHALL be `f"Error: Session returned status {status_code}"`

#### Scenario: Timeout error format
- **WHEN** request times out
- **THEN** the error message SHALL be `"Error: Request timeout"`

### Requirement: CLI module exports

The CLI module SHALL export public classes via `__init__.py`.

#### Scenario: CLI module exports public classes
- **WHEN** importing from `psi_agent.channel.cli`
- **THEN** `Cli`, `CliConfig`, `CliClient` SHALL be available