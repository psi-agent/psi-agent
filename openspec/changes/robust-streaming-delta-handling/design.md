## Context

The `_reconstruct_tool_calls` method processes streaming tool call deltas from LLM providers. The OpenAI streaming API specification allows fields to be `null` or absent in delta chunks. Different providers (OpenRouter, Tencent hy3, etc.) may have slightly different implementations of this spec.

The current implementation uses string concatenation (`+=`) to merge delta chunks, but doesn't verify that the values being concatenated are actually strings (not `None`).

## Goals / Non-Goals

**Goals:**
- Fix null-safety in `_reconstruct_tool_calls` for `name` and `arguments` fields
- Establish a pattern for defensive handling of streaming deltas
- Ensure all string operations on delta fields check for `None` first

**Non-Goals:**
- Changing the streaming protocol or API
- Refactoring the entire streaming code path (only fix the immediate issues)
- Adding validation for all possible delta fields (focus on the crash points)

## Decisions

**Decision 1: Use explicit null checks before concatenation**

In `_reconstruct_tool_calls`, check that values are not `None` before concatenating:

```python
if "name" in func and func["name"] is not None:
    tool_calls_map[index]["function"]["name"] += func["name"]
if "arguments" in func and func["arguments"] is not None:
    tool_calls_map[index]["function"]["arguments"] += func["arguments"]
```

Rationale: This is the minimal fix that addresses the crash. The pattern `"key" in dict and dict["key"] is not None` is explicit and clear.

**Alternative considered**: Using `func.get("name", "")` with default empty string. Rejected because:
- The first chunk may have `name: null` (not just missing), and `get()` would return `""` which is correct
- But `get()` with default doesn't distinguish between "field is null" and "field is absent"
- For concatenation purposes, both cases should result in no change to the accumulated value
- Actually, this alternative would work fine for this use case

**Decision 2: Consider using `get()` with default for concatenation**

Actually, for concatenation specifically, using `get()` with empty string default is cleaner:

```python
name_part = func.get("name") or ""
if name_part:
    tool_calls_map[index]["function"]["name"] += name_part
args_part = func.get("arguments") or ""
if args_part:
    tool_calls_map[index]["function"]["arguments"] += args_part
```

This handles both `None` and missing field cases uniformly.

## Risks / Trade-offs

**Risk: Other fields in delta may also have null issues**
→ Mitigation: The fix is localized to the known crash points. If other issues appear, they can be fixed similarly.

**Risk: The pattern may not be applied consistently in future code**
→ Mitigation: Add a comment or docstring noting the defensive pattern requirement.