## ADDED Requirements

### Requirement: Client translates response format

The client SHALL translate Anthropic Messages response format to OpenAI chat completions format.

#### Scenario: Non-streaming response translation
- **WHEN** client receives Anthropic message response
- **THEN** client SHALL convert to OpenAI format with `id`, `object`, `choices`, `usage` fields

#### Scenario: Choices array construction
- **WHEN** translating response
- **THEN** client SHALL construct `choices` array with `index`, `message`, `finish_reason`

#### Scenario: Usage statistics mapping
- **WHEN** Anthropic response includes `usage` with `input_tokens`, `output_tokens`
- **THEN** client SHALL map to OpenAI `prompt_tokens`, `completion_tokens`, `total_tokens`

### Requirement: Client translates streaming events

The client SHALL translate Anthropic streaming events to OpenAI chunk format.

#### Scenario: Content delta event
- **WHEN** Anthropic sends `content_block_delta` with `delta.text`
- **THEN** client SHALL emit OpenAI chunk with `choices[0].delta.content`

#### Scenario: Message start event
- **WHEN** Anthropic sends `message_start` event
- **THEN** client SHALL emit OpenAI chunk with `id` and `model` fields

#### Scenario: Message stop event
- **WHEN** Anthropic sends `message_stop` event
- **THEN** client SHALL emit OpenAI `data: [DONE]` chunk
