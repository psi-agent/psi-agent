## MODIFIED Requirements

### Requirement: Session handles streaming responses

The session SHALL support streaming (SSE) responses from psi-ai-* and forward them to channel in OpenAI format.

#### Scenario: Streaming response forwarded to channel
- **WHEN** psi-ai returns streaming response
- **THEN** session forwards SSE chunks to channel in OpenAI format

#### Scenario: Session uses streaming by default for AI calls
- **WHEN** session calls AI component for inference
- **THEN** session SHALL send `stream: true` request
- **AND** internally collect complete response for tool call handling

#### Scenario: Tool calls require complete response
- **WHEN** streaming response contains tool_calls
- **THEN** session SHALL collect all streaming chunks completely
- **AND** reconstruct tool_calls before executing tools

## ADDED Requirements

### Requirement: Session provides streaming control

The session SHALL support both streaming and non-streaming response modes based on channel request.

#### Scenario: Channel requests streaming
- **WHEN** channel sends request with `stream: true`
- **THEN** session SHALL forward streaming response directly to channel

#### Scenario: Channel requests non-streaming
- **WHEN** channel sends request with `stream: false`
- **THEN** session SHALL collect complete response and return as single JSON
