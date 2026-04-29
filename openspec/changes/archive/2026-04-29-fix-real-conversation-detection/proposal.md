## Why

The `examples/an-openclaw-like-workspace` implementation has three inconsistencies with OpenClaw that cause DIFF.md's claim of "Real Conversation Detection 已实现" to be inaccurate:

1. **`is_real_conversation_message()` signature mismatch**: OpenClaw accepts `(message, messages, index)` and performs a 20-message lookback for tool results, while the current implementation only accepts `(message)` and returns `False` for all tool results.

2. **`_has_meaningful_text()` heartbeat handling is incomplete**: OpenClaw uses `stripHeartbeatToken()` to handle `HEARTBEAT_OK` embedded in markup (e.g., `**HEARTBEAT_OK**`, `<b>HEARTBEAT_OK</b>`) or with trailing punctuation. The current implementation only does simple `== HEARTBEAT_OK` comparison.

3. **`SILENT_TOKEN` value differs from OpenClaw**: OpenClaw uses `"NO_REPLY"` while the current implementation uses `"SILENT_TOKEN"`. This should be aligned for OpenClaw compatibility.

## What Changes

- Fix `is_real_conversation_message()` to accept `(message, history, index)` and implement tool result lookback logic
- Add `TOOL_RESULT_REAL_CONVERSATION_LOOKBACK = 20` constant
- Implement `strip_heartbeat_token()` function to handle `HEARTBEAT_OK` with markup/punctuation
- Update `_has_meaningful_text()` to use `strip_heartbeat_token()` instead of simple comparison
- Change `SILENT_TOKEN` from `"SILENT_TOKEN"` to `"NO_REPLY"` to match OpenClaw

## Capabilities

### New Capabilities

(none - this is a bug fix)

### Modified Capabilities

- `real-conversation-detection`: Complete implementation matching OpenClaw's behavior for tool result messages, heartbeat token stripping, and silent reply token

## Impact

- `examples/an-openclaw-like-workspace/systems/system.py`:
  - Add `TOOL_RESULT_REAL_CONVERSATION_LOOKBACK` constant
  - Add `strip_heartbeat_token()` function
  - Modify `_has_meaningful_text()` to use proper heartbeat stripping
  - Modify `is_real_conversation_message()` signature and add lookback logic
  - Modify `_contains_real_conversation_messages()` to pass history and index
  - Change `SILENT_TOKEN` value to `"NO_REPLY"`
