## ADDED Requirements

### Requirement: Session runner initialization
The session runner SHALL properly initialize with workspace configuration.

#### Scenario: Initialize with valid workspace
- **WHEN** runner is created with valid workspace path
- **THEN** runner loads tools and skills from workspace

#### Scenario: Initialize with invalid workspace
- **WHEN** runner is created with invalid workspace path
- **THEN** runner raises appropriate error

### Requirement: Message processing loop
The session runner SHALL process messages through the agent loop.

#### Scenario: Process user message
- **WHEN** runner receives user message
- **THEN** message is sent to AI component for processing

#### Scenario: Handle tool call request
- **WHEN** AI returns tool call request
- **THEN** runner executes tool and returns result to AI

### Requirement: Tool execution integration
The session runner SHALL integrate with tool executor for tool calls.

#### Scenario: Execute valid tool
- **WHEN** runner receives tool call for valid tool
- **THEN** tool is executed and result returned

#### Scenario: Handle tool execution error
- **WHEN** tool execution fails
- **THEN** error is properly handled and returned to AI

### Requirement: History management
The session runner SHALL manage conversation history.

#### Scenario: Append to history
- **WHEN** message is processed
- **THEN** message is appended to history

#### Scenario: Compact history when needed
- **WHEN** history exceeds token limit
- **THEN** history is compacted using system prompt function