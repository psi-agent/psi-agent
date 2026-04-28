## Why

The current REPL implementation uses basic `sys.stdin.readline()` which lacks essential features for a production-ready interactive interface: no input history navigation, no line editing, no multi-line support, and poor async integration. Using `prompt-toolkit` with its native async API will provide a modern, feature-rich REPL experience with proper async handling.

## What Changes

- Replace `sys.stdin.readline()` with `prompt-toolkit`'s async `PromptSession`
- Add input history navigation (up/down arrows)
- Add line editing capabilities (left/right arrows, home/end, etc.)
- Add multi-line input support
- Add customizable prompt styling
- Improve async integration by using `prompt-toolkit`'s native async API instead of `run_in_executor`

## Capabilities

### New Capabilities

- `repl-input-editing`: Line editing with cursor movement, text insertion/deletion
- `repl-history-navigation`: Navigate through previous inputs using arrow keys
- `repl-multi-line`: Support for multi-line input with proper handling

### Modified Capabilities

- `repl-channel`: Update input handling to use prompt-toolkit async API instead of basic stdin reading
