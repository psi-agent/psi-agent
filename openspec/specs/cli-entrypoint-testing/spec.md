## ADDED Requirements

### Requirement: Main entrypoint routes to correct component

The `psi-agent` main entrypoint SHALL route commands to the correct component subcommand.

#### Scenario: Invoke session subcommand
- **WHEN** user runs `psi-agent session --workspace ./workspace`
- **THEN** session component SHALL be invoked with the provided arguments

#### Scenario: Invoke ai subcommand
- **WHEN** user runs `psi-agent ai openai-completions --model gpt-4`
- **THEN** openai-completions AI component SHALL be invoked with the provided arguments

#### Scenario: Invoke channel subcommand
- **WHEN** user runs `psi-agent channel repl`
- **THEN** REPL channel component SHALL be invoked

#### Scenario: Invoke workspace subcommand
- **WHEN** user runs `psi-agent workspace pack --input ./workspace`
- **THEN** workspace pack component SHALL be invoked

### Requirement: CLI validates required arguments

The CLI SHALL validate required arguments and display helpful error messages when missing.

#### Scenario: Missing required argument
- **WHEN** user runs `psi-agent session` without required `--workspace` argument
- **THEN** CLI SHALL display an error message indicating the missing argument
- **AND** CLI SHALL exit with non-zero status

### Requirement: CLI handles help flag

The CLI SHALL display help information when `--help` flag is provided.

#### Scenario: Display main help
- **WHEN** user runs `psi-agent --help`
- **THEN** CLI SHALL display available subcommands and their descriptions

#### Scenario: Display subcommand help
- **WHEN** user runs `psi-agent session --help`
- **THEN** CLI SHALL display session-specific options and their descriptions
