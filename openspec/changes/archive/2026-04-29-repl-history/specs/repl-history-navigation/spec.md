## MODIFIED Requirements

### Requirement: REPL maintains input history during session

The REPL SHALL maintain a history of previously entered inputs using persistent file-based storage.

#### Scenario: History is populated
- **WHEN** user submits multiple inputs
- **THEN** each submitted input SHALL be added to the history

#### Scenario: History excludes empty inputs
- **WHEN** user submits an empty input
- **THEN** the empty input SHALL NOT be added to history

#### Scenario: History persists across sessions
- **WHEN** user exits and restarts REPL
- **THEN** previous inputs SHALL be available for navigation

### Requirement: REPL supports navigating history with arrow keys

The REPL SHALL allow users to navigate through input history using up and down arrow keys.

#### Scenario: Navigate to previous input
- **WHEN** user presses up arrow key
- **THEN** the previous input from history SHALL be displayed in the input line

#### Scenario: Navigate to next input
- **WHEN** user has navigated back in history and presses down arrow key
- **THEN** the next input from history SHALL be displayed, or empty line if at most recent

#### Scenario: History navigation preserves cursor position
- **WHEN** user navigates to a history entry
- **THEN** cursor SHALL be positioned at the end of the displayed input

### Requirement: REPL allows editing history entries

The REPL SHALL allow users to edit history entries before resubmitting.

#### Scenario: Edit history entry
- **WHEN** user navigates to a history entry and modifies it
- **THEN** the modified text SHALL be editable in the input line

#### Scenario: Submit modified history
- **WHEN** user edits a history entry and submits
- **THEN** the modified input SHALL be sent as a new message and added to history
