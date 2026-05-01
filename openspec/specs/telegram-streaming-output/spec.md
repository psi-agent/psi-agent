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

### Requirement: Streaming message edits occur at configured interval

The Telegram channel SHALL edit streaming messages at approximately the configured `stream_interval` during an active stream.

#### Scenario: Chunks arrive during streaming
- **WHEN** streaming is enabled with `stream_interval` set to N seconds
- **AND** content chunks arrive from the session at arbitrary intervals
- **THEN** the accumulated buffer SHALL be flushed (message edited) approximately every N seconds
- **AND** users SHALL see progressive updates to the message during streaming

#### Scenario: Rapid chunks within interval
- **WHEN** multiple chunks arrive within one `stream_interval` period
- **THEN** these chunks SHALL be batched together
- **AND** a single edit SHALL be performed after the interval

#### Scenario: Stream completes with pending buffer
- **WHEN** the stream completes
- **AND** there is content remaining in the buffer that hasn't been flushed
- **THEN** the remaining content SHALL be flushed immediately

#### Scenario: Empty buffer
- **WHEN** a flush is scheduled but the buffer is empty
- **THEN** no edit SHALL be performed

### Requirement: Background task manages periodic flushing

The Telegram channel SHALL use a background task to ensure flush operations execute during streaming.

#### Scenario: Background flush task starts with streaming
- **WHEN** streaming begins
- **THEN** a background task SHALL start that flushes the buffer every `stream_interval` seconds

#### Scenario: Background flush task stops on stream end
- **WHEN** streaming ends (successfully or with error)
- **THEN** the background flush task SHALL be cancelled
- **AND** a final flush SHALL be performed for any remaining content

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

### Requirement: Telegram streaming placeholder indicates incomplete content

The Telegram channel SHALL display a placeholder that indicates content is still being generated, only when content has been received.

#### Scenario: First message sent when first chunk arrives
- **WHEN** the first streaming chunk arrives
- **THEN** the channel SHALL send a new message with the chunk content appended with "..."
- **AND** subsequent chunks SHALL edit this message

#### Scenario: Non-empty buffer shows content with placeholder suffix
- **WHEN** streaming is in progress and buffer contains content
- **THEN** the channel SHALL display the buffered content truncated to fit
- **AND** append "..." to indicate more content is coming
- **AND** reserve 3 characters for the placeholder suffix when truncating

#### Scenario: Final message removes placeholder
- **WHEN** streaming completes
- **THEN** the channel SHALL display the complete content without the "..." suffix

#### Scenario: Empty response sends fallback message
- **WHEN** streaming completes with no content received
- **THEN** the channel SHALL send a message with just "..."

### Requirement: Telegram streaming output includes typing indicator

The Telegram streaming output feature SHALL include typing indicator feedback during message processing.

#### Scenario: Typing indicator shown during streaming
- **WHEN** streaming mode is enabled and a user message is received
- **THEN** the channel SHALL display a typing indicator to the user
- **AND** the indicator SHALL remain visible until the first message is sent