## ADDED Requirements

### Requirement: REPL client async context manager logging

The REPL client SHALL log connector cleanup in `__aexit__` at DEBUG level.

#### Scenario: Connector close logging
- **WHEN** exiting `ReplClient` async context
- **THEN** connector close SHALL be logged at DEBUG level

### Requirement: REPL request body includes model field

The REPL request body SHALL include the `model` field.

#### Scenario: Request body structure
- **WHEN** REPL sends request to session
- **THEN** the request body SHALL include `"model": "session"`

### Requirement: REPL streaming content handling

The REPL streaming handler SHALL use consistent content checking.

#### Scenario: Empty content string handling
- **WHEN** streaming chunk has `content: ""`
- **THEN** it SHALL be appended to buffer but not logged or passed to callback

#### Scenario: None content handling
- **WHEN** streaming chunk has no content field or `content: null`
- **THEN** it SHALL NOT be appended to buffer