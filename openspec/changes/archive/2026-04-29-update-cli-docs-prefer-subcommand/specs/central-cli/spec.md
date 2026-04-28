## MODIFIED Requirements

### Requirement: README documentation
The system SHALL have brief documentation in README files mentioning the unified CLI interface as the preferred method.

#### Scenario: README mentions unified CLI
- **WHEN** user reads README.md or README_CN.md
- **THEN** there is a sentence explaining `uvx psi-agent <subcommand>` usage
- **AND** the subcommand interface is marked as preferred over standalone commands

## ADDED Requirements

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
