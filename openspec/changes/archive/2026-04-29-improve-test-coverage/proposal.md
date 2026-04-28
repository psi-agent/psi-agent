## Why

Current test coverage is 59%, with several critical modules having very low coverage (session/runner: 27%, session/server: 30%, workspace/snapshot: 28%, workspace/umount: 31%). This poses risk for refactoring and makes it harder to catch regressions. Improving test coverage will increase confidence in code changes and help catch bugs early.

## What Changes

- Add comprehensive tests for low-coverage modules
- Focus on core business logic paths (session runner, tool execution, workspace operations)
- Add edge case and error handling tests
- Improve coverage for CLI entry points where practical

## Capabilities

### New Capabilities
- `test-coverage-analysis`: Define test coverage requirements and identify gaps
- `session-runner-tests`: Comprehensive tests for session runner core logic
- `workspace-snapshot-tests`: Tests for workspace snapshot functionality
- `workspace-umount-tests`: Tests for workspace unmount functionality
- `error-handling-tests`: Tests for error paths and edge cases across modules

### Modified Capabilities
- None (this is purely additive - adding tests, not changing behavior)

## Impact

- Test files in `tests/` directory (no production code changes)
- CI pipeline may need adjustment for coverage thresholds
- Developer workflow: more comprehensive test suite to run
