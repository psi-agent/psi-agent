## ADDED Requirements

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

`pathlib.Path` MAY be used for type annotations, function return types, and pure path manipulation operations that do not involve file system I/O.

#### Scenario: Type annotation for path parameters
- **WHEN** a function accepts or returns a path
- **THEN** it MAY use `pathlib.Path` for type annotations without async operations

#### Scenario: Path manipulation without I/O
- **WHEN** code constructs paths by joining components
- **THEN** it MAY use `pathlib.Path` operators like `/` for path concatenation

#### Scenario: Config class path conversion
- **WHEN** a config class converts string paths to Path objects for return
- **THEN** it MAY use `pathlib.Path` since no I/O is performed
