## Context

The session component's `_stream_conversation()` method processes streaming responses from the AI component. When parsing SSE chunks, it extracts delta fields including `tool_calls`. The current implementation checks for key presence but doesn't handle null values.

**Current problematic code** (runner.py:561-562):
```python
if "tool_calls" in delta:
    tool_calls_data.extend(delta["tool_calls"])
```

**Observed behavior from Tencent hy3 model via OpenRouter**:
```json
{"delta":{"content":"","function_call":null,"refusal":null,"role":"assistant","tool_calls":null,...}
```

The `tool_calls` key exists but has value `null`, causing `list.extend(None)` to fail.

## Goals / Non-Goals

**Goals:**
- Fix the crash when `tool_calls` field has null value in streaming delta
- Make streaming delta processing robust against null values for any field that expects an iterable
- Maintain backward compatibility with existing providers

**Non-Goals:**
- Changing the streaming protocol or API
- Adding new features or capabilities
- Modifying error handling beyond the null check

## Decisions

**Decision 1: Add explicit null check before extend**

Use `if delta.get("tool_calls")` instead of `if "tool_calls" in delta` to handle both missing key and null value cases.

Rationale:
- Simple one-line fix with minimal risk
- `dict.get()` returns `None` for both missing key and null value
- Empty list `[]` is falsy, but we don't want to extend with empty list anyway (no-op)
- Alternative: explicit `is not None` check - more verbose, same effect

**Decision 2: Apply same pattern to other delta fields**

Review all delta field accesses in the streaming loop and apply defensive null checks where appropriate.

## Risks / Trade-offs

**Risk: Provider behavior variation**
- Some providers might send empty list `[]` vs null vs missing key
- Mitigation: The fix handles all three cases correctly - `None`, `[]`, and missing key all result in no extend operation

**Risk: Missing other null-prone fields**
- Other fields like `content` might also have null values
- Mitigation: Check all delta field accesses in the streaming loop; `content` is handled differently (string concatenation, not extend)
