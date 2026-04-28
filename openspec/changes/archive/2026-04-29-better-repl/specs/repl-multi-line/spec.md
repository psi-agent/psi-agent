## ADDED Requirements

### Requirement: REPL supports multi-line input mode

The REPL SHALL provide a mechanism for entering multi-line input.

#### Scenario: Enter multi-line mode
- **WHEN** user presses Meta+Enter (Alt+Enter) or Escape followed by Enter
- **THEN** a new line SHALL be inserted without submitting the message

#### Scenario: Display multi-line input
- **WHEN** user has entered multiple lines
- **THEN** all lines SHALL be displayed in the input area

#### Scenario: Submit multi-line input
- **WHEN** user presses Enter in multi-line mode
- **THEN** the entire multi-line text SHALL be submitted as a single message

### Requirement: REPL preserves line breaks in multi-line input

The REPL SHALL preserve line breaks when submitting multi-line messages.

#### Scenario: Line breaks preserved
- **WHEN** user submits multi-line input
- **THEN** the message sent to session SHALL contain newline characters between lines

#### Scenario: Response handles multi-line
- **WHEN** session receives a multi-line message
- **THEN** the response SHALL be displayed normally (session handles multi-line content)
