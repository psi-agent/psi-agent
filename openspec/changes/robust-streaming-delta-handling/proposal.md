## Why

The session runner's streaming delta handling code has multiple null-safety issues that cause crashes when processing LLM responses from different providers. The root cause is **defensive coding inconsistency**: the code assumes all fields in streaming deltas are present and non-null, but the OpenAI streaming API specification allows fields to be `null` or absent in delta chunks.

This is the second crash in the same code path within minutes:
1. First crash: `delta['content']` was `None` when slicing for debug log
2. Second crash: `func['name']` was `None` when concatenating in `_reconstruct_tool_calls`

The pattern indicates a systemic issue: **the code doesn't validate that values are non-null before operating on them**.

## What Changes

- Add null-safety checks in `_reconstruct_tool_calls` for `name` and `arguments` fields
- Add null-safety checks in streaming delta processing for all fields
- Establish a defensive coding pattern: always check `is not None` before string operations

## Capabilities

### New Capabilities

None - this is a bug fix.

### Modified Capabilities

- `streaming-null-handling`: Extend to cover null values in tool_calls reconstruction (currently only covers `tool_calls: null` and `content: null` in delta)

## Impact

- **Affected Code**: `src/psi_agent/session/runner.py` - `_reconstruct_tool_calls` method and streaming delta processing
- **Affected Components**: psi-session
- **Design Issue**: The streaming code path lacks systematic null-safety. Each field access should be guarded.

## Root Cause Analysis

The OpenAI streaming API sends tool calls as incremental deltas:

```json
// First chunk - has id and name
{"delta": {"tool_calls": [{"index": 0, "id": "call_123", "function": {"name": "bash", "arguments": ""}}]}}

// Subsequent chunks - only have arguments (name is null/absent)
{"delta": {"tool_calls": [{"index": 0, "function": {"arguments": "{\"com"}}]}}
```

The current code uses `+=` concatenation assuming values are always strings, but:
- `func["name"]` can be `None` in subsequent chunks
- `func["arguments"]` can be `None` in some chunks
- The `"name" in func` check passes even when `func["name"]` is `None`
