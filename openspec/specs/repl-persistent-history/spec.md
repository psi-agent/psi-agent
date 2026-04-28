## ADDED Requirements

### Requirement: REPL persists input history to file

The REPL SHALL persist input history to a file for recall across sessions.

#### Scenario: History file is created
- **WHEN** REPL starts for the first time
- **THEN** a history file SHALL be created at `~/.cache/psi-agent/repl_history.txt`

#### Scenario: History is loaded on startup
- **WHEN** REPL starts with existing history file
- **THEN** previous inputs SHALL be available for navigation

#### Scenario: History is saved after each input
- **WHEN** user submits a non-empty input
- **THEN** the input SHALL be appended to the history file

#### Scenario: History directory is created if missing
- **WHEN** REPL starts and `~/.cache/psi-agent/` does not exist
- **THEN** the directory SHALL be created automatically

### Requirement: REPL uses platform cache directory

The REPL SHALL store history in the platform's standard cache directory.

#### Scenario: Linux cache directory
- **WHEN** running on Linux
- **THEN** history SHALL be stored in `~/.cache/psi-agent/repl_history.txt`

#### Scenario: Custom history path via config
- **WHEN** a custom history file path is configured
- **THEN** history SHALL be stored at the configured path

### Requirement: REPL excludes empty inputs from history

The REPL SHALL NOT add empty inputs to the persistent history.

#### Scenario: Empty input ignored
- **WHEN** user submits an empty input (whitespace only)
- **THEN** the input SHALL NOT be added to history file