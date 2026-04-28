## Why

After moving `channel/cli.py` to `channel/cli/cli.py`, the test file `tests/channel/test_cli.py` has broken imports. Additionally, for consistency with `tests/channel/repl/`, the CLI tests should also be in a subdirectory.

## What Changes

- Move `tests/channel/test_cli.py` to `tests/channel/cli/test_cli.py`
- Update import statements in the test file to use the new module path
- Update exports in `channel/cli/cli.py` to expose `send_message` function for testing

## Capabilities

### New Capabilities

None

### Modified Capabilities

None (this is a test structure fix, no spec-level behavior changes)

## Impact

- `tests/channel/test_cli.py` → `tests/channel/cli/test_cli.py`
- `src/psi_agent/channel/cli/cli.py` - ensure `send_message` is exported
