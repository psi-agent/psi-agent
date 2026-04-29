## ADDED Requirements

### Requirement: Skip compaction for non-real conversation

The `compact_history()` function in the OpenClaw-like workspace SHALL skip LLM summarization when the conversation history contains no real conversation messages.

#### Scenario: No real conversation messages
- **WHEN** conversation history contains no messages with meaningful user or assistant content
- **THEN** compaction is skipped
- **AND** history is returned unchanged

#### Scenario: At least one real conversation message
- **WHEN** conversation history contains at least one message with meaningful user or assistant content
- **THEN** normal compaction proceeds with LLM summarization
