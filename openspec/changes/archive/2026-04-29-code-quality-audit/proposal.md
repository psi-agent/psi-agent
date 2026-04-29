## Why

The codebase has accumulated inconsistencies with the coding standards defined in CLAUDE.md. A comprehensive audit revealed multiple violations across all components, including missing `from __future__ import annotations` imports, inconsistent import ordering, missing type annotations, and other deviations from the established conventions. Fixing these issues will improve code quality, maintainability, and ensure consistent code style across the entire project.

## What Changes

- Add missing `from __future__ import annotations` to all Python files that lack it
- Fix import ordering to follow stdlib → third-party → local convention
- Add missing type annotations to function parameters and return types
- Fix docstring formatting to follow Google style consistently
- Remove unused imports and clean up code
- Ensure all async context managers properly set resource variables to `None` after cleanup
- Standardize error handling patterns across components

## Capabilities

### New Capabilities

- `code-quality-enforcement`: Establishes automated code quality checks and enforcement mechanisms

### Modified Capabilities

None - this is a code quality improvement that doesn't change functional requirements.

## Impact

- **Affected files**: All 57 Python files in `src/psi_agent/`
- **Components impacted**: ai, channel, session, utils, workspace
- **No breaking changes**: All fixes are internal code quality improvements
- **Dependencies**: No new dependencies required
