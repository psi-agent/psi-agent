## Why

The codebase has grown organically, and while recent commits have addressed some code quality issues, a comprehensive audit is needed to ensure all 107 Python files consistently follow the coding standards defined in CLAUDE.md. This audit will identify remaining violations of the documented conventions and create a systematic plan to address them.

## What Changes

- Audit all Python files for compliance with CLAUDE.md coding standards
- Identify violations across multiple categories:
  - Missing `from __future__ import annotations` (type annotation compliance)
  - Use of legacy `Optional[X]`, `Union[X, Y]`, `List[X]`, `Dict[K, V]` instead of modern `X | None`, `X | Y`, `list[X]`, `dict[K, V]`
  - Import order violations (stdlib, third-party, local not properly separated)
  - Missing type annotations on functions
  - Non-async functions in workspace tools (must be async)
  - Use of `pathlib.Path` for IO operations instead of `anyio.Path`
  - Missing Google-style docstrings
  - Incorrect docstring format
  - Missing `__all__` exports in `__init__.py` files
  - CLI classes missing sensitive argument masking
- Create detailed task list for fixing each category of violations
- Ensure all fixes maintain backward compatibility

## Capabilities

### New Capabilities
- `code-quality-audit`: Comprehensive audit of Python codebase for CLAUDE.md compliance, generating detailed reports and fix tasks

### Modified Capabilities
- None (this is a new audit capability)

## Impact

- All 107 Python files in the codebase will be reviewed
- Fixes will be applied to ensure consistent code quality
- No breaking changes to public APIs
- Improves code maintainability and consistency
- Ensures all code follows modern Python 3.14+ conventions
