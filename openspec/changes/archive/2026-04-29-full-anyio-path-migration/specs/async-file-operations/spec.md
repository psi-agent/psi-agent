## MODIFIED Requirements

### Requirement: All file I/O operations must use async methods

All file system I/O operations in the psi-agent codebase SHALL use async methods from `anyio.Path` or `anyio.open_file()` to prevent blocking the async event loop.

#### Scenario: Reading file content
- **WHEN** code needs to read file content
- **THEN** it SHALL use `await anyio.Path(path).read_text()` or `await anyio.open_file(path)` instead of `pathlib.Path.read_text()`

#### Scenario: Checking file existence
- **WHEN** code needs to check if a file exists
- **THEN** it SHALL use `await anyio.Path(path).exists()` instead of `pathlib.Path.exists()`

#### Scenario: Deleting a file
- **WHEN** code needs to delete a file
- **THEN** it SHALL use `await anyio.Path(path).unlink()` instead of `pathlib.Path.unlink()`

#### Scenario: Iterating directory contents
- **WHEN** code needs to iterate over directory contents
- **THEN** it SHALL use `async for item in anyio.Path(path).iterdir()` instead of `for item in pathlib.Path(path).iterdir()`

#### Scenario: Creating directories
- **WHEN** code needs to create a directory
- **THEN** it SHALL use `await anyio.Path(path).mkdir()` instead of `pathlib.Path.mkdir()`

#### Scenario: Resolving paths
- **WHEN** code needs to resolve a path to its absolute form
- **THEN** it SHALL use `await anyio.Path(path).resolve()` instead of `pathlib.Path.resolve()` when the operation involves I/O

### Requirement: pathlib.Path may be used for type annotations and path manipulation

**REMOVED** - `pathlib.Path` SHALL NOT be used anywhere in the codebase. All path-related code SHALL use `anyio.Path`.

**Reason**: Code consistency - using a single path type throughout the codebase.

**Migration**: Replace all `pathlib.Path` with `anyio.Path`:
- Type annotations: `Path` → `anyio.Path`
- Data class fields: `task_dir: Path` → `task_dir: anyio.Path`
- Import statements: `from pathlib import Path` → `import anyio` (use `anyio.Path`)
- Path construction: `Path(path)` → `anyio.Path(path)`

## ADDED Requirements

### Requirement: All path types must be anyio.Path

All path-related types in the psi-agent codebase SHALL use `anyio.Path`, including type annotations, data class fields, and function parameters/returns.

#### Scenario: Type annotation for path parameters
- **WHEN** a function accepts a path parameter
- **THEN** it SHALL use `anyio.Path` as the type annotation

#### Scenario: Type annotation for path returns
- **WHEN** a function returns a path
- **THEN** it SHALL use `anyio.Path` as the return type

#### Scenario: Data class path fields
- **WHEN** a data class stores a path
- **THEN** the field type SHALL be `anyio.Path`

#### Scenario: Config class path properties
- **WHEN** a config class provides a path property
- **THEN** the return type SHALL be `anyio.Path`