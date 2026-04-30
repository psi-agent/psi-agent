## ADDED Requirements

### Requirement: Streaming Message Edit Timing

The Telegram channel MUST edit streaming messages at approximately the configured `stream_interval` during an active stream, ensuring users see progressive updates.

#### Scenario: Chunks arrive during streaming
- **WHEN** streaming is enabled with `stream_interval` set to N seconds
- **AND** content chunks arrive from the session at arbitrary intervals
- **THEN** the accumulated buffer MUST be flushed (message edited) approximately every N seconds
- **AND** users MUST see progressive updates to the message during streaming

#### Scenario: Rapid chunks within interval
- **WHEN** multiple chunks arrive within one `stream_interval` period
- **THEN** these chunks MUST be batched together
- **AND** a single edit MUST be performed after the interval from the last chunk

#### Scenario: Stream completes with pending buffer
- **WHEN** the stream completes
- **AND** there is content remaining in the buffer that hasn't been flushed
- **THEN** the remaining content MUST be flushed immediately

#### Scenario: Empty buffer
- **WHEN** a flush is scheduled but the buffer is empty
- **THEN** no edit MUST be performed
