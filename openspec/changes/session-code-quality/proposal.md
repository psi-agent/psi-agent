## Why

The session module has code quality issues that affect maintainability and debugging: significant code duplication between `_run_conversation` and `_stream_conversation`, inconsistent logging coverage, and inconsistent error handling patterns.

## What Changes

- **Refactor streaming response parsing**: Extract common streaming parsing logic from `_run_conversation` and `_stream_conversation` into a shared helper method
- **Add missing DEBUG logs**:
  - `_stream_conversation`: Log request body like `_run_conversation` does
  - `server.py`: Log streaming response completion details
  - `tool_loader.py`: Log which tools are being loaded in `load_all_tools`
  - `schedule.py`: Add DEBUG log in `load_schedule` for successful loads
- **Standardize error handling**: Ensure consistent error response format between streaming and non-streaming paths

## Capabilities

### New Capabilities

None - this is an internal code quality improvement.

### Modified Capabilities

None - no spec-level behavior changes, only implementation improvements.

## Impact

- `src/psi_agent/session/runner.py` — Refactor streaming parsing, add DEBUG log
- `src/psi_agent/session/server.py` — Add DEBUG log for streaming
- `src/psi_agent/session/tool_loader.py` — Add DEBUG log for tool loading
- `src/psi_agent/session/schedule.py` — Add DEBUG log for schedule loading
