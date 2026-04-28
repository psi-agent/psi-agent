## Why

The `a-simple-bash-only-workspace` is meant to be a minimal example workspace. However, the recent addition of tool result pairing repair made it unnecessarily complex. The simple workspace should remain simple - just basic skill scanning for system prompt and simple message count-based truncation for compaction.

## What Changes

- Remove tool result pairing repair functions from `a-simple-bash-only-workspace/systems/system.py`
- Simplify `compact_history()` to just keep the most recent 20 messages (no token counting, no repair)
- Simplify `build_system_prompt()` to just concatenate skill descriptions with basic guidelines

## Capabilities

### New Capabilities

- None (this is a simplification, not a new capability)

### Modified Capabilities

- None (the simple workspace has no formal specs; this is an implementation simplification)

## Impact

- **Affected files**:
  - `examples/a-simple-bash-only-workspace/systems/system.py` - Simplify to minimal implementation
- **Backward compatibility**: The interface remains the same, only the implementation is simplified
- **Dependencies**: None
