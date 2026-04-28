## Purpose

Improve type safety by removing unnecessary type ignores and adding proper type annotations.

## Requirements

### Requirement: Code passes type checking without ignores

The codebase SHALL pass `ty check` without any `# type: ignore` comments or global ignore rules in `pyproject.toml`.

#### Scenario: No type ignore comments in source files
- **WHEN** running `grep -r "# type: ignore" src/`
- **THEN** no matches are found

#### Scenario: No global ty ignore rules
- **WHEN** reading `pyproject.toml`
- **THEN** the `[tool.ty.rules]` section does not contain ignore rules

### Requirement: Code passes lint checking without noqa comments

The codebase SHALL pass `ruff check` without any `# noqa` comments for fixable issues.

#### Scenario: No E402 noqa comments
- **WHEN** running `grep -r "# noqa: E402" src/`
- **THEN** no matches are found

#### Scenario: Ruff check passes
- **WHEN** running `ruff check src/`
- **THEN** all checks pass with no errors

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
