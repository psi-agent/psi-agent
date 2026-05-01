## ADDED Requirements

### Requirement: Session module logs critical operations at DEBUG level

The session module SHALL log the following operations at DEBUG level for traceability:
- Tool call reconstruction from streaming chunks
- Message building including system prompt status
- History compaction requests
- Parallel tool execution start

#### Scenario: Tool call reconstruction is logged
- **WHEN** `_reconstruct_tool_calls` is called
- **THEN** a DEBUG log SHALL be emitted with the number of chunks and resulting tool calls

#### Scenario: Message building is logged
- **WHEN** `_build_messages` is called
- **THEN** a DEBUG log SHALL be emitted with system prompt status and message count

#### Scenario: History compaction is logged
- **WHEN** `_complete_fn` is called for history compaction
- **THEN** a DEBUG log SHALL be emitted indicating the compaction request

#### Scenario: Parallel tool execution is logged
- **WHEN** `execute_tools_parallel` starts execution
- **THEN** a DEBUG log SHALL be emitted with the number of tools being executed

### Requirement: Server handles null content defensively

The server SHALL handle null content in user messages without crashing or masking errors.

#### Scenario: Null content is handled safely
- **WHEN** a user message has null or missing content
- **THEN** the server SHALL not crash and SHALL log an empty or placeholder string
