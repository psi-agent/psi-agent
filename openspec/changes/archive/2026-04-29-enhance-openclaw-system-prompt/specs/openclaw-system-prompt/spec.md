## MODIFIED Requirements

### Requirement: System prompt builder loads bootstrap files

The system prompt builder SHALL load the following bootstrap files from the workspace root in order:
1. AGENTS.md
2. SOUL.md
3. TOOLS.md
4. IDENTITY.md
5. USER.md
6. HEARTBEAT.md
7. BOOTSTRAP.md
8. MEMORY.md (only in main session context)

#### Scenario: All bootstrap files present
- **WHEN** all bootstrap files exist in the workspace root
- **THEN** the system prompt builder loads each file and includes its content in the system prompt

#### Scenario: Bootstrap file missing
- **WHEN** a bootstrap file does not exist
- **THEN** the system prompt builder continues without error and may include a placeholder indicating the file is missing

### Requirement: YAML frontmatter is stripped

The system prompt builder SHALL strip YAML frontmatter (content between `---` markers at the start of a file) before including file content in the system prompt.

#### Scenario: File with frontmatter
- **WHEN** a bootstrap file contains YAML frontmatter
- **THEN** the frontmatter is removed and only the content after the closing `---` is included in the system prompt

#### Scenario: File without frontmatter
- **WHEN** a bootstrap file does not contain YAML frontmatter
- **THEN** the entire file content is included in the system prompt unchanged

### Requirement: System prompt has clear structure

The system prompt builder SHALL combine all sections with clear headers that identify each section's contribution.

#### Scenario: System prompt structure
- **WHEN** the system prompt is built
- **THEN** each section is preceded by a clear header (e.g., "## AGENTS.md", "## Tooling")

### Requirement: MEMORY.md privacy protection

The system prompt builder SHALL only load MEMORY.md in main session context to prevent private information from leaking to shared contexts.

#### Scenario: Main session loads MEMORY.md
- **WHEN** the session is a main session (direct chat with user)
- **THEN** MEMORY.md content is included in the system prompt

#### Scenario: Non-main session skips MEMORY.md
- **WHEN** the session is not a main session (e.g., shared channel, subagent)
- **THEN** MEMORY.md is not loaded and its content is not included in the system prompt

### Requirement: Async file reading

The system prompt builder SHALL use async file I/O operations to read bootstrap files.

#### Scenario: Async file operations
- **WHEN** reading bootstrap files
- **THEN** the operation uses async I/O (anyio.open_file or equivalent) to avoid blocking the event loop

### Requirement: System prompt combines all sections in order

The system prompt builder SHALL combine all sections in a specific order: identity, tooling, tool call style, execution bias, safety, workspace, skills, memory, project context, cache boundary, heartbeats, silent replies, date/time, runtime.

#### Scenario: Section order
- **WHEN** the system prompt is built
- **THEN** sections appear in the defined order with stable sections before the cache boundary and dynamic sections after
