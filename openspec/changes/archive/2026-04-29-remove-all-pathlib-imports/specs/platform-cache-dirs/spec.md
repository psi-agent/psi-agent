## MODIFIED Requirements

### Requirement: No pathlib.Path imports in source code
The source code SHALL NOT import `pathlib.Path` directly, using `anyio.Path` for all path operations and `platformdirs` for determining platform-specific directories. This requirement applies to all Python files including tests.

#### Scenario: Source code review
- **WHEN** reviewing all Python files in the repository
- **THEN** no file SHALL contain `from pathlib import Path` or `import pathlib`

#### Scenario: Test file review
- **WHEN** reviewing test files in `tests/`
- **THEN** no file SHALL import `pathlib` for any purpose, including type annotations
