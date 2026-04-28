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
