## MODIFIED Requirements

### Requirement: REPL uses streaming by default

The REPL SHALL use streaming requests by default for better user experience.

#### Scenario: Default streaming request
- **WHEN** user enters a message
- **THEN** REPL SHALL send request with `stream: true`
- **AND** display response chunks in real-time

#### Scenario: Non-streaming via CLI flag
- **WHEN** REPL is started with `--no-stream` flag
- **THEN** REPL SHALL use non-streaming mode
- **AND** wait for complete response before displaying

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

## REMOVED Requirements

### Requirement: REPL provides graceful exit

**Reason**: REPL 简化为纯消息转发，不再支持命令。

**Migration**: 用户使用 Ctrl+D (EOF) 或 Ctrl+C 退出 REPL。

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

### Requirement: REPL is pure message forwarder

The REPL SHALL act as a pure message forwarder without command support.

#### Scenario: No command parsing
- **WHEN** user enters text starting with `/`
- **THEN** REPL SHALL treat it as normal message
- **AND** forward it to session without interpretation

#### Scenario: Exit via EOF
- **WHEN** user presses Ctrl+D
- **THEN** REPL SHALL exit cleanly

#### Scenario: Exit via interrupt
- **WHEN** user presses Ctrl+C
- **THEN** REPL SHALL exit cleanly
