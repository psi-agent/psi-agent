## MODIFIED Requirements

### Requirement: Telegram channel sends typing indicator during streaming

The Telegram channel SHALL maintain continuous typing indicator feedback during streaming, re-sending after each message send.

#### Scenario: Typing indicator re-sent after message send
- **WHEN** a message is sent via `reply_text()` during streaming
- **THEN** the channel SHALL immediately send another typing indicator
- **AND** the typing indicator SHALL remain visible to the user

#### Scenario: Typing indicator continues without gap
- **WHEN** the periodic typing indicator task runs
- **THEN** the task SHALL send typing indicator immediately (not after first sleep interval)
- **AND** the typing indicator SHALL remain visible continuously during streaming
