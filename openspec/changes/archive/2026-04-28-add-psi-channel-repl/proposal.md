## Why

psi-agent currently lacks a simple interactive interface for testing and development. While `psi-channel-tui` is planned for a full terminal UI, a lightweight REPL (Read-Eval-Print Loop) interface would provide quick, iterative interaction with the agent without the overhead of a full TUI. This is essential for development, debugging, and quick testing of agent behavior.

## What Changes

- Add new `psi-channel-repl` component under `src/psi_agent/channel/repl/`
- Implement a simple REPL loop that:
  - Reads user input from stdin
  - Sends messages to psi-session via Unix socket
  - Displays responses to stdout
  - Maintains conversation history for context
- Add CLI entry point `psi-channel-repl`
- Support graceful exit with Ctrl+D or `/quit` command

## Capabilities

### New Capabilities

- `repl-channel`: Interactive REPL interface for continuous conversation with the agent, supporting message history and graceful exit

### Modified Capabilities

None. This is a new component with no changes to existing specs.

## Impact

- **New code**: `src/psi_agent/channel/repl/` module with `__init__.py`, `config.py`, `client.py`, `cli.py`
- **Dependencies**: No new external dependencies (uses stdlib `asyncio` for async I/O)
- **Entry points**: Add `psi-channel-repl` CLI command to `pyproject.toml`
- **No breaking changes**: Existing components remain unchanged
