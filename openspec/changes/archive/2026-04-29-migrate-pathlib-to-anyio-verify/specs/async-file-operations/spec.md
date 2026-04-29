## ADDED Requirements

### Requirement: All file IO operations must use async methods

All file system operations in the psi-agent codebase SHALL use `anyio.Path` async methods instead of synchronous `pathlib.Path` methods to avoid blocking the event loop.

#### Scenario: Reading file content
- **WHEN** code reads file content
- **THEN** it SHALL use `await anyio.Path(path).read_text()` or `await anyio.Path(path).read_bytes()`

#### Scenario: Checking file existence
- **WHEN** code checks if a file exists
- **THEN** it SHALL use `await anyio.Path(path).exists()`

#### Scenario: Iterating directory contents
- **WHEN** code iterates over directory contents
- **THEN** it SHALL use `async for item in anyio.Path(dir).iterdir()`

#### Scenario: Creating directories
- **WHEN** code creates a directory
- **THEN** it SHALL use `await anyio.Path(path).mkdir(parents=True, exist_ok=True)`

#### Scenario: Deleting files
- **WHEN** code deletes a file
- **THEN** it SHALL use `await anyio.Path(path).unlink()`

### Requirement: pathlib.Path may be used for non-IO operations

`pathlib.Path` MAY be used for type annotations and path manipulation that does not involve file system IO.

#### Scenario: Type annotations
- **WHEN** defining function parameter or return types
- **THEN** `pathlib.Path` MAY be used as the type annotation

#### Scenario: Path manipulation
- **WHEN** code manipulates paths without accessing the file system
- **THEN** `pathlib.Path` MAY be used for operations like `.parent`, `.name`, `.suffix`, and `/` operator
