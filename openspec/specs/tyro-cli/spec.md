## ADDED Requirements

### Requirement: Tyro-based CLI implementation
The system SHALL use tyro's native subcommand mechanism for the unified CLI entry point.

#### Scenario: Tyro subcommand structure
- **WHEN** the psi-agent CLI is invoked
- **THEN** it uses tyro.cli() with a Union type for subcommands

### Requirement: Intermediate help support
The system SHALL provide help text at all command levels.

#### Scenario: Top-level help
- **WHEN** user runs `psi-agent --help`
- **THEN** system displays all available component subcommands

#### Scenario: Component-level help
- **WHEN** user runs `psi-agent ai --help`
- **THEN** system displays all available ai subcommands (openai-completions, anthropic-messages)

#### Scenario: Subcommand-level help
- **WHEN** user runs `psi-agent ai openai-completions --help`
- **THEN** system displays the full help for openai-completions command

### Requirement: Consistent CLI interface
Each component SHALL expose a Commands class or callable compatible with tyro subcommands.

#### Scenario: Component Commands class
- **WHEN** a component has multiple subcommands
- **THEN** it exposes a Commands class with typed fields for each subcommand

#### Scenario: Single command component
- **WHEN** a component has only one command
- **THEN** it exposes a callable or class directly
