## ADDED Requirements

### Requirement: Central CLI entry point exists
The system SHALL provide a `psi-agent` command that serves as the unified entry point for all component CLIs.

#### Scenario: Run psi-agent without arguments
- **WHEN** user runs `psi-agent` without arguments
- **THEN** system displays help text listing all available subcommands

### Requirement: Dynamic subcommand discovery
The system SHALL dynamically discover subcommands from the `psi_agent` package structure without hardcoding component names.

#### Scenario: Discover ai subcommand
- **WHEN** `psi_agent.ai` package exists with a `chat_completions` submodule
- **THEN** `psi-agent ai chat-completions` command is available

#### Scenario: Discover channel subcommand
- **WHEN** `psi_agent.channel` package exists with a `cli` submodule
- **THEN** `psi-agent channel cli` command is available

#### Scenario: Auto-discover new components
- **WHEN** a new subpackage is added to `psi_agent`
- **THEN** it automatically becomes available as a subcommand without modifying `__main__.py`

### Requirement: Command equivalence
The system SHALL ensure that `psi-agent <component> <subcommand>` produces identical behavior to the corresponding standalone CLI.

#### Scenario: ai chat-completions equivalence
- **WHEN** user runs `psi-agent ai chat-completions --help`
- **THEN** output is identical to `psi-ai-chat-completions --help`

#### Scenario: channel cli equivalence
- **WHEN** user runs `psi-agent channel cli --help`
- **THEN** output is identical to `psi-channel-cli --help`

### Requirement: uvx compatibility
The system SHALL be invocable via `uvx psi-agent <subcommand>` without requiring repository clone.

#### Scenario: Run via uvx
- **WHEN** user runs `uvx psi-agent --help`
- **THEN** system displays help text and exits successfully

### Requirement: README documentation
The system SHALL have brief documentation in README files mentioning the unified CLI interface.

#### Scenario: README mentions unified CLI
- **WHEN** user reads README.md or README_CN.md
- **THEN** there is a sentence explaining `uvx psi-agent <subcommand>` usage
