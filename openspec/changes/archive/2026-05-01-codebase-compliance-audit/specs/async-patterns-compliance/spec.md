## ADDED Requirements

### Requirement: Async context managers follow standard pattern
All async context managers SHALL implement `__aenter__` and `__aexit__` methods following the standard pattern: `__aenter__` initializes resources and returns self, `__aexit__` closes resources and sets the resource variable to `None`.

#### Scenario: Async context manager implementation
- **WHEN** a class implements async context manager pattern
- **THEN** `__aenter__` SHALL initialize resources and return self, and `__aexit__` SHALL close resources and set resource variables to `None`

### Requirement: All IO operations use async methods
All file system, network, and subprocess operations SHALL use async methods from `anyio`, `aiohttp`, or `asyncio` instead of synchronous alternatives.

#### Scenario: File system operations
- **WHEN** code performs file IO
- **THEN** it SHALL use `anyio.Path` async methods or `anyio.open_file()` instead of `pathlib.Path` synchronous methods

#### Scenario: Network requests
- **WHEN** code makes HTTP requests
- **THEN** it SHALL use `aiohttp.ClientSession` instead of synchronous HTTP clients

#### Scenario: Subprocess execution
- **WHEN** code runs subprocesses
- **THEN** it SHALL use `asyncio.create_subprocess_exec` or `asyncio.create_subprocess_shell` instead of `subprocess.run`

### Requirement: Error handling with loguru
All error handling in async operations SHALL use try-except blocks with loguru logging at appropriate levels (ERROR for failures, DEBUG for details).

#### Scenario: Network error handling
- **WHEN** a network request fails
- **THEN** the error SHALL be caught, logged with loguru at ERROR level, and return a dict with `error` and `status_code` fields

### Requirement: Async functions for workspace tools
All tool functions in workspace/tools/ SHALL be async functions.

#### Scenario: Tool function definition
- **WHEN** a tool is defined in workspace/tools/
- **THEN** the `tool()` function SHALL be an async function
