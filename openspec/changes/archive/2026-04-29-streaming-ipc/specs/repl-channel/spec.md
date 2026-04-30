## MODIFIED Requirements

### Requirement: REPL sends messages to session

The REPL SHALL send user messages to psi-session via Unix socket using HTTP POST.

#### Scenario: Send message to session
- **WHEN** user enters a non-empty message
- **THEN** REPL SHALL send POST request to session with message in request body

#### Scenario: Receive response from session
- **WHEN** session returns a response
- **THEN** REPL SHALL display the response content to stdout

#### Scenario: Streaming response display
- **WHEN** session returns streaming (SSE) response
- **THEN** REPL SHALL display content chunks in real-time as they arrive

## ADDED Requirements

### Requirement: REPL uses streaming by default

The REPL SHALL use streaming requests by default for better user experience.

#### Scenario: Default streaming request
- **WHEN** user enters a message
- **THEN** REPL SHALL send request with `stream: true`
- **AND** display response chunks in real-time

#### Scenario: Real-time output display
- **WHEN** streaming response arrives
- **THEN** REPL SHALL print each content chunk immediately
- **AND** NOT wait for complete response

### Requirement: REPL client provides streaming API

The REPL client SHALL provide both streaming and non-streaming methods.

#### Scenario: Streaming method
- **WHEN** calling `send_message_stream()` with a callback
- **THEN** client SHALL invoke callback for each received chunk
- **AND** return when stream completes

#### Scenario: Non-streaming method
- **WHEN** calling `send_message()`
- **THEN** client SHALL wait for complete response
- **AND** return full response string
