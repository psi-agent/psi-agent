## ADDED Requirements

### Requirement: REPL reads user input from stdin

The REPL SHALL read user input using `prompt-toolkit`'s async `PromptSession` for enhanced editing capabilities.

#### Scenario: User enters message
- **WHEN** user types a message and presses Enter
- **THEN** REPL SHALL accept the input and process it

#### Scenario: User sends empty message
- **WHEN** user presses Enter without typing anything
- **THEN** REPL SHALL ignore the empty input and prompt again

#### Scenario: User edits input before submitting
- **WHEN** user types text, moves cursor, and modifies the text
- **THEN** REPL SHALL accept the modified input when Enter is pressed

#### Scenario: User navigates history
- **WHEN** user presses up/down arrow keys
- **THEN** REPL SHALL display previous/next history entries

### Requirement: REPL uses prompt-toolkit for input handling

The REPL SHALL use `prompt-toolkit` library with async API for all input operations.

#### Scenario: Async input without blocking
- **WHEN** REPL waits for user input
- **THEN** the input operation SHALL use native async API without executor threads

#### Scenario: Prompt session initialized
- **WHEN** REPL starts
- **THEN** a `PromptSession` with `InMemoryHistory` SHALL be created for input handling

### Requirement: REPL sends messages to session

The REPL SHALL send user messages to psi-session via Unix socket using HTTP POST.

#### Scenario: Send message to session
- **WHEN** user enters a non-empty message
- **THEN** REPL SHALL send POST request to session with message in request body

#### Scenario: Receive response from session
- **WHEN** session returns a response
- **THEN** REPL SHALL display the response content to stdout

### Requirement: REPL sends only current message to session

The REPL SHALL send only the current user message to session, not the entire conversation history. Session is the single source of truth for conversation state.

#### Scenario: Send single message
- **WHEN** user enters a message
- **THEN** REPL SHALL send only that message to session

#### Scenario: Message format
- **WHEN** REPL sends a message to session
- **THEN** the request body SHALL contain a messages array with a single user message

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
