## Why

When processing streaming responses from LLM providers, the session component crashes when encountering delta chunks where `tool_calls` field exists but has a `null` value. This occurs because the code checks for key presence (`"tool_calls" in delta`) but doesn't handle the case where the value is `None`, leading to `TypeError: 'NoneType' object is not iterable` when calling `list.extend(None)`.

This is a critical bug that breaks the entire streaming flow when using certain LLM providers (like Tencent's hy3 model via OpenRouter) that include `tool_calls: null` in their streaming delta chunks.

## What Changes

- Fix null value handling in streaming delta processing for `tool_calls` field
- Add defensive null checks before calling `list.extend()` on delta fields
- Ensure robust handling of LLM provider variations in streaming response format

## Capabilities

### New Capabilities

None - this is a bug fix.

### Modified Capabilities

None - this is an implementation-level fix, not a spec-level behavior change.

## Impact

- **Affected code**: `src/psi_agent/session/runner.py` - `_stream_conversation()` method, lines 561-562
- **Affected components**: psi-session
- **Affected providers**: Any LLM provider that returns `tool_calls: null` in streaming delta chunks (observed with Tencent hy3 model via OpenRouter)
- **No API changes**: Internal fix only, no external API modifications