## ADDED Requirements

### Requirement: Buffer flushes after time window expires

The streaming buffer SHALL flush accumulated content after a configurable time window (`stream_interval`) expires, regardless of whether new content arrives.

#### Scenario: Buffer flushes when no new chunks arrive
- **WHEN** chunks arrive and accumulate in buffer
- **AND** no new chunks arrive for `stream_interval` seconds
- **THEN** the buffer SHALL be flushed and content sent to Telegram

#### Scenario: Buffer flushes when streaming ends
- **WHEN** streaming response completes
- **AND** buffer contains accumulated content
- **THEN** all remaining buffered content SHALL be flushed immediately

### Requirement: Time window extends on new chunk arrival

The flush timer SHALL reset when a new chunk arrives, ensuring the flush happens `stream_interval` seconds after the last chunk.

#### Scenario: Timer resets on each new chunk
- **WHEN** a new chunk arrives while timer is running
- **THEN** the flush timer SHALL reset to `stream_interval` seconds from the current time

#### Scenario: Multiple chunks within interval batched together
- **WHEN** multiple chunks arrive within `stream_interval` seconds
- **THEN** all chunks SHALL be accumulated and flushed together when the timer expires