## MODIFIED Requirements

### Requirement: Tool result messages are identified as real conversation when following meaningful user message

A tool result message SHALL be considered part of a real conversation if, within the lookback window (20 messages), there exists a user message with meaningful content.

#### Scenario: Tool result follows meaningful user message
- **WHEN** a tool result message is at index 5 and a user message with meaningful content is at index 3
- **THEN** the tool result SHALL be identified as part of a real conversation

#### Scenario: Tool result follows only non-meaningful messages
- **WHEN** a tool result message is at index 5 and all user messages within the lookback window have no meaningful content
- **THEN** the tool result SHALL NOT be identified as part of a real conversation

#### Scenario: Tool result lookback exceeds history start
- **WHEN** a tool result message is at index 10 with lookback 20
- **THEN** the search SHALL start at index 0 (no negative index)

### Requirement: Function signature matches OpenClaw

The `is_real_conversation_message()` function SHALL accept three parameters:
1. `message`: The message to check
2. `history`: The full message history list
3. `index`: The index of the message in the history

#### Scenario: Function called with correct parameters
- **WHEN** checking if a message is part of a real conversation
- **THEN** the function SHALL receive the message, full history, and message index

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