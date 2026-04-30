## ADDED Requirements

### Requirement: Filter non-standard Anthropic SDK events

The Anthropic Messages client SHALL filter out non-standard SDK convenience events before yielding to the translator.

#### Scenario: Standard events are passed through
- **WHEN** the SDK emits a standard event (`message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop`, or `ping`)
- **THEN** the event SHALL be yielded to the translator

#### Scenario: Text convenience events are filtered
- **WHEN** the SDK emits a `text` event (SDK convenience event with snapshot field)
- **THEN** the event SHALL NOT be yielded to the translator
- **AND** the event SHALL be logged at DEBUG level

#### Scenario: Unknown events are filtered
- **WHEN** the SDK emits an event type not in the known standard events list
- **THEN** the event SHALL NOT be yielded to the translator
- **AND** the event SHALL be logged at DEBUG level
