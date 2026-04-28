## Why

The current REPL implementation maintains its own message history and sends the entire history to session on each request. However, session also maintains its own history. This results in duplicate history management and inefficient data transfer - channel sends 11 messages when session only needs the latest user message.

The root cause: `repl-channel` spec incorrectly requires channel to manage history, violating the architectural principle that session is the single source of truth for conversation state.

## What Changes

- **BREAKING**: Remove history management from REPL channel
- Channel now sends only the current user message to session
- Session remains the single source of truth for conversation history
- Update `repl-channel` spec to remove history management requirements

## Capabilities

### New Capabilities

None - this is a fix to existing behavior.

### Modified Capabilities

- `repl-channel`: Remove requirement for REPL to maintain and send conversation history. Channel now sends only the current user message.

## Impact

- `src/psi_agent/channel/repl/repl.py` - Remove `self.history` and related logic
- `src/psi_agent/channel/repl/client.py` - Change `send_message` to accept single message instead of message list
- `openspec/specs/repl-channel/spec.md` - Update spec to reflect new behavior
- Tests in `tests/channel/repl/` - Update to match new API
