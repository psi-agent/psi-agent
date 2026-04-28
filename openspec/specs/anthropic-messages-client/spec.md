## Requirements

### Requirement: Client sends messages to Anthropic API

The client SHALL send message requests to Anthropic Messages API endpoint.

#### Scenario: Non-streaming request
- **WHEN** client sends request with `stream: false`
- **THEN** client SHALL return complete response as dict in OpenAI format

#### Scenario: Streaming request
- **WHEN** client sends request with `stream: true`
- **THEN** client SHALL return async generator yielding OpenAI SSE chunks

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

### Requirement: Client handles authentication

The client SHALL include API key in request headers for authentication.

#### Scenario: Valid API key
- **WHEN** client has valid API key configured
- **THEN** client SHALL include `x-api-key` header with all requests

#### Scenario: Invalid API key
- **WHEN** API key is invalid or expired
- **THEN** client SHALL return error dict with status_code 401

### Requirement: Client supports content blocks

The client SHALL support Anthropic content block format in messages.

#### Scenario: Text content block
- **WHEN** message contains text content block
- **THEN** client SHALL send content block to API unchanged

#### Scenario: Image content block
- **WHEN** message contains image content block (base64 or URL)
- **THEN** client SHALL send content block to API unchanged

### Requirement: Client supports tool use

The client SHALL support Anthropic tool definitions and tool result content blocks.

#### Scenario: Tool definition provided
- **WHEN** request includes `tools` parameter
- **THEN** client SHALL include tools in API request

#### Scenario: Tool result in message
- **WHEN** message contains `tool_result` content block
- **THEN** client SHALL send tool result to API unchanged

### Requirement: Client handles connection errors

The client SHALL handle network errors gracefully.

#### Scenario: Connection failure
- **WHEN** network connection to API fails
- **THEN** client SHALL return error dict with status_code 500 and error message

#### Scenario: Request timeout
- **WHEN** API request exceeds timeout
- **THEN** client SHALL return error dict with status_code 500 and timeout message

### Requirement: Client uses async context manager

The client SHALL implement async context manager protocol for resource management.

#### Scenario: Enter context
- **WHEN** client enters async context
- **THEN** client SHALL initialize HTTP session

#### Scenario: Exit context
- **WHEN** client exits async context
- **THEN** client SHALL close HTTP session and clean up resources

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
