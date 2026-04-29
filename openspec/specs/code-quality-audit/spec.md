## ADDED Requirements

### Requirement: All Python files must have `from __future__ import annotations`

Every Python file in the codebase SHALL include `from __future__ import annotations` at the top of the file (after the module docstring if present) to enable modern type annotation syntax.

#### Scenario: File with module docstring
- **WHEN** a Python file has a module docstring
- **THEN** the `from __future__ import annotations` import SHALL appear immediately after the docstring

#### Scenario: File without module docstring
- **WHEN** a Python file has no module docstring
- **THEN** the `from __future__ import annotations` import SHALL be the first line

### Requirement: All type annotations must use modern Python 3.14+ syntax

All type annotations SHALL use modern union syntax (`X | Y`) instead of legacy `Union[X, Y]`, and `X | None` instead of `Optional[X]`. Generic types SHALL use lowercase forms (`list[X]`, `dict[K, V]`) instead of `List[X]`, `Dict[K, V]`.

#### Scenario: Optional type annotation
- **WHEN** a parameter or return type is optional
- **THEN** the annotation SHALL use `X | None` syntax, not `Optional[X]`

#### Scenario: Union type annotation
- **WHEN** a type can be one of multiple types
- **THEN** the annotation SHALL use `X | Y | Z` syntax, not `Union[X, Y, Z]`

#### Scenario: Generic container types
- **WHEN** using list, dict, or other generic containers
- **THEN** the annotation SHALL use `list[X]`, `dict[K, V]` syntax, not `List[X]`, `Dict[K, V]`

### Requirement: Imports must follow the specified ordering

All Python files SHALL organize imports in three groups, separated by blank lines, in this order:
1. Standard library imports (sorted alphabetically)
2. Third-party imports (sorted alphabetically)
3. Local imports (sorted alphabetically)

#### Scenario: Import order validation
- **WHEN** a Python file is checked with `ruff check --select I`
- **THEN** no import order violations SHALL be reported

### Requirement: All functions must have type annotations

All function parameters and return types SHALL have type annotations. The `Any` type is acceptable when the type is truly dynamic.

#### Scenario: Function with parameters
- **WHEN** a function is defined
- **THEN** each parameter SHALL have a type annotation

#### Scenario: Function return type
- **WHEN** a function is defined
- **THEN** the return type SHALL be annotated

### Requirement: Workspace tool functions must be async

All tool functions in workspace `tools/` directories SHALL be async functions. Synchronous tool functions are not supported.

#### Scenario: Tool function definition
- **WHEN** a `.py` file in a `tools/` directory defines a `tool` function
- **THEN** the function SHALL be defined with `async def`

### Requirement: File IO operations must use anyio.Path

All file system IO operations SHALL use `anyio.Path` async methods instead of `pathlib.Path` synchronous methods. The `pathlib.Path` may be used for type annotations and path manipulation without IO.

#### Scenario: Reading file content
- **WHEN** code needs to read a file
- **THEN** it SHALL use `await anyio.Path(path).read_text()` or `await anyio.open_file()`

#### Scenario: Checking file existence
- **WHEN** code needs to check if a file exists
- **THEN** it SHALL use `await anyio.Path(path).exists()`

#### Scenario: Iterating directory contents
- **WHEN** code needs to iterate over directory contents
- **THEN** it SHALL use `async for entry in anyio.Path(path).iterdir()`

### Requirement: All public modules must have docstrings

All Python modules SHALL have a module-level docstring at the top of the file describing the module's purpose.

#### Scenario: Module docstring presence
- **WHEN** a Python file is opened
- **THEN** the first statement SHALL be a docstring describing the module

### Requirement: All functions must have Google-style docstrings

All functions SHALL have docstrings following Google style format with Args, Returns, and Raises sections as applicable.

#### Scenario: Function docstring with parameters
- **WHEN** a function has parameters
- **THEN** the docstring SHALL include an `Args:` section listing each parameter

#### Scenario: Function docstring with return value
- **WHEN** a function returns a value
- **THEN** the docstring SHALL include a `Returns:` section describing the return value

### Requirement: CLI classes handling sensitive credentials must mask arguments

All CLI entry points that accept sensitive credentials (API keys, tokens, passwords) SHALL call `mask_sensitive_args()` at the start of their `__call__` method to hide these values from process listings.

#### Scenario: CLI with API key parameter
- **WHEN** a CLI class has an `api_key` or `token` parameter
- **THEN** the `__call__` method SHALL call `mask_sensitive_args(["api_key"])` or `mask_sensitive_args(["token"])` as its first action

### Requirement: All __init__.py files must define __all__

All `__init__.py` files SHALL define `__all__` to explicitly list the public API of the module.

#### Scenario: Module exports
- **WHEN** a package's `__init__.py` is created
- **THEN** it SHALL include `__all__ = [...]` listing all exported names
