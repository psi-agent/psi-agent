## MODIFIED Requirements

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
