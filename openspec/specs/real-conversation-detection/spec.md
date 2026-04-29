## ADDED Requirements

### Requirement: Detect meaningful conversation content

The system SHALL provide a function `has_meaningful_conversation_content()` that determines whether a message contains meaningful user-AI dialogue content.

#### Scenario: Empty string content
- **WHEN** message content is an empty string or whitespace-only
- **THEN** the function returns `False`

#### Scenario: Silent token content
- **WHEN** message content is exactly `SILENT_TOKEN` (`"NO_REPLY"`)
- **THEN** the function returns `False`

#### Scenario: Heartbeat-only content
- **WHEN** message content contains only heartbeat-related text (e.g., `HEARTBEAT_OK`) including cases with markdown wrappers or trailing punctuation
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

The system SHALL provide a function `is_real_conversation_message(message, history, index)` that determines whether a message in the conversation history is part of a real user-AI dialogue.

#### Scenario: User message with meaningful content
- **WHEN** message role is `user` and has meaningful conversation content
- **THEN** the function returns `True`

#### Scenario: Assistant message with meaningful content
- **WHEN** message role is `assistant` and has meaningful conversation content
- **THEN** the function returns `True`

#### Scenario: Tool result message following meaningful user message
- **WHEN** message role is `toolResult`, `tool`, or `tool_result` AND a user message with meaningful content exists within the lookback window (20 messages)
- **THEN** the function returns `True`

#### Scenario: Tool result message with no meaningful user message
- **WHEN** message role is `toolResult`, `tool`, or `tool_result` AND no user message with meaningful content exists within the lookback window
- **THEN** the function returns `False`

#### Scenario: User message without meaningful content
- **WHEN** message role is `user` but content is empty, `SILENT_TOKEN`, or heartbeat-only
- **THEN** the function returns `False`

#### Scenario: Assistant message without meaningful content
- **WHEN** message role is `assistant` but content contains only tool calls or thinking blocks
- **THEN** the function returns `False`

### Requirement: Heartbeat token stripping handles markup and punctuation

The `_has_meaningful_text()` function SHALL properly strip `HEARTBEAT_OK` from text edges, including cases with markdown wrappers and trailing punctuation.

#### Scenario: HEARTBEAT_OK with markdown wrapper
- **WHEN** text is `"**HEARTBEAT_OK**"`
- **THEN** the function SHALL identify it as non-meaningful (empty after stripping)

#### Scenario: HEARTBEAT_OK with trailing punctuation
- **WHEN** text is `"HEARTBEAT_OK."`
- **THEN** the function SHALL identify it as non-meaningful

#### Scenario: HEARTBEAT_OK with preceding content
- **WHEN** text is `"Some text HEARTBEAT_OK"`
- **THEN** the function SHALL identify `"Some text"` as meaningful content

### Requirement: Silent reply token matches OpenClaw

The `SILENT_TOKEN` constant SHALL be `"NO_REPLY"` to match OpenClaw's `SILENT_REPLY_TOKEN`.

#### Scenario: Silent token value
- **WHEN** checking for silent reply
- **THEN** the token SHALL be `"NO_REPLY"` (not `"SILENT_TOKEN"`)

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
