## MODIFIED Requirements

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

### Requirement: Telegram channel supports streaming output via message editing

The Telegram channel SHALL support streaming output by editing messages in real-time when streaming mode is enabled.

#### Scenario: Streaming mode enabled by default
- **WHEN** Telegram channel starts without `--no-stream` flag
- **THEN** the channel SHALL use streaming mode for message responses
- **AND** edit messages in real-time as content arrives

#### Scenario: Streaming message editing
- **WHEN** streaming mode is enabled and a chunk arrives from session
- **THEN** the channel SHALL edit the previously sent message with new content
- **AND** accumulate content across multiple edits

#### Scenario: First chunk sends initial message
- **WHEN** the first streaming chunk arrives
- **THEN** the channel SHALL send a new message to Telegram
- **AND** subsequent chunks SHALL edit this message

## REMOVED Requirements

### Requirement: Telegram channel uses no_stream parameter

**Reason**: Parameter renamed to `stream` with inverted default for clearer CLI flags.

**Migration**: Use `stream: bool = True` instead of `no_stream: bool = False`. The CLI flags are now `--stream` (default) and `--no-stream` (to disable).