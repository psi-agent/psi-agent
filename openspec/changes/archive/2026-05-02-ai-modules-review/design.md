## Context

The psi-ai-* modules (openai_completions and anthropic_messages) are LLM provider adapters that follow a consistent design pattern. After reviewing all files in both modules, several inconsistencies were identified:

1. **Streaming request logging gap**: `_non_stream_request` logs the full request body at DEBUG level, but `_stream_request` does not. This makes debugging streaming issues harder.

2. **Streaming completion logging gap**: The session module's server logs "SSE stream completed successfully" at DEBUG level before the INFO log, but the AI module servers only log at INFO level.

3. **Redundant assertions**: Both server modules have `assert self.client is not None` immediately after assignment in `start()`, which is unnecessary.

4. **Non-streaming tool_calls translation bug**: `translate_anthropic_to_openai()` does not extract `tool_use` content blocks from Anthropic responses. When `stop_reason == "tool_use"`, the `finish_reason` is correctly set to `"tool_calls"`, but the `message.tool_calls` field is missing. This breaks the OpenAI format contract.

5. **Streaming error handling gap**: When AI modules yield an error chunk during streaming (`{"error": "...", "status_code": ...}`), the session module's `_parse_streaming_response` silently ignores it.

## Goals / Non-Goals

**Goals:**
- Achieve logging consistency between streaming and non-streaming code paths
- Achieve logging consistency with session module patterns
- Remove unnecessary code
- Fix protocol translation bug to ensure consistent interface
- Improve error handling robustness

**Non-Goals:**
- Adding new features
- Major refactoring
- Changing any external behavior (except fixing the bug)

## Decisions

### Add DEBUG log for streaming request body

**Decision**: Add `logger.debug(f"Request body: {json.dumps(body, ensure_ascii=False, indent=2)}")` at the start of `_stream_request` in both client modules.

**Rationale**: Parity with `_non_stream_request` which already has this log. This helps debug streaming issues.

**Alternative considered**: Log only a summary. Rejected because the full body is needed for debugging.

### Add DEBUG log for streaming completion

**Decision**: Add `logger.debug("SSE stream completed successfully")` before the INFO log in `_handle_streaming` of both server modules.

**Rationale**: Parity with session module's server which has this pattern. Provides consistent DEBUG-level traceability.

### Remove redundant assertions

**Decision**: Remove `assert self.client is not None` after assignment in `start()` method of both server modules.

**Rationale**: The assertion immediately follows `self.client = ...` assignment, so it can never fail. The None check in `_handle_chat_completions` is sufficient.

### Fix non-streaming tool_calls translation

**Decision**: Modify `translate_anthropic_to_openai()` to extract `tool_use` content blocks and populate `message.tool_calls` field.

**Rationale**: The current implementation only extracts `text` content blocks, completely ignoring `tool_use` blocks. This breaks the OpenAI format contract when Anthropic returns tool calls.

**Implementation**:
1. Iterate through `content_blocks` to find `type == "tool_use"` blocks
2. Convert each `tool_use` block to OpenAI `tool_calls` format
3. Add `tool_calls` to the `message` dict when present

**Impact**: Session always uses streaming internally, so this bug doesn't affect normal operation. However, it's a protocol compliance issue that could affect other clients.

### Handle streaming error chunks in session

**Decision**: Add error detection in `_parse_streaming_response` to check for `error` field in chunks.

**Rationale**: When streaming fails mid-stream, the error is silently ignored, leading to empty responses. Users should see the error message.

**Implementation**: Check if chunk contains `error` field, log the error, and raise an exception or yield an error indicator.

## Risks / Trade-offs

**Minimal change risk**: The changes are small and focused.
→ Mitigation: Run all existing tests to verify no regressions.

**Protocol fix risk**: The tool_calls fix changes behavior, but only for non-streaming responses which are not used by session.
→ Mitigation: Add tests to verify the fix works correctly.

## Protocol Translation Consistency Analysis

### Verified Consistent ✓

| Aspect | OpenAI | Anthropic | Status |
|--------|--------|-----------|--------|
| [DONE] marker | `data: [DONE]\n\n` | `data: [DONE]\n\n` (via translator) | ✓ |
| Error chunk format | `{"error": str, "status_code": int}` | Same | ✓ |
| Streaming tool_calls | Via SDK | Via translator `StreamingTranslator` | ✓ |
| finish_reason mapping | Via SDK | `end_turn→stop, tool_use→tool_calls, max_tokens→length` | ✓ |

### Fixed by this change

| Aspect | Issue | Fix |
|--------|-------|-----|
| Non-streaming tool_calls | `translate_anthropic_to_openai` ignores `tool_use` blocks | Extract and convert to `message.tool_calls` |

### Robustness Patterns

Both modules use defensive `.get()` access consistently. The translator has proper null checks throughout.
