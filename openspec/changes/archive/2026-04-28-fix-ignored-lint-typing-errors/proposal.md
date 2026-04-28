## Why

The codebase contains several ignored lint and typing errors that can be fixed with straightforward code modifications. These ignores accumulate technical debt and mask potential issues. Fixing them improves code quality and type safety.

## What Changes

- Remove `no-matching-overload = "ignore"` rule from `pyproject.toml`
- Fix `# type: ignore[no-any-return]` in `schedule.py` by adding proper type annotation for croniter's `get_next()` return value
- Fix `# type: ignore` in `server.py` by passing the correct request object to `response.prepare()`
- Refactor `# noqa: E402` imports in `__init__.py` files to avoid module-level imports after class definitions

## Capabilities

### New Capabilities

- `type-safety-improvements`: Improve type safety by removing unnecessary type ignores and adding proper type annotations

### Modified Capabilities

- `session-core`: Fix typing issues in session server and schedule handling
- `psi-ai-openai-completions`: Refactor CLI imports to avoid E402 violations
- `central-cli`: Refactor channel and workspace CLI imports to avoid E402 violations

## Impact

- `src/psi_agent/session/schedule.py`: Add type cast for croniter return value
- `src/psi_agent/session/server.py`: Fix request parameter in streaming response
- `src/psi_agent/ai/__init__.py`: Restructure imports to avoid E402
- `src/psi_agent/workspace/__init__.py`: Restructure imports to avoid E402
- `src/psi_agent/channel/__init__.py`: Restructure imports to avoid E402
- `pyproject.toml`: Remove `no-matching-overload` ignore rule
