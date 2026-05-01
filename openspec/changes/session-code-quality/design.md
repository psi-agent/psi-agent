## Context

The session module's `runner.py` has two methods (`_run_conversation` and `_stream_conversation`) that both handle streaming responses from the AI component. These methods have ~80 lines of nearly identical streaming parsing logic, violating DRY principles and making maintenance harder.

Additionally, logging coverage is inconsistent across the module, and error handling patterns differ between streaming and non-streaming code paths.

## Goals / Non-Goals

**Goals:**
- Reduce code duplication by extracting shared streaming parsing logic
- Add missing DEBUG logs for better traceability
- Improve code maintainability

**Non-Goals:**
- Changing external behavior or API
- Adding new features
- Major refactoring beyond the identified issues

## Decisions

### Streaming Parsing Extraction

**Decision**: Extract streaming parsing into a private async generator method `_parse_streaming_response()`.

**Rationale**: Both `_run_conversation` and `_stream_conversation` need to:
1. Read SSE lines from response content
2. Parse JSON chunks
3. Extract content, reasoning, and tool_calls from delta
4. Handle malformed data gracefully

By extracting this into a helper that yields `(content, reasoning, tool_calls)` tuples, we eliminate ~80 lines of duplicate code.

**Alternative considered**: Keep duplication but add comments. Rejected because it doesn't solve the maintenance burden.

### Logging Additions

| Location | Log Message | Level |
|----------|-------------|-------|
| `_stream_conversation` | Request body | DEBUG |
| `server._handle_streaming` | Response completion | DEBUG |
| `tool_loader.load_all_tools` | Tools being loaded | DEBUG |
| `schedule.load_schedule` | Successful load | DEBUG |

### Error Handling Consistency

Both methods already handle errors appropriately for their context:
- `_run_conversation`: Returns error response dict
- `_stream_conversation`: Yields error SSE chunk

This is the correct behavior for each context, so no changes needed.

## Risks / Trade-offs

**Refactoring risk**: Extracting streaming logic could introduce bugs.
→ Mitigation: Comprehensive test coverage exists; run all tests after changes.

**Performance**: Adding more DEBUG logs has minimal overhead since they're only evaluated when DEBUG level is enabled.
