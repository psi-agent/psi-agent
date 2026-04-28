## ADDED Requirements

### Requirement: All file I/O operations use async methods
All file I/O operations in workspace system.py files SHALL use async methods from `anyio.Path` instead of synchronous `pathlib.Path` methods.

#### Scenario: Reading file content asynchronously
- **WHEN** a system.py file reads file content
- **THEN** it SHALL use `await anyio.Path(path).read_text()` instead of `path.read_text()`

#### Scenario: Checking file existence asynchronously
- **WHEN** a system.py file checks if a file or directory exists
- **THEN** it SHALL use `await anyio.Path(path).exists()` instead of `path.exists()`

#### Scenario: Iterating directory contents asynchronously
- **WHEN** a system.py file iterates over directory contents
- **THEN** it SHALL use `async for item in anyio.Path(path).iterdir()` instead of `for item in path.iterdir()`

#### Scenario: Checking if path is directory asynchronously
- **WHEN** a system.py file checks if a path is a directory
- **THEN** it SHALL use `await anyio.Path(path).is_dir()` instead of `path.is_dir()`

#### Scenario: Checking if path is file asynchronously
- **WHEN** a system.py file checks if a path is a file
- **THEN** it SHALL use `await anyio.Path(path).is_file()` instead of `path.is_file()`

### Requirement: pathlib.Path allowed for non-I/O operations
The `pathlib.Path` class MAY still be used for type annotations and path manipulation that does not involve I/O operations.

#### Scenario: Path type annotations
- **WHEN** a function parameter or return type represents a file path
- **THEN** it MAY use `pathlib.Path` for the type annotation

#### Scenario: Path manipulation without I/O
- **WHEN** code constructs new paths by joining or manipulating existing paths
- **THEN** it MAY use `pathlib.Path` operators like `/` for path concatenation
