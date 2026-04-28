## ADDED Requirements

### Requirement: CLI imports follow Python module structure

The `psi_agent.ai.__init__.py` file SHALL import CLI classes in a way that avoids E402 lint violations.

#### Scenario: No E402 violations in ai __init__.py
- **WHEN** running `ruff check src/psi_agent/ai/__init__.py`
- **THEN** no E402 errors are reported

#### Scenario: CLI commands still work
- **WHEN** running `psi-agent ai openai-completions --help`
- **THEN** the help text is displayed correctly

#### Scenario: Anthropic messages command works
- **WHEN** running `psi-agent ai anthropic-messages --help`
- **THEN** the help text is displayed correctly
