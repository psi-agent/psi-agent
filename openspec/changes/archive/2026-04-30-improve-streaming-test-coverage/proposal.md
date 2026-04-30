## Why

The recent streaming behavior changes have insufficient test coverage (70.06% patch coverage with 44 lines missing). Additionally, a manual code review is needed to ensure all changes comply with CLAUDE.md coding standards that are not enforced by ruff or ty.

## What Changes

- Add missing test coverage for streaming-related code paths
- Review all modified files for CLAUDE.md compliance
- Fix any non-compliant code patterns

## Capabilities

### New Capabilities

None - this is a quality improvement change.

### Modified Capabilities

None - no spec-level behavior changes, only test coverage and code quality improvements.

## Impact

- `src/psi_agent/session/runner.py` - 23 missing lines, 2 partials
- `src/psi_agent/channel/repl/client.py` - 8 missing lines, 2 partials
- `src/psi_agent/channel/repl/repl.py` - 4 missing lines, 1 partial
- `src/psi_agent/channel/cli/cli.py` - 2 missing lines
- `src/psi_agent/channel/repl/cli.py` - 2 missing lines
