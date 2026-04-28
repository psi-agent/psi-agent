## Why

After rebasing onto main, the CLI architecture was refactored to use tyro's native subcommand mechanism. The telegram channel CLI was updated to use the new dataclass pattern, but the spec was not updated to reflect these changes. This proposal updates the telegram-channel spec to align with the new tyro CLI requirements.

## What Changes

- Update `telegram-channel` spec to include tyro CLI requirements
- Add requirements for dataclass-based CLI implementation
- Add requirements for subcommand integration with `psi-agent channel telegram`

## Capabilities

### New Capabilities

None - no new capabilities being introduced.

### Modified Capabilities

- `telegram-channel`: Add requirements for tyro dataclass CLI pattern and subcommand integration

## Impact

- `openspec/specs/telegram-channel/spec.md` - Add new requirements
- No code changes required - implementation already complete
