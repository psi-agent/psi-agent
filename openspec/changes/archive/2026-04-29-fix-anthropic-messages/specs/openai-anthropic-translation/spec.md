## Requirements

### Requirement: Translate OpenAI request to Anthropic format

The translator SHALL convert OpenAI chat completions request format to Anthropic Messages format.

#### Scenario: Basic text message translation
- **WHEN** request contains messages with `role` and `content` fields
- **THEN** translator SHALL convert content strings to Anthropic content block arrays

#### Scenario: System message extraction
- **WHEN** request contains a message with `role: "system"`
- **THEN** translator SHALL extract it as the `system` parameter for Anthropic API

#### Scenario: Parameter mapping
- **WHEN** request contains `max_tokens`, `temperature`, or `stream`
- **THEN** translator SHALL pass these parameters unchanged to Anthropic API

### Requirement: Translate Anthropic response to OpenAI format

The translator SHALL convert Anthropic Messages response format to OpenAI chat completions format.

#### Scenario: Non-streaming response translation
- **WHEN** Anthropic API returns a message response
- **THEN** translator SHALL convert to OpenAI format with `choices` array containing `message` object

#### Scenario: Content block to text conversion
- **WHEN** Anthropic response contains content blocks
- **THEN** translator SHALL extract text from content blocks for OpenAI `message.content`

#### Scenario: Response metadata preservation
- **WHEN** Anthropic response includes `id`, `model`, `usage`
- **THEN** translator SHALL include these in OpenAI response format

### Requirement: Translate streaming events

The translator SHALL convert Anthropic streaming events to OpenAI chunk format.

#### Scenario: Content delta translation
- **WHEN** Anthropic sends `content_block_delta` event with text
- **THEN** translator SHALL emit OpenAI chunk with `delta.content`

#### Scenario: Stream completion
- **WHEN** Anthropic sends `message_stop` event
- **THEN** translator SHALL emit OpenAI `data: [DONE]` chunk

#### Scenario: Error during streaming
- **WHEN** Anthropic sends error event during streaming
- **THEN** translator SHALL emit OpenAI error chunk format
