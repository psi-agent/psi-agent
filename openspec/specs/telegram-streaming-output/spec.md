## ADDED Requirements

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

### Requirement: Telegram channel buffers streaming chunks by time interval

The Telegram channel SHALL buffer streaming chunks and update messages at configurable time intervals to avoid API rate limits.

#### Scenario: Buffer chunks within interval
- **WHEN** multiple chunks arrive within the configured interval
- **THEN** the channel SHALL buffer all chunks
- **AND** send a single edit at the end of the interval

#### Scenario: Default interval is 1 second
- **WHEN** Telegram channel starts without `--stream-interval` flag
- **THEN** the channel SHALL use 1.0 second as default interval

#### Scenario: Custom interval configuration
- **WHEN** Telegram channel starts with `--stream-interval 0.5`
- **THEN** the channel SHALL use 0.5 second as the update interval

### Requirement: Telegram channel handles long streaming messages

The Telegram channel SHALL handle streaming messages that exceed Telegram's 4096 character limit.

#### Scenario: Message exceeds limit during streaming
- **WHEN** accumulated streaming content exceeds 4096 characters
- **THEN** the channel SHALL truncate the displayed message to 4096 characters
- **AND** send remaining content as a new message when streaming completes

#### Scenario: Final message splitting
- **WHEN** streaming completes and total content exceeds 4096 characters
- **THEN** the channel SHALL split the complete content into multiple messages
- **AND** use existing `split_message()` function for splitting