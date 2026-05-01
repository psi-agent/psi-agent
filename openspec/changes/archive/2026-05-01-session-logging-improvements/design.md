## Context

The session module has grown to include multiple subsystems (message processing, tool execution, workspace watching, scheduling). Logging coverage is inconsistent across these subsystems, making debugging difficult. The CLAUDE.md specifies that DEBUG level should log all component communication and execution details.

## Goals / Non-Goals

**Goals:**
- Add DEBUG logs for critical operations that are currently missing logging
- Fix defensive programming issue in server.py
- Ensure consistency with the logging standards in CLAUDE.md

**Non-Goals:**
- Changing any external behavior
- Adding new features
- Refactoring existing logic beyond logging additions

## Decisions

### Logging Additions

| Location | Log Message | Rationale |
|----------|-------------|-----------|
| `runner._reconstruct_tool_calls` | DEBUG: Number of chunks and resulting tool calls | Trace streaming tool call reconstruction |
| `runner._build_messages` | DEBUG: System prompt status and message count | Trace message building |
| `runner._complete_fn` | DEBUG: Request for compaction | Trace history compaction calls |
| `tool_executor.execute_tools_parallel` | DEBUG: Starting parallel execution of N tools | Trace parallel execution start |

### Defensive Programming Fix

In `server.py` line 79, the current code:
```python
logger.debug(f"Processing user message: {(user_message.get('content') or '')[:100]}...")
```

Should be changed to properly handle None:
```python
content = user_message.get('content')
content_preview = content[:100] if content else ""
logger.debug(f"Processing user message: {content_preview}...")
```

This follows the defensive programming pattern specified in CLAUDE.md.

## Risks / Trade-offs

**Log verbosity**: Adding more DEBUG logs increases verbosity.
→ Mitigation: DEBUG is only enabled during development/debugging, not in production.

**Performance**: String formatting for logs has minimal overhead.
→ Mitigation: Only format strings when DEBUG level is enabled.
