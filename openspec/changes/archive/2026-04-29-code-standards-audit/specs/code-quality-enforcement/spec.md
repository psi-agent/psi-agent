## ADDED Requirements

### Requirement: Import order follows stdlib → third-party → local pattern
All Python files SHALL organize imports in three groups separated by blank lines:
1. Standard library imports (alphabetically sorted)
2. Third-party imports (alphabetically sorted)
3. Local imports (alphabetically sorted)

This requirement aligns with ruff isort (I rule) configuration.

#### Scenario: Correct import order
- **WHEN** a Python file contains imports from stdlib, third-party, and local modules
- **THEN** imports SHALL be ordered as stdlib first, third-party second, local third, with each group alphabetically sorted

#### Scenario: Import order violation detected
- **WHEN** ruff check is run on a file with incorrect import order
- **THEN** ruff SHALL report an I rule violation

### Requirement: Async context managers set resources to None on exit
All async context manager `__aexit__` implementations SHALL set resource references to `None` after closing them, ensuring proper cleanup state and enabling debug logging.

#### Scenario: Resource cleanup in async context manager
- **WHEN** an async context manager exits
- **THEN** all resource attributes SHALL be set to `None` after their `close()` methods are called
- **AND** a debug log message SHALL record the cleanup

### Requirement: Type annotations use modern Python 3.14+ syntax
All Python files SHALL use modern type annotation syntax:
- `X | Y` instead of `Union[X, Y]`
- `list[X]` instead of `List[X]`
- `dict[K, V]` instead of `Dict[K, V]`
- `X | None` instead of `Optional[X]`

#### Scenario: Modern union syntax
- **WHEN** a function returns either a string or None
- **THEN** the return type annotation SHALL use `str | None`

### Requirement: All files include future annotations import
All Python files SHALL include `from __future__ import annotations` as the first import (after module docstring) to enable modern type annotation syntax in all Python versions.

#### Scenario: Future annotations present
- **WHEN** a Python file is created or modified
- **THEN** it SHALL include `from __future__ import annotations` before any other imports

### Requirement: Docstrings follow Google style format
All functions and classes SHALL use Google-style docstrings with:
- One-line summary
- Args section with parameter descriptions
- Returns section for functions that return values
- Raises section for functions that can raise exceptions

#### Scenario: Complete function documentation
- **WHEN** a function has parameters, a return value, and can raise exceptions
- **THEN** its docstring SHALL include Args, Returns, and Raises sections

### Requirement: File IO operations use async methods
All file system IO operations SHALL use `anyio.Path` async methods instead of synchronous `pathlib.Path` methods. The `pathlib.Path` MAY be used for type annotations and path construction without IO.

#### Scenario: Async file read
- **WHEN** code needs to read a file
- **THEN** it SHALL use `await anyio.Path(path).read_text()` instead of `Path(path).read_text()`

#### Scenario: Path construction without IO
- **WHEN** code constructs a path for later use or type annotation
- **THEN** `pathlib.Path` MAY be used since no IO is performed
