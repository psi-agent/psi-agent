## Why

Current test coverage is 85%, with several modules having coverage below 70%. The lowest coverage modules are CLI entry points (39-69%) and server/client implementations (63-79%). Improving test coverage ensures better code quality and catches regressions early.

## What Changes

- Add tests for CLI modules with low coverage:
  - `channel/cli/cli.py` (39%)
  - `ai/openai_completions/cli.py` (52%)
  - `session/cli.py` (52%)
  - `ai/anthropic_messages/cli.py` (53%)
  - `channel/repl/cli.py` (68%)
  - `channel/telegram/cli.py` (69%)
- Add tests for API modules with low coverage:
  - `workspace/umount/api.py` (63%)
  - `ai/anthropic_messages/server.py` (65%)
  - `ai/anthropic_messages/client.py` (67%)
  - `session/server.py` (76%)
  - `workspace/mount/api.py` (78%)
- Target: Increase overall coverage from 85% to 90%+

## Capabilities

### New Capabilities

- `cli-coverage-testing`: Tests for CLI entry points across all components
- `api-coverage-testing`: Tests for API modules with low coverage

### Modified Capabilities

- `test-coverage-improvement`: Increase minimum coverage requirement

## Impact

- `tests/`: Add new test files for CLI and API modules
- Coverage report will show improved metrics
- No changes to production code
