## Why

The codebase has grown organically, and we need to ensure all Python files strictly follow the coding standards defined in CLAUDE.md. A comprehensive compliance audit will identify deviations from established conventions, improve code maintainability, and ensure consistent code quality across all components.

## What Changes

- **Code Style Compliance**: Verify all files follow Python 3.14+ modern syntax (`X | Y` instead of `Optional[X]`, `list[X]` instead of `List[X]`)
- **Import Order**: Ensure all files follow the stdlib → third-party → local import ordering
- **Type Annotations**: Verify all functions have proper type annotations with `from __future__ import annotations`
- **Docstring Standards**: Check all functions have Google-style docstrings
- **Async Patterns**: Verify all async context managers follow the `__aenter__`/`__aexit__` pattern correctly
- **Error Handling**: Ensure proper error handling with loguru logging
- **Defensive Programming**: Check null-safety patterns for external data

## Capabilities

### New Capabilities

- `code-style-compliance`: Standards for Python code style including type annotations, import ordering, and modern syntax
- `async-patterns-compliance`: Standards for async context managers, async IO operations, and error handling
- `defensive-programming`: Standards for null-safe handling of external data

### Modified Capabilities

None - this is a compliance audit, not a feature change.

## Impact

- All Python files in `src/psi_agent/`
- Development workflow (linting, type checking)
- Code review process
