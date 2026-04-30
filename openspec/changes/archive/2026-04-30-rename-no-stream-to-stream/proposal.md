## Why

The current CLI parameter `no_stream` produces confusing command-line flags (`--no-no-stream` and `--no-stream`) due to tyro's automatic negation handling for boolean flags. This is unintuitive for users. Renaming to `stream` with default `True` will produce cleaner flags: `--stream` (default) and `--no-stream` to disable.

## What Changes

- Rename `no_stream: bool = False` to `stream: bool = True` in three CLI modules:
  - `src/psi_agent/channel/cli/cli.py`
  - `src/psi_agent/channel/repl/cli.py`
  - `src/psi_agent/channel/telegram/cli.py`
- Update all internal logic from `not self.no_stream` to `self.stream`
- Update docstrings to reflect the new parameter semantics
- Update all test files to use the new parameter name

## Capabilities

### New Capabilities

None - this is a pure refactoring of existing functionality.

### Modified Capabilities

- `channel-cli`: CLI parameter renamed from `no_stream` to `stream` with inverted default
- `repl-channel`: CLI parameter renamed from `no_stream` to `stream` with inverted default
- `telegram-channel`: CLI parameter renamed from `no_stream` to `stream` with inverted default

## Impact

- **CLI users**: Will use `--stream` (default) or `--no-stream` instead of `--no-no-stream`/`--no-stream`
- **API users**: No impact - internal config objects already use `stream` parameter
- **Tests**: All test assertions on `no_stream` will be updated to use `stream`
