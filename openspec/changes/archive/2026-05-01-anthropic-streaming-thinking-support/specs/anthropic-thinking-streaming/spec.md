## ADDED Requirements

### Requirement: Translate thinking content blocks in streaming

The translator SHALL convert Anthropic `thinking` content blocks to OpenAI streaming format with `reasoning_content` field.

#### Scenario: Thinking block start event
- **WHEN** Anthropic sends `content_block_start` event with `content_block.type: "thinking"`
- **THEN** translator SHALL NOT emit any output chunk (thinking starts with first delta)

#### Scenario: Thinking delta event
- **WHEN** Anthropic sends `content_block_delta` event with `delta.type: "thinking_delta"`
- **THEN** translator SHALL emit OpenAI chunk with `delta.reasoning_content` containing `delta.thinking` value

#### Scenario: Signature delta event
- **WHEN** Anthropic sends `content_block_delta` event with `delta.type: "signature_delta"`
- **THEN** translator SHALL NOT emit any output chunk (signature is metadata only)

#### Scenario: Multiple thinking deltas concatenation
- **WHEN** Anthropic sends multiple `thinking_delta` events in sequence
- **THEN** translator SHALL emit separate chunks for each delta (client concatenates)

### Requirement: Handle redacted thinking blocks gracefully

The translator SHALL skip `redacted_thinking` content blocks without error.

#### Scenario: Redacted thinking block start
- **WHEN** Anthropic sends `content_block_start` event with `content_block.type: "redacted_thinking"`
- **THEN** translator SHALL skip the block and log debug message

#### Scenario: Redacted thinking block delta
- **WHEN** Anthropic sends `content_block_delta` for a redacted thinking block
- **THEN** translator SHALL NOT emit any output chunk
