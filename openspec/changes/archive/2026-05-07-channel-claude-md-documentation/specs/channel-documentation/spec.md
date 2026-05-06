## ADDED Requirements

### Requirement: Channel package documentation structure

The channel package SHALL have a CLAUDE.md file documenting the overall architecture and design.

#### Scenario: Channel package has CLAUDE.md
- **WHEN** examining `src/psi_agent/channel/` directory
- **THEN** it SHALL contain a `CLAUDE.md` file

#### Scenario: Documentation covers architecture
- **WHEN** reading `src/psi_agent/channel/CLAUDE.md`
- **THEN** it SHALL document the three-layer separation pattern (CLI/Config/Client)

### Requirement: CLI subpackage documentation

The CLI subpackage SHALL have a CLAUDE.md file documenting its implementation details.

#### Scenario: CLI subpackage has CLAUDE.md
- **WHEN** examining `src/psi_agent/channel/cli/` directory
- **THEN** it SHALL contain a `CLAUDE.md` file

#### Scenario: Documentation covers Cli class
- **WHEN** reading `src/psi_agent/channel/cli/CLAUDE.md`
- **THEN** it SHALL document the `Cli` dataclass and its usage

#### Scenario: Documentation covers CliClient
- **WHEN** reading `src/psi_agent/channel/cli/CLAUDE.md`
- **THEN** it SHALL document `CliClient` class including async context manager pattern

#### Scenario: Documentation covers CliConfig
- **WHEN** reading `src/psi_agent/channel/cli/CLAUDE.md`
- **THEN** it SHALL document `CliConfig` dataclass and its fields

### Requirement: REPL subpackage documentation

The REPL subpackage SHALL have a CLAUDE.md file documenting its implementation details.

#### Scenario: REPL subpackage has CLAUDE.md
- **WHEN** examining `src/psi_agent/channel/repl/` directory
- **THEN** it SHALL contain a `CLAUDE.md` file

#### Scenario: Documentation covers Repl class
- **WHEN** reading `src/psi_agent/channel/repl/CLAUDE.md`
- **THEN** it SHALL document the `Repl` class and prompt-toolkit integration

#### Scenario: Documentation covers ReplClient
- **WHEN** reading `src/psi_agent/channel/repl/CLAUDE.md`
- **THEN** it SHALL document `ReplClient` streaming and non-streaming methods

### Requirement: Telegram subpackage documentation

The Telegram subpackage SHALL have a CLAUDE.md file documenting its implementation details.

#### Scenario: Telegram subpackage has CLAUDE.md
- **WHEN** examining `src/psi_agent/channel/telegram/` directory
- **THEN** it SHALL contain a `CLAUDE.md` file

#### Scenario: Documentation covers TelegramBot
- **WHEN** reading `src/psi_agent/channel/telegram/CLAUDE.md`
- **THEN** it SHALL document `TelegramBot` class and streaming message editing

#### Scenario: Documentation covers proxy configuration
- **WHEN** reading `src/psi_agent/channel/telegram/CLAUDE.md`
- **THEN** it SHALL document proxy configuration including SOCKS5 support

### Requirement: Documentation includes usage examples

Each subpackage documentation SHALL include practical usage examples.

#### Scenario: CLI documentation has examples
- **WHEN** reading `src/psi_agent/channel/cli/CLAUDE.md`
- **THEN** it SHALL include CLI command examples

#### Scenario: REPL documentation has examples
- **WHEN** reading `src/psi_agent/channel/repl/CLAUDE.md`
- **THEN** it SHALL include REPL startup and usage examples

#### Scenario: Telegram documentation has examples
- **WHEN** reading `src/psi_agent/channel/telegram/CLAUDE.md`
- **THEN** it SHALL include Telegram bot startup examples
