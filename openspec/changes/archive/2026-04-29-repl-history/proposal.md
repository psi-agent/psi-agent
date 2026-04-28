## Why

The REPL channel currently uses `InMemoryHistory` from prompt-toolkit, which means input history is lost when the session ends. Users need persistent history across REPL sessions to recall and reuse previously entered commands and messages.

## What Changes

- Add persistent history storage for REPL input
- History file stored at `~/.cache/psi-agent/repl_history.txt`
- History persists across REPL sessions
- Use prompt-toolkit's `FileHistory` for automatic file-based history management

## Capabilities

### New Capabilities

- `repl-persistent-history`: Persistent input history for REPL channel, stored in platform cache directory

### Modified Capabilities

- `repl-history-navigation`: Update to use persistent file-based history instead of in-memory history

## Impact

- `src/psi_agent/channel/repl/repl.py` - Replace `InMemoryHistory` with `FileHistory`
- `src/psi_agent/channel/repl/config.py` - Add optional history file path configuration
- `~/.cache/psi-agent/` - New directory for storing history file
