## ADDED Requirements

### Requirement: Sensitive argument masking principle

CLAUDE.md SHALL document the security principle that all CLI entry points accepting sensitive credentials (API keys, tokens, passwords) MUST mask them from the process title.

#### Scenario: New CLI with sensitive arguments
- **WHEN** a new CLI entry point is created that accepts sensitive credentials
- **THEN** the CLI SHALL call the masking utility immediately after argument parsing
- **AND** this requirement SHALL be documented in CLAUDE.md coding principles
