## ADDED Requirements

### Requirement: Channel CLI routes to correct subcommand

The channel CLI SHALL route commands to the correct channel implementation.

#### Scenario: Invoke REPL channel
- **WHEN** user runs `psi-agent channel repl --session-socket ./socket`
- **THEN** REPL channel SHALL be started with the provided socket path

#### Scenario: Invoke Telegram channel
- **WHEN** user runs `psi-agent channel telegram --token xxx --session-socket ./socket`
- **THEN** Telegram channel SHALL be started with the provided credentials

### Requirement: Channel CLI validates required arguments

The channel CLI SHALL validate required arguments for each channel type.

#### Scenario: Missing session socket
- **WHEN** channel is started without `--session-socket` argument
- **THEN** CLI SHALL display an error message indicating the missing argument

#### Scenario: Missing Telegram token
- **WHEN** Telegram channel is started without `--token` argument
- **THEN** CLI SHALL display an error message indicating the missing token

### Requirement: Channel CLI handles help flag

The channel CLI SHALL display help information when `--help` flag is provided.

#### Scenario: Display channel help
- **WHEN** user runs `psi-agent channel --help`
- **THEN** CLI SHALL display available channel types and their options
