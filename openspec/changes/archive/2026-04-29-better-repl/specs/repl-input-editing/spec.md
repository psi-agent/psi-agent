## ADDED Requirements

### Requirement: REPL supports cursor movement within input line

The REPL SHALL allow users to move the cursor within the current input line using arrow keys.

#### Scenario: Move cursor left
- **WHEN** user types some text and presses left arrow key
- **THEN** cursor SHALL move one character to the left without deleting text

#### Scenario: Move cursor right
- **WHEN** user has moved cursor left and presses right arrow key
- **THEN** cursor SHALL move one character to the right without deleting text

#### Scenario: Move to line start
- **WHEN** user presses Home key or Ctrl+A
- **THEN** cursor SHALL move to the beginning of the input line

#### Scenario: Move to line end
- **WHEN** user presses End key or Ctrl+E
- **THEN** cursor SHALL move to the end of the input line

### Requirement: REPL supports text insertion at cursor position

The REPL SHALL insert typed characters at the current cursor position.

#### Scenario: Insert in middle of line
- **WHEN** user moves cursor to middle of existing text and types a character
- **THEN** the character SHALL be inserted at cursor position, pushing existing text to the right

#### Scenario: Append at end of line
- **WHEN** cursor is at end of line and user types a character
- **THEN** the character SHALL be appended to the end of the line

### Requirement: REPL supports text deletion

The REPL SHALL allow users to delete text using Backspace and Delete keys.

#### Scenario: Delete character before cursor
- **WHEN** user presses Backspace key with cursor not at line start
- **THEN** the character before the cursor SHALL be deleted and cursor position updated

#### Scenario: Delete character at cursor
- **WHEN** user presses Delete key with cursor not at line end
- **THEN** the character at cursor position SHALL be deleted

### Requirement: REPL supports clearing input

The REPL SHALL allow users to clear the current input line.

#### Scenario: Clear line with Ctrl+U
- **WHEN** user presses Ctrl+U
- **THEN** all text before the cursor SHALL be cleared

#### Scenario: Clear line with Ctrl+K
- **WHEN** user presses Ctrl+K
- **THEN** all text from cursor to end of line SHALL be cleared
