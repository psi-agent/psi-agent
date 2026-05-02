## ADDED Requirements

### Requirement: Telegram module exports public classes

The Telegram module SHALL export public classes via `__init__.py`.

#### Scenario: Telegram module exports public classes
- **WHEN** importing from `psi_agent.channel.telegram`
- **THEN** `Telegram`, `TelegramConfig`, `TelegramClient` SHALL be available

### Requirement: Telegram client async context manager logging

The Telegram client SHALL log connector cleanup in `__aexit__` at DEBUG level.

#### Scenario: Connector close logging
- **WHEN** exiting `TelegramClient` async context
- **THEN** connector close SHALL be logged at DEBUG level

### Requirement: Telegram streaming content handling

The Telegram streaming handler SHALL use consistent content checking.

#### Scenario: Empty content string handling
- **WHEN** streaming chunk has `content: ""`
- **THEN** it SHALL be appended to buffer but not logged or passed to callback

#### Scenario: None content handling
- **WHEN** streaming chunk has no content field or `content: null`
- **THEN** it SHALL NOT be appended to buffer