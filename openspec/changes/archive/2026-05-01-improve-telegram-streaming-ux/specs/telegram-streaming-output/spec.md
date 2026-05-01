## MODIFIED Requirements

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

### Requirement: Telegram streaming placeholder indicates incomplete content

The Telegram channel SHALL display a placeholder that indicates content is still being generated.

#### Scenario: Empty buffer shows standalone placeholder
- **WHEN** streaming starts and no content has been received yet
- **THEN** the channel SHALL display "..." as the placeholder

#### Scenario: Non-empty buffer shows content with placeholder suffix
- **WHEN** streaming is in progress and buffer contains content
- **THEN** the channel SHALL display the buffered content truncated to fit
- **AND** append "..." to indicate more content is coming
- **AND** reserve 3 characters for the placeholder suffix when truncating

#### Scenario: Final message removes placeholder
- **WHEN** streaming completes
- **THEN** the channel SHALL display the complete content without the "..." suffix
