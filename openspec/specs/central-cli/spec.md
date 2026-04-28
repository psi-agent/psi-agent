## Purpose

Central CLI entry point that provides unified access to all psi-agent component commands through a single `psi-agent` command.

## Requirements

### Requirement: Central CLI entry point exists
The system SHALL provide a `psi-agent` command that serves as the unified entry point for all component CLIs.

#### Scenario: Run psi-agent without arguments
- **WHEN** user runs `psi-agent` without arguments
- **THEN** system displays help text listing all available subcommands

### Requirement: Dynamic subcommand discovery
The system SHALL dynamically discover subcommands from the `psi_agent` package structure without hardcoding component names.

#### Scenario: Discover ai subcommand
- **WHEN** `psi_agent.ai` package exists with a `openai_completions` submodule
- **THEN** `psi-agent ai openai-completions` command is available

#### Scenario: Discover channel subcommand
- **WHEN** `psi_agent.channel` package exists with a `cli` submodule
- **THEN** `psi-agent channel cli` command is available

#### Scenario: Auto-discover new components
- **WHEN** a new subpackage is added to `psi_agent`
- **THEN** it automatically becomes available as a subcommand without modifying `__main__.py`

### Requirement: Command equivalence
The system SHALL ensure that `psi-agent <component> <subcommand>` produces identical behavior to the corresponding standalone CLI.

#### Scenario: ai openai-completions equivalence
- **WHEN** user runs `psi-agent ai openai-completions --help`
- **THEN** output is identical to `psi-ai-openai-completions --help`

#### Scenario: channel cli equivalence
- **WHEN** user runs `psi-agent channel cli --help`
- **THEN** output is identical to `psi-channel-cli --help`

### Requirement: uvx compatibility
The system SHALL be invocable via `uvx psi-agent <subcommand>` without requiring repository clone.

#### Scenario: Run via uvx
- **WHEN** user runs `uvx psi-agent --help`
- **THEN** system displays help text and exits successfully

### Requirement: README documentation
The system SHALL have brief documentation in README files mentioning the unified CLI interface as the preferred method.

#### Scenario: README mentions unified CLI
- **WHEN** user reads README.md or README_CN.md
- **THEN** there is a sentence explaining `uvx psi-agent <subcommand>` usage
- **AND** the subcommand interface is marked as preferred over standalone commands

### Requirement: Intermediate help support
The system SHALL provide help text at all command levels using tyro's native subcommand mechanism.

#### Scenario: Component-level help
- **WHEN** user runs `psi-agent ai --help`
- **THEN** system displays all available ai subcommands (openai-completions, anthropic-messages)

#### Scenario: Subcommand-level help
- **WHEN** user runs `psi-agent ai openai-completions --help`
- **THEN** system displays the full help for openai-completions command

### Requirement: Subcommand interface is preferred
The system SHALL document that `psi-agent <component> <subcommand>` is the preferred CLI interface over standalone commands like `psi-ai-openai-completions`.

#### Scenario: Documentation shows preference
- **WHEN** user reads documentation (README, CLAUDE.md)
- **THEN** examples primarily use subcommand format
- **AND** there is a note explaining standalone commands are also available for backward compatibility

#### Scenario: Both interfaces documented
- **WHEN** user reads the CLI documentation
- **THEN** they understand both interfaces exist
- **AND** they know subcommand interface works with `uvx` without cloning
- **AND** they know standalone commands are shorter but less discoverable

### Requirement: Channel CLI imports follow Python module structure

The `psi_agent.channel.__init__.py` file SHALL import CLI classes in a way that avoids E402 lint violations.

#### Scenario: No E402 violations in channel __init__.py
- **WHEN** running `ruff check src/psi_agent/channel/__init__.py`
- **THEN** no E402 errors are reported

#### Scenario: Channel CLI commands still work
- **WHEN** running `psi-agent channel cli --help`
- **THEN** the help text is displayed correctly

#### Scenario: Channel REPL command works
- **WHEN** running `psi-agent channel repl --help`
- **THEN** the help text is displayed correctly

#### Scenario: Channel Telegram command works
- **WHEN** running `psi-agent channel telegram --help`
- **THEN** the help text is displayed correctly

### Requirement: Workspace CLI imports follow Python module structure

The `psi_agent.workspace.__init__.py` file SHALL import CLI classes in a way that avoids E402 lint violations.

#### Scenario: No E402 violations in workspace __init__.py
- **WHEN** running `ruff check src/psi_agent/workspace/__init__.py`
- **THEN** no E402 errors are reported

#### Scenario: Workspace pack command works
- **WHEN** running `psi-agent workspace pack --help`
- **THEN** the help text is displayed correctly

#### Scenario: Workspace unpack command works
- **WHEN** running `psi-agent workspace unpack --help`
- **THEN** the help text is displayed correctly

#### Scenario: Workspace mount command works
- **WHEN** running `psi-agent workspace mount --help`
- **THEN** the help text is displayed correctly

#### Scenario: Workspace umount command works
- **WHEN** running `psi-agent workspace umount --help`
- **THEN** the help text is displayed correctly

#### Scenario: Workspace snapshot command works
- **WHEN** running `psi-agent workspace snapshot --help`
- **THEN** the help text is displayed correctly
