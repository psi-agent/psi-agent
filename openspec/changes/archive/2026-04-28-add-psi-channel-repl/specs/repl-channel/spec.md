## ADDED Requirements

### Requirement: REPL reads user input from stdin

The REPL SHALL read user input from stdin in a loop, prompting for each message.

#### Scenario: User enters message
- **WHEN** user types a message and presses Enter
- **THEN** REPL SHALL accept the input and process it

#### Scenario: User sends empty message
- **WHEN** user presses Enter without typing anything
- **THEN** REPL SHALL ignore the empty input and prompt again

### Requirement: REPL sends messages to session

The REPL SHALL send user messages to psi-session via Unix socket using HTTP POST.

#### Scenario: Send message to session
- **WHEN** user enters a non-empty message
- **THEN** REPL SHALL send POST request to session with message in request body

#### Scenario: Receive response from session
- **WHEN** session returns a response
- **THEN** REPL SHALL display the response content to stdout

### Requirement: REPL maintains conversation history

The REPL SHALL maintain a list of messages for conversation context.

#### Scenario: Add user message to history
- **WHEN** user sends a message
- **THEN** REPL SHALL add the message to conversation history

#### Scenario: Add assistant message to history
- **WHEN** session returns a response
- **THEN** REPL SHALL add the response to conversation history

#### Scenario: Send history with request
- **WHEN** REPL sends a new message to session
- **THEN** REPL SHALL include all previous messages in the request

### Requirement: REPL supports graceful exit

The REPL SHALL provide mechanisms for graceful exit.

#### Scenario: Exit with Ctrl+D
- **WHEN** user presses Ctrl+D (EOF)
- **THEN** REPL SHALL exit cleanly without error

#### Scenario: Exit with quit command
- **WHEN** user types `/quit`
- **THEN** REPL SHALL exit cleanly

### Requirement: REPL provides CLI entry point

The REPL SHALL provide a CLI command `psi-channel-repl` for starting the interface.

#### Scenario: CLI starts REPL
- **WHEN** `psi-channel-repl` is invoked with session socket path
- **THEN** REPL SHALL connect to session and start interactive loop
