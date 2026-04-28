## MODIFIED Requirements

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
