## ADDED Requirements

### Requirement: Server listens on Unix socket

The server SHALL listen for HTTP requests on a Unix socket path specified in configuration.

#### Scenario: Server starts successfully
- **WHEN** server is started with valid socket path
- **THEN** server SHALL create socket file and listen for connections

#### Scenario: Socket file already exists
- **WHEN** socket file already exists at configured path
- **THEN** server SHALL remove existing file before creating new socket

### Requirement: Server handles POST /v1/messages

The server SHALL accept POST requests to `/v1/messages` endpoint with Anthropic Messages API format.

#### Scenario: Valid request received
- **WHEN** POST /v1/messages is received with valid Anthropic request body
- **THEN** server SHALL forward request to Anthropic API and return response

#### Scenario: Invalid JSON body
- **WHEN** POST /v1/messages is received with malformed JSON
- **THEN** server SHALL return HTTP 400 with error message

### Requirement: Server supports streaming responses

The server SHALL support streaming responses when `stream: true` is in request body.

#### Scenario: Streaming request
- **WHEN** request includes `stream: true`
- **THEN** server SHALL return SSE stream with Anthropic streaming events

#### Scenario: Non-streaming request
- **WHEN** request does not include `stream` or `stream: false`
- **THEN** server SHALL return complete JSON response

### Requirement: Server forwards errors appropriately

The server SHALL map Anthropic API errors to appropriate HTTP status codes.

#### Scenario: Authentication failure
- **WHEN** Anthropic API returns 401 authentication error
- **THEN** server SHALL return HTTP 401 to client

#### Scenario: Rate limit exceeded
- **WHEN** Anthropic API returns 429 rate limit error
- **THEN** server SHALL return HTTP 429 with retry information

### Requirement: Server provides CLI entry point

The server SHALL provide a CLI command `psi-ai-anthropic-messages` for starting the server.

#### Scenario: CLI starts server
- **WHEN** `psi-ai-anthropic-messages` is invoked with required arguments
- **THEN** server SHALL start and log connection information
