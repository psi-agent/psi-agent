## Why

The session module has inconsistent logging coverage and one defensive programming issue. Some critical operations lack DEBUG-level logs, making it harder to trace execution flow during debugging. Additionally, there's a potential issue with null content handling that could cause errors.

## What Changes

- Add missing DEBUG logs in `runner.py` for:
  - Tool call reconstruction details
  - History compaction calls
  - System prompt cache status
- Add DEBUG log in `tool_executor.py` for parallel execution start
- Fix defensive programming issue in `server.py` line 79 where `user_message.get('content') or ''` could mask issues

## Capabilities

### New Capabilities

None - this is an internal improvement to logging and defensive coding.

### Modified Capabilities

None - no spec-level behavior changes, only implementation improvements.

## Impact

- `src/psi_agent/session/runner.py` — Add DEBUG logs
- `src/psi_agent/session/tool_executor.py` — Add DEBUG log for parallel execution
- `src/psi_agent/session/server.py` — Fix defensive programming issue
