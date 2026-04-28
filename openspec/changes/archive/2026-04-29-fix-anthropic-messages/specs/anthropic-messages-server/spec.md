## MODIFIED Requirements

### Requirement: Server handles POST /v1/chat/completions

The server SHALL accept POST requests to `/v1/chat/completions` endpoint with OpenAI chat completions format.

#### Scenario: Valid request received
- **WHEN** POST /v1/chat/completions is received with valid OpenAI request body
- **THEN** server SHALL translate request to Anthropic format and forward to API

#### Scenario: Invalid JSON body
- **WHEN** POST /v1/chat/completions is received with malformed JSON
- **THEN** server SHALL return HTTP 400 with error message

### Requirement: Server supports streaming responses

The server SHALL support streaming responses when `stream: true` is in request body.

#### Scenario: Streaming request
- **WHEN** request includes `stream: true`
- **THEN** server SHALL return SSE stream with OpenAI streaming chunk format

#### Scenario: Non-streaming request
- **WHEN** request does not include `stream` or `stream: false`
- **THEN** server SHALL return complete JSON response in OpenAI format

### Requirement: Server translates request format

The server SHALL translate OpenAI chat completions format to Anthropic Messages format before forwarding.

#### Scenario: System message handling
- **WHEN** OpenAI request contains message with `role: "system"`
- **THEN** server SHALL extract content as `system` parameter for Anthropic API

#### Scenario: Message content conversion
- **WHEN** OpenAI message has string content
- **THEN** server SHALL convert to Anthropic content block array format

## REMOVED Requirements

### Requirement: Server handles POST /v1/messages

**Reason**: Component now uses OpenAI-compatible endpoint to match session expectations

**Migration**: Use `/v1/chat/completions` endpoint with OpenAI format
