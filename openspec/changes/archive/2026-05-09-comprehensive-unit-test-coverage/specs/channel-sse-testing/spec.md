## ADDED Requirements

### Requirement: Channel clients handle null content in SSE delta
All channel clients (ReplClient, CliClient, TelegramClient) SHALL handle `content: null` in streaming delta without crashing.

#### Scenario: ReplClient null content in delta
- **WHEN** `ReplClient.send_message_stream` receives a chunk with `content: null`
- **THEN** the null content SHALL be skipped (not appended to result)

#### Scenario: TelegramClient null content in delta
- **WHEN** `TelegramClient.send_message_stream` receives a chunk with `content: null`
- **THEN** the null content SHALL be skipped

### Requirement: Channel clients handle empty string content in SSE delta
All channel clients SHALL handle `content: ""` in streaming delta correctly.

#### Scenario: CliClient empty string content
- **WHEN** `CliClient._send_streaming` receives a chunk with `content: ""`
- **THEN** the empty string SHALL be handled without error

### Requirement: Channel clients handle reasoning field in SSE delta
All channel clients SHALL handle the `reasoning` field in streaming delta.

#### Scenario: ReplClient reasoning field
- **WHEN** `ReplClient.send_message_stream` receives a chunk with a `reasoning` field
- **THEN** the reasoning content SHALL be handled (logged or displayed, not crashed)

#### Scenario: TelegramClient reasoning field
- **WHEN** `TelegramClient.send_message_stream` receives a chunk with a `reasoning` field
- **THEN** the reasoning content SHALL be handled without error

### Requirement: Channel clients handle empty choices in SSE chunk
All channel clients SHALL handle streaming chunks with empty `choices` list.

#### Scenario: Empty choices list
- **WHEN** a streaming chunk has `choices: []`
- **THEN** the chunk SHALL be skipped without error

### Requirement: Channel clients handle missing delta key in SSE chunk
All channel clients SHALL handle streaming chunks where the `delta` key is missing.

#### Scenario: Missing delta key
- **WHEN** a streaming chunk has `choices` but no `delta` key in the first choice
- **THEN** the chunk SHALL be handled without crashing

### Requirement: Channel clients handle non-UTF-8 bytes in SSE stream
All channel clients SHALL handle non-UTF-8 bytes in the SSE stream.

#### Scenario: Non-UTF-8 bytes in SSE line
- **WHEN** a line in the SSE stream cannot be decoded as UTF-8
- **THEN** the error SHALL be handled gracefully (logged, not crashed)

### Requirement: Channel send_message handles null content in response
All channel clients' `send_message` SHALL handle null content in the non-streaming response.

#### Scenario: ReplClient null content in response
- **WHEN** `ReplClient.send_message` receives a response with `content: null`
- **THEN** an empty string SHALL be returned

#### Scenario: TelegramClient null content in response
- **WHEN** `TelegramClient.send_message` receives a response with `content: null`
- **THEN** an empty string SHALL be returned

### Requirement: Channel send_message handles missing choices in response
All channel clients' `send_message` SHALL handle responses with missing `choices` key.

#### Scenario: Response with no choices key
- **WHEN** `send_message` receives a response with no `choices` key
- **THEN** an appropriate error SHALL be raised or empty string returned

### Requirement: TelegramClient includes user_id in request body
`TelegramClient.send_message` and `send_message_stream` SHALL include the `user_id` in the request body.

#### Scenario: send_message includes user field
- **WHEN** `TelegramClient.send_message` is called with `user_id="123"`
- **THEN** the request body SHALL include `"user": "123"`

#### Scenario: send_message_stream includes user field
- **WHEN** `TelegramClient.send_message_stream` is called with `user_id="123"`
- **THEN** the request body SHALL include `"user": "123"`
