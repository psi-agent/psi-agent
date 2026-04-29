## ADDED Requirements

### Requirement: All Python files must include future annotations import

All Python files in the codebase SHALL include `from __future__ import annotations` as the first import statement (after the module docstring) to enable modern type annotation syntax.

#### Scenario: New Python file created
- **WHEN** a new Python file is created in the project
- **THEN** the file SHALL include `from __future__ import annotations` after the module docstring

#### Scenario: Type annotations use modern syntax
- **WHEN** type annotations are written in the code
- **THEN** they SHALL use modern union syntax (`X | Y`) instead of `Optional[X]` or `Union[X, Y]`

### Requirement: Import statements must follow ordering convention

All Python files SHALL organize imports in three groups in the following order:
1. Standard library imports
2. Third-party library imports
3. Local project imports

Each group SHALL be sorted alphabetically.

#### Scenario: Import order validation
- **WHEN** a Python file is checked for import order
- **THEN** all stdlib imports SHALL appear before third-party imports
- **AND** all third-party imports SHALL appear before local imports
- **AND** imports within each group SHALL be sorted alphabetically

### Requirement: Type annotations must be complete

All function parameters and return types SHALL have type annotations. The only exceptions are:
- `self` and `cls` parameters in methods
- Parameters with `*args` and `**kwargs`

#### Scenario: Function definition checked
- **WHEN** a function is defined
- **THEN** all parameters SHALL have type annotations
- **AND** the return type SHALL be annotated

### Requirement: Docstrings must follow Google style

All modules, classes, and public functions SHALL have docstrings following Google style format.

#### Scenario: Function docstring format
- **WHEN** a function has a docstring
- **THEN** it SHALL include a brief description
- **AND** it MAY include Args, Returns, and Raises sections as appropriate

#### Scenario: Class docstring format
- **WHEN** a class has a docstring
- **THEN** it SHALL include a brief description
- **AND** it MAY include an Attributes section

### Requirement: Exception classes must have proper docstrings

Exception classes SHALL have docstrings on the class definition, not on the `pass` statement.

#### Scenario: Exception class definition
- **WHEN** an exception class is defined
- **THEN** the docstring SHALL be placed immediately after the class definition line
- **AND** the docstring SHALL NOT be placed after the `pass` statement

### Requirement: Async operations must use async methods

All IO operations SHALL use async methods from the appropriate libraries:
- File operations: `anyio.Path` or `anyio.open_file()`
- HTTP requests: `aiohttp.ClientSession`
- Subprocess: `asyncio.create_subprocess_exec` or `asyncio.create_subprocess_shell`

#### Scenario: File read operation
- **WHEN** a file needs to be read
- **THEN** the code SHALL use `await anyio.Path(path).read_text()` or `await anyio.open_file()`

#### Scenario: Subprocess execution
- **WHEN** a subprocess command needs to be executed
- **THEN** the code SHALL use `asyncio.create_subprocess_exec()` or `asyncio.create_subprocess_shell()`

### Requirement: CLI sensitive arguments must be masked

CLI entry points that accept sensitive credentials (API keys, tokens, passwords) SHALL call `mask_sensitive_args()` immediately after argument parsing.

#### Scenario: CLI with API key argument
- **WHEN** a CLI accepts an `api_key` argument
- **THEN** the CLI SHALL call `mask_sensitive_args(["api_key"])` at the start of `__call__`

#### Scenario: Process list inspection
- **WHEN** the process is running
- **THEN** sensitive arguments SHALL NOT be visible in process listings (ps, top, /proc)
