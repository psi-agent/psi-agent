## ADDED Requirements

### Requirement: All Python files must include future annotations import

All Python source files in the `src/` and `tests/` directories SHALL include `from __future__ import annotations` after the module docstring (if present) and before any other imports.

#### Scenario: Source file with module docstring
- **WHEN** a Python file in `src/` has a module docstring
- **THEN** the file SHALL have `from __future__ import annotations` immediately after the docstring

#### Scenario: Source file without module docstring
- **WHEN** a Python file in `src/` has no module docstring
- **THEN** the file SHALL have `from __future__ import annotations` as the first statement

#### Scenario: Test file
- **WHEN** a Python file is in the `tests/` directory
- **THEN** the file SHALL have `from __future__ import annotations` after any module docstring

### Requirement: File IO operations must use async methods

All file system IO operations SHALL use `anyio.Path` async methods instead of `pathlib.Path` synchronous methods.

#### Scenario: File existence check
- **WHEN** code needs to check if a file exists
- **THEN** it SHALL use `await anyio.Path(path).exists()` instead of `Path(path).exists()`

#### Scenario: File deletion
- **WHEN** code needs to delete a file
- **THEN** it SHALL use `await anyio.Path(path).unlink()` instead of `Path(path).unlink()`

#### Scenario: Directory iteration
- **WHEN** code needs to iterate over directory contents
- **THEN** it SHALL use `async for item in anyio.Path(path).iterdir()` instead of `for item in Path(path).iterdir()`

#### Scenario: File reading
- **WHEN** code needs to read file content
- **THEN** it SHALL use `await anyio.Path(path).read_text()` or `await anyio.open_file(path)` instead of `Path(path).read_text()`

### Requirement: pathlib.Path may be used for non-IO operations

`pathlib.Path` MAY be used for type annotations and path manipulation operations that do not perform IO.

#### Scenario: Path type annotation
- **WHEN** a function parameter or return type is a path
- **THEN** `pathlib.Path` MAY be used in the type annotation

#### Scenario: Path concatenation
- **WHEN** code needs to construct a path from parts
- **THEN** `pathlib.Path` MAY be used for the concatenation operation

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

### Requirement: Docstrings follow Google style format

All functions and classes SHALL use Google-style docstrings with:
- One-line summary
- Args section with parameter descriptions
- Returns section for functions that return values
- Raises section for functions that can raise exceptions

#### Scenario: Complete function documentation
- **WHEN** a function has parameters, a return value, and can raise exceptions
- **THEN** its docstring SHALL include Args, Returns, and Raises sections

### Requirement: Type annotations must be complete

All function parameters and return types SHALL have type annotations. The only exceptions are:
- `self` and `cls` parameters in methods
- Parameters with `*args` and `**kwargs`

#### Scenario: Function definition checked
- **WHEN** a function is defined
- **THEN** all parameters SHALL have type annotations
- **AND** the return type SHALL be annotated

### Requirement: Exception classes must have proper docstrings

Exception classes SHALL have docstrings on the class definition, not on the `pass` statement.

#### Scenario: Exception class definition
- **WHEN** an exception class is defined
- **THEN** the docstring SHALL be placed immediately after the class definition line
- **AND** the docstring SHALL NOT be placed after the `pass` statement

### Requirement: CLI sensitive arguments must be masked

CLI entry points that accept sensitive credentials (API keys, tokens, passwords) SHALL call `mask_sensitive_args()` immediately after argument parsing.

#### Scenario: CLI with API key argument
- **WHEN** a CLI accepts an `api_key` argument
- **THEN** the CLI SHALL call `mask_sensitive_args(["api_key"])` at the start of `__call__`

#### Scenario: Process list inspection
- **WHEN** the process is running
- **THEN** sensitive arguments SHALL NOT be visible in process listings (ps, top, /proc)
