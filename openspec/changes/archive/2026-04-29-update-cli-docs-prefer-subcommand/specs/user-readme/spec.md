## MODIFIED Requirements

### Requirement: README.md contains essential sections
The README.md SHALL include the following sections:
1. Project title and brief description
2. Language switch link (to README_zh.md)
3. Installation instructions (documenting both CLI interfaces)
4. Quick start example (using subcommand interface)
5. Component overview
6. Available scripts list (explaining both interfaces)
7. Link to detailed documentation

#### Scenario: User reads README.md structure
- **WHEN** a user reads README.md
- **THEN** they can quickly understand what psi-agent is, how to install it, and how to get started
- **AND** they can switch to the Chinese version via the language link
- **AND** they understand that `psi-agent <component> <subcommand>` is the preferred interface

### Requirement: README.md documents both CLI interfaces
The README.md SHALL document both the unified subcommand interface and standalone commands, clearly stating that the subcommand interface is preferred.

#### Scenario: User sees subcommand preference
- **WHEN** a user reads the Quick Start section
- **THEN** all examples use `psi-agent <component> <subcommand>` format
- **AND** there is a note explaining standalone commands are also available

#### Scenario: User understands both interfaces
- **WHEN** a user reads the Available Scripts section
- **THEN** they see both `psi-agent ai openai-completions` and `psi-ai-openai-completions` documented
- **AND** there is clear indication that subcommand format is preferred