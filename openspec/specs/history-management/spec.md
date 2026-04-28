## ADDED Requirements

### Requirement: History is maintained in memory

The session SHALL maintain conversation history as a messages array in memory.

#### Scenario: User message added to history
- **WHEN** user sends a message
- **THEN** the message is appended to messages array

#### Scenario: Assistant response added to history
- **WHEN** assistant responds
- **THEN** the response is appended to messages array

#### Scenario: Tool call and result added to history
- **WHEN** tool is called and returns result
- **THEN** tool_call message and tool result message are appended

### Requirement: History can be persisted to JSON file

The session SHALL optionally persist history to a JSON file when history_file parameter is provided.

#### Scenario: History loaded from file on startup
- **WHEN** session starts with history_file path
- **THEN** existing history is loaded from JSON file

#### Scenario: History saved to file after each request
- **WHEN** request processing completes
- **THEN** history is saved to JSON file

#### Scenario: No persistence when history_file is None
- **WHEN** history_file is None or not provided
- **THEN** history is not persisted to any file

### Requirement: History can be compacted when too long

The session SHALL support calling compact_history. Threshold triggering mechanism to be implemented later.

#### Scenario: compact_history interface available
- **WHEN** compact_history function exists in systems/system.py
- **THEN** session can call it when needed (future implementation)