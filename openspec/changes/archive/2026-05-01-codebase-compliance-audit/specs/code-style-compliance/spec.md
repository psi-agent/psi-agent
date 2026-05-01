## ADDED Requirements

### Requirement: All Python files must start with future annotations
All Python files in the codebase SHALL include `from __future__ import annotations` at the top of the file (after module docstring) to enable modern type annotation syntax.

#### Scenario: File with future annotations
- **WHEN** a Python file is created or modified
- **THEN** it SHALL contain `from __future__ import annotations` after the module docstring

### Requirement: Use modern union type syntax
All type annotations SHALL use Python 3.14+ modern syntax: `X | Y` instead of `Optional[X]` or `Union[X, Y]`, `list[X]` instead of `List[X]`, `dict[K, V]` instead of `Dict[K, V]`.

#### Scenario: Optional type annotation
- **WHEN** a function parameter or return type is optional
- **THEN** it SHALL use `X | None` syntax instead of `Optional[X]`

#### Scenario: Generic type annotation
- **WHEN** a function uses generic types
- **THEN** it SHALL use lowercase generics (`list[X]`, `dict[K, V]`) instead of capitalized generics (`List[X]`, `Dict[K, V]`)

### Requirement: Import order follows stdlib-third-party-local
All Python files SHALL organize imports in three groups, separated by blank lines:
1. Standard library imports (alphabetically sorted)
2. Third-party imports (alphabetically sorted)
3. Local imports (alphabetically sorted)

#### Scenario: Correct import order
- **WHEN** a Python file has multiple imports
- **THEN** imports SHALL be grouped as stdlib → third-party → local, with each group alphabetically sorted

### Requirement: All functions have type annotations
All function parameters and return types SHALL have type annotations using Python's type hint syntax.

#### Scenario: Function with type annotations
- **WHEN** a function is defined
- **THEN** all parameters SHALL have type annotations and the return type SHALL be specified

### Requirement: Google-style docstrings
All public functions, classes, and modules SHALL have docstrings following Google-style format with Args, Returns, and Raises sections as applicable.

#### Scenario: Function docstring
- **WHEN** a function is documented
- **THEN** it SHALL use Google-style docstring format with Args and Returns sections
