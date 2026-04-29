## ADDED Requirements

### Requirement: Detect meaningful conversation content

The system SHALL provide a function `has_meaningful_conversation_content()` that determines whether a message contains meaningful user-AI dialogue content.

#### Scenario: Empty string content
- **WHEN** message content is an empty string or whitespace-only
- **THEN** the function returns `False`

#### Scenario: Silent token content
- **WHEN** message content is exactly `SILENT_TOKEN`
- **THEN** the function returns `False`

#### Scenario: Heartbeat-only content
- **WHEN** message content contains only heartbeat-related text (e.g., `HEARTBEAT_OK`)
- **THEN** the function returns `False`

#### Scenario: Meaningful text content
- **WHEN** message content contains non-empty text that is not `SILENT_TOKEN` or heartbeat-only
- **THEN** the function returns `True`

#### Scenario: List content with meaningful text block
- **WHEN** message content is a list containing at least one text block with meaningful content
- **THEN** the function returns `True`

#### Scenario: List content with only tool call blocks
- **WHEN** message content is a list containing only toolCall, toolUse, functionCall, thinking, or reasoning blocks
- **THEN** the function returns `False`

#### Scenario: List content with non-text meaningful block
- **WHEN** message content is a list containing an image or other non-text block that is not a tool call/thinking block
- **THEN** the function returns `True`

### Requirement: Identify real conversation messages

The system SHALL provide a function `is_real_conversation_message()` that determines whether a message in the conversation history is part of a real user-AI dialogue.

#### Scenario: User message with meaningful content
- **WHEN** message role is `user` and has meaningful conversation content
- **THEN** the function returns `True`

#### Scenario: Assistant message with meaningful content
- **WHEN** message role is `assistant` and has meaningful conversation content
- **THEN** the function returns `True`

#### Scenario: Tool result message
- **WHEN** message role is `toolResult`, `tool`, or `tool_result`
- **THEN** the function returns `False`

#### Scenario: User message without meaningful content
- **WHEN** message role is `user` but content is empty, `SILENT_TOKEN`, or heartbeat-only
- **THEN** the function returns `False`

#### Scenario: Assistant message without meaningful content
- **WHEN** message role is `assistant` but content contains only tool calls or thinking blocks
- **THEN** the function returns `False`

### Requirement: Skip compaction for non-real conversation

The system SHALL modify `compact_history()` to skip LLM summarization when the conversation history contains no real conversation messages.

#### Scenario: History with only heartbeat messages
- **WHEN** conversation history contains only heartbeat replies (e.g., `HEARTBEAT_OK`)
- **THEN** compaction is skipped and history is returned unchanged

#### Scenario: History with only silent replies
- **WHEN** conversation history contains only `SILENT_TOKEN` responses
- **THEN** compaction is skipped and history is returned unchanged

#### Scenario: History with only tool calls
- **WHEN** conversation history contains only tool call and tool result messages without user/assistant text
- **THEN** compaction is skipped and history is returned unchanged

#### Scenario: History with real conversation
- **WHEN** conversation history contains at least one real conversation message
- **THEN** normal compaction proceeds with LLM summarization

#### Scenario: Mixed history with minimal real conversation
- **WHEN** conversation history contains some heartbeat/silent messages AND at least one real conversation message
- **THEN** normal compaction proceeds (real conversation messages trigger compaction)