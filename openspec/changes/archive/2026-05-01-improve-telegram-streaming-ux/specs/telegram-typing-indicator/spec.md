## MODIFIED Requirements

### Requirement: Telegram channel sends typing indicator during streaming

The Telegram channel SHALL send a "typing" chat action indicator continuously during streaming mode without gaps.

#### Scenario: Typing indicator sent before streaming starts
- **WHEN** streaming mode is enabled and a user message is received
- **THEN** the channel SHALL send `send_chat_action(chat_id, "typing")` before sending the initial placeholder message
- **AND** the typing indicator SHALL be visible to the user

#### Scenario: Typing indicator continues without gap
- **WHEN** the periodic typing indicator task starts
- **THEN** the task SHALL send typing indicator immediately (not after first sleep interval)
- **AND** the typing indicator SHALL remain visible continuously during streaming

#### Scenario: Typing indicator cancelled when streaming ends
- **WHEN** streaming completes or is interrupted
- **THEN** the periodic typing task SHALL be cancelled
- **AND** no more typing indicators SHALL be sent

#### Scenario: Non-streaming mode does not send typing indicator
- **WHEN** streaming mode is disabled
- **THEN** the channel SHALL NOT send typing indicator
- **AND** proceed directly to sending the response
