## ADDED Requirements

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

### Requirement: English and Chinese README maintain parity

All changes to README.md SHALL be reflected in README_zh.md with equivalent Chinese translations.

#### Scenario: Documentation parity
- **WHEN** README.md is updated
- **THEN** README_zh.md contains the same information in Chinese
