## ADDED Requirements

### Requirement: Test files pass type checking
All test files SHALL pass `uv run ty check` without errors.

#### Scenario: Type check passes
- **WHEN** running `uv run ty check`
- **THEN** no type errors SHALL be reported for test files

### Requirement: Test files pass lint checking
All test files SHALL pass `uv run ruff check` without errors.

#### Scenario: Lint check passes
- **WHEN** running `uv run ruff check`
- **THEN** no lint errors SHALL be reported
