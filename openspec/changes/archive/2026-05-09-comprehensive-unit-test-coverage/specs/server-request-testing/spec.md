## ADDED Requirements

### Requirement: Server handles user_message with None content
`SessionServer._handle_chat_completions` SHALL handle requests where the user message has `content: None` without crashing.

#### Scenario: User message with None content
- **WHEN** a chat completion request has the last user message with `content: None`
- **THEN** the server SHALL not crash on `content[:100]` and SHALL process the request

#### Scenario: User message with empty string content
- **WHEN** a chat completion request has the last user message with `content: ""`
- **THEN** the server SHALL process the request normally

### Requirement: Server _filter_for_channel handles missing fields
`SessionServer._filter_for_channel` SHALL handle responses with missing or malformed fields gracefully.

#### Scenario: Response with no choices key
- **WHEN** the response dict has no `choices` key
- **THEN** the filtered response SHALL handle this gracefully (return empty choices or error)

#### Scenario: Response with empty choices list
- **WHEN** the response has `choices: []`
- **THEN** the filtered response SHALL preserve the empty choices list

#### Scenario: Choice with missing message key
- **WHEN** a choice dict has no `message` key
- **THEN** the filtered response SHALL handle this gracefully

#### Scenario: Choice with None content
- **WHEN** a choice has `message: {"content": None}`
- **THEN** the filtered content SHALL be None or empty string

### Requirement: Server start handles exceptions
`SessionServer.start` SHALL handle exceptions during startup gracefully.

#### Scenario: Runner __aenter__ raises exception
- **WHEN** `runner.__aenter__()` raises an exception
- **THEN** the exception SHALL propagate (server fails to start)

#### Scenario: Socket removal permission error
- **WHEN** removing an existing socket file raises PermissionError
- **THEN** the error SHALL propagate or be handled appropriately

### Requirement: Server stop handles exceptions
`SessionServer.stop` SHALL handle exceptions during cleanup gracefully.

#### Scenario: Double stop
- **WHEN** `stop()` is called twice
- **THEN** no exception SHALL be raised on the second call

#### Scenario: Runner __aexit__ raises exception
- **WHEN** `runner.__aexit__()` raises an exception
- **THEN** the exception SHALL be logged but not crash the server
