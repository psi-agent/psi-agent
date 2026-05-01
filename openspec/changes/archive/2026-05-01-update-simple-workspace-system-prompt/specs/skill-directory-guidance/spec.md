## ADDED Requirements

### Requirement: System prompt includes skills directory location
The system prompt SHALL include explicit information about where skills are located in the workspace directory structure.

#### Scenario: Skills directory mentioned in system prompt
- **WHEN** the system prompt is built by `build_system_prompt()`
- **THEN** the prompt includes a statement indicating that all skills are located in the `skills/` directory within the workspace

#### Scenario: Skills directory path is clear
- **WHEN** the agent reads the system prompt
- **THEN** the agent can determine the exact location of the skills directory relative to the workspace directory
