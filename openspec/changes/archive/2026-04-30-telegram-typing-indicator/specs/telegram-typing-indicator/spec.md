## ADDED Requirements

### Requirement: Telegram channel sends typing indicator during streaming

The Telegram channel SHALL send a "typing" chat action indicator when streaming mode is enabled and a message is being processed.

#### Scenario: Typing indicator sent before streaming starts
- **WHEN** streaming mode is enabled and a user message is received
- **THEN** the channel SHALL send `send_chat_action(chat_id, "typing")` before sending the initial placeholder message
- **AND** the typing indicator SHALL be visible to the user

#### Scenario: Typing indicator cancelled when message sent
- **WHEN** the initial placeholder message is sent
- **THEN** the typing indicator SHALL be automatically cancelled by Telegram

#### Scenario: Non-streaming mode does not send typing indicator
- **WHEN** streaming mode is disabled
- **THEN** the channel SHALL NOT send typing indicator
- **AND** proceed directly to sending the response