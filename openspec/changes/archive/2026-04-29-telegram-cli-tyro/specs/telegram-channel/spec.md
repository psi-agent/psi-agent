## ADDED Requirements

### Requirement: Telegram channel uses tyro dataclass CLI pattern

The Telegram channel CLI SHALL use a dataclass with `__call__` method for tyro integration.

#### Scenario: Dataclass CLI implementation
- **WHEN** the telegram CLI module is defined
- **THEN** it SHALL use a `@dataclass` class named `Telegram`
- **AND** the class SHALL have a `__call__` method that executes the command

#### Scenario: CLI parameters as dataclass fields
- **WHEN** the `Telegram` dataclass is defined
- **THEN** `token` and `session_socket` SHALL be dataclass fields
- **AND** tyro SHALL automatically generate CLI arguments from these fields

### Requirement: Telegram channel integrates with channel subcommands

The Telegram channel SHALL be available as a subcommand under `psi-agent channel`.

#### Scenario: Channel subcommand integration
- **WHEN** user runs `psi-agent channel telegram --token <token> --session-socket <path>`
- **THEN** the telegram channel SHALL start

#### Scenario: Channel Commands class includes Telegram
- **WHEN** the `psi_agent.channel` module is imported
- **THEN** the `Commands` class SHALL include `Telegram` as a subcommand option

#### Scenario: Help at channel level
- **WHEN** user runs `psi-agent channel --help`
- **THEN** the help text SHALL show `telegram` as an available subcommand
