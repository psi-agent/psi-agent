## ADDED Requirements

### Requirement: Client sends messages to Anthropic API

The client SHALL send message requests to Anthropic Messages API endpoint.

#### Scenario: Non-streaming request
- **WHEN** client sends request with `stream: false`
- **THEN** client SHALL return complete response as dict

#### Scenario: Streaming request
- **WHEN** client sends request with `stream: true`
- **THEN** client SHALL return async generator yielding SSE chunks

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
