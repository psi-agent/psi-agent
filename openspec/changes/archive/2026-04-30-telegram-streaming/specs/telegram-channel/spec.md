## ADDED Requirements

### Requirement: Telegram channel CLI supports streaming configuration

The Telegram channel CLI SHALL support streaming mode configuration via command-line arguments.

#### Scenario: Default streaming mode
- **WHEN** `psi-agent channel telegram --token <token> --session-socket <path>` is invoked
- **THEN** streaming mode SHALL be enabled by default

#### Scenario: Disable streaming with flag
- **WHEN** `psi-agent channel telegram --token <token> --session-socket <path> --no-stream` is invoked
- **THEN** streaming mode SHALL be disabled
- **AND** the channel SHALL wait for complete response before sending

#### Scenario: Configure stream interval
- **WHEN** `psi-agent channel telegram --token <token> --session-socket <path> --stream-interval 2.0` is invoked
- **THEN** the channel SHALL use 2.0 second as the minimum edit interval

#### Scenario: Stream interval is a float
- **WHEN** `--stream-interval` is specified
- **THEN** the value SHALL be parsed as a float
- **AND** support values like 0.5, 1.0, 2.5

### Requirement: Telegram channel client supports streaming requests

The Telegram channel client SHALL provide a streaming method for communicating with psi-session.

#### Scenario: Streaming method sends stream request
- **WHEN** `send_message_stream()` is called
- **THEN** the client SHALL send request with `stream: true`
- **AND** invoke callback for each received chunk

#### Scenario: Non-streaming method sends regular request
- **WHEN** `send_message()` is called
- **THEN** the client SHALL send request with `stream: false`
- **AND** wait for complete response

#### Scenario: Streaming callback receives chunks
- **WHEN** session returns streaming (SSE) response
- **THEN** the callback SHALL be invoked for each content chunk
- **AND** chunks SHALL be passed as strings