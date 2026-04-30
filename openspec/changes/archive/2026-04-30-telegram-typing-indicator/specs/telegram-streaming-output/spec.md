## ADDED Requirements

### Requirement: Telegram streaming output includes typing indicator

The Telegram streaming output feature SHALL include typing indicator feedback during message processing.

#### Scenario: Typing indicator shown during streaming
- **WHEN** streaming mode is enabled and a user message is received
- **THEN** the channel SHALL display a typing indicator to the user
- **AND** the indicator SHALL remain visible until the first message is sent