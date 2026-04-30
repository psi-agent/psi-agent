## ADDED Requirements

### Requirement: AI component supports streaming by default

The psi-ai-openai-completions component SHALL support streaming requests as the primary mode.

#### Scenario: Streaming request handling
- **WHEN** session sends request with `stream: true`
- **THEN** server SHALL forward streaming response from upstream API
- **AND** yield SSE chunks as they arrive

#### Scenario: Non-streaming request handling
- **WHEN** session sends request with `stream: false`
- **THEN** server SHALL wait for complete response from upstream API
- **AND** return single JSON response

### Requirement: Streaming error handling

The AI component SHALL properly handle errors during streaming.

#### Scenario: Streaming error event
- **WHEN** error occurs during streaming
- **THEN** server SHALL send SSE error event
- **AND** log the error details

#### Scenario: Connection error before streaming
- **WHEN** connection to upstream API fails
- **THEN** server SHALL return error response before starting stream
- **AND** NOT start SSE stream
