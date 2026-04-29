## 1. Constants and Helper Functions

- [x] 1.1 Change `SILENT_TOKEN` from `"SILENT_TOKEN"` to `"NO_REPLY"`
- [x] 1.2 Add `TOOL_RESULT_REAL_CONVERSATION_LOOKBACK = 20` constant
- [x] 1.3 Add `strip_heartbeat_token()` function to handle HEARTBEAT_OK with markup/punctuation

## 2. Core Function Fixes

- [x] 2.1 Update `_has_meaningful_text()` to use `strip_heartbeat_token()` instead of simple comparison
- [x] 2.2 Update `is_real_conversation_message()` signature to accept `(message, history, index)`
- [x] 2.3 Implement tool result lookback logic in `is_real_conversation_message()`
- [x] 2.4 Update `_contains_real_conversation_messages()` to pass history and index via `enumerate()`

## 3. Verification

- [x] 3.1 Run `ruff format` on modified files
- [x] 3.2 Run `ruff check` on modified files
- [x] 3.3 Run `ty check` for type checking
- [x] 3.4 Verify the implementation matches OpenClaw's behavior for all three fixes