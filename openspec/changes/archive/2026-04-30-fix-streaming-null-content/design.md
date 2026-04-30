## Context

The session runner's `_stream_conversation` method processes streaming SSE responses from the AI component. When the LLM returns a tool call without text content, the delta object contains `content: null`. The current code at line 559 attempts to log the content chunk by slicing `delta['content'][:100]`, which fails when content is `None`.

This is a straightforward null-safety bug. The OpenAI API specification allows `content` to be `null` in streaming deltas, particularly when tool calls are being streamed.

## Goals / Non-Goals

**Goals:**
- Fix the crash when `delta['content']` is `None`
- Maintain existing behavior for non-null content
- Ensure debug logging continues to work correctly

**Non-Goals:**
- Changing the streaming protocol or API
- Modifying how tool calls are processed
- Adding new features or capabilities

## Decisions

**Decision 1: Guard the debug log statement**

Add a null check before slicing the content string:
```python
if delta.get("content") is not None:
    content_chunks.append(delta["content"])
    logger.debug(f"Stream content chunk: {delta['content'][:100]}...")
```

Rationale: This is the minimal fix that addresses the root cause. Using `delta.get("content")` is safer than `delta["content"]` and the explicit `is not None` check handles the null case correctly.

**Alternative considered**: Using `delta.get("content", "")` with a default empty string. Rejected because:
- `None` and `""` have different semantic meanings in the OpenAI API
- We should preserve the distinction between "no content" and "empty content"
- The content_chunks list should only contain actual content, not placeholders

## Risks / Trade-offs

**Risk: Other code paths may have similar null-safety issues**
→ Mitigation: The fix is localized and tested. If similar issues exist elsewhere, they can be addressed separately.

**Risk: The fix changes behavior for empty string content**
→ Mitigation: Empty string `""` is truthy-falsy different from `None`. The check `is not None` correctly handles both cases - empty strings will still be logged (though `[:100]` of `""` is just `""`).
