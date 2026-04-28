## ADDED Requirements

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
