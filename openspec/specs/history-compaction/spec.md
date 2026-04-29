## ADDED Requirements

### Requirement: compact_history accepts complete function

The `compact_history()` function SHALL accept a required `complete_fn` parameter that provides a single-turn conversation interface to an LLM.

#### Scenario: complete function signature
- **WHEN** a complete function is provided
- **THEN** it accepts `list[dict[str, Any]]` as input (messages for a single turn)
- **AND** it returns `Awaitable[str]` as output (the LLM response)

### Requirement: OpenClaw-like workspace uses LLM summarization

The OpenClaw-like workspace's `compact_history()` function SHALL use `complete_fn` to generate conversation summaries.

#### Scenario: Summary replaces old messages
- **WHEN** LLM summarization is used in OpenClaw-like workspace
- **THEN** old messages are replaced by a single summary message
- **AND** recent messages are preserved unchanged

### Requirement: Simple workspace ignores complete function

The simple workspace's `compact_history()` function SHALL accept `complete_fn` but ignore it, using simple truncation instead.

#### Scenario: Simple truncation
- **WHEN** compacting history in simple workspace
- **THEN** the function ignores `complete_fn`
- **AND** only recent messages are kept

### Requirement: recent messages preserved

The `compact_history()` function SHALL preserve a configurable number of recent messages without summarization.

#### Scenario: Recent messages not summarized
- **WHEN** compacting history with LLM summarization
- **THEN** the most recent messages (based on `max_tokens` or message count) are kept as-is
- **AND** only older messages are summarized

### Requirement: Skip compaction for non-real conversation

The `compact_history()` function in the OpenClaw-like workspace SHALL skip LLM summarization when the conversation history contains no real conversation messages.

#### Scenario: No real conversation messages
- **WHEN** conversation history contains no messages with meaningful user or assistant content
- **THEN** compaction is skipped
- **AND** history is returned unchanged

#### Scenario: At least one real conversation message
- **WHEN** conversation history contains at least one message with meaningful user or assistant content
- **THEN** normal compaction proceeds with LLM summarization
