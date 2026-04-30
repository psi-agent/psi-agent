## Context

The `AnthropicMessagesClient._stream_request()` method in `src/psi_agent/ai/anthropic_messages/client.py` incorrectly passes a `stream` parameter to the Anthropic SDK's `messages.stream()` method. The SDK's streaming API doesn't accept this parameter because streaming is implied by using `.stream()` instead of `.create()`.

Current problematic code (line 127):
```python
body["stream"] = True
try:
    logger.info("Starting streaming request")

    async def anthropic_event_stream() -> AsyncGenerator[str]:
        async with client.messages.stream(**body) as stream:  # Error: 'stream' kwarg
            ...
```

## Goals / Non-Goals

**Goals:**
- Fix the `TypeError` by removing the `stream` key from the body before calling `messages.stream()`

**Non-Goals:**
- No API changes
- No behavioral changes to streaming functionality
- No changes to non-streaming code path

## Decisions

**Decision: Remove `stream` key before calling `.stream()`**

The `stream` key is set on line 127 and passed to `messages.stream()` on line 133. The fix is to simply remove this line since:
1. The `stream` parameter is not accepted by `messages.stream()`
2. Streaming is already implied by using `.stream()` instead of `.create()`
3. The `stream` key is already present in the body from the translator (line 65 in `translator.py`)

## Risks / Trade-offs

No risks. This is a straightforward bug fix with no behavioral changes.
