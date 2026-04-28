## ADDED Requirements

### Requirement: README.md exists with user-facing content
The project SHALL have a README.md file in the root directory that provides a user-friendly introduction to the project.

#### Scenario: User views README.md
- **WHEN** a user opens the repository or PyPI page
- **THEN** they see a README.md with project introduction, installation instructions, and quick start guide

### Requirement: README.md contains essential sections
The README.md SHALL include the following sections:
1. Project title and brief description
2. Installation instructions
3. Quick start example
4. Component overview
5. Link to detailed documentation

#### Scenario: User reads README.md structure
- **WHEN** a user reads README.md
- **THEN** they can quickly understand what psi-agent is, how to install it, and how to get started

### Requirement: pyproject.toml references README.md
The pyproject.toml file SHALL reference README.md in the `readme` field.

#### Scenario: PyPI displays README.md
- **WHEN** the package is published to PyPI
- **THEN** the README.md content is displayed on the package page
