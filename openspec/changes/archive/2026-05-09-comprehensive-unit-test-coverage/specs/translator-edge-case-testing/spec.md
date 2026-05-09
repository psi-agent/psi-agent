## ADDED Requirements

### Requirement: Translator handles invalid JSON in tool_call arguments
`_translate_message_to_anthropic` SHALL handle tool_call arguments that are not valid JSON by falling back to an empty dict `{}`.

#### Scenario: Invalid JSON in arguments
- **WHEN** an assistant message has `tool_calls` with `arguments` that is not valid JSON (e.g., `"not json"`)
- **THEN** the translated message SHALL use `input: {}` for that tool call

#### Scenario: None arguments in tool_call
- **WHEN** an assistant message has `tool_calls` with `arguments` being `None`
- **THEN** the translated message SHALL use `input: {}` for that tool call

#### Scenario: Empty string arguments in tool_call
- **WHEN** an assistant message has `tool_calls` with `arguments` being `""`
- **THEN** the translated message SHALL use `input: {}` for that tool call

### Requirement: Translator handles None tool result content
`_translate_message_to_anthropic` SHALL handle tool result messages where `content` is `None` by using an empty string.

#### Scenario: Tool result with None content
- **WHEN** a tool result message has `content: None`
- **THEN** the translated content block SHALL have `"text": ""`

### Requirement: Translator handles unknown tool format
`_translate_tool_to_anthropic` SHALL pass through tools that don't match OpenAI or Anthropic format unchanged.

#### Scenario: Unknown tool format
- **WHEN** a tool dict has neither `type: "function"` (OpenAI) nor `type: "custom"` with `input_schema` (Anthropic)
- **THEN** the tool SHALL be returned unchanged

### Requirement: Translator handles Anthropic response with missing fields
`translate_anthropic_to_openai` SHALL handle responses with missing optional fields by using sensible defaults.

#### Scenario: Response with no usage field
- **WHEN** Anthropic response has no `usage` field
- **THEN** the translated response SHALL have `prompt_tokens: 0`, `completion_tokens: 0`, `total_tokens: 0`

#### Scenario: Response with no stop_reason
- **WHEN** Anthropic response has no `stop_reason` field
- **THEN** the translated response SHALL default `finish_reason` to `"end_turn"`

#### Scenario: Response with unknown stop_reason
- **WHEN** Anthropic response has `stop_reason: "unknown_reason"`
- **THEN** the translated response SHALL default `finish_reason` to `"stop"`

#### Scenario: Response with no id field
- **WHEN** Anthropic response has no `id` field
- **THEN** the translated response SHALL use empty string for `id`

#### Scenario: Response with no model field
- **WHEN** Anthropic response has no `model` field
- **THEN** the translated response SHALL use empty string for `model`

#### Scenario: Response with empty content list
- **WHEN** Anthropic response has `content: []`
- **THEN** the translated message SHALL have `content: None`

### Requirement: Translator handles multiple system messages
`translate_openai_to_anthropic` SHALL extract only the first system message as the `system` parameter and keep subsequent system messages in the messages list.

#### Scenario: Multiple system messages
- **WHEN** the request has two system messages
- **THEN** the first SHALL be extracted as `system` parameter, and the second SHALL remain in the messages list

### Requirement: Translator handles malformed SSE events
`translate_anthropic_stream` SHALL handle malformed SSE events gracefully.

#### Scenario: SSE event missing event line
- **WHEN** an SSE chunk has `data:` but no `event:` line
- **THEN** the event SHALL be skipped (no output yielded)

#### Scenario: Empty stream
- **WHEN** the stream produces zero events
- **THEN** the generator SHALL yield zero chunks

#### Scenario: Ping event
- **WHEN** the stream produces a `ping` event
- **THEN** the event SHALL be skipped (no output yielded)

### Requirement: Translator handles assistant message with whitespace-only content and tool_calls
`_translate_message_to_anthropic` SHALL handle assistant messages that have `tool_calls` and whitespace-only content by not including a text content block.

#### Scenario: Whitespace-only content with tool_calls
- **WHEN** an assistant message has `content: "   "` and `tool_calls` present
- **THEN** the translated content SHALL NOT include a text content block, only tool_use blocks

#### Scenario: Empty string content with tool_calls
- **WHEN** an assistant message has `content: ""` and `tool_calls` present
- **THEN** the translated content SHALL NOT include a text content block, only tool_use blocks
