## ADDED Requirements

### Requirement: Telegram bot uses assert for type narrowing

The `TelegramBot` class SHALL use `assert` statements to help type checkers understand that `_app` and `_app.updater` are not `None` after initialization.

#### Scenario: No ty ignore in telegram bot
- **WHEN** running `ty check` on `channel/telegram/bot.py`
- **THEN** no type errors are reported for `updater` access

### Requirement: Examples have no E501 violations

The example files SHALL not use `# ruff: noqa: E501` to ignore line length violations.

#### Scenario: No E501 noqa in examples
- **WHEN** running `grep -r "noqa: E501" examples/`
- **THEN** no matches are found

### Requirement: Tests have no E402 violations

The test files SHALL not use `# noqa: E402` to ignore import position violations.

#### Scenario: No E402 noqa in tests
- **WHEN** running `grep -r "noqa: E402" tests/`
- **THEN** no matches are found
