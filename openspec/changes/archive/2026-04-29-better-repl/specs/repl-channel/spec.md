## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: REPL uses prompt-toolkit for input handling

The REPL SHALL use `prompt-toolkit` library with async API for all input operations.

#### Scenario: Async input without blocking
- **WHEN** REPL waits for user input
- **THEN** the input operation SHALL use native async API without executor threads

#### Scenario: Prompt session initialized
- **WHEN** REPL starts
- **THEN** a `PromptSession` with `InMemoryHistory` SHALL be created for input handling
