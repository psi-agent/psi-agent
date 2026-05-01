## Why

The session module's CLAUDE.md documentation was created before the recent code quality improvements. After extracting `_parse_streaming_response` as a shared helper method and adding consistent DEBUG logging, the documentation should reflect these architectural changes to help future developers understand the streaming parsing design.

## What Changes

- **Update runner.py module description**: Add mention of `_parse_streaming_response` helper method for centralized SSE parsing
- **Update streaming processing section**: Clarify that both `_run_conversation` and `_stream_conversation` use the shared parsing helper
- **Add internal methods section**: Document key private methods in SessionRunner that are important for understanding the architecture

## Capabilities

### New Capabilities

None - this is a documentation update only.

### Modified Capabilities

None - no spec-level behavior changes, only documentation improvements.

## Impact

- `src/psi_agent/session/CLAUDE.md` — Documentation updates to reflect current architecture