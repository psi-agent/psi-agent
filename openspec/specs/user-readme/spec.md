## ADDED Requirements

### Requirement: README.md exists with user-facing content
The project SHALL have a README.md file in the root directory that provides a user-friendly introduction to the project.

#### Scenario: User views README.md
- **WHEN** a user opens the repository or PyPI page
- **THEN** they see a README.md with project introduction, installation instructions, and quick start guide

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

### Requirement: pyproject.toml references README.md
The pyproject.toml file SHALL reference README.md in the `readme` field.

#### Scenario: PyPI displays README.md
- **WHEN** the package is published to PyPI
- **THEN** the README.md content is displayed on the package page

### Requirement: Chinese README uses common naming convention
The Chinese README SHALL be named `README_zh.md` following common conventions.

#### Scenario: User accesses Chinese README
- **WHEN** a user wants to read the Chinese documentation
- **THEN** they can find it at `README_zh.md`

### Requirement: Language switch links are provided
Both README.md and README_zh.md SHALL provide language switch links at the top of the file.

#### Scenario: User switches language
- **WHEN** a user is reading README.md
- **THEN** they see a link to README_zh.md at the top
- **WHEN** a user is reading README_zh.md
- **THEN** they see a link to README.md at the top

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

### Requirement: README Quick Start references example workspaces
The README Quick Start section SHALL reference the `examples/` directory to guide users to available workspace templates.

#### Scenario: User sees example workspace options
- **WHEN** user reads Step 1 of Quick Start
- **THEN** user is informed about available example workspaces in `examples/` directory

### Requirement: README Quick Start Step 2 accurately describes session startup
The README Quick Start Step 2 SHALL describe the command as starting the session only, not the session with an AI provider.

#### Scenario: User understands Step 2 purpose
- **WHEN** user reads Step 2 description
- **THEN** user understands this step only starts the session component

### Requirement: README Quick Start Step 3 uses consistent terminology
The README Quick Start Step 3 SHALL use the term "AI provider" instead of "AI component" for consistency with project terminology.

#### Scenario: User sees consistent terminology
- **WHEN** user reads Step 3 description
- **THEN** user sees "AI provider" terminology consistent with project documentation

### Requirement: README Quick Start Step 4 clarifies interaction target
The README Quick Start Step 4 SHALL specify that the channel interacts with the "agent session" rather than just "agent" to prevent confusion.

#### Scenario: User understands channel interaction
- **WHEN** user reads Step 4 description
- **THEN** user understands the channel communicates with the agent session
