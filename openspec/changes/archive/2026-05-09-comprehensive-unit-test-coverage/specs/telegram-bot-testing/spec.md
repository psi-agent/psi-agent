## ADDED Requirements

### Requirement: TelegramBot _stop method handles graceful shutdown
`TelegramBot._stop` SHALL gracefully stop the bot application.

#### Scenario: Normal stop
- **WHEN** `_stop()` is called with a running application
- **THEN** the updater, application, and shutdown SHALL be called in order

#### Scenario: Stop when app is None
- **WHEN** `_stop()` is called and `self._app` is None
- **THEN** no exception SHALL be raised

### Requirement: split_message handles exact boundary positions
`split_message` SHALL correctly handle text at exact boundary positions.

#### Scenario: Newline exactly at midpoint
- **WHEN** text has a newline at exactly `max_length // 2` position
- **THEN** the split SHALL occur at the newline

#### Scenario: Space exactly at midpoint
- **WHEN** text has a space at exactly `max_length // 2` position and no newline in first half
- **THEN** the split SHALL occur at the space

#### Scenario: Very small max_length
- **WHEN** `split_message` is called with `max_length=3` and text longer than 3
- **THEN** the text SHALL be split into chunks of at most 3 characters

### Requirement: TelegramBot streaming handles content_buffer fallback
`_handle_message_streaming` SHALL use the `response` variable as fallback when `content_buffer` is empty.

#### Scenario: Empty content_buffer with non-empty response
- **WHEN** streaming completes with `content_buffer` empty but `response` has content
- **THEN** the `response` content SHALL be used for the final message

### Requirement: TelegramBot streaming handles typing indicator cancellation on error
`_handle_message_streaming` SHALL cancel the typing indicator task when `send_message_stream` raises an exception.

#### Scenario: Error during streaming cancels typing indicator
- **WHEN** `send_message_stream` raises an exception while typing indicator is running
- **THEN** the typing indicator task SHALL be cancelled

### Requirement: TelegramBot non-streaming handles multiple split chunks
`_handle_message_non_streaming` SHALL handle messages that split into more than 2 chunks.

#### Scenario: Very long message split into 3+ chunks
- **WHEN** the response is long enough to split into 3 or more chunks
- **THEN** all chunks SHALL be sent as separate replies

### Requirement: TelegramBot start without proxy
`TelegramBot.start` SHALL work correctly without a proxy configured.

#### Scenario: Start without proxy
- **WHEN** `start()` is called with no proxy configured
- **THEN** the application SHALL be created without proxy settings

### Requirement: TelegramBot start registers handlers
`TelegramBot.start` SHALL register the correct command and message handlers.

#### Scenario: Handler registration
- **WHEN** `start()` is called
- **THEN** a CommandHandler for `/start` and a MessageHandler SHALL be added to the application
