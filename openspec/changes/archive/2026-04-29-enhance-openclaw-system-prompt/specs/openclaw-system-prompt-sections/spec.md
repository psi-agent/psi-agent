## ADDED Requirements

### Requirement: System prompt includes identity statement

The system prompt builder SHALL include an identity statement at the beginning: "You are a personal assistant running inside OpenClaw."

#### Scenario: Identity statement present
- **WHEN** the system prompt is built
- **THEN** the prompt begins with the identity statement

### Requirement: System prompt includes tooling section

The system prompt builder SHALL include a Tooling section that lists all available tools with their names and descriptions.

#### Scenario: Tooling section present
- **WHEN** the system prompt is built
- **THEN** the prompt includes a "## Tooling" section with tool names and descriptions

### Requirement: System prompt includes tool call style section

The system prompt builder SHALL include a Tool Call Style section with guidance on how to call tools (do not narrate routine calls, keep narration brief, use plain human language).

#### Scenario: Tool call style section present
- **WHEN** the system prompt is built
- **THEN** the prompt includes a "## Tool Call Style" section with core principles

### Requirement: System prompt includes execution bias section

The system prompt builder SHALL include an Execution Bias section with guidance on how to work (act in this turn, continue until done, final answer needs evidence).

#### Scenario: Execution bias section present
- **WHEN** the system prompt is built
- **THEN** the prompt includes a "## Execution Bias" section with behavior guidance

### Requirement: System prompt includes safety section

The system prompt builder SHALL include a Safety section with AI safety principles (no independent goals, prioritize safety, do not manipulate).

#### Scenario: Safety section present
- **WHEN** the system prompt is built
- **THEN** the prompt includes a "## Safety" section with safety principles

### Requirement: System prompt includes workspace section

The system prompt builder SHALL include a Workspace section that specifies the current working directory.

#### Scenario: Workspace section present
- **WHEN** the system prompt is built
- **THEN** the prompt includes a "## Workspace" section with the workspace directory path

### Requirement: System prompt includes runtime section

The system prompt builder SHALL include a Runtime section with runtime information (host, os, arch, model, shell, Python version).

#### Scenario: Runtime section present
- **WHEN** the system prompt is built
- **THEN** the prompt includes a "## Runtime" section with runtime information

### Requirement: System prompt includes skills section

The system prompt builder SHALL include a Skills section with guidance on how to use skills (scan skills, read SKILL.md, follow instructions).

#### Scenario: Skills section present
- **WHEN** the system prompt is built
- **THEN** the prompt includes a "## Skills" section with skill usage guidance

### Requirement: System prompt includes memory section

The system prompt builder SHALL include a Memory section with guidance on how to use MEMORY.md for long-term memory.

#### Scenario: Memory section present
- **WHEN** the system prompt is built
- **THEN** the prompt includes a "## Memory" section with memory usage guidance

### Requirement: System prompt includes heartbeats section

The system prompt builder SHALL include a Heartbeats section with guidance on how to respond to heartbeat polls (HEARTBEAT_OK or alert text).

#### Scenario: Heartbeats section present
- **WHEN** the system prompt is built
- **THEN** the prompt includes a "## Heartbeats" section with heartbeat response guidance

### Requirement: System prompt includes silent replies section

The system prompt builder SHALL include a Silent Replies section with guidance on when and how to use SILENT_TOKEN.

#### Scenario: Silent replies section present
- **WHEN** the system prompt is built
- **THEN** the prompt includes a "## Silent Replies" section with silent reply rules

### Requirement: System prompt includes current date and time section

The system prompt builder SHALL include a Current Date & Time section with the user's timezone.

#### Scenario: Date and time section present
- **WHEN** the system prompt is built
- **THEN** the prompt includes a "## Current Date & Time" section with timezone information

### Requirement: System prompt includes cache boundary marker

The system prompt builder SHALL include a cache boundary marker (`<!-- OPENCLAW_CACHE_BOUNDARY -->`) to separate stable and dynamic content.

#### Scenario: Cache boundary present
- **WHEN** the system prompt is built
- **THEN** the prompt includes the cache boundary marker between stable and dynamic sections

### Requirement: Runtime information is dynamically generated

The system prompt builder SHALL dynamically generate runtime information using Python standard library (platform, sys, os modules).

#### Scenario: Runtime info dynamically generated
- **WHEN** the system prompt is built
- **THEN** host, os, arch, Python version, and shell are obtained from the current runtime environment
